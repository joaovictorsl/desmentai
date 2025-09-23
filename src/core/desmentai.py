"""
Classe principal do DesmentAI - Sistema de combate a fake news.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..utils import LLMLoader, DocumentProcessor, EmbeddingManager
from ..agents import (
    SupervisorAgent, 
    RetrieverAgent, 
    SelfCheckAgent, 
    AnswerAgent, 
    SafetyAgent
)
from .graph import DesmentAIGraph

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DesmentAI:
    """Classe principal do sistema DesmentAI."""
    
    def __init__(
        self,
        model_name: str = "llama3.1:8b",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_store_path: str = "data/vector_store",
        data_path: str = "data/raw"
    ):
        """
        Inicializa o DesmentAI.
        
        Args:
            model_name: Nome do modelo LLM
            embedding_model: Nome do modelo de embeddings
            vector_store_path: Caminho para o vector store
            data_path: Caminho para os dados brutos
        """
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.vector_store_path = vector_store_path
        self.data_path = data_path
        
        # Inicializar componentes
        self.llm_loader = None
        self.document_processor = None
        self.embedding_manager = None
        self.agents = {}
        self.graph = None
        self.vector_store = None
        
        # Status do sistema
        self.is_initialized = False
        self.initialization_error = None
        
        logger.info("DesmentAI inicializado")
        
        # Inicializar automaticamente
        self.initialize()
    
    def initialize(self) -> bool:
        """
        Inicializa todos os componentes do sistema.
        
        Returns:
            True se inicialização bem-sucedida, False caso contrário
        """
        try:
            logger.info("Inicializando DesmentAI...")
            
            # 1. Inicializar LLM loader
            self.llm_loader = LLMLoader()
            
            # Verificar conexão com o provedor configurado
            if not self.llm_loader.check_connection():
                provider = self.llm_loader.provider
                if provider == "gemini":
                    raise Exception("Falha na conexão com Gemini. Verifique sua GEMINI_API_KEY.")
                else:
                    raise Exception("Servidor Ollama não está rodando. Execute: ollama serve")
            
            # 2. Inicializar processador de documentos
            self.document_processor = DocumentProcessor()
            
            # 3. Inicializar gerenciador de embeddings
            self.embedding_manager = EmbeddingManager(self.embedding_model)
            
            # 4. Carregar ou criar vector store
            self._setup_vector_store()
            
            # 5. Inicializar agentes
            self._initialize_agents()
            
            # 6. Criar grafo
            self.graph = DesmentAIGraph(self.agents)
            
            self.is_initialized = True
            logger.info("DesmentAI inicializado com sucesso!")
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"Erro na inicialização: {str(e)}")
            return False
    
    def _setup_vector_store(self):
        """Configura o vector store."""
        try:
            # Tentar carregar vector store existente
            if os.path.exists(self.vector_store_path):
                logger.info("Carregando vector store existente...")
                self.vector_store = self.embedding_manager.load_vector_store(self.vector_store_path)
                
                if self.vector_store is None:
                    raise Exception("Falha ao carregar vector store existente")
            else:
                # Criar novo vector store
                logger.info("Criando novo vector store...")
                self._create_vector_store()
                
        except Exception as e:
            logger.error(f"Erro ao configurar vector store: {str(e)}")
            raise
    
    def _create_vector_store(self):
        """Cria um novo vector store a partir dos dados."""
        try:
            # Verificar se existem dados
            if not os.path.exists(self.data_path):
                logger.warning(f"Diretório de dados não encontrado: {self.data_path}")
                # Criar diretório vazio
                os.makedirs(self.data_path, exist_ok=True)
                return
            
            # Processar documentos
            logger.info("Processando documentos...")
            documents = self.document_processor.process_directory(self.data_path)
            
            if not documents:
                logger.warning("Nenhum documento encontrado para processar")
                return
            
            # Deduplicar e filtrar
            documents = self.document_processor.deduplicate_documents(documents)
            documents = self.document_processor.filter_documents(documents)
            
            if not documents:
                logger.warning("Nenhum documento válido após filtragem")
                return
            
            # Criar chunks
            chunks = self.document_processor.chunk_documents(documents)
            
            # Criar vector store
            self.vector_store = self.embedding_manager.create_vector_store(
                chunks, 
                self.vector_store_path
            )
            
            logger.info(f"Vector store criado com {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Erro ao criar vector store: {str(e)}")
            raise
    
    def _initialize_agents(self):
        """Inicializa todos os agentes."""
        try:
            llm = self.llm_loader.get_llm()
            
            # Criar agentes
            self.agents = {
                "supervisor": SupervisorAgent(llm),
                "retriever": RetrieverAgent(llm, self.vector_store),
                "self_check": SelfCheckAgent(llm),
                "answer": AnswerAgent(llm),
                "safety": SafetyAgent(llm)
            }
            
            logger.info("Agentes inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar agentes: {str(e)}")
            raise
    
    def verify_news(self, query: str) -> Dict[str, Any]:
        """
        Verifica uma notícia/afirmação.
        
        Args:
            query: Notícia ou afirmação a ser verificada
            
        Returns:
            Resultado da verificação
        """
        if not self.is_initialized:
            return {
                "error": "Sistema não inicializado",
                "success": False
            }
        
        try:
            logger.info(f"Verificando: {query[:100]}...")
            
            # Processar através do grafo
            result = self.graph.process_query(query)
            
            logger.info(f"Verificação concluída: {result['success']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro na verificação: {str(e)}")
            return {
                "query": query,
                "final_answer": f"❌ Erro na verificação: {str(e)}",
                "conclusion": "ERRO",
                "citations": [],
                "agent_results": {},
                "error": str(e),
                "success": False
            }
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Adiciona novos documentos ao sistema.
        
        Args:
            documents: Lista de documentos para adicionar
            
        Returns:
            True se sucesso, False caso contrário
        """
        if not self.is_initialized:
            logger.error("Sistema não inicializado")
            return False
        
        try:
            # Processar documentos
            processed_docs = []
            for doc_data in documents:
                if "content" in doc_data:
                    from langchain.schema import Document
                    doc = Document(
                        page_content=doc_data["content"],
                        metadata=doc_data.get("metadata", {})
                    )
                    processed_docs.append(doc)
            
            if not processed_docs:
                logger.warning("Nenhum documento válido para adicionar")
                return False
            
            # Criar chunks
            chunks = self.document_processor.chunk_documents(processed_docs)
            
            # Adicionar ao vector store
            success = self.embedding_manager.add_documents(chunks)
            
            if success:
                # Salvar vector store atualizado
                self.vector_store.save_local(self.vector_store_path)
                logger.info(f"Adicionados {len(chunks)} chunks ao sistema")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {str(e)}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Retorna o status do sistema.
        
        Returns:
            Dicionário com status do sistema
        """
        status = {
            "initialized": self.is_initialized,
            "model_name": self.model_name,
            "embedding_model": self.embedding_model,
            "vector_store_path": self.vector_store_path,
            "data_path": self.data_path,
            "initialization_error": self.initialization_error
        }
        
        if self.is_initialized:
            # Adicionar informações do vector store
            vector_info = self.embedding_manager.get_vector_store_info()
            status["vector_store"] = vector_info
            
            # Verificar conexão Gemini
            status["gemini_connected"] = self.llm_loader.check_connection()
            
            # Configurações de performance do LLM
            config_info = self.llm_loader.get_config_info()
            status.update({
                "temperature": config_info.get("temperature", 0.1),
                "top_p": config_info.get("top_p", 0.9),
                "top_k": config_info.get("top_k", 40),
                "repeat_penalty": config_info.get("repeat_penalty", 1.1),
                "model_name": config_info.get("model_name", "gemini-2.0-flash"),
                "provider": config_info.get("provider", "gemini")
            })
        
        return status
    
    def reload_data(self) -> bool:
        """
        Recarrega os dados do sistema.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info("Recarregando dados...")
            
            # Recriar vector store
            self._create_vector_store()
            
            # Reinicializar agente retriever
            if self.agents.get("retriever"):
                self.agents["retriever"] = RetrieverAgent(
                    self.llm_loader.get_llm(), 
                    self.vector_store
                )
            
            logger.info("Dados recarregados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao recarregar dados: {str(e)}")
            return False

