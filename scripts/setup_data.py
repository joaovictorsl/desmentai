#!/usr/bin/env python3
"""
Script para configurar dados iniciais do DesmentAI.
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.data_ingestion import DataIngestion
from src.utils.document_processor import DocumentProcessor
from src.utils.embeddings import EmbeddingManager
from src.core import DesmentAI
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_initial_data():
    """Configura dados iniciais para o DesmentAI."""
    try:
        logger.info("Configurando dados iniciais do DesmentAI...")
        
        # 1. Inicializar sistema de ingestão
        ingestion = DataIngestion()
        
        # 2. Baixar dados de exemplo
        logger.info("Baixando dados de exemplo...")
        success = ingestion.download_sample_data()
        
        if not success:
            logger.error("Falha ao baixar dados de exemplo")
            return False
        
        # 3. Criar arquivos HTML de exemplo
        logger.info("Criando arquivos HTML de exemplo...")
        success = ingestion.create_sample_html()
        
        if not success:
            logger.error("Falha ao criar arquivos HTML de exemplo")
            return False
        
        # 4. Mostrar status
        status = ingestion.get_ingestion_status()
        logger.info(f"Dados configurados:")
        logger.info(f"  - Arquivos: {status['num_files']}")
        logger.info(f"  - Tamanho total: {status['total_size']} bytes")
        logger.info(f"  - Pasta: {status['data_path']}")
        
        # 5. Inicializar DesmentAI para criar vector store
        logger.info("Inicializando DesmentAI...")
        desmentai = DesmentAI()
        success = desmentai.initialize()
        
        if success:
            logger.info("✅ DesmentAI inicializado com sucesso!")
            logger.info("Você pode agora executar: streamlit run app.py")
        else:
            logger.error("❌ Falha na inicialização do DesmentAI")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na configuração: {str(e)}")
        return False


def main():
    """Função principal."""
    print("🔍 DesmentAI - Configuração de Dados Iniciais")
    print("=" * 50)
    
    success = setup_initial_data()
    
    if success:
        print("\n✅ Configuração concluída com sucesso!")
        print("\nPróximos passos:")
        print("1. Execute: ollama serve")
        print("2. Execute: ollama pull llama3.1:8b")
        print("3. Execute: streamlit run app.py")
    else:
        print("\n❌ Falha na configuração")
        sys.exit(1)


if __name__ == "__main__":
    main()
