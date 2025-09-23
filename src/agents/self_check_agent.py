"""
Agente Self-Check - Verifica se há evidências suficientes para responder.
"""

from typing import Dict, Any, List
from langchain_core.language_models.base import BaseLanguageModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SelfCheckAgent:
    """
    Agente responsável por verificar se há evidências suficientes para responder.
    """
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Inicializa o agente self-check.
        
        Args:
            llm: Instância do modelo de linguagem
        """
        self.llm = llm
        self.system_prompt = """Você é um agente especializado em avaliar a qualidade e suficiência de evidências para verificação de notícias.

Sua função é determinar se há evidências suficientes para verificar uma afirmação.

REGRAS IMPORTANTES:
1. Se os documentos são RELEVANTES para o tópico da afirmação, marque como SUFFICIENT
2. Não exija evidências diretas - evidências indiretas são suficientes
3. Se há informações sobre o mesmo tópico (ex: vacinas, saúde, clima), considere como SUFFICIENT
4. Use conhecimento geral + evidências dos documentos para avaliar
5. Seja permissivo quando há relevância temática

EXEMPLOS:
- Afirmação: "Vacina causa autismo" + Documentos sobre "Vacinas são seguras" = SUFFICIENT
- Afirmação: "Aquecimento global é real" + Documentos sobre "Mudanças climáticas" = SUFFICIENT
- Afirmação: "Exercícios melhoram saúde" + Documentos sobre "Vacinas COVID" = INSUFFICIENT"""

    def process_query(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa uma consulta verificando se há evidências suficientes.
        
        Args:
            query: Consulta/afirmação a ser verificada
            documents: Lista de documentos com evidências
            
        Returns:
            Dicionário com resultado da verificação
        """
        try:
            if not documents:
                return {
                    "has_evidence": False,
                    "evidence_quality": "INSUFFICIENT",
                    "reasoning": "Nenhum documento encontrado",
                    "confidence": 0.0,
                    "query": query,
                    "num_documents": 0,
                    "agent": "SELF_CHECK"
                }
            
            # Preparar contexto dos documentos
            doc_context = self._prepare_document_context(documents)
            
            # Prompt de avaliação melhorado
            evaluation_prompt = f"""
            Afirmação a verificar: "{query}"
            
            Documentos encontrados:
            {doc_context}
            
            Avalie se há evidências suficientes para verificar esta afirmação.
            
            IMPORTANTE: Seja PERMISSIVO! Se os documentos são sobre o mesmo tópico geral, marque como SUFFICIENT.
            
            Exemplos de relevância:
            - "Vacina causa autismo" + documentos sobre "vacinas são seguras" = SUFFICIENT
            - "Aquecimento global é real" + documentos sobre "mudanças climáticas" = SUFFICIENT
            - "Exercícios melhoram saúde" + documentos sobre "vacinas COVID" = INSUFFICIENT
            
            Considere:
            1. Os documentos são sobre o mesmo tópico geral da afirmação?
            2. Há informações que podem apoiar ou contradizer a afirmação?
            3. As fontes são confiáveis?
            4. Há informações suficientes para uma conclusão baseada em evidências + conhecimento geral?
            
            Se há relevância temática, marque como SUFFICIENT mesmo que não seja uma resposta direta.
            
            Responda no formato:
            DECISÃO: [SUFFICIENT/INSUFFICIENT/CONTRADICTORY]
            CONFIANÇA: [0.0-1.0]
            JUSTIFICATIVA: [explicação detalhada]
            """
            
            # Fazer chamada para o LLM
            response = self.llm.invoke(evaluation_prompt)
            
            # Processar resposta
            result = self._parse_evaluation_response(response)
            
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
                "num_documents": len(documents),
                "agent": "SELF_CHECK"
            }
    
    def _prepare_document_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Prepara o contexto dos documentos para o prompt.
        
        Args:
            documents: Lista de documentos
            
        Returns:
            String com contexto formatado
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            source = doc.get("source", "Fonte desconhecida")
            url = doc.get("url", "")
            
            context_parts.append(f"Documento {i}:")
            context_parts.append(f"Fonte: {source}")
            if url:
                context_parts.append(f"URL: {url}")
            context_parts.append(f"Conteúdo: {content[:500]}...")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _parse_evaluation_response(self, response) -> Dict[str, Any]:
        """
        Processa a resposta do LLM para extrair informações estruturadas.
        
        Args:
            response: Resposta do LLM
            
        Returns:
            Dicionário com avaliação processada
        """
        try:
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            lines = response_text.strip().split('\n')
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
            
            # Determinar se há evidências suficientes - MAIS PERMISSIVO
            has_evidence = decision in ["SUFFICIENT", "CONTRADICTORY"]
            
            # Se a confiança é alta (>0.6) e há documentos relevantes, considerar como SUFFICIENT
            if confidence > 0.6 and decision == "INSUFFICIENT":
                # Verificar se há palavras-chave que indicam relevância
                reasoning_lower = reasoning.lower()
                relevant_keywords = ["relevante", "relacionado", "tópico", "assunto", "similar"]
                if any(keyword in reasoning_lower for keyword in relevant_keywords):
                    decision = "SUFFICIENT"
                    has_evidence = True
            
            return {
                "has_evidence": has_evidence,
                "evidence_quality": decision,
                "reasoning": reasoning,
                "confidence": confidence,
                "source_reliability": {
                    "total_sources": 1,  # Simplificado
                    "reliable_sources": 1 if has_evidence else 0,
                    "reliability_score": confidence,
                    "is_reliable": has_evidence
                },
                "should_proceed": has_evidence
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta: {str(e)}")
            return {
                "has_evidence": False,
                "evidence_quality": "INSUFFICIENT",
                "reasoning": f"Erro no processamento: {str(e)}",
                "confidence": 0.0,
                "source_reliability": {
                    "total_sources": 0,
                    "reliable_sources": 0,
                    "reliability_score": 0.0,
                    "is_reliable": False
                },
                "should_proceed": False
            }
