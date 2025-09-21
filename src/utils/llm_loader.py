"""
Módulo para carregamento e configuração de LLMs locais via Ollama.
"""

import os
from typing import Optional
from langchain_community.llms import Ollama
from langchain_core.language_models.base import BaseLanguageModel


class LLMLoader:
    """Classe para carregar e configurar modelos de linguagem locais."""
    
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Inicializa o carregador de LLM.
        
        Args:
            model_name: Nome do modelo Ollama a ser usado
            base_url: URL base do servidor Ollama
        """
        self.model_name = model_name
        self.base_url = base_url
        self._llm: Optional[BaseLanguageModel] = None
    
    def get_llm(self) -> BaseLanguageModel:
        """
        Retorna uma instância do LLM configurado.
        
        Returns:
            Instância do LLM configurado
        """
        if self._llm is None:
            self._llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.1,  # Baixa temperatura para respostas mais determinísticas
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1
            )
        return self._llm
    
    def get_embedding_model(self) -> str:
        """
        Retorna o nome do modelo de embeddings a ser usado.
        
        Returns:
            Nome do modelo de embeddings
        """
        return "sentence-transformers/all-MiniLM-L6-v2"
    
    def check_ollama_connection(self) -> bool:
        """
        Verifica se o servidor Ollama está rodando.
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self) -> list:
        """
        Retorna lista de modelos disponíveis no Ollama.
        
        Returns:
            Lista de nomes de modelos disponíveis
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except Exception:
            return []
