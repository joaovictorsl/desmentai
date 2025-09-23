"""
Módulo para carregamento e configuração do Google Gemini.
"""

import os
from typing import Optional, Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.base import BaseLanguageModel
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class LLMLoader:
    """Classe para carregar e configurar o Google Gemini."""
    
    def __init__(self):
        """Inicializa o carregador de LLM baseado nas configurações do .env."""
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self._llm: Optional[BaseLanguageModel] = None
        
        # Configurações de performance
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self.top_p = float(os.getenv("LLM_TOP_P", "0.9"))
        self.top_k = int(os.getenv("LLM_TOP_K", "40"))
        self.repeat_penalty = float(os.getenv("LLM_REPEAT_PENALTY", "1.1"))
    
    def get_llm(self) -> BaseLanguageModel:
        """
        Retorna uma instância do Gemini configurado.
        
        Returns:
            Instância do Gemini configurado
        """
        if self._llm is None:
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY é obrigatória. Configure sua chave API no arquivo .env")
            
            # Configurar modelo Gemini baseado no nome
            gemini_model = self._get_gemini_model_name()
            
            self._llm = ChatGoogleGenerativeAI(
                model=gemini_model,
                google_api_key=self.gemini_api_key,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                convert_system_message_to_human=True
            )
        return self._llm
    
    def _get_gemini_model_name(self) -> str:
        """
        Converte o nome do modelo para o formato do Gemini.
        
        Returns:
            Nome do modelo no formato do Gemini
        """
        # Mapear nomes de modelos para os modelos do Gemini
        model_mapping = {
            "gemini-pro": "gemini-2.0-flash",  # gemini-pro foi descontinuado
            "gemini-2.0-flash": "gemini-2.0-flash",
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-1.0-pro": "gemini-1.0-pro"
        }
        
        # Se o modelo já está no formato correto, usar diretamente
        if self.model_name in model_mapping:
            return model_mapping[self.model_name]
        
        # Se contém "gemini", assumir que é o nome correto
        if "gemini" in self.model_name.lower():
            return self.model_name
        
        # Padrão para Gemini 2.0 Flash
        return "gemini-2.0-flash"
    
    def get_embedding_model(self) -> str:
        """
        Retorna o nome do modelo de embeddings a ser usado.
        
        Returns:
            Nome do modelo de embeddings
        """
        return self.embedding_model
    
    def check_connection(self) -> bool:
        """
        Verifica a conexão com o Gemini.
        
        Returns:
            True se a conexão estiver funcionando, False caso contrário
        """
        return self._check_gemini_connection()
    
    def _check_gemini_connection(self) -> bool:
        """
        Verifica a conexão com a API do Gemini.
        
        Returns:
            True se a conexão estiver funcionando, False caso contrário
        """
        try:
            if not self.gemini_api_key:
                return False
            
            # Tentar criar uma instância do LLM para verificar a conexão
            test_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=self.gemini_api_key,
                temperature=0.1
            )
            
            # Fazer uma chamada simples para testar
            response = test_llm.invoke("Teste de conexão")
            return response is not None
            
        except Exception as e:
            print(f"Erro na conexão com Gemini: {str(e)}")
            return False
    
    
    
    
    def get_recommended_embeddings(self) -> List[Dict[str, str]]:
        """
        Retorna lista de modelos de embeddings recomendados.
        
        Returns:
            Lista de dicionários com informações dos modelos de embeddings
        """
        return [
            {
                "name": "sentence-transformers/all-MiniLM-L6-v2",
                "description": "Modelo rápido e eficiente (22MB)",
                "size": "22MB",
                "recommended": True
            },
            {
                "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "description": "Multilíngue, bom para português (118MB)",
                "size": "118MB",
                "recommended": True
            },
            {
                "name": "sentence-transformers/all-mpnet-base-v2",
                "description": "Alta qualidade, mais lento (420MB)",
                "size": "420MB",
                "recommended": False
            },
            {
                "name": "BAAI/bge-small-en-v1.5",
                "description": "BGE Small - Boa qualidade, rápido (33MB)",
                "size": "33MB",
                "recommended": True
            },
            {
                "name": "BAAI/bge-base-en-v1.5",
                "description": "BGE Base - Alta qualidade (438MB)",
                "size": "438MB",
                "recommended": False
            }
        ]
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Retorna informações de configuração do Gemini.
        
        Returns:
            Dicionário com informações de configuração
        """
        return {
            "provider": "gemini",
            "model_name": self.model_name,
            "embedding_model": self.embedding_model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
            "connection_status": self.check_connection(),
            "gemini_api_key_configured": bool(self.gemini_api_key)
        }
    
    def update_model(self, model_name: str) -> None:
        """
        Atualiza o modelo atual.
        
        Args:
            model_name: Nome do novo modelo
        """
        self.model_name = model_name
        self._llm = None  # Força recriação do LLM
    
    
    def update_embedding_model(self, embedding_model: str) -> None:
        """
        Atualiza o modelo de embeddings.
        
        Args:
            embedding_model: Nome do novo modelo de embeddings
        """
        self.embedding_model = embedding_model