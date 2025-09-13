from typing_extensions import List
from src.datasource.interface import Datasource
from src.entity.document import Document
from tavily import TavilyClient

class WebDatasource(Datasource):
    client = TavilyClient()

    @classmethod
    def search(cls, q: str) -> List[Document]:
        response = cls.client.search(
            query=q,
        )
        results = response['results']
        return [Document(r['url'], r['url'], r['content']) for r in results]
