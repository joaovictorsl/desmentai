"""
Agente Retriever - Busca informações relevantes na base de conhecimento.
Implementa busca híbrida: local + web quando necessário.
"""

from typing import Dict, Any, List
from langchain.schema import Document
from langchain_core.language_models.base import BaseLanguageModel
from langchain_community.vectorstores import FAISS
from ..datasource.web import WebDatasource
from ..entity.document import Document as EntityDocument
from ..utils.document_processor import DocumentProcessor
from ..utils.embeddings import EmbeddingManager
import logging
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrieverAgent:
    """Agente responsável por buscar informações relevantes na base de conhecimento.
    Implementa busca híbrida: primeiro busca localmente, depois na web se necessário."""
    
    def __init__(self, llm: BaseLanguageModel, vector_store: FAISS, 
                 document_processor: DocumentProcessor = None, 
                 embedding_manager: EmbeddingManager = None,
                 min_local_docs: int = 2,
                 web_search_threshold: float = 0.6):
        """
        Inicializa o agente retriever.
        
        Args:
            llm: Instância do modelo de linguagem
            vector_store: Vector store com os documentos indexados
            document_processor: Processador de documentos para salvar novos docs
            embedding_manager: Gerenciador de embeddings para indexar novos docs
            min_local_docs: Número mínimo de documentos locais para não buscar na web
            web_search_threshold: Threshold de similaridade para considerar busca local suficiente
        """
        self.llm = llm
        self.vector_store = vector_store
        self.document_processor = document_processor
        self.embedding_manager = embedding_manager
        self.min_local_docs = min_local_docs
        self.web_search_threshold = web_search_threshold
        self.web_datasource = WebDatasource()
        
        self.system_prompt = """Você é um agente especializado em busca de informações relevantes para verificação de notícias.

Sua função é:
1. Analisar a consulta do usuário
2. Buscar documentos mais relevantes na base de conhecimento local
3. Se necessário, buscar informações adicionais na web
4. Retornar os documentos encontrados com suas relevâncias

SEMPRE retorne os documentos encontrados, mesmo que sejam poucos."""

    def search_documents_local(self, query: str, k: int = 5, score_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Busca documentos relevantes na base local.
        
        Args:
            query: Consulta do usuário
            k: Número de documentos a retornar
            score_threshold: Limiar mínimo de similaridade
            
        Returns:
            Dicionário com os documentos encontrados e metadados
        """
        try:
            logger.info(f"Buscando documentos locais para: {query[:100]}...")
            
            # Buscar documentos similares
            documents = self.vector_store.similarity_search_with_score(
                query, 
                k=k
            )
            
            # Filtrar por score threshold (FAISS usa distância, então menor = melhor)
            # Converter threshold de similaridade para distância
            distance_threshold = (1.0 / score_threshold) - 1.0 if score_threshold > 0 else float('inf')
            
            filtered_docs = [
                (doc, score) for doc, score in documents 
                if score <= distance_threshold
            ]
            
            # Se não encontrou documentos suficientes, relaxar o threshold
            if len(filtered_docs) < 2:
                logger.warning("Poucos documentos locais encontrados, relaxando threshold")
                filtered_docs = documents[:3]  # Pegar os 3 melhores
            
            # Preparar resultado
            result = {
                "query": query,
                "documents": [],
                "num_documents": len(filtered_docs),
                "search_successful": len(filtered_docs) > 0,
                "source": "local"
            }
            
            # Processar documentos encontrados
            for i, (doc, score) in enumerate(filtered_docs):
                # FAISS retorna distância (menor = mais similar)
                # Converter para similaridade (maior = mais similar)
                # Usar 1 / (1 + score) para normalizar entre 0 e 1
                similarity_score = 1.0 / (1.0 + float(score))
                
                doc_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": similarity_score,
                    "raw_distance": float(score),  # Manter distância original para debug
                    "rank": i + 1,
                    "source": "local"
                }
                result["documents"].append(doc_info)
            
            logger.info(f"Encontrados {len(filtered_docs)} documentos locais relevantes")
            return result
            
        except Exception as e:
            logger.error(f"Erro na busca de documentos locais: {str(e)}")
            return {
                "query": query,
                "documents": [],
                "num_documents": 0,
                "search_successful": False,
                "source": "local",
                "error": str(e)
            }
    
    def search_documents_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Busca documentos na web usando Tavily.
        
        Args:
            query: Consulta do usuário
            max_results: Número máximo de resultados
            
        Returns:
            Dicionário com os documentos encontrados e metadados
        """
        try:
            logger.info(f"Buscando documentos na web para: {query[:100]}...")
            
            # Buscar na web
            web_documents = self.web_datasource.search(query)
            
            # Limitar número de resultados
            web_documents = web_documents[:max_results]
            
            # Preparar resultado
            result = {
                "query": query,
                "documents": [],
                "num_documents": len(web_documents),
                "search_successful": len(web_documents) > 0,
                "source": "web"
            }
            
            # Processar documentos encontrados
            for i, doc in enumerate(web_documents):
                # Calcular score de similaridade baseado na posição
                # Documentos web têm score decrescente baseado na ordem
                base_score = 0.8 - (i * 0.1)  # 0.8, 0.7, 0.6, etc.
                base_score = max(0.5, base_score)  # Mínimo de 0.5
                
                doc_info = {
                    "content": doc.content,
                    "metadata": {
                        "source": doc.source,
                        "id": doc.id,
                        "type": "web"
                    },
                    "relevance_score": base_score,
                    "rank": i + 1,
                    "source": "web"
                }
                result["documents"].append(doc_info)
            
            logger.info(f"Encontrados {len(web_documents)} documentos na web")
            return result
            
        except Exception as e:
            logger.error(f"Erro na busca de documentos na web: {str(e)}")
            return {
                "query": query,
                "documents": [],
                "num_documents": 0,
                "search_successful": False,
                "source": "web",
                "error": str(e)
            }
    
    def should_search_web(self, local_result: Dict[str, Any]) -> bool:
        """
        Decide se deve buscar na web baseado nos resultados locais.
        
        Args:
            local_result: Resultado da busca local
            
        Returns:
            True se deve buscar na web, False caso contrário
        """
        # Se não encontrou documentos locais suficientes
        if local_result["num_documents"] < self.min_local_docs:
            logger.info(f"Poucos documentos locais encontrados ({local_result['num_documents']} < {self.min_local_docs}), buscando na web")
            return True
        
        # Se os documentos encontrados têm baixa relevância
        if local_result["documents"]:
            scores = [doc["relevance_score"] for doc in local_result["documents"]]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            # Log detalhado para debug
            logger.info(f"Scores locais: avg={avg_score:.3f}, max={max_score:.3f}, min={min_score:.3f}")
            
            # Buscar na web se:
            # 1. Score médio baixo OU
            # 2. Melhor score individual baixo OU  
            # 3. Todos os scores são baixos
            should_search = (
                avg_score < self.web_search_threshold or 
                max_score < (self.web_search_threshold + 0.1) or  # Ligeiramente mais rigoroso
                (max_score < 0.6 and avg_score < 0.5)  # Ambos baixos
            )
            
            if should_search:
                logger.info(f"Documentos locais com baixa relevância (avg: {avg_score:.3f}, max: {max_score:.3f}), buscando na web")
                return True
        
        logger.info("Documentos locais suficientes, não buscando na web")
        return False
    
    def save_web_documents(self, web_documents: List[Dict[str, Any]]) -> bool:
        """
        Salva documentos da web no vector store local.
        
        Args:
            web_documents: Lista de documentos da web
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        if not self.document_processor or not self.embedding_manager:
            logger.warning("Document processor ou embedding manager não disponível para salvar documentos")
            return False
        
        try:
            # Converter para formato LangChain Document
            langchain_docs = []
            for doc in web_documents:
                langchain_doc = Document(
                    page_content=doc["content"],
                    metadata={
                        **doc["metadata"],
                        "saved_from_web": True,
                        "saved_at": str(pd.Timestamp.now())
                    }
                )
                langchain_docs.append(langchain_doc)
            
            # Criar chunks
            chunks = self.document_processor.chunk_documents(langchain_docs)
            
            # Adicionar ao vector store
            success = self.embedding_manager.add_documents(chunks)
            
            if success:
                # Atualizar vector store local
                self.vector_store = self.embedding_manager.vector_store
                logger.info(f"Salvos {len(chunks)} chunks da web no vector store local")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao salvar documentos da web: {str(e)}")
            return False
    
    def search_documents(self, query: str, k: int = 5, score_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Busca documentos usando estratégia híbrida (local + web).
        
        Args:
            query: Consulta do usuário
            k: Número de documentos a retornar
            score_threshold: Limiar mínimo de similaridade
            
        Returns:
            Dicionário com os documentos encontrados e metadados
        """
        try:
            logger.info(f"Iniciando busca híbrida para: {query[:100]}...")
            
            # 1. Buscar localmente primeiro
            local_result = self.search_documents_local(query, k, score_threshold)
            
            # 2. Decidir se deve buscar na web
            if self.should_search_web(local_result):
                web_result = self.search_documents_web(query, max_results=3)
                
                # 3. Salvar documentos da web se encontrou
                if web_result["search_successful"] and web_result["documents"]:
                    self.save_web_documents(web_result["documents"])
                
                # 4. Combinar resultados
                combined_documents = local_result["documents"] + web_result["documents"]
                
                # 5. Reordenar por relevância
                combined_documents.sort(key=lambda x: x["relevance_score"], reverse=True)
                
                # 6. Atualizar ranks
                for i, doc in enumerate(combined_documents):
                    doc["rank"] = i + 1
                
                result = {
                    "query": query,
                    "documents": combined_documents,
                    "num_documents": len(combined_documents),
                    "search_successful": True,
                    "source": "hybrid",
                    "local_docs": local_result["num_documents"],
                    "web_docs": web_result["num_documents"]
                }
                
                logger.info(f"Busca híbrida concluída: {local_result['num_documents']} locais + {web_result['num_documents']} web")
            else:
                # Usar apenas resultados locais
                result = local_result
                result["source"] = "local_only"
                logger.info("Usando apenas resultados locais")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na busca híbrida: {str(e)}")
            return {
                "query": query,
                "documents": [],
                "num_documents": 0,
                "search_successful": False,
                "source": "error",
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
        Processa uma consulta completa usando busca híbrida.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Resultado completo da busca
        """
        try:
            # Buscar documentos usando estratégia híbrida
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
                "agent": "RETRIEVER",
                "search_source": search_result.get("source", "unknown"),
                "local_docs": search_result.get("local_docs", 0),
                "web_docs": search_result.get("web_docs", 0)
            }
            
            logger.info(f"Retriever processou consulta com sucesso: {len(documents)} documentos ({search_result.get('source', 'unknown')})")
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
                "agent": "RETRIEVER",
                "search_source": "error"
            }
