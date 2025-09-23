"""
Módulo para processamento de documentos e criação de chunks.
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Classe para processamento e chunking de documentos."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa o processador de documentos.
        
        Args:
            chunk_size: Tamanho dos chunks em caracteres
            chunk_overlap: Sobreposição entre chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Carrega e processa um arquivo PDF.
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            Lista de documentos processados
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Adicionar metadados
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "type": "pdf",
                    "file_hash": self._get_file_hash(file_path)
                })
            
            logger.info(f"Carregados {len(documents)} páginas do PDF: {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao carregar PDF {file_path}: {str(e)}")
            return []
    
    def load_web_page(self, url: str) -> List[Document]:
        """
        Carrega e processa uma página web.
        
        Args:
            url: URL da página web
            
        Returns:
            Lista de documentos processados
        """
        try:
            loader = WebBaseLoader(url)
            documents = loader.load()
            
            # Adicionar metadados
            for doc in documents:
                doc.metadata.update({
                    "source": url,
                    "type": "web",
                    "url": url
                })
            
            logger.info(f"Carregada página web: {url}")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao carregar página web {url}: {str(e)}")
            return []
    
    def load_html_file(self, file_path: str) -> List[Document]:
        """
        Carrega e processa um arquivo HTML local.
        
        Args:
            file_path: Caminho para o arquivo HTML
            
        Returns:
            Lista de documentos processados
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            
            # Criar documento
            doc = Document(
                page_content=text,
                metadata={
                    "source": file_path,
                    "type": "html",
                    "file_hash": self._get_file_hash(file_path)
                }
            )
            
            logger.info(f"Carregado arquivo HTML: {file_path}")
            return [doc]
            
        except Exception as e:
            logger.error(f"Erro ao carregar HTML {file_path}: {str(e)}")
            return []
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Divide documentos em chunks menores.
        
        Args:
            documents: Lista de documentos para dividir
            
        Returns:
            Lista de chunks de documentos
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            
            # Adicionar metadados de chunk
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_id": i,
                    "chunk_size": len(chunk.page_content)
                })
            
            logger.info(f"Criados {len(chunks)} chunks de {len(documents)} documentos")
            return chunks
            
        except Exception as e:
            logger.error(f"Erro ao criar chunks: {str(e)}")
            return []
    
    def process_directory(self, directory_path: str, file_extensions: List[str] = None) -> List[Document]:
        """
        Processa todos os arquivos de um diretório.
        
        Args:
            directory_path: Caminho do diretório
            file_extensions: Extensões de arquivo a processar
            
        Returns:
            Lista de todos os documentos processados
        """
        if file_extensions is None:
            file_extensions = ['.pdf', '.html', '.txt']
        
        all_documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.warning(f"Diretório não encontrado: {directory_path}")
            return all_documents
        
        for file_path in directory.rglob("*"):
            if file_path.suffix.lower() in file_extensions:
                if file_path.suffix.lower() == '.pdf':
                    documents = self.load_pdf(str(file_path))
                elif file_path.suffix.lower() == '.html':
                    documents = self.load_html_file(str(file_path))
                else:
                    continue
                
                all_documents.extend(documents)
        
        logger.info(f"Processados {len(all_documents)} documentos do diretório: {directory_path}")
        return all_documents
    
    def deduplicate_documents(self, documents: List[Document]) -> List[Document]:
        """
        Remove documentos duplicados baseado no hash do conteúdo.
        
        Args:
            documents: Lista de documentos
            
        Returns:
            Lista de documentos únicos
        """
        seen_hashes = set()
        unique_documents = []
        
        for doc in documents:
            content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_documents.append(doc)
        
        logger.info(f"Removidas {len(documents) - len(unique_documents)} duplicatas")
        return unique_documents
    
    def filter_documents(self, documents: List[Document], min_length: int = 100) -> List[Document]:
        """
        Filtra documentos por tamanho mínimo.
        
        Args:
            documents: Lista de documentos
            min_length: Tamanho mínimo do conteúdo
            
        Returns:
            Lista de documentos filtrados
        """
        filtered = [doc for doc in documents if len(doc.page_content.strip()) >= min_length]
        logger.info(f"Filtrados {len(documents) - len(filtered)} documentos muito curtos")
        return filtered
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calcula hash MD5 de um arquivo."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return "unknown"
