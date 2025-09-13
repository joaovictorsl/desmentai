from dataclasses import dataclass

@dataclass
class Document:
    id: str
    source: str
    content: str
