# 🔍 DesmentAI - Sistema de Combate a Fake News

Sistema inteligente de verificação de notícias utilizando **RAG (Retrieval-Augmented Generation)** e **agentes LangGraph** com Google Gemini.

## 🚀 Características

- **☁️ Google Gemini**: Modelos de linguagem avançados via API
- **🧠 RAG Avançado**: Recuperação e geração baseada em documentos confiáveis
- **🕸️ Agentes Inteligentes**: Arquitetura multi-agente com LangGraph
- **📊 Avaliação RAGAS**: Métricas de qualidade e performance
- **🎨 Interface Streamlit**: Interface web moderna e responsiva
- **🐳 Docker**: Containerização completa para reproduzibilidade

## 🏗️ Arquitetura

### Stack Tecnológica
- **Python 3.11+**
- **LangChain + LangGraph** - Framework de agentes
- **FAISS/Chroma** - Banco de dados vetorial
- **Google Gemini** - Modelos de linguagem via API
- **HuggingFace** - Embeddings (all-MiniLM-L6-v2, bge-small)
- **Streamlit** - Interface de usuário

### Modelos Suportados

#### Modelos de Linguagem (Google Gemini)
| Modelo | Descrição | Recomendado |
|--------|-----------|-------------|
| `gemini-2.0-flash` | Versão mais recente e rápida | ⭐ |
| `gemini-1.5-pro` | Versão mais avançada | ⭐ |
| `gemini-1.5-flash` | Versão rápida | |
| `gemini-1.0-pro` | Versão estável | |

#### Modelos de Embeddings
| Modelo | Tamanho | Descrição | Recomendado |
|--------|---------|-----------|-------------|
| `all-MiniLM-L6-v2` | 22MB | Rápido e eficiente | ⭐ |
| `paraphrase-multilingual-MiniLM-L12-v2` | 118MB | Multilíngue | ⭐ |
| `BAAI/bge-small-en-v1.5` | 33MB | Boa qualidade | ⭐ |

## ⚡ Início Rápido

### 1. Configuração Rápida (Recomendada)
```bash
# Clone o repositório
git clone <repository-url>
cd desmentai

# Configuração com Gemini 2.0 Flash
make quick-start

# Configure sua API key no arquivo .env
# Obtenha sua chave em: https://makersuite.google.com/app/apikey
```

### 2. Configuração Manual
```bash
# Instalar dependências
make install

# Configurar modelo (escolha uma opção)
make config-gemini           # Gemini 2.0 Flash (recomendado)
make config-gemini-1.5       # Gemini 1.5 Pro (melhor qualidade)
make config-gemini-flash     # Gemini 1.5 Flash (mais rápido)

# Configurar dados
make setup

# Executar sistema
make run
```

## 🎯 Configurações Disponíveis

### Configuração Padrão (Recomendada)
- **Modelo**: Gemini 2.0 Flash
- **Embeddings**: all-MiniLM-L6-v2
- **Uso**: Uso geral, boa qualidade e velocidade

### Configuração de Alta Qualidade
- **Modelo**: Gemini 1.5 Pro
- **Embeddings**: all-MiniLM-L6-v2
- **Uso**: Máxima qualidade, mais lenta

### Configuração Rápida
- **Modelo**: Gemini 1.5 Flash
- **Embeddings**: all-MiniLM-L6-v2
- **Uso**: Respostas mais rápidas

## 🛠️ Comandos Úteis

### Configuração
```bash
make config-gemini           # Gemini 2.0 Flash (recomendado)
make config-gemini-1.5       # Gemini 1.5 Pro (melhor qualidade)
make config-gemini-flash     # Gemini 1.5 Flash (mais rápido)
```

### Sistema
```bash
make run                     # Executar sistema
make test-config             # Testar configurações
make evaluate                # Avaliação RAGAS
make status                  # Status do sistema
```

### Desenvolvimento
```bash
make install                 # Instalar dependências
make setup                   # Configurar dados
make test                    # Executar testes
make clean                   # Limpar arquivos temporários
```

### Docker
```bash
make docker-build            # Construir imagem
make docker-run              # Executar com Docker
make docker-stop             # Parar Docker
```

## 📊 Avaliação

O sistema inclui avaliação automática usando **RAGAS** com métricas de qualidade para verificação de fake news.

### 🎯 Métricas de Qualidade

| Métrica | Pontuação | Descrição | Status |
|---------|-----------|-----------|---------|
| **Faithfulness** | 0.384 | Fidelidade da resposta às fontes | ⚠️ Melhorar |
| **Answer Relevancy** | 0.326 | Relevância da resposta à pergunta | ⚠️ Melhorar |
| **Context Precision** | 0.775 | Precisão do contexto recuperado | ✅ Excelente |
| **Context Recall** | 0.650 | Cobertura do contexto relevante | ✅ Bom |
| **Answer Correctness** | 0.428 | Correção da resposta | ⚠️ Melhorar |

### 📈 Resultados da Avaliação

- **Total de Perguntas**: 10 perguntas de teste
- **Pontuação Geral**: 0.513/1.0
- **Melhor Métrica**: Context Precision (0.775)
- **Pior Métrica**: Answer Relevancy (0.326)

### 🔍 Análise dos Resultados

**✅ Pontos Fortes:**
- **Context Precision (0.775)**: O sistema recupera contextos muito relevantes
- **Context Recall (0.650)**: Boa cobertura do contexto necessário

**⚠️ Pontos de Melhoria:**
- **Faithfulness (0.384)**: Respostas precisam ser mais baseadas nas fontes
- **Answer Relevancy (0.326)**: Respostas precisam ser mais diretas à pergunta
- **Answer Correctness (0.428)**: Precisão das respostas pode ser melhorada

### 🚀 Como Executar a Avaliação

```bash
# Avaliação rápida (3 perguntas)
make evaluate-quick

# Avaliação completa (10 perguntas)
make evaluate

# Avaliação com relatório detalhado
python scripts/evaluate.py full
```

### 📊 Relatórios Gerados

A avaliação gera automaticamente:
- **Relatório Markdown**: `eval/results/evaluation_report_*.md`
- **Dados Detalhados**: `eval/results/evaluation_detailed_*.json`
- **Resumo das Métricas**: `eval/results/evaluation_summary_*.json`

### 🎯 Configuração para RAGAS

Para executar a avaliação, configure as chaves API necessárias:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Para RAGAS
TAVILY_API_KEY=your_tavily_api_key_here  # Para busca web
```

**Nota**: O RAGAS utiliza OpenAI para algumas métricas, mas o sistema principal funciona com Gemini.

## 🐳 Docker

### Execução com Docker
```bash
# Construir e executar
make docker-run

# Apenas construir
make docker-build

# Parar
make docker-stop
```

### Configuração para Docker
```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar .env com sua API key
nano .env

# Executar
make docker-run
```

## 📁 Estrutura do Projeto

```
desmentai/
├── src/
│   ├── agents/           # Agentes LangGraph
│   ├── core/            # Lógica principal
│   ├── utils/           # Utilitários
│   └── evaluation/      # Avaliação RAGAS
├── app.py               # Interface Streamlit
├── scripts/             # Scripts de configuração
├── data/                # Dados e vector store
├── docs/                # Documentação
├── requirements.txt     # Dependências
├── Dockerfile          # Container
├── docker-compose.yml  # Orquestração
└── Makefile            # Automação
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente (.env)
```bash
# Modelo de linguagem
MODEL_NAME=gemini-2.0-flash

# Chave API do Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Modelo de embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Configurações de performance
LLM_TEMPERATURE=0.1
LLM_TOP_P=0.9
LLM_TOP_K=40
LLM_REPEAT_PENALTY=1.1

# Caminhos
VECTOR_STORE_PATH=data/vector_store
DATA_PATH=data/raw
```

### Personalização de Modelos
```python
# src/utils/llm_loader.py
loader = LLMLoader()
loader.update_model("gemini-1.5-pro")
loader.update_embedding_model("BAAI/bge-small-en-v1.5")
```

## 🚨 Solução de Problemas

### Gemini não conecta
```bash
# Verificar status
make status

# Verificar API key
grep GEMINI_API_KEY .env
```

### Erro de dependências
```bash
# Limpar e reinstalar
make clean
make install
```

### Performance lenta
- Use modelo mais rápido: `make config-gemini-flash`
- Ajuste temperatura: `LLM_TEMPERATURE=0.0`
- Verifique conexão com a API do Gemini

### Docker não inicia
```bash
# Verificar se .env existe
ls -la .env

# Verificar configuração
make show-config
```

## 📈 Performance

### Tempos de Resposta (aproximados)
- **Gemini 2.0 Flash**: ~2-5s
- **Gemini 1.5 Pro**: ~3-8s
- **Gemini 1.5 Flash**: ~1-4s
- **Gemini 1.0 Pro**: ~2-6s

### Requisitos de Sistema
- **RAM**: 4GB+ (recomendado 8GB+)
- **CPU**: 2+ cores
- **Armazenamento**: 5GB+ livres
- **Internet**: Conexão estável para API do Gemini

## 🔑 Configuração da API

### Obter Chave do Google Gemini
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada
5. Cole no arquivo `.env`:
   ```bash
   GEMINI_API_KEY=sua_chave_aqui
   ```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Equipe

- **Desenvolvimento**: Equipe DesmentAI
- **Arquitetura**: RAG + LangGraph + Google Gemini
- **Avaliação**: RAGAS Framework

---

**DesmentAI** - Combatendo fake news com inteligência artificial! 🚀