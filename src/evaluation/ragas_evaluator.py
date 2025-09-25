"""
Sistema de avaliação RAGAS v2 para o DesmentAI - Com dados reais do sistema.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness
)
from datasets import Dataset
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGASEvaluatorV2:
    """Classe para avaliação do DesmentAI usando RAGAS com dados reais."""
    
    def __init__(self, results_dir: str = "eval/results"):
        """
        Inicializa o avaliador RAGAS v2.
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics = [
            faithfulness,
            context_precision,
            context_recall,
            answer_correctness,
            answer_relevancy
        ]
        
        self.llm = None
        logger.info("Usando configuração padrão do RAGAS (sem LLM customizado)")
    
    def _setup_llm(self):
        """
        Configura o LLM para o RAGAS (prioriza OpenAI, fallback para Gemini).
        """
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            try:
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    api_key=openai_key,
                    temperature=0.1
                )
                logger.info("LLM OpenAI configurado: gpt-3.5-turbo")
                return llm
            except Exception as e:
                logger.warning(f"Erro ao configurar OpenAI: {str(e)}")
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            try:
                model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash')
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=gemini_key,
                    temperature=0.1,
                    convert_system_message_to_human=True
                )
                logger.info(f"LLM Gemini configurado: {model_name}")
                return llm
            except Exception as e:
                logger.warning(f"Erro ao configurar Gemini: {str(e)}")
        
        logger.warning("Nenhuma API key configurada. RAGAS usará configuração padrão.")
        return None
    
    def create_test_dataset(self) -> Dataset:
        """
        Cria dataset de teste para avaliação com ground truth manual.
        """
        test_data = {
            "question": [
                "A USAID, agência dos EUA, financiou a imprensa brasileira para aumentar os números de mortes por Covid-19 e influenciar as eleições de 2022?",
                "O governo irá notificar e taxar adultos que moram com os pais sem pagar aluguel a partir de 2026?",
                "O novo sistema de recolhimento automático de impostos da Receita Federal irá criar uma taxa extra para transações via Pix?",
                "O presidente Lula teve seu microfone cortado durante o discurso na Assembleia Geral da ONU em setembro de 2025?",
                "Os artistas Caetano Veloso, Chico Buarque, Gilberto Gil e Djavan foram beneficiados pela Lei da Anistia de 1979?",
                "Uma mensagem dos Correios sobre 'taxa de encomenda' pendente para liberação de um pacote é verdadeira?",
                "O Brasil saiu oficialmente do Mapa da Fome da ONU em 2025?",
                "É verdade que o desmatamento na Amazônia foi reduzido pela metade nos últimos dois anos (2023-2025)?",
                "O governo de São Paulo removeu a escolta policial do delegado Ruy Fontes após sua aposentadoria?",
                "Um vídeo mostra uma cobra gigante mergulhando em um rio na floresta amazônica?"
            ],
            "ground_truth": [
                "FALSO: Não há nenhum registro de transferência de dinheiro da USAID para veículos de imprensa brasileiros. A checagem mostra que os recursos da agência no Brasil foram destinados a projetos sociais e de meio ambiente (Projeto Comprova, 2025).",
                "FALSO: A Receita Federal negou oficialmente o boato, afirmando que a alegação 'não faz o menor sentido'. A legislação atual já prevê isenção para cessão gratuita de imóveis a parentes de primeiro grau (Estadão Verifica, 2025).",
                "FALSO: A Receita Federal esclareceu que o novo sistema automatiza a cobrança de tributos já existentes sobre a venda de produtos e serviços por empresas, e não cria nenhuma taxa extra para o cidadão ou para o Pix (Estadão Verifica, 2025).",
                "FALSO: A fala do presidente na Assembleia Geral da ONU em 2025 ocorreu sem interrupções. Vídeos que circulam são de um evento diferente, em 2024, quando ele ultrapassou o tempo de fala (Aos Fatos, 2025).",
                "FALSO: Os nomes dos artistas não constam na lista oficial de anistiados políticos. Além disso, Caetano, Chico e Gil retornaram do exílio no início da década de 1970, antes da promulgação da lei em 1979 (Estadão Verifica, 2025).",
                "FALSO: Trata-se de um golpe. Os Correios e outras transportadoras afirmam que não enviam links por WhatsApp, SMS ou e-mail para cobrar taxas e liberar encomendas retidas (Fato ou Fake G1, 2025).",
                "VERDADEIRO: A Organização das Nações Unidas para a Alimentação e a Agricultura (FAO) confirmou em julho de 2025 que o Brasil saiu do Mapa da Fome, por ter um percentual de pessoas em subalimentação abaixo do critério estabelecido (Estadão Verifica, 2025).",
                "VERDADEIRO: Dados do INPE (Instituto Nacional de Pesquisas Espaciais) mostram que a área desmatada na Amazônia Legal em 2024 foi de 6,5 mil km², uma redução de aproximadamente 56% em comparação com os 11,5 mil km² de 2022 (Estadão Verifica, 2025).",
                "FALSO: A Secretaria de Segurança Pública de São Paulo informou que o delegado aposentado nunca teve escolta pessoal fornecida pelo Estado, portanto, ela não poderia ter sido retirada (Aos Fatos, 2025).",
                "FALSO: O vídeo é uma criação digital feita com Inteligência Artificial. Ferramentas de detecção apontaram 99% de probabilidade de o conteúdo ser gerado artificialmente, além de apresentar diversas incoerências visuais (Fato ou Fake G1, 2025)."
            ],
            "source": [
                "Projeto Comprova / Estadão Verifica",
                "Estadão Verifica",
                "Estadão Verifica",
                "Aos Fatos",
                "Estadão Verifica",
                "Fato ou Fake G1",
                "Estadão Verifica / FAO",
                "Estadão Verifica / INPE",
                "Aos Fatos",
                "Fato ou Fake G1"
            ]
        }
        
        return Dataset.from_dict(test_data)
    
    def evaluate_desmentai(self, desmentai, test_dataset: Optional[Dataset] = None) -> Dict[str, Any]:
        """
        Avalia o DesmentAI usando RAGAS com dados reais do sistema.
        """
        try:
            logger.info("Iniciando avaliação do DesmentAI com dados reais...")
            
            if test_dataset is None:
                test_dataset = self.create_test_dataset()
            
            evaluation_data = self._generate_real_evaluation_data(desmentai, test_dataset)
            
            logger.info("Executando avaliação RAGAS com dados reais...")
            
            # Usar configuração padrão do RAGAS
            result = evaluate(
                Dataset.from_dict(evaluation_data),
                metrics=self.metrics
            )
            
            results = self._process_evaluation_results(result)
            
            # Adicionar informações sobre o dataset real
            results["dataset_info"] = {
                "total_questions": len(evaluation_data["question"]),
                "questions_with_answers": len([a for a in evaluation_data["answer"] if a and not a.startswith("Erro:")]),
                "questions_with_contexts": len([c for c in evaluation_data["contexts"] if c and c != [""]]),
                "evaluation_type": "real_system_data"
            }
            
            self._save_results(results)
            
            logger.info("Avaliação concluída com sucesso!")
            return results
            
        except Exception as e:
            logger.error(f"Erro na avaliação: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _generate_real_evaluation_data(self, desmentai, test_dataset: Dataset) -> Dict[str, List]:
        questions = test_dataset["question"]
        ground_truths = test_dataset["ground_truth"]
        sources = test_dataset["source"] if "source" in test_dataset.column_names else []
        
        answers = []
        contexts = []
        
        logger.info(f"Processando {len(questions)} perguntas com o sistema real...")
        
        for i, question in enumerate(questions):
            logger.info(f"Processando pergunta {i+1}/{len(questions)}: {question[:50]}...")
            
            try:
                result = desmentai.verify_news(question)
                
                if result.get("success", False):
                    answer = result.get("final_answer", "")
                    answers.append(answer)
                    
                    agent_results = result.get("agent_results", {})
                    retriever_result = agent_results.get("retriever", {})
                    documents = retriever_result.get("documents", [])
                    
                    doc_contexts = []
                    for doc in documents[:5]:
                        content = doc.get("content", "")
                        if content:
                            truncated_content = content[:500] + "..." if len(content) > 500 else content
                            doc_contexts.append(truncated_content)
                    
                    contexts.append(doc_contexts if doc_contexts else [""])
                    
                    logger.info(f"✅ Pergunta {i+1} processada com sucesso")
                    logger.info(f"   - Documentos encontrados: {len(documents)}")
                    logger.info(f"   - Contextos extraídos: {len(doc_contexts)}")
                    
                else:
                    error_msg = result.get("error", "Erro desconhecido")
                    answers.append(f"Erro: {error_msg}")
                    contexts.append([""])
                    logger.warning(f"❌ Falha na pergunta {i+1}: {error_msg}")
                
                # Pausa para evitar rate limiting
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Erro ao processar pergunta {i+1}: {str(e)}")
                answers.append(f"Erro: {str(e)}")
                contexts.append([""])
        
        return {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths
        }
    
    def _process_evaluation_results(self, result) -> Dict[str, Any]:
        """
        Processa resultados da avaliação RAGAS.
        """
        try:
            df = result.to_pandas()
            
            metrics_summary = {
                "faithfulness": df["faithfulness"].mean(),
                "answer_relevancy": df["answer_relevancy"].mean(),
                "context_precision": df["context_precision"].mean(),
                "context_recall": df["context_recall"].mean(),
                "answer_correctness": df["answer_correctness"].mean()
            }
            
            analysis = {
                "total_questions": len(df),
                "average_scores": metrics_summary,
                "best_performing_metric": max(metrics_summary, key=metrics_summary.get),
                "worst_performing_metric": min(metrics_summary, key=metrics_summary.get),
                "overall_score": sum(metrics_summary.values()) / len(metrics_summary)
            }
            
            problematic_questions = df[df["faithfulness"] < 0.7]
            analysis["problematic_questions"] = len(problematic_questions)
            
            analysis["performance_by_question"] = []
            for idx, row in df.iterrows():
                analysis["performance_by_question"].append({
                    "question": row.get("question", "")[:100] + "...",
                    "faithfulness": row["faithfulness"],
                    "answer_relevancy": row["answer_relevancy"],
                    "context_precision": row["context_precision"],
                    "context_recall": row["context_recall"],
                    "answer_correctness": row["answer_correctness"]
                })
            
            return {
                "summary": analysis,
                "detailed_results": df.to_dict("records"),
                "raw_results": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resultados: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _save_results(self, results: Dict[str, Any]):
        try:
            timestamp = int(time.time())
            
            summary_file = self.results_dir / f"evaluation_summary_v2_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(results["summary"], f, indent=2, ensure_ascii=False)
            
            detailed_file = self.results_dir / f"evaluation_detailed_v2_{timestamp}.json"
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(results["detailed_results"], f, indent=2, ensure_ascii=False)
            
            report_file = self.results_dir / f"evaluation_report_v2_{timestamp}.md"
            self._generate_markdown_report(results, report_file)
            
            logger.info(f"Resultados salvos em: {self.results_dir}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
    
    def _generate_markdown_report(self, results: Dict[str, Any], file_path: Path):
        try:
            summary = results["summary"]
            dataset_info = results.get("dataset_info", {})
            
            report = f"""# Relatório de Avaliação DesmentAI v2 - Dados Reais

## Resumo Executivo

- **Total de Perguntas:** {summary['total_questions']}
- **Perguntas Processadas com Sucesso:** {dataset_info.get('questions_with_answers', 'N/A')}
- **Perguntas com Contextos:** {dataset_info.get('questions_with_contexts', 'N/A')}
- **Pontuação Geral:** {summary['overall_score']:.3f}
- **Questões Problemáticas:** {summary['problematic_questions']}

## Métricas de Qualidade

| Métrica | Pontuação | Descrição |
|---------|-----------|-----------|
| Faithfulness | {summary['average_scores']['faithfulness']:.3f} | Fidelidade da resposta às fontes |
| Answer Relevancy | {summary['average_scores']['answer_relevancy']:.3f} | Relevância da resposta à pergunta |
| Context Precision | {summary['average_scores']['context_precision']:.3f} | Precisão do contexto recuperado |
| Context Recall | {summary['average_scores']['context_recall']:.3f} | Cobertura do contexto relevante |
| Answer Correctness | {summary['average_scores']['answer_correctness']:.3f} | Correção da resposta |

## Análise Detalhada

### Melhor Métrica
- **{summary['best_performing_metric']}**: {summary['average_scores'][summary['best_performing_metric']]:.3f}

### Pior Métrica
- **{summary['worst_performing_metric']}**: {summary['average_scores'][summary['worst_performing_metric']]:.3f}

## Questões Problemáticas

{summary['problematic_questions']} questões apresentaram faithfulness < 0.7

## Detalhes Técnicos

- **Data da Avaliação**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Tipo de Avaliação**: Dados reais do sistema
- **Métricas Utilizadas**: RAGAS (Faithfulness, Answer Relevancy, Context Precision, Context Recall, Answer Correctness)
- **Modelo de Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **Busca**: Híbrida (Local + Web)

---
*Relatório gerado automaticamente pelo sistema de avaliação DesmentAI v2 com dados reais*
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
    
    def run_quick_evaluation(self, desmentai) -> Dict[str, Any]:
        """
        Executa avaliação rápida com poucas perguntas.
        """
        try:
            logger.info("Executando avaliação rápida...")
            
            quick_data = {
                "question": [
                    "O Brasil é o maior produtor de café do mundo?",
                    "As vacinas contra COVID-19 causam autismo?",
                    "A Terra é plana?"
                ],
                "ground_truth": [
                    "VERDADEIRO: O Brasil é o maior produtor de café do mundo, responsável por cerca de 1/3 da produção global (FAO, 2023).",
                    "FALSO: Não há evidências científicas que comprovem que vacinas contra COVID-19 causam autismo (CDC, OMS, 2023).",
                    "FALSO: A Terra é esférica, não plana. Evidências científicas incontestáveis comprovam isso (NASA, 2023)."
                ],
                "source": [
                    "FAO (Organização das Nações Unidas para Alimentação e Agricultura)",
                    "CDC (Centers for Disease Control and Prevention) e OMS",
                    "NASA (National Aeronautics and Space Administration)"
                ]
            }
            
            test_dataset = Dataset.from_dict(quick_data)
            return self.evaluate_desmentai(desmentai, test_dataset)
            
        except Exception as e:
            logger.error(f"Erro na avaliação rápida: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
