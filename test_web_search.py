#!/usr/bin/env python3
"""
Script de teste específico para verificar se a busca web está sendo acionada.
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


def test_web_search_trigger():
    """Testa se a busca web está sendo acionada corretamente."""
    try:
        print("🔍 Testando acionamento da busca web")
        print("=" * 50)
        
        # Inicializar DesmentAI
        print("Inicializando DesmentAI...")
        desmentai = DesmentAI()
        
        if not desmentai.is_initialized:
            print("❌ Falha na inicialização do DesmentAI")
            return False
        
        print("✅ DesmentAI inicializado com sucesso!")
        
        # Teste com consulta que NÃO deve ter documentos locais relevantes
        print("\n🌐 Teste: Consulta sem documentos locais relevantes")
        print("-" * 50)
        
        query = "Últimas notícias sobre inteligência artificial em 2024"
        print(f"Query: {query}")
        
        # Verificar status do retriever
        retriever = desmentai.agents.get("retriever")
        if retriever:
            print(f"Min local docs: {retriever.min_local_docs}")
            print(f"Web search threshold: {retriever.web_search_threshold}")
        
        # Executar verificação
        result = desmentai.verify_news(query)
        
        # Analisar resultado
        print(f"\n📊 Resultado da Verificação:")
        print(f"Sucesso: {result['success']}")
        
        # Verificar resultado do retriever
        retriever_result = result.get('agent_results', {}).get('retriever', {})
        print(f"Fonte da busca: {retriever_result.get('search_source', 'N/A')}")
        print(f"Documentos locais: {retriever_result.get('local_docs', 0)}")
        print(f"Documentos web: {retriever_result.get('web_docs', 0)}")
        print(f"Total de documentos: {retriever_result.get('num_documents', 0)}")
        
        # Verificar se buscou na web
        if retriever_result.get('search_source') == 'hybrid':
            print("✅ Busca híbrida acionada corretamente!")
        elif retriever_result.get('search_source') == 'web_only':
            print("✅ Busca web acionada corretamente!")
        elif retriever_result.get('search_source') == 'local_only':
            print("⚠️  Apenas busca local - pode precisar ajustar thresholds")
        else:
            print("❌ Fonte de busca desconhecida")
        
        # Mostrar documentos encontrados
        documents = retriever_result.get('documents', [])
        if documents:
            print(f"\n📄 Documentos encontrados ({len(documents)}):")
            for i, doc in enumerate(documents[:3]):  # Mostrar apenas os 3 primeiros
                print(f"  {i+1}. Score: {doc.get('relevance_score', 0):.3f} | Fonte: {doc.get('source', 'N/A')}")
                print(f"     Conteúdo: {doc.get('content', '')[:100]}...")
        else:
            print("❌ Nenhum documento encontrado")
        
        # Teste adicional com consulta completamente diferente
        print("\n🧪 Teste adicional: Consulta sobre tópico não coberto")
        print("-" * 50)
        
        query2 = "Notícias sobre criptomoedas e blockchain em 2024"
        print(f"Query: {query2}")
        
        result2 = desmentai.verify_news(query2)
        retriever_result2 = result2.get('agent_results', {}).get('retriever', {})
        
        print(f"Fonte da busca: {retriever_result2.get('search_source', 'N/A')}")
        print(f"Documentos locais: {retriever_result2.get('local_docs', 0)}")
        print(f"Documentos web: {retriever_result2.get('web_docs', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        logger.error(f"Erro no teste: {str(e)}")
        return False


def main():
    """Função principal."""
    print("🚀 DesmentAI - Teste de Acionamento da Busca Web")
    print("=" * 60)
    
    success = test_web_search_trigger()
    
    if success:
        print("\n🎉 Teste concluído!")
        print("\nSe a busca web não foi acionada, verifique:")
        print("1. Se TAVILY_API_KEY está configurada")
        print("2. Se os thresholds estão adequados")
        print("3. Se os documentos locais são realmente irrelevantes")
    else:
        print("\n❌ Teste falhou")
        sys.exit(1)


if __name__ == "__main__":
    main()
