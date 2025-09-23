#!/usr/bin/env python3
"""
Script de teste para demonstrar a busca híbrida do DesmentAI.
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from src.core import DesmentAI
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_hybrid_search():
    """Testa a funcionalidade de busca híbrida."""
    try:
        print("🔍 Testando busca híbrida do DesmentAI")
        print("=" * 50)
        
        # Inicializar DesmentAI
        print("Inicializando DesmentAI...")
        desmentai = DesmentAI()
        
        if not desmentai.is_initialized:
            print("❌ Falha na inicialização do DesmentAI")
            return False
        
        print("✅ DesmentAI inicializado com sucesso!")
        
        # Teste 1: Consulta que deve encontrar documentos locais
        print("\n📚 Teste 1: Consulta com documentos locais")
        print("-" * 30)
        
        query1 = "Brasil é o maior produtor de café do mundo"
        result1 = desmentai.verify_news(query1)
        
        print(f"Query: {query1}")
        print(f"Sucesso: {result1['success']}")
        print(f"Fonte da busca: {result1.get('agent_results', {}).get('retriever', {}).get('search_source', 'N/A')}")
        print(f"Documentos locais: {result1.get('agent_results', {}).get('retriever', {}).get('local_docs', 0)}")
        print(f"Documentos web: {result1.get('agent_results', {}).get('retriever', {}).get('web_docs', 0)}")
        
        # Teste 2: Consulta que provavelmente precisará buscar na web
        print("\n🌐 Teste 2: Consulta que pode precisar de busca web")
        print("-" * 30)
        
        query2 = "Últimas notícias sobre inteligência artificial em 2024"
        result2 = desmentai.verify_news(query2)
        
        print(f"Query: {query2}")
        print(f"Sucesso: {result2['success']}")
        print(f"Fonte da busca: {result2.get('agent_results', {}).get('retriever', {}).get('search_source', 'N/A')}")
        print(f"Documentos locais: {result2.get('agent_results', {}).get('retriever', {}).get('local_docs', 0)}")
        print(f"Documentos web: {result2.get('agent_results', {}).get('retriever', {}).get('web_docs', 0)}")
        
        # Teste 3: Consulta sobre COVID-19 (deve ter documentos locais)
        print("\n🦠 Teste 3: Consulta sobre COVID-19")
        print("-" * 30)
        
        query3 = "Vacinas contra COVID-19 são seguras"
        result3 = desmentai.verify_news(query3)
        
        print(f"Query: {query3}")
        print(f"Sucesso: {result3['success']}")
        print(f"Fonte da busca: {result3.get('agent_results', {}).get('retriever', {}).get('search_source', 'N/A')}")
        print(f"Documentos locais: {result3.get('agent_results', {}).get('retriever', {}).get('local_docs', 0)}")
        print(f"Documentos web: {result3.get('agent_results', {}).get('retriever', {}).get('web_docs', 0)}")
        
        # Mostrar status do sistema
        print("\n📊 Status do Sistema")
        print("-" * 30)
        status = desmentai.get_system_status()
        print(f"Modelo: {status.get('model_name', 'N/A')}")
        print(f"Provider: {status.get('provider', 'N/A')}")
        print(f"Vector Store: {status.get('vector_store', {}).get('status', 'N/A')}")
        print(f"Documentos indexados: {status.get('vector_store', {}).get('num_documents', 'N/A')}")
        
        print("\n✅ Teste de busca híbrida concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        logger.error(f"Erro no teste: {str(e)}")
        return False


def main():
    """Função principal."""
    print("🚀 DesmentAI - Teste de Busca Híbrida")
    print("=" * 50)
    
    success = test_hybrid_search()
    
    if success:
        print("\n🎉 Teste executado com sucesso!")
        print("\nO sistema agora implementa busca híbrida:")
        print("1. 🔍 Busca primeiro nos documentos locais")
        print("2. 🌐 Se necessário, busca na web usando Tavily")
        print("3. 💾 Salva documentos da web para consultas futuras")
        print("4. 🔄 Combina e reordena resultados por relevância")
    else:
        print("\n❌ Teste falhou")
        sys.exit(1)


if __name__ == "__main__":
    main()
