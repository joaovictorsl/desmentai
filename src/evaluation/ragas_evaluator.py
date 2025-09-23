"""
Sistema de avaliação usando RAGAS para o DesmentAI.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
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


class RAGASEvaluator:
    """Classe para avaliação do DesmentAI usando RAGAS."""
    
    def __init__(self, results_dir: str = "eval/results"):
        """
        Inicializa o avaliador RAGAS.
        
        Args:
            results_dir: Diretório para salvar resultados
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar métricas (usar configuração padrão do RAGAS)
        # Nota: Reordenar métricas para evitar incompatibilidade entre answer_relevancy e context_precision
        # answer_relevancy deve vir por último para evitar IndexError
        self.metrics = [
            faithfulness,
            context_precision,
            context_recall,
            answer_correctness,
            answer_relevancy  # Colocado por último para evitar conflito com context_precision
        ]
        
        # Não configurar LLM customizado para evitar incompatibilidades
        self.llm = None
        logger.info("Usando configuração padrão do RAGAS (sem LLM customizado)")
    
    def _setup_llm(self):
        """
        Configura o LLM para o RAGAS (prioriza OpenAI, fallback para Gemini).
        
        Returns:
            LLM configurado (OpenAI ou Gemini)
        """
        # Tentar OpenAI primeiro (melhor compatibilidade com RAGAS)
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
        
        # Fallback para Gemini
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
        
        # Se nenhuma chave estiver configurada
        logger.warning("Nenhuma API key configurada. RAGAS usará configuração padrão.")
        return None
    
    def create_test_dataset(self) -> Dataset:
        """
        Cria dataset de teste para avaliação.
        
        Returns:
            Dataset de teste
        """
        test_data = {
            "question": [
                "O Brasil é o maior produtor de café do mundo?",
                "As vacinas contra COVID-19 causam autismo?",
                "A Terra é plana?",
                "O aquecimento global é causado pelo homem?",
                "As eleições brasileiras são seguras?",
                "Exercícios físicos melhoram a saúde mental?",
                "A inflação no Brasil está controlada?",
                "O governo brasileiro aprovou uma nova lei de proteção de dados?",
                "O sistema eleitoral brasileiro é confiável?",
                "As mudanças climáticas são uma farsa?"
            ],
            "answer": [
                "Sim, o Brasil é o maior produtor de café do mundo, responsável por cerca de 1/3 da produção global.",
                "Não, não há evidências científicas que comprovem que vacinas contra COVID-19 causam autismo.",
                "Não, a Terra é esférica, não plana. Evidências científicas incontestáveis comprovam isso.",
                "Sim, o consenso científico é claro: as mudanças climáticas são causadas principalmente pela atividade humana.",
                "Sim, o sistema eleitoral brasileiro é considerado um dos mais seguros do mundo.",
                "Sim, estudos científicos comprovam que exercícios físicos regulares melhoram a saúde mental.",
                "Parcialmente, a inflação no Brasil apresentou redução significativa em 2024, mas ainda está próxima da meta.",
                "Sim, o Congresso Nacional aprovou uma nova lei que fortalece a proteção de dados pessoais no Brasil.",
                "Sim, o sistema eleitoral brasileiro possui múltiplas camadas de segurança e é considerado confiável.",
                "Não, as mudanças climáticas são uma realidade científica comprovada por evidências incontestáveis."
            ],
            "contexts": [
                ["O Brasil é realmente o maior produtor de café do mundo, responsável por cerca de 1/3 da produção global. O país produz aproximadamente 60 milhões de sacas de café por ano."],
                ["Não há evidências científicas que comprovem que vacinas contra COVID-19 causam autismo. Estudos científicos extensivos mostram que as vacinas são seguras e eficazes."],
                ["A Terra é esférica, não plana. Evidências científicas incontestáveis incluem fotos de satélites, observações astronômicas e medições de sombras."],
                ["O consenso científico é claro: as mudanças climáticas são causadas principalmente pela atividade humana. Dados da NASA mostram aumento de 1,1°C desde 1880."],
                ["O sistema eleitoral brasileiro é considerado um dos mais seguros do mundo. A urna eletrônica possui múltiplas camadas de segurança."],
                ["Estudos científicos comprovam que exercícios físicos regulares melhoram significativamente a saúde mental, reduzindo sintomas de ansiedade e depressão."],
                ["A inflação no Brasil apresentou redução significativa em 2024. O IPCA acumulado em 12 meses ficou em 4,5%, próximo ao centro da meta."],
                ["O Congresso Nacional aprovou uma nova lei que fortalece a proteção de dados pessoais no Brasil. A medida estabelece regras mais rígidas."],
                ["O sistema eleitoral brasileiro possui múltiplas camadas de segurança, incluindo criptografia, auditoria e verificação independente."],
                ["As mudanças climáticas são uma realidade científica comprovada. Dados da NASA mostram que a temperatura média da Terra aumentou 1,1°C desde 1880."]
            ],
            "ground_truth": [
                "O Brasil é o maior produtor de café do mundo, responsável por cerca de 1/3 da produção global.",
                "As vacinas contra COVID-19 não causam autismo. Esta é uma informação falsa sem base científica.",
                "A Terra é esférica, não plana. Esta é uma afirmação falsa baseada em pseudociência.",
                "O aquecimento global é causado principalmente pela atividade humana, conforme comprovado por evidências científicas.",
                "As eleições brasileiras são seguras e confiáveis, com sistema eleitoral considerado um dos mais seguros do mundo.",
                "Exercícios físicos melhoram a saúde mental, conforme comprovado por estudos científicos.",
                "A inflação no Brasil está próxima da meta, mas ainda requer monitoramento contínuo.",
                "O governo brasileiro aprovou uma nova lei de proteção de dados que fortalece a privacidade dos cidadãos.",
                "O sistema eleitoral brasileiro é confiável e seguro, com múltiplas camadas de proteção.",
                "As mudanças climáticas são uma realidade científica comprovada, não uma farsa."
            ]
        }
        
        return Dataset.from_dict(test_data)
    
    def evaluate_desmentai(self, desmentai, test_dataset: Optional[Dataset] = None) -> Dict[str, Any]:
        """
        Avalia o DesmentAI usando RAGAS.
        
        Args:
            desmentai: Instância do DesmentAI
            test_dataset: Dataset de teste (opcional)
            
        Returns:
            Resultados da avaliação
        """
        try:
            logger.info("Iniciando avaliação do DesmentAI...")
            
            if test_dataset is None:
                test_dataset = self.create_test_dataset()
            
            evaluation_data = self._prepare_evaluation_data(desmentai, test_dataset)
            
            logger.info("Executando avaliação RAGAS...")
            
            # Sempre usar configuração padrão do RAGAS para evitar incompatibilidades
            logger.info("Usando configuração padrão do RAGAS")
            result = evaluate(
                Dataset.from_dict(evaluation_data),
                metrics=self.metrics
            )
            
            results = self._process_evaluation_results(result)
            
            self._save_results(results)
            
            logger.info("Avaliação concluída com sucesso!")
            return results
            
        except Exception as e:
            logger.error(f"Erro na avaliação: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _prepare_evaluation_data(self, desmentai, test_dataset: Dataset) -> Dict[str, List]:
        """
        Prepara dados para avaliação.
        
        Args:
            desmentai: Instância do DesmentAI
            test_dataset: Dataset de teste
            
        Returns:
            Dados preparados para avaliação
        """
        questions = test_dataset["question"]
        answers = []
        contexts = []
        
        logger.info(f"Processando {len(questions)} perguntas...")
        
        for i, question in enumerate(questions):
            logger.info(f"Processando pergunta {i+1}/{len(questions)}: {question[:50]}...")
            
            try:
                result = desmentai.verify_news(question)
                
                answer = result.get("final_answer", "")
                answers.append(answer)
                
                agent_results = result.get("agent_results", {})
                retriever_result = agent_results.get("retriever", {})
                documents = retriever_result.get("documents", [])
                
                doc_contexts = []
                for doc in documents[:3]:  # Limitar a 3 documentos
                    content = doc.get("content", "")
                    if content:
                        doc_contexts.append(content)
                
                contexts.append(doc_contexts if doc_contexts else [""])
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Erro ao processar pergunta {i+1}: {str(e)}")
                answers.append(f"Erro: {str(e)}")
                contexts.append([""])
        
        return {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": test_dataset["ground_truth"]
        }
    
    def _process_evaluation_results(self, result) -> Dict[str, Any]:
        """
        Processa resultados da avaliação RAGAS.
        
        Args:
            result: Resultado da avaliação RAGAS
            
        Returns:
            Resultados processados
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
        """
        Salva resultados da avaliação.
        
        Args:
            results: Resultados da avaliação
        """
        try:
            timestamp = int(time.time())
            
            summary_file = self.results_dir / f"evaluation_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(results["summary"], f, indent=2, ensure_ascii=False)
            
            detailed_file = self.results_dir / f"evaluation_detailed_{timestamp}.json"
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(results["detailed_results"], f, indent=2, ensure_ascii=False)
            
            report_file = self.results_dir / f"evaluation_report_{timestamp}.md"
            self._generate_markdown_report(results, report_file)
            
            logger.info(f"Resultados salvos em: {self.results_dir}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
    
    def _generate_markdown_report(self, results: Dict[str, Any], file_path: Path):
        """
        Gera relatório em Markdown.
        
        Args:
            results: Resultados da avaliação
            file_path: Caminho do arquivo
        """
        try:
            summary = results["summary"]
            
            report = f"""# Relatório de Avaliação DesmentAI

## Resumo Executivo

- **Total de Perguntas:** {summary['total_questions']}
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

## Análise

### Melhor Métrica
- **{summary['best_performing_metric']}**: {summary['average_scores'][summary['best_performing_metric']]:.3f}

### Pior Métrica
- **{summary['worst_performing_metric']}**: {summary['average_scores'][summary['worst_performing_metric']]:.3f}

## Recomendações

1. **Melhorar Faithfulness**: Focar em respostas mais baseadas nas fontes
2. **Melhorar Answer Relevancy**: Garantir que as respostas sejam mais diretas
3. **Melhorar Context Precision**: Buscar contextos mais precisos
4. **Melhorar Context Recall**: Garantir cobertura completa do tópico
5. **Melhorar Answer Correctness**: Verificar precisão das respostas

## Detalhes Técnicos

- **Data da Avaliação**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Métricas Utilizadas**: RAGAS (Faithfulness, Answer Relevancy, Context Precision, Context Recall, Answer Correctness)
- **Modelo de Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS

---
*Relatório gerado automaticamente pelo sistema de avaliação DesmentAI*
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
    
    def run_quick_evaluation(self, desmentai) -> Dict[str, Any]:
        """
        Executa avaliação rápida com poucas perguntas.
        
        Args:
            desmentai: Instância do DesmentAI
            
        Returns:
            Resultados da avaliação rápida
        """
        try:
            logger.info("Executando avaliação rápida...")
            
            quick_data = {
                "question": [
                    "O Brasil é o maior produtor de café do mundo?",
                    "As vacinas contra COVID-19 causam autismo?",
                    "A Terra é plana?"
                ],
                "answer": [
                    "Sim, o Brasil é o maior produtor de café do mundo.",
                    "Não, as vacinas contra COVID-19 não causam autismo.",
                    "Não, a Terra é esférica, não plana."
                ],
                "contexts": [
                    ["O Brasil é o maior produtor de café do mundo, responsável por 1/3 da produção global."],
                    ["Não há evidências científicas que comprovem que vacinas causam autismo."],
                    ["A Terra é esférica, conforme comprovado por evidências científicas."]
                ],
                "ground_truth": [
                    "O Brasil é o maior produtor de café do mundo.",
                    "As vacinas contra COVID-19 não causam autismo.",
                    "A Terra é esférica, não plana."
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

