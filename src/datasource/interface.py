from typing_extensions import List
from abc import ABC, abstractmethod
from src.entity.document import Document

class Datasource(ABC):
    @classmethod
    @abstractmethod
    def search(self, q: str) -> List[Document]:
        pass
