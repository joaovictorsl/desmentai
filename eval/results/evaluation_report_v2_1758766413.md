# Relatório de Avaliação DesmentAI v2 - Dados Reais

## Resumo Executivo

- **Total de Perguntas:** 10
- **Perguntas Processadas com Sucesso:** 10
- **Perguntas com Contextos:** 10
- **Pontuação Geral:** 0.421
- **Questões Problemáticas:** 9

## Métricas de Qualidade

| Métrica | Pontuação | Descrição |
|---------|-----------|-----------|
| Faithfulness | 0.424 | Fidelidade da resposta às fontes |
| Answer Relevancy | 0.000 | Relevância da resposta à pergunta |
| Context Precision | 0.738 | Precisão do contexto recuperado |
| Context Recall | 0.433 | Cobertura do contexto relevante |
| Answer Correctness | 0.508 | Correção da resposta |

## Análise Detalhada

### Melhor Métrica
- **context_precision**: 0.738

### Pior Métrica
- **answer_relevancy**: 0.000

## Questões Problemáticas

9 questões apresentaram faithfulness < 0.7

## Detalhes Técnicos

- **Data da Avaliação**: 2025-09-24 23:13:33
- **Tipo de Avaliação**: Dados reais do sistema
- **Métricas Utilizadas**: RAGAS (Faithfulness, Answer Relevancy, Context Precision, Context Recall, Answer Correctness)
- **Modelo de Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **Busca**: Híbrida (Local + Web)

---
*Relatório gerado automaticamente pelo sistema de avaliação DesmentAI v2 com dados reais*
