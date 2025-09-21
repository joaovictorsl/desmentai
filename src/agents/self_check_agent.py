"""
Agente SelfCheck - Verifica se há evidências suficientes para responder.
"""

from typing import Dict, Any, List
from langchain_core.language_models.base import BaseLanguageModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SelfCheckAgent:
    """Agente responsável por verificar se há evidências suficientes para responder."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Inicializa o agente self-check.
        
        Args:
            llm: Instância do modelo de linguagem
        """
        self.llm = llm
        self.system_prompt = """Você é um agente especializado em verificação de evidências para combate a fake news.

Sua função é analisar se os documentos encontrados contêm evidências suficientes para verificar uma afirmação.

CRITÉRIOS DE AVALIAÇÃO:
1. RELEVÂNCIA: Os documentos são diretamente relevantes para a afirmação?
2. EVIDÊNCIA DIRETA: Há evidências diretas que apoiem ou contradigam a afirmação?
3. CONFIABILIDADE: As fontes são confiáveis e verificáveis?
4. COMPLETUDE: Há informações suficientes para uma conclusão?

RESPOSTAS POSSÍVEIS:
- "SUFFICIENT": Evidências suficientes encontradas
- "INSUFFICIENT": Evidências insuficientes
- "CONTRADICTORY": Evidências contraditórias encontradas

SEMPRE justifique sua decisão."""

    def evaluate_evidence(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Avalia se há evidências suficientes nos documentos encontrados.
        
        Args:
            query: Consulta/afirmação a ser verificada
            documents: Lista de documentos encontrados
            
        Returns:
            Dicionário com avaliação das evidências
        """
        try:
            if not documents:
                return {
                    "has_evidence": False,
                    "evidence_quality": "INSUFFICIENT",
                    "reasoning": "Nenhum documento encontrado",
                    "confidence": 0.0
                }
            
            # Preparar contexto dos documentos
            doc_context = self._prepare_document_context(documents)
            
            # Prompt de avaliação
            evaluation_prompt = f"""
            Afirmação a verificar: "{query}"
            
            Documentos encontrados:
            {doc_context}
            
            Avalie se há evidências suficientes para verificar esta afirmação.
            
            Considere:
            1. Os documentos são relevantes para a afirmação?
            2. Há evidências diretas que apoiem ou contradigam a afirmação?
            3. As fontes são confiáveis?
            4. Há informações suficientes para uma conclusão?
            
            Responda no formato:
            DECISÃO: [SUFFICIENT/INSUFFICIENT/CONTRADICTORY]
            CONFIANÇA: [0.0-1.0]
            JUSTIFICATIVA: [explicação detalhada]
            """
            
            # Fazer chamada para o LLM
            response = self.llm.invoke(evaluation_prompt)
            
            # Processar resposta
            result = self._parse_evaluation_response(response.content)
            
            # Adicionar metadados
            result.update({
                "query": query,
                "num_documents": len(documents),
                "agent": "SELF_CHECK"
            })
            
            logger.info(f"Self-check concluído: {result['evidence_quality']} (confiança: {result['confidence']})")
            return result
            
        except Exception as e:
            logger.error(f"Erro na avaliação de evidências: {str(e)}")
            return {
                "has_evidence": False,
                "evidence_quality": "INSUFFICIENT",
                "reasoning": f"Erro na avaliação: {str(e)}",
                "confidence": 0.0,
                "query": query,
                "num_documents": len(documents) if documents else 0,
                "agent": "SELF_CHECK"
            }
    
    def _prepare_document_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Prepara o contexto dos documentos para avaliação.
        
        Args:
            documents: Lista de documentos
            
        Returns:
            String com contexto formatado
        """
        context_parts = []
        
        for i, doc in enumerate(documents[:5], 1):  # Limitar a 5 documentos
            content = doc["content"][:500]  # Limitar tamanho
            source = doc["metadata"].get("source", "Fonte desconhecida")
            score = doc.get("relevance_score", 0.0)
            
            context_parts.append(f"""
            Documento {i}:
            Fonte: {source}
            Relevância: {score:.2f}
            Conteúdo: {content}...
            """)
        
        return "\n".join(context_parts)
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """
        Processa a resposta do LLM para extrair a avaliação.
        
        Args:
            response: Resposta do LLM
            
        Returns:
            Dicionário com avaliação processada
        """
        try:
            lines = response.strip().split('\n')
            decision = "INSUFFICIENT"
            confidence = 0.5
            reasoning = "Resposta não processada corretamente"
            
            for line in lines:
                line = line.strip()
                if line.startswith("DECISÃO:"):
                    decision = line.split(":", 1)[1].strip().upper()
                elif line.startswith("CONFIANÇA:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        confidence = 0.5
                elif line.startswith("JUSTIFICATIVA:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            # Determinar se há evidências suficientes
            has_evidence = decision in ["SUFFICIENT", "CONTRADICTORY"]
            
            return {
                "has_evidence": has_evidence,
                "evidence_quality": decision,
                "reasoning": reasoning,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta: {str(e)}")
            return {
                "has_evidence": False,
                "evidence_quality": "INSUFFICIENT",
                "reasoning": f"Erro no processamento: {str(e)}",
                "confidence": 0.0
            }
    
    def check_source_reliability(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Avalia a confiabilidade das fontes dos documentos.
        
        Args:
            documents: Lista de documentos
            
        Returns:
            Dicionário com avaliação das fontes
        """
        try:
            sources = []
            for doc in documents:
                source = doc["metadata"].get("source", "Fonte desconhecida")
                sources.append(source)
            
            # Fontes confiáveis conhecidas
            trusted_sources = [
                "agencialupa.com.br",
                "aosfatos.org",
                "boatos.org",
                "g1.globo.com",
                "folha.uol.com.br",
                "estadao.com.br",
                "oglobo.globo.com"
            ]
            
            reliable_count = 0
            for source in sources:
                if any(trusted in source.lower() for trusted in trusted_sources):
                    reliable_count += 1
            
            reliability_score = reliable_count / len(sources) if sources else 0.0
            
            return {
                "total_sources": len(sources),
                "reliable_sources": reliable_count,
                "reliability_score": reliability_score,
                "is_reliable": reliability_score >= 0.5
            }
            
        except Exception as e:
            logger.error(f"Erro na verificação de fontes: {str(e)}")
            return {
                "total_sources": 0,
                "reliable_sources": 0,
                "reliability_score": 0.0,
                "is_reliable": False
            }
    
    def process_query(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa uma consulta completa, verificando evidências.
        
        Args:
            query: Consulta do usuário
            documents: Lista de documentos encontrados
            
        Returns:
            Resultado completo da verificação
        """
        try:
            # Avaliar evidências
            evidence_result = self.evaluate_evidence(query, documents)
            
            # Verificar confiabilidade das fontes
            source_reliability = self.check_source_reliability(documents)
            
            # Combinar resultados
            result = {
                **evidence_result,
                "source_reliability": source_reliability,
                "should_proceed": evidence_result["has_evidence"] and source_reliability["is_reliable"]
            }
            
            logger.info(f"Self-check processou consulta: {result['should_proceed']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento da consulta: {str(e)}")
            return {
                "has_evidence": False,
                "evidence_quality": "INSUFFICIENT",
                "reasoning": f"Erro no processamento: {str(e)}",
                "confidence": 0.0,
                "should_proceed": False,
                "query": query,
                "num_documents": len(documents) if documents else 0,
                "agent": "SELF_CHECK"
            }
