# Relatório de Avaliação DesmentAI v2 - Dados Reais

## Resumo Executivo

- **Total de Perguntas:** 3
- **Perguntas Processadas com Sucesso:** 3
- **Perguntas com Contextos:** 3
- **Pontuação Geral:** 0.513
- **Questões Problemáticas:** 3

## Métricas de Qualidade

| Métrica | Pontuação | Descrição |
|---------|-----------|-----------|
| Faithfulness | 0.394 | Fidelidade da resposta às fontes |
| Answer Relevancy | 0.333 | Relevância da resposta à pergunta |
| Context Precision | 0.629 | Precisão do contexto recuperado |
| Context Recall | 0.667 | Cobertura do contexto relevante |
| Answer Correctness | 0.544 | Correção da resposta |

## Análise Detalhada

### Melhor Métrica
- **context_recall**: 0.667

### Pior Métrica
- **answer_relevancy**: 0.333

## Questões Problemáticas

3 questões apresentaram faithfulness < 0.7

## Detalhes Técnicos

- **Data da Avaliação**: 2025-09-24 22:49:46
- **Tipo de Avaliação**: Dados reais do sistema
- **Métricas Utilizadas**: RAGAS (Faithfulness, Answer Relevancy, Context Precision, Context Recall, Answer Correctness)
- **Modelo de Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **Busca**: Híbrida (Local + Web)

---
*Relatório gerado automaticamente pelo sistema de avaliação DesmentAI v2 com dados reais*
