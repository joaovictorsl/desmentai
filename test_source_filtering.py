#!/usr/bin/env python3
"""
Script de teste para verificar a filtragem de fontes por tipo de busca.
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from src.agents.answer_agent import AnswerAgent
from langchain.schema import Document
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_source_filtering():
    """Testa a filtragem de fontes por tipo de busca."""
    try:
        print("🔍 Testando filtragem de fontes por tipo de busca")
        print("=" * 60)
        
        # Criar documentos de teste
        test_documents = [
            {
                "content": "Brasil é o maior produtor de café do mundo, responsável por cerca de 1/3 da produção global.",
                "metadata": {
                    "source": "data/raw/agencia_lupa.txt",
                    "type": "local",
                    "url": ""
                },
                "relevance_score": 0.8,
                "source": "local"
            },
            {
                "content": "As vacinas contra COVID-19 são seguras e eficazes, conforme comprovado por estudos científicos rigorosos.",
                "metadata": {
                    "source": "data/raw/verificacao_covid.html",
                    "type": "local",
                    "url": ""
                },
                "relevance_score": 0.9,
                "source": "local"
            },
            {
                "content": "Últimas notícias sobre inteligência artificial em 2024 mostram avanços significativos em modelos de linguagem.",
                "metadata": {
                    "source": "https://example.com/ia-2024",
                    "type": "web",
                    "url": "https://example.com/ia-2024"
                },
                "relevance_score": 0.7,
                "source": "web"
            },
            {
                "content": "Criptomoedas e blockchain continuam evoluindo em 2024 com novas regulamentações e adoção institucional.",
                "metadata": {
                    "source": "https://example.com/crypto-2024",
                    "type": "web",
                    "url": "https://example.com/crypto-2024"
                },
                "relevance_score": 0.6,
                "source": "web"
            }
        ]
        
        # Criar instância do AnswerAgent (sem LLM para teste)
        answer_agent = AnswerAgent(llm=None)
        
        print(f"📄 Documentos de teste: {len(test_documents)}")
        print("  - 2 documentos locais")
        print("  - 2 documentos web")
        
        # Teste 1: Busca apenas local
        print(f"\n🧪 Teste 1: Busca apenas local (local_only)")
        print("-" * 40)
        
        result_local = answer_agent._filter_documents_by_source(test_documents, "local_only")
        print(f"Documentos filtrados: {len(result_local)}")
        print("Fontes encontradas:")
        for i, doc in enumerate(result_local, 1):
            source = doc["metadata"].get("source", "Desconhecida")
            doc_source = doc.get("source", "unknown")
            print(f"  {i}. {source} (tipo: {doc_source})")
        
        # Teste 2: Busca híbrida (deve mostrar apenas web)
        print(f"\n🧪 Teste 2: Busca híbrida (hybrid)")
        print("-" * 40)
        
        result_hybrid = answer_agent._filter_documents_by_source(test_documents, "hybrid")
        print(f"Documentos filtrados: {len(result_hybrid)}")
        print("Fontes encontradas:")
        for i, doc in enumerate(result_hybrid, 1):
            source = doc["metadata"].get("source", "Desconhecida")
            doc_source = doc.get("source", "unknown")
            print(f"  {i}. {source} (tipo: {doc_source})")
        
        # Teste 3: Busca apenas web
        print(f"\n🧪 Teste 3: Busca apenas web (web_only)")
        print("-" * 40)
        
        result_web = answer_agent._filter_documents_by_source(test_documents, "web_only")
        print(f"Documentos filtrados: {len(result_web)}")
        print("Fontes encontradas:")
        for i, doc in enumerate(result_web, 1):
            source = doc["metadata"].get("source", "Desconhecida")
            doc_source = doc.get("source", "unknown")
            print(f"  {i}. {source} (tipo: {doc_source})")
        
        # Teste 4: Fonte desconhecida (deve mostrar todos)
        print(f"\n🧪 Teste 4: Fonte desconhecida (unknown)")
        print("-" * 40)
        
        result_unknown = answer_agent._filter_documents_by_source(test_documents, "unknown")
        print(f"Documentos filtrados: {len(result_unknown)}")
        print("Fontes encontradas:")
        for i, doc in enumerate(result_unknown, 1):
            source = doc["metadata"].get("source", "Desconhecida")
            doc_source = doc.get("source", "unknown")
            print(f"  {i}. {source} (tipo: {doc_source})")
        
        # Verificar resultados
        print(f"\n📊 Verificação dos Resultados")
        print("=" * 60)
        
        # Verificar busca local
        local_sources = [doc.get("source") for doc in result_local]
        expected_local = ["local", "local", "web", "web"]  # Deve mostrar todos
        local_correct = local_sources == expected_local
        print(f"✅ Busca local: {'CORRETO' if local_correct else 'INCORRETO'}")
        print(f"   Esperado: {expected_local}")
        print(f"   Obtido: {local_sources}")
        
        # Verificar busca híbrida
        hybrid_sources = [doc.get("source") for doc in result_hybrid]
        expected_hybrid = ["web", "web"]  # Deve mostrar apenas web
        hybrid_correct = hybrid_sources == expected_hybrid
        print(f"✅ Busca híbrida: {'CORRETO' if hybrid_correct else 'INCORRETO'}")
        print(f"   Esperado: {expected_hybrid}")
        print(f"   Obtido: {hybrid_sources}")
        
        # Verificar busca web
        web_sources = [doc.get("source") for doc in result_web]
        expected_web = ["web", "web"]  # Deve mostrar apenas web
        web_correct = web_sources == expected_web
        print(f"✅ Busca web: {'CORRETO' if web_correct else 'INCORRETO'}")
        print(f"   Esperado: {expected_web}")
        print(f"   Obtido: {web_sources}")
        
        # Verificar fonte desconhecida
        unknown_sources = [doc.get("source") for doc in result_unknown]
        expected_unknown = ["local", "local", "web", "web"]  # Deve mostrar todos
        unknown_correct = unknown_sources == expected_unknown
        print(f"✅ Fonte desconhecida: {'CORRETO' if unknown_correct else 'INCORRETO'}")
        print(f"   Esperado: {expected_unknown}")
        print(f"   Obtido: {unknown_sources}")
        
        # Resumo
        all_correct = local_correct and hybrid_correct and web_correct and unknown_correct
        print(f"\n🎯 Resultado Geral: {'✅ TODOS OS TESTES PASSARAM' if all_correct else '❌ ALGUNS TESTES FALHARAM'}")
        
        return all_correct
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        logger.error(f"Erro no teste: {str(e)}")
        return False


def main():
    """Função principal."""
    print("🚀 DesmentAI - Teste de Filtragem de Fontes")
    print("=" * 60)
    
    success = test_source_filtering()
    
    if success:
        print("\n🎉 Teste de filtragem concluído com sucesso!")
        print("\n📋 Resumo da funcionalidade:")
        print("  - Busca local (local_only): Mostra todas as fontes")
        print("  - Busca híbrida (hybrid): Mostra apenas fontes web")
        print("  - Busca web (web_only): Mostra apenas fontes web")
        print("  - Fonte desconhecida: Mostra todas as fontes")
    else:
        print("\n❌ Teste falhou")
        sys.exit(1)


if __name__ == "__main__":
    main()
