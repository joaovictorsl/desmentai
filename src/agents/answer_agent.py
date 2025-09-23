"""
Agente Answer - Gera respostas baseadas em evidências encontradas.
"""

from typing import Dict, Any, List
from langchain_core.language_models.base import BaseLanguageModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerAgent:
    """Agente responsável por gerar respostas baseadas em evidências."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Inicializa o agente answer.
        
        Args:
            llm: Instância do modelo de linguagem
        """
        self.llm = llm
        self.system_prompt = """Você é um agente especializado em gerar respostas verificadas para combate a fake news.

Sua função é criar respostas claras, precisas e baseadas em evidências encontradas.

REGRAS IMPORTANTES:
1. SEMPRE baseie sua resposta nas evidências fornecidas
2. INCLUA citações obrigatórias (fonte + URL/fragmento)
3. Seja objetivo e imparcial
4. Use linguagem clara e acessível
5. Indique claramente se a afirmação é VERDADEIRA, FALSA ou PARCIALMENTE VERDADEIRA
6. Explique o raciocínio por trás da conclusão

FORMATO DA RESPOSTA:
- CONCLUSÃO: [VERDADEIRA/FALSA/PARCIALMENTE VERDADEIRA/INSUFICIENTE]
- EVIDÊNCIAS: [lista das evidências encontradas]
- CITAÇÕES: [fonte + URL/fragmento para cada evidência]
- EXPLICAÇÃO: [explicação detalhada do raciocínio]"""

    def generate_answer(self, query: str, documents: List[Dict[str, Any]], evidence_quality: str, 
                       search_source: str = "unknown") -> Dict[str, Any]:
        """
        Gera uma resposta baseada nas evidências encontradas.
        
        Args:
            query: Consulta/afirmação a ser verificada
            documents: Lista de documentos com evidências
            evidence_quality: Qualidade das evidências (SUFFICIENT, INSUFFICIENT, etc.)
            
        Returns:
            Dicionário com a resposta gerada
        """
        try:
            if evidence_quality == "INSUFFICIENT":
                return self._generate_insufficient_evidence_response(query)
            
            # Preparar contexto das evidências
            evidence_context = self._prepare_evidence_context(documents)
            
            # Prompt para gerar resposta
            answer_prompt = f"""
            Afirmação a verificar: "{query}"
            
            Evidências encontradas:
            {evidence_context}
            
            Com base nas evidências fornecidas, gere uma resposta completa seguindo o formato especificado.
            
            IMPORTANTE:
            - Seja objetivo e baseado apenas nas evidências
            - Inclua citações específicas para cada evidência
            - Use linguagem clara e acessível
            - Indique claramente a conclusão sobre a veracidade da afirmação
            """
            
            # Fazer chamada para o LLM
            response = self.llm.invoke(answer_prompt)
            
            # Processar resposta
            result = self._parse_answer_response(response, documents, search_source)
            
            # Adicionar metadados
            result.update({
                "query": query,
                "evidence_quality": evidence_quality,
                "num_documents": len(documents),
                "agent": "ANSWER"
            })
            
            logger.info(f"Answer gerou resposta: {result.get('conclusion', 'UNKNOWN')}")
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {str(e)}")
            return {
                "conclusion": "ERRO",
                "answer": f"Erro ao gerar resposta: {str(e)}",
                "citations": [],
                "evidence_summary": [],
                "query": query,
                "evidence_quality": evidence_quality,
                "num_documents": len(documents) if documents else 0,
                "agent": "ANSWER"
            }
    
    def _generate_insufficient_evidence_response(self, query: str) -> Dict[str, Any]:
        """
        Gera resposta para casos de evidências insuficientes.
        
        Args:
            query: Consulta original
            
        Returns:
            Resposta padrão para evidências insuficientes
        """
        return {
            "conclusion": "INSUFICIENTE",
            "answer": f"Não foi possível encontrar informações suficientes para verificar a afirmação '{query}' em nossas fontes confiáveis. Recomendamos consultar fontes primárias ou especialistas para obter informações mais precisas.",
            "citations": [],
            "evidence_summary": [],
            "query": query,
            "evidence_quality": "INSUFFICIENT",
            "num_documents": 0,
            "agent": "ANSWER"
        }
    
    def _prepare_evidence_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Prepara o contexto das evidências para geração de resposta.
        
        Args:
            documents: Lista de documentos com evidências
            
        Returns:
            String com contexto formatado
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc["content"]
            source = doc["metadata"].get("source", "Fonte desconhecida")
            url = doc["metadata"].get("url", "")
            relevance = doc.get("relevance_score", 0.0)
            
            context_parts.append(f"""
            Evidência {i}:
            Fonte: {source}
            URL: {url}
            Relevância: {relevance:.2f}
            Conteúdo: {content}
            """)
        
        return "\n".join(context_parts)
    
    def _filter_documents_by_source(self, documents: List[Dict[str, Any]], search_source: str) -> List[Dict[str, Any]]:
        """
        Filtra documentos baseado na fonte da busca.
        
        Args:
            documents: Lista de documentos
            search_source: Fonte da busca (local_only, hybrid, web_only)
            
        Returns:
            Lista de documentos filtrados
        """
        if search_source == "local_only":
            # Apenas local: mostrar todos os documentos
            return documents
        elif search_source in ["hybrid", "web_only"]:
            # Híbrido ou apenas web: mostrar apenas documentos da web
            web_docs = [doc for doc in documents if doc.get("source") == "web"]
            logger.info(f"Filtrados {len(documents)} documentos para {len(web_docs)} documentos web")
            return web_docs
        else:
            # Fonte desconhecida: mostrar todos
            return documents
    
    def _parse_answer_response(self, response: str, documents: List[Dict[str, Any]], 
                              search_source: str = "unknown") -> Dict[str, Any]:
        """
        Processa a resposta do LLM para extrair componentes estruturados.
        
        Args:
            response: Resposta do LLM
            documents: Lista de documentos para extrair citações
            search_source: Fonte da busca (local_only, hybrid, web_only)
            
        Returns:
            Dicionário com resposta processada
        """
        try:
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            lines = response_text.strip().split('\n')
            conclusion = "INSUFICIENTE"
            answer = response_text
            citations = []
            evidence_summary = []
            
            # Extrair conclusão
            for line in lines:
                if line.startswith("CONCLUSÃO:"):
                    conclusion = line.split(":", 1)[1].strip().upper()
                    break
            
            # Filtrar documentos baseado na fonte da busca
            filtered_documents = self._filter_documents_by_source(documents, search_source)
            
            # Extrair citações dos documentos filtrados
            for doc in filtered_documents:
                source = doc["metadata"].get("source", "Fonte desconhecida")
                url = doc["metadata"].get("url", "")
                citation = {
                    "source": source,
                    "url": url,
                    "relevance_score": doc.get("relevance_score", 0.0)
                }
                citations.append(citation)
            
            # Extrair resumo das evidências dos documentos filtrados
            for doc in filtered_documents:
                evidence_summary.append({
                    "content": doc["content"][:200] + "...",
                    "source": doc["metadata"].get("source", "Fonte desconhecida")
                })
            
            return {
                "conclusion": conclusion,
                "answer": response_text,
                "citations": citations,
                "evidence_summary": evidence_summary
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta: {str(e)}")
            return {
                "conclusion": "ERRO",
                "answer": response,
                "citations": [],
                "evidence_summary": []
            }
    
    def format_citations(self, citations: List[Dict[str, Any]]) -> str:
        """
        Formata citações para exibição.
        
        Args:
            citations: Lista de citações
            
        Returns:
            String formatada com citações
        """
        if not citations:
            return "Nenhuma citação disponível."
        
        formatted_citations = []
        for i, citation in enumerate(citations, 1):
            source = citation.get("source", "Fonte desconhecida")
            url = citation.get("url", "")
            score = citation.get("relevance_score", 0.0)
            
            if url:
                formatted_citations.append(f"{i}. {source} - {url} (relevância: {score:.2f})")
            else:
                formatted_citations.append(f"{i}. {source} (relevância: {score:.2f})")
        
        return "\n".join(formatted_citations)
    
    def process_query(self, query: str, documents: List[Dict[str, Any]], evidence_quality: str, 
                     search_source: str = "unknown") -> Dict[str, Any]:
        """
        Processa uma consulta completa, gerando resposta baseada em evidências.
        
        Args:
            query: Consulta do usuário
            documents: Lista de documentos com evidências
            evidence_quality: Qualidade das evidências
            
        Returns:
            Resultado completo da geração de resposta
        """
        try:
            # Gerar resposta
            result = self.generate_answer(query, documents, evidence_quality, search_source)
            
            # Formatar citações
            if result.get("citations"):
                result["formatted_citations"] = self.format_citations(result["citations"])
            
            logger.info(f"Answer processou consulta: {result.get('conclusion', 'UNKNOWN')}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento da consulta: {str(e)}")
            return {
                "conclusion": "ERRO",
                "answer": f"Erro ao processar consulta: {str(e)}",
                "citations": [],
                "evidence_summary": [],
                "formatted_citations": "Erro ao formatar citações",
                "query": query,
                "evidence_quality": evidence_quality,
                "num_documents": len(documents) if documents else 0,
                "agent": "ANSWER"
            }

