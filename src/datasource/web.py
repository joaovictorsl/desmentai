from typing_extensions import List
from src.datasource.interface import Datasource
from src.entity.document import Document
import os
import logging

logger = logging.getLogger(__name__)

class WebDatasource(Datasource):
    def __init__(self):
        """Inicializa o WebDatasource com verificação de API key."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente Tavily se a API key estiver disponível."""
        try:
            from tavily import TavilyClient
            api_key = os.getenv('TAVILY_API_KEY')
            if api_key:
                self.client = TavilyClient(api_key=api_key)
                logger.info("Cliente Tavily inicializado com sucesso")
            else:
                logger.warning("TAVILY_API_KEY não encontrada. Busca web desabilitada.")
        except ImportError:
            logger.warning("Tavily não instalado. Busca web desabilitada.")
        except Exception as e:
            logger.error(f"Erro ao inicializar Tavily: {str(e)}")

    @classmethod
    def search(cls, q: str) -> List[Document]:
        """Busca documentos na web."""
        instance = cls()
        return instance._search(q)
    
    def _search(self, q: str) -> List[Document]:
        """Implementa a busca na web."""
        if not self.client:
            logger.warning("Cliente Tavily não disponível. Retornando lista vazia.")
            return []
        
        try:
            response = self.client.search(query=q)
            results = response.get('results', [])
            return [Document(r['url'], r['url'], r['content']) for r in results]
        except Exception as e:
            logger.error(f"Erro na busca web: {str(e)}")
            return []
