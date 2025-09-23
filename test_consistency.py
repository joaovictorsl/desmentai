#!/usr/bin/env python3
"""
Script de teste para verificar consistência do sistema de busca híbrida.
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


def test_consistency():
    """Testa a consistência do sistema de busca."""
    try:
        print("🔍 Testando consistência do sistema de busca")
        print("=" * 60)
        
        # Inicializar DesmentAI
        print("Inicializando DesmentAI...")
        desmentai = DesmentAI()
        
        if not desmentai.is_initialized:
            print("❌ Falha na inicialização do DesmentAI")
            return False
        
        print("✅ DesmentAI inicializado com sucesso!")
        
        # Lista de consultas para testar
        test_queries = [
            "Brasil é o maior produtor de café do mundo",
            "Vacinas contra COVID-19 são seguras", 
            "Últimas notícias sobre inteligência artificial em 2024",
            "Notícias sobre criptomoedas e blockchain em 2024",
            "Aquecimento global é causado pelo homem",
            "Exercícios físicos melhoram a saúde mental",
            "Eleições brasileiras são seguras e confiáveis",
            "Inflação no Brasil está controlada"
        ]
        
        results = []
        
        print(f"\n🧪 Testando {len(test_queries)} consultas...")
        print("-" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            
            # Executar verificação
            result = desmentai.verify_news(query)
            
            # Extrair informações do retriever
            retriever_result = result.get('agent_results', {}).get('retriever', {})
            
            # Informações básicas
            source = retriever_result.get('search_source', 'unknown')
            local_docs = retriever_result.get('local_docs', 0)
            web_docs = retriever_result.get('web_docs', 0)
            total_docs = retriever_result.get('num_documents', 0)
            
            # Informações de relevância
            documents = retriever_result.get('documents', [])
            if documents:
                scores = [doc.get('relevance_score', 0) for doc in documents]
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
            else:
                avg_score = max_score = min_score = 0
            
            # Armazenar resultado
            query_result = {
                'query': query,
                'source': source,
                'local_docs': local_docs,
                'web_docs': web_docs,
                'total_docs': total_docs,
                'avg_score': avg_score,
                'max_score': max_score,
                'min_score': min_score,
                'success': result.get('success', False)
            }
            results.append(query_result)
            
            # Mostrar resultado
            print(f"   Fonte: {source}")
            print(f"   Docs: {local_docs} locais + {web_docs} web = {total_docs} total")
            print(f"   Scores: avg={avg_score:.3f}, max={max_score:.3f}, min={min_score:.3f}")
            print(f"   Sucesso: {result.get('success', False)}")
        
        # Análise de consistência
        print(f"\n📊 Análise de Consistência")
        print("=" * 60)
        
        # Contar fontes
        sources = [r['source'] for r in results]
        source_counts = {}
        for source in sources:
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("Distribuição de fontes:")
        for source, count in source_counts.items():
            print(f"  {source}: {count} consultas")
        
        # Análise de scores
        all_scores = [r['avg_score'] for r in results if r['avg_score'] > 0]
        if all_scores:
            avg_all_scores = sum(all_scores) / len(all_scores)
            print(f"\nScores médios:")
            print(f"  Média geral: {avg_all_scores:.3f}")
            print(f"  Range: {min(all_scores):.3f} - {max(all_scores):.3f}")
        
        # Verificar inconsistências
        print(f"\n🔍 Verificando Inconsistências:")
        
        # 1. Consultas similares com fontes diferentes
        similar_queries = []
        for i, r1 in enumerate(results):
            for j, r2 in enumerate(results[i+1:], i+1):
                if r1['source'] != r2['source'] and r1['avg_score'] > 0.5 and r2['avg_score'] > 0.5:
                    similar_queries.append((r1, r2))
        
        if similar_queries:
            print(f"  ⚠️  {len(similar_queries)} pares de consultas similares com fontes diferentes")
            for r1, r2 in similar_queries[:3]:  # Mostrar apenas os primeiros 3
                print(f"    '{r1['query'][:30]}...' ({r1['source']}) vs '{r2['query'][:30]}...' ({r2['source']})")
        else:
            print("  ✅ Nenhuma inconsistência de fonte detectada")
        
        # 2. Scores muito baixos
        low_scores = [r for r in results if r['avg_score'] < 0.3 and r['avg_score'] > 0]
        if low_scores:
            print(f"  ⚠️  {len(low_scores)} consultas com scores muito baixos (< 0.3)")
            for r in low_scores[:3]:
                print(f"    '{r['query'][:40]}...' (score: {r['avg_score']:.3f})")
        else:
            print("  ✅ Nenhum score muito baixo detectado")
        
        # 3. Consultas que falharam
        failed_queries = [r for r in results if not r['success']]
        if failed_queries:
            print(f"  ⚠️  {len(failed_queries)} consultas falharam")
            for r in failed_queries:
                print(f"    '{r['query'][:40]}...'")
        else:
            print("  ✅ Todas as consultas foram bem-sucedidas")
        
        print(f"\n📈 Resumo:")
        print(f"  Total de consultas: {len(results)}")
        print(f"  Consultas bem-sucedidas: {len([r for r in results if r['success']])}")
        print(f"  Busca híbrida: {len([r for r in results if r['source'] == 'hybrid'])}")
        print(f"  Apenas local: {len([r for r in results if r['source'] == 'local_only'])}")
        print(f"  Apenas web: {len([r for r in results if r['source'] == 'web_only'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        logger.error(f"Erro no teste: {str(e)}")
        return False


def main():
    """Função principal."""
    print("🚀 DesmentAI - Teste de Consistência")
    print("=" * 60)
    
    success = test_consistency()
    
    if success:
        print("\n🎉 Teste de consistência concluído!")
    else:
        print("\n❌ Teste falhou")
        sys.exit(1)


if __name__ == "__main__":
    main()
