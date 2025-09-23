"""
Agente Retriever - Busca informações relevantes na base de conhecimento.
"""

from typing import Dict, Any, List
from langchain.schema import Document
from langchain_core.language_models.base import BaseLanguageModel
from langchain_community.vectorstores import FAISS
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrieverAgent:
    """Agente responsável por buscar informações relevantes na base de conhecimento."""
    
    def __init__(self, llm: BaseLanguageModel, vector_store: FAISS):
        """
        Inicializa o agente retriever.
        
        Args:
            llm: Instância do modelo de linguagem
            vector_store: Vector store com os documentos indexados
        """
        self.llm = llm
        self.vector_store = vector_store
        self.system_prompt = """Você é um agente especializado em busca de informações relevantes para verificação de notícias.

Sua função é:
1. Analisar a consulta do usuário
2. Buscar documentos mais relevantes na base de conhecimento
3. Retornar os documentos encontrados com suas relevâncias

SEMPRE retorne os documentos encontrados, mesmo que sejam poucos."""

    def search_documents(self, query: str, k: int = 5, score_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Busca documentos relevantes para uma consulta.
        
        Args:
            query: Consulta do usuário
            k: Número de documentos a retornar
            score_threshold: Limiar mínimo de similaridade
            
        Returns:
            Dicionário com os documentos encontrados e metadados
        """
        try:
            logger.info(f"Buscando documentos para: {query[:100]}...")
            
            # Buscar documentos similares
            documents = self.vector_store.similarity_search_with_score(
                query, 
                k=k
            )
            
            # Filtrar por score threshold
            filtered_docs = [
                (doc, score) for doc, score in documents 
                if score >= score_threshold
            ]
            
            # Se não encontrou documentos suficientes, relaxar o threshold
            if len(filtered_docs) < 2:
                logger.warning("Poucos documentos encontrados, relaxando threshold")
                filtered_docs = documents[:3]  # Pegar os 3 melhores
            
            # Preparar resultado
            result = {
                "query": query,
                "documents": [],
                "num_documents": len(filtered_docs),
                "search_successful": len(filtered_docs) > 0
            }
            
            # Processar documentos encontrados
            for i, (doc, score) in enumerate(filtered_docs):
                doc_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score),
                    "rank": i + 1
                }
                result["documents"].append(doc_info)
            
            logger.info(f"Encontrados {len(filtered_docs)} documentos relevantes")
            return result
            
        except Exception as e:
            logger.error(f"Erro na busca de documentos: {str(e)}")
            return {
                "query": query,
                "documents": [],
                "num_documents": 0,
                "search_successful": False,
                "error": str(e)
            }
    
    def rerank_documents(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Reordena documentos baseado na relevância para a consulta.
        
        Args:
            query: Consulta original
            documents: Lista de documentos com scores
            
        Returns:
            Lista de documentos reordenados
        """
        try:
            # Implementação simples de reranking baseada em palavras-chave
            query_words = set(query.lower().split())
            
            for doc in documents:
                content_words = set(doc["content"].lower().split())
                # Calcular overlap de palavras-chave
                overlap = len(query_words.intersection(content_words))
                doc["keyword_overlap"] = overlap
            
            # Reordenar por overlap de palavras-chave + score de similaridade
            documents.sort(
                key=lambda x: (x["keyword_overlap"], x["relevance_score"]), 
                reverse=True
            )
            
            # Atualizar ranks
            for i, doc in enumerate(documents):
                doc["rank"] = i + 1
            
            logger.info("Documentos reordenados por relevância")
            return documents
            
        except Exception as e:
            logger.error(f"Erro no reranking: {str(e)}")
            return documents
    
    def extract_key_claims(self, query: str, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Extrai as principais afirmações dos documentos encontrados.
        
        Args:
            query: Consulta original
            documents: Lista de documentos
            
        Returns:
            Lista de afirmações principais
        """
        try:
            if not documents:
                return []
            
            # Combinar conteúdo dos documentos
            combined_content = "\n\n".join([doc["content"] for doc in documents])
            
            # Prompt para extrair afirmações
            extraction_prompt = f"""
            Com base na consulta "{query}" e nos documentos encontrados, extraia as principais afirmações/fatos relevantes.
            
            Documentos:
            {combined_content[:2000]}...
            
            Retorne apenas as afirmações principais, uma por linha, sem numeração.
            """
            
            # Fazer chamada para o LLM
            response = self.llm.invoke(extraction_prompt)
            
            # Processar resposta
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            claims = [
                claim.strip() 
                for claim in response_text.split('\n') 
                if claim.strip() and not claim.strip().startswith(('1.', '2.', '3.', '-', '*'))
            ]
            
            logger.info(f"Extraídas {len(claims)} afirmações principais")
            return claims[:5]  # Limitar a 5 afirmações
            
        except Exception as e:
            logger.error(f"Erro na extração de afirmações: {str(e)}")
            return []
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processa uma consulta completa, buscando e processando documentos.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Resultado completo da busca
        """
        try:
            # Buscar documentos
            search_result = self.search_documents(query)
            
            if not search_result["search_successful"]:
                return search_result
            
            # Reordenar documentos
            documents = self.rerank_documents(query, search_result["documents"])
            
            # Extrair afirmações principais
            key_claims = self.extract_key_claims(query, documents)
            
            # Preparar resultado final
            result = {
                "query": query,
                "documents": documents,
                "key_claims": key_claims,
                "num_documents": len(documents),
                "search_successful": True,
                "agent": "RETRIEVER"
            }
            
            logger.info(f"Retriever processou consulta com sucesso: {len(documents)} documentos")
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento da consulta: {str(e)}")
            return {
                "query": query,
                "documents": [],
                "key_claims": [],
                "num_documents": 0,
                "search_successful": False,
                "error": str(e),
                "agent": "RETRIEVER"
            }
