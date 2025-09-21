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

# RAGAS imports
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness
)
from datasets import Dataset

# Configurar logging
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
        
        # Métricas a serem avaliadas
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness
        ]
    
    def create_test_dataset(self) -> Dataset:
        """
        Cria dataset de teste para avaliação.
        
        Returns:
            Dataset de teste
        """
        # Conjunto de perguntas de teste com gabaritos
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
            
            # Usar dataset padrão se não fornecido
            if test_dataset is None:
                test_dataset = self.create_test_dataset()
            
            # Preparar dados para avaliação
            evaluation_data = self._prepare_evaluation_data(desmentai, test_dataset)
            
            # Executar avaliação
            logger.info("Executando avaliação RAGAS...")
            result = evaluate(
                Dataset.from_dict(evaluation_data),
                metrics=self.metrics
            )
            
            # Processar resultados
            results = self._process_evaluation_results(result)
            
            # Salvar resultados
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
                # Verificar notícia
                result = desmentai.verify_news(question)
                
                # Extrair resposta
                answer = result.get("final_answer", "")
                answers.append(answer)
                
                # Extrair contextos (documentos encontrados)
                agent_results = result.get("agent_results", {})
                retriever_result = agent_results.get("retriever", {})
                documents = retriever_result.get("documents", [])
                
                # Preparar contextos
                doc_contexts = []
                for doc in documents[:3]:  # Limitar a 3 documentos
                    content = doc.get("content", "")
                    if content:
                        doc_contexts.append(content)
                
                contexts.append(doc_contexts if doc_contexts else [""])
                
                # Pequena pausa para não sobrecarregar
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
            # Converter para DataFrame
            df = result.to_pandas()
            
            # Calcular métricas médias
            metrics_summary = {
                "faithfulness": df["faithfulness"].mean(),
                "answer_relevancy": df["answer_relevancy"].mean(),
                "context_precision": df["context_precision"].mean(),
                "context_recall": df["context_recall"].mean(),
                "answer_correctness": df["answer_correctness"].mean()
            }
            
            # Análise detalhada
            analysis = {
                "total_questions": len(df),
                "average_scores": metrics_summary,
                "best_performing_metric": max(metrics_summary, key=metrics_summary.get),
                "worst_performing_metric": min(metrics_summary, key=metrics_summary.get),
                "overall_score": sum(metrics_summary.values()) / len(metrics_summary)
            }
            
            # Identificar questões problemáticas
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
            
            # Salvar resumo
            summary_file = self.results_dir / f"evaluation_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(results["summary"], f, indent=2, ensure_ascii=False)
            
            # Salvar resultados detalhados
            detailed_file = self.results_dir / f"evaluation_detailed_{timestamp}.json"
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(results["detailed_results"], f, indent=2, ensure_ascii=False)
            
            # Salvar relatório em Markdown
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
            
            # Dataset pequeno para teste rápido
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
