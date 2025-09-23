#!/usr/bin/env python3
"""
Script de teste específico para verificar o cálculo de scores de relevância.
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from src.utils.embeddings import EmbeddingManager
from src.agents.retriever_agent import RetrieverAgent
from src.utils.document_processor import DocumentProcessor
from langchain.schema import Document
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_scoring_calculation():
    """Testa o cálculo de scores de relevância."""
    try:
        print("🔍 Testando cálculo de scores de relevância")
        print("=" * 60)
        
        # Inicializar componentes
        print("Inicializando componentes...")
        embedding_manager = EmbeddingManager()
        document_processor = DocumentProcessor()
        
        # Carregar vector store
        vector_store = embedding_manager.load_vector_store("data/vector_store")
        if not vector_store:
            print("❌ Falha ao carregar vector store")
            return False
        
        print("✅ Vector store carregado com sucesso!")
        
        # Criar retriever agent (sem LLM para teste)
        retriever = RetrieverAgent(
            llm=None,  # Não precisamos do LLM para este teste
            vector_store=vector_store,
            document_processor=document_processor,
            embedding_manager=embedding_manager,
            min_local_docs=3,
            web_search_threshold=0.7
        )
        
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
        
        print(f"\n🧪 Testando {len(test_queries)} consultas...")
        print("-" * 60)
        
        results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            
            # Buscar documentos locais
            local_result = retriever.search_documents_local(query, k=5, score_threshold=0.6)
            
            # Mostrar resultados
            print(f"   Documentos encontrados: {local_result['num_documents']}")
            
            if local_result['documents']:
                scores = [doc['relevance_score'] for doc in local_result['documents']]
                raw_distances = [doc.get('raw_distance', 0) for doc in local_result['documents']]
                
                print(f"   Scores de relevância: {[f'{s:.3f}' for s in scores]}")
                print(f"   Distâncias brutas: {[f'{d:.3f}' for d in raw_distances]}")
                print(f"   Média: {sum(scores)/len(scores):.3f}")
                print(f"   Máximo: {max(scores):.3f}")
                print(f"   Mínimo: {min(scores):.3f}")
                
                # Verificar se deve buscar na web
                should_search_web = retriever.should_search_web(local_result)
                print(f"   Deve buscar na web: {should_search_web}")
                
                # Armazenar resultado
                results.append({
                    'query': query,
                    'num_docs': local_result['num_documents'],
                    'avg_score': sum(scores)/len(scores),
                    'max_score': max(scores),
                    'min_score': min(scores),
                    'should_search_web': should_search_web
                })
            else:
                print("   Nenhum documento encontrado")
                results.append({
                    'query': query,
                    'num_docs': 0,
                    'avg_score': 0,
                    'max_score': 0,
                    'min_score': 0,
                    'should_search_web': True
                })
        
        # Análise de consistência
        print(f"\n📊 Análise de Consistência")
        print("=" * 60)
        
        # Verificar distribuição de scores
        all_scores = [r['avg_score'] for r in results if r['avg_score'] > 0]
        if all_scores:
            print(f"Scores de relevância:")
            print(f"  Média geral: {sum(all_scores)/len(all_scores):.3f}")
            print(f"  Range: {min(all_scores):.3f} - {max(all_scores):.3f}")
            print(f"  Desvio padrão: {(sum([(s - sum(all_scores)/len(all_scores))**2 for s in all_scores]) / len(all_scores))**0.5:.3f}")
        
        # Verificar decisões de busca web
        web_searches = [r for r in results if r['should_search_web']]
        local_only = [r for r in results if not r['should_search_web']]
        
        print(f"\nDecisões de busca:")
        print(f"  Buscar na web: {len(web_searches)} consultas")
        print(f"  Apenas local: {len(local_only)} consultas")
        
        # Mostrar consultas que devem buscar na web
        if web_searches:
            print(f"\nConsultas que devem buscar na web:")
            for r in web_searches:
                print(f"  '{r['query'][:40]}...' (score: {r['avg_score']:.3f})")
        
        # Mostrar consultas que usam apenas local
        if local_only:
            print(f"\nConsultas que usam apenas local:")
            for r in local_only:
                print(f"  '{r['query'][:40]}...' (score: {r['avg_score']:.3f})")
        
        # Verificar inconsistências
        print(f"\n🔍 Verificando Inconsistências:")
        
        # 1. Consultas com scores similares mas decisões diferentes
        similar_scores = []
        for i, r1 in enumerate(results):
            for j, r2 in enumerate(results[i+1:], i+1):
                score_diff = abs(r1['avg_score'] - r2['avg_score'])
                if score_diff < 0.1 and r1['should_search_web'] != r2['should_search_web']:
                    similar_scores.append((r1, r2, score_diff))
        
        if similar_scores:
            print(f"  ⚠️  {len(similar_scores)} pares com scores similares mas decisões diferentes")
            for r1, r2, diff in similar_scores[:3]:
                print(f"    '{r1['query'][:30]}...' (score: {r1['avg_score']:.3f}, web: {r1['should_search_web']})")
                print(f"    '{r2['query'][:30]}...' (score: {r2['avg_score']:.3f}, web: {r2['should_search_web']})")
                print(f"    Diferença: {diff:.3f}")
        else:
            print("  ✅ Nenhuma inconsistência de decisão detectada")
        
        # 2. Scores muito baixos que não acionam busca web
        low_scores_no_web = [r for r in results if r['avg_score'] < 0.5 and not r['should_search_web']]
        if low_scores_no_web:
            print(f"  ⚠️  {len(low_scores_no_web)} consultas com scores baixos que não acionam busca web")
            for r in low_scores_no_web:
                print(f"    '{r['query'][:40]}...' (score: {r['avg_score']:.3f})")
        else:
            print("  ✅ Todas as consultas com scores baixos acionam busca web")
        
        print(f"\n📈 Resumo:")
        print(f"  Total de consultas: {len(results)}")
        print(f"  Consultas com documentos: {len([r for r in results if r['num_docs'] > 0])}")
        print(f"  Consultas que devem buscar na web: {len(web_searches)}")
        print(f"  Consultas que usam apenas local: {len(local_only)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        logger.error(f"Erro no teste: {str(e)}")
        return False


def main():
    """Função principal."""
    print("🚀 DesmentAI - Teste de Cálculo de Scores")
    print("=" * 60)
    
    success = test_scoring_calculation()
    
    if success:
        print("\n🎉 Teste de scores concluído!")
    else:
        print("\n❌ Teste falhou")
        sys.exit(1)


if __name__ == "__main__":
    main()
