# Relatório de Avaliação DesmentAI

## Resumo Executivo

- **Total de Perguntas:** 10
- **Pontuação Geral:** 0.513
- **Questões Problemáticas:** 10

## Métricas de Qualidade

| Métrica | Pontuação | Descrição |
|---------|-----------|-----------|
| Faithfulness | 0.384 | Fidelidade da resposta às fontes |
| Answer Relevancy | 0.326 | Relevância da resposta à pergunta |
| Context Precision | 0.775 | Precisão do contexto recuperado |
| Context Recall | 0.650 | Cobertura do contexto relevante |
| Answer Correctness | 0.428 | Correção da resposta |

## Análise

### Melhor Métrica
- **context_precision**: 0.775

### Pior Métrica
- **answer_relevancy**: 0.326

## Recomendações

1. **Melhorar Faithfulness**: Focar em respostas mais baseadas nas fontes
2. **Melhorar Answer Relevancy**: Garantir que as respostas sejam mais diretas
3. **Melhorar Context Precision**: Buscar contextos mais precisos
4. **Melhorar Context Recall**: Garantir cobertura completa do tópico
5. **Melhorar Answer Correctness**: Verificar precisão das respostas

## Detalhes Técnicos

- **Data da Avaliação**: 2025-09-22 23:29:21
- **Métricas Utilizadas**: RAGAS (Faithfulness, Answer Relevancy, Context Precision, Context Recall, Answer Correctness)
- **Modelo de Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS

---
*Relatório gerado automaticamente pelo sistema de avaliação DesmentAI*
