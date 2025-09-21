"""
Módulo para gerenciamento de embeddings e vector stores.
"""

import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Classe para gerenciar embeddings e vector stores."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa o gerenciador de embeddings.
        
        Args:
            model_name: Nome do modelo de embeddings
        """
        self.model_name = model_name
        self.embedding_model = None
        self.vector_store = None
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        """Carrega o modelo de embeddings."""
        try:
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},  # Usar CPU para compatibilidade
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"Modelo de embeddings carregado: {self.model_name}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de embeddings: {str(e)}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Cria embeddings para uma lista de textos.
        
        Args:
            texts: Lista de textos para criar embeddings
            
        Returns:
            Array numpy com os embeddings
        """
        try:
            embeddings = self.embedding_model.embed_documents(texts)
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Erro ao criar embeddings: {str(e)}")
            raise
    
    def create_vector_store(self, documents: List[Document], persist_directory: str = None) -> FAISS:
        """
        Cria um vector store FAISS a partir de documentos.
        
        Args:
            documents: Lista de documentos para indexar
            persist_directory: Diretório para persistir o vector store
            
        Returns:
            Vector store FAISS
        """
        try:
            if not documents:
                logger.warning("Nenhum documento fornecido para criar vector store")
                return None
            
            # Criar vector store
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model
            )
            
            # Persistir se diretório especificado
            if persist_directory:
                os.makedirs(persist_directory, exist_ok=True)
                self.vector_store.save_local(persist_directory)
                logger.info(f"Vector store salvo em: {persist_directory}")
            
            logger.info(f"Vector store criado com {len(documents)} documentos")
            return self.vector_store
            
        except Exception as e:
            logger.error(f"Erro ao criar vector store: {str(e)}")
            raise
    
    def load_vector_store(self, persist_directory: str) -> FAISS:
        """
        Carrega um vector store existente.
        
        Args:
            persist_directory: Diretório onde o vector store está salvo
            
        Returns:
            Vector store carregado
        """
        try:
            if not os.path.exists(persist_directory):
                logger.warning(f"Diretório não encontrado: {persist_directory}")
                return None
            
            self.vector_store = FAISS.load_local(
                persist_directory,
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
            
            logger.info(f"Vector store carregado de: {persist_directory}")
            return self.vector_store
            
        except Exception as e:
            logger.error(f"Erro ao carregar vector store: {str(e)}")
            return None
    
    def similarity_search(self, query: str, k: int = 5, score_threshold: float = 0.7) -> List[Document]:
        """
        Realiza busca por similaridade no vector store.
        
        Args:
            query: Consulta de busca
            k: Número de documentos a retornar
            score_threshold: Limiar mínimo de similaridade
            
        Returns:
            Lista de documentos similares
        """
        if self.vector_store is None:
            logger.warning("Vector store não inicializado")
            return []
        
        try:
            # Busca com scores
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Filtrar por score threshold
            filtered_docs = [
                doc for doc, score in docs_with_scores 
                if score >= score_threshold
            ]
            
            logger.info(f"Encontrados {len(filtered_docs)} documentos similares para: {query[:50]}...")
            return filtered_docs
            
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {str(e)}")
            return []
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o vector store.
        
        Returns:
            Dicionário com informações do vector store
        """
        if self.vector_store is None:
            return {"status": "not_initialized"}
        
        try:
            # Tentar obter informações básicas
            info = {
                "status": "initialized",
                "model_name": self.model_name,
                "index_type": "FAISS"
            }
            
            # Adicionar número de documentos se possível
            if hasattr(self.vector_store, 'index') and hasattr(self.vector_store.index, 'ntotal'):
                info["num_documents"] = self.vector_store.index.ntotal
            
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do vector store: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Adiciona novos documentos ao vector store existente.
        
        Args:
            documents: Lista de documentos para adicionar
            
        Returns:
            True se sucesso, False caso contrário
        """
        if self.vector_store is None:
            logger.warning("Vector store não inicializado")
            return False
        
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Adicionados {len(documents)} documentos ao vector store")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {str(e)}")
            return False
