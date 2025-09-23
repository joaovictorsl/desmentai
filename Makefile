# DesmentAI - Sistema de Combate a Fake News
# Makefile para facilitar o desenvolvimento e uso

.PHONY: help install setup run test evaluate clean docker-build docker-run docker-stop

# Variáveis
PYTHON = python3
PIP = pip3
STREAMLIT = streamlit
DOCKER = docker
DOCKER_COMPOSE = docker compose

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m

help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)DesmentAI - Sistema de Combate a Fake News$(NC)"
	@echo "================================================"
	@echo ""
	@echo "$(YELLOW)Comandos disponíveis:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ===========================================
# COMANDOS BÁSICOS
# ===========================================

install: ## Instala as dependências Python
	@echo "$(YELLOW)Instalando dependências Python...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

setup: ## Configura dados iniciais e inicializa o sistema
	@echo "$(YELLOW)Configurando dados iniciais...$(NC)"
	$(PYTHON) scripts/setup_data.py
	@echo "$(GREEN)✅ Dados configurados!$(NC)"

run: ## Executa o sistema DesmentAI
	@echo "$(YELLOW)Iniciando DesmentAI...$(NC)"
	@echo "$(YELLOW)Certifique-se de que sua GEMINI_API_KEY está configurada$(NC)"
	$(STREAMLIT) run app.py
	@echo "$(GREEN)✅ DesmentAI iniciado!$(NC)"

test: ## Executa testes do sistema
	@echo "$(YELLOW)Executando testes...$(NC)"
	$(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)✅ Testes concluídos!$(NC)"

test-config: ## Testa configurações do sistema
	@echo "$(YELLOW)Testando configurações...$(NC)"
	$(PYTHON) scripts/test_configurations.py
	@echo "$(GREEN)✅ Teste de configurações concluído!$(NC)"

evaluate: ## Executa avaliação completa com RAGAS (10 perguntas)
	@echo "$(YELLOW)Executando avaliação RAGAS completa...$(NC)"
	$(PYTHON) scripts/evaluate.py full
	@echo "$(GREEN)✅ Avaliação completa concluída!$(NC)"

evaluate-quick: ## Executa avaliação rápida (3 perguntas)
	@echo "$(YELLOW)Executando avaliação rápida...$(NC)"
	$(PYTHON) scripts/evaluate.py
	@echo "$(GREEN)✅ Avaliação rápida concluída!$(NC)"

clean: ## Limpa arquivos temporários e cache
	@echo "$(YELLOW)Limpando arquivos temporários...$(NC)"
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.pyc
	rm -rf .streamlit/
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

clean-data: ## Limpa dados processados (mantém dados brutos)
	@echo "$(YELLOW)Limpando dados processados...$(NC)"
	rm -rf data/processed/
	rm -rf data/vector_store/
	rm -rf eval/results/
	@echo "$(GREEN)✅ Dados processados limpos!$(NC)"

# ===========================================
# COMANDOS DOCKER
# ===========================================

docker-build: ## Constrói a imagem Docker
	@echo "$(YELLOW)Construindo imagem Docker...$(NC)"
	$(DOCKER) build -t desmentai .
	@echo "$(GREEN)✅ Imagem Docker construída!$(NC)"

docker-run: ## Executa o sistema com Docker Compose
	@echo "$(YELLOW)Executando com Docker Compose...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Arquivo .env não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute: make config-gemini$(NC)"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) up --build
	@echo "$(GREEN)✅ Sistema executado com Docker!$(NC)"

docker-stop: ## Para o sistema Docker
	@echo "$(YELLOW)Parando sistema Docker...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Sistema Docker parado!$(NC)"

# ===========================================
# CONFIGURAÇÕES DE MODELO
# ===========================================

config-gemini: ## Configura para Gemini 2.0 Flash (recomendado)
	@echo "$(YELLOW)Configurando para Gemini 2.0 Flash...$(NC)"
	@echo "MODEL_NAME=gemini-2.0-flash" > .env
	@echo "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2" >> .env
	@echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
	@echo "LLM_TEMPERATURE=0.1" >> .env
	@echo "LLM_TOP_P=0.9" >> .env
	@echo "LLM_TOP_K=40" >> .env
	@echo "LLM_REPEAT_PENALTY=1.1" >> .env
	@echo "VECTOR_STORE_PATH=data/vector_store" >> .env
	@echo "DATA_PATH=data/raw" >> .env
	@echo "CHUNK_SIZE=1000" >> .env
	@echo "CHUNK_OVERLAP=200" >> .env
	@echo "MAX_DOCUMENTS=5" >> .env
	@echo "SIMILARITY_THRESHOLD=0.6" >> .env
	@echo "LOG_LEVEL=INFO" >> .env
	@echo "$(GREEN)✅ Configurado para Gemini 2.0 Flash!$(NC)"
	@echo "$(BLUE)Modelo: Gemini 2.0 Flash (via API)$(NC)"
	@echo "$(BLUE)Embeddings: all-MiniLM-L6-v2 (22MB)$(NC)"
	@echo "$(YELLOW)⚠️  Lembre-se de configurar sua GEMINI_API_KEY no arquivo .env$(NC)"

config-gemini-1.5: ## Configura para Gemini 1.5 Pro (melhor qualidade)
	@echo "$(YELLOW)Configurando para Gemini 1.5 Pro...$(NC)"
	@echo "MODEL_NAME=gemini-1.5-pro" > .env
	@echo "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2" >> .env
	@echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
	@echo "LLM_TEMPERATURE=0.1" >> .env
	@echo "LLM_TOP_P=0.9" >> .env
	@echo "LLM_TOP_K=40" >> .env
	@echo "LLM_REPEAT_PENALTY=1.1" >> .env
	@echo "VECTOR_STORE_PATH=data/vector_store" >> .env
	@echo "DATA_PATH=data/raw" >> .env
	@echo "CHUNK_SIZE=1000" >> .env
	@echo "CHUNK_OVERLAP=200" >> .env
	@echo "MAX_DOCUMENTS=5" >> .env
	@echo "SIMILARITY_THRESHOLD=0.6" >> .env
	@echo "LOG_LEVEL=INFO" >> .env
	@echo "$(GREEN)✅ Configurado para Gemini 1.5 Pro!$(NC)"
	@echo "$(BLUE)Modelo: Gemini 1.5 Pro (via API)$(NC)"
	@echo "$(BLUE)Embeddings: all-MiniLM-L6-v2 (22MB)$(NC)"
	@echo "$(YELLOW)⚠️  Lembre-se de configurar sua GEMINI_API_KEY no arquivo .env$(NC)"

config-gemini-flash: ## Configura para Gemini 1.5 Flash (mais rápido)
	@echo "$(YELLOW)Configurando para Gemini 1.5 Flash...$(NC)"
	@echo "MODEL_NAME=gemini-1.5-flash" > .env
	@echo "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2" >> .env
	@echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
	@echo "LLM_TEMPERATURE=0.1" >> .env
	@echo "LLM_TOP_P=0.9" >> .env
	@echo "LLM_TOP_K=40" >> .env
	@echo "LLM_REPEAT_PENALTY=1.1" >> .env
	@echo "VECTOR_STORE_PATH=data/vector_store" >> .env
	@echo "DATA_PATH=data/raw" >> .env
	@echo "CHUNK_SIZE=1000" >> .env
	@echo "CHUNK_OVERLAP=200" >> .env
	@echo "MAX_DOCUMENTS=5" >> .env
	@echo "SIMILARITY_THRESHOLD=0.6" >> .env
	@echo "LOG_LEVEL=INFO" >> .env
	@echo "$(GREEN)✅ Configurado para Gemini 1.5 Flash!$(NC)"
	@echo "$(BLUE)Modelo: Gemini 1.5 Flash (via API)$(NC)"
	@echo "$(BLUE)Embeddings: all-MiniLM-L6-v2 (22MB)$(NC)"
	@echo "$(YELLOW)⚠️  Lembre-se de configurar sua GEMINI_API_KEY no arquivo .env$(NC)"

# ===========================================
# CONFIGURAÇÕES RÁPIDAS COMPLETAS
# ===========================================

quick-start: config-gemini install setup ## Configuração rápida completa
	@echo "$(GREEN)✅ Configuração rápida concluída!$(NC)"
	@echo "$(YELLOW)⚠️  Lembre-se de configurar sua GEMINI_API_KEY no arquivo .env$(NC)"
	@echo "$(BLUE)Para executar: make run$(NC)"

quick-start-1.5: config-gemini-1.5 install setup ## Configuração rápida com Gemini 1.5 Pro
	@echo "$(GREEN)✅ Configuração rápida com Gemini 1.5 Pro concluída!$(NC)"
	@echo "$(YELLOW)⚠️  Lembre-se de configurar sua GEMINI_API_KEY no arquivo .env$(NC)"
	@echo "$(BLUE)Para executar: make run$(NC)"

# ===========================================
# COMANDOS DE STATUS E INFORMAÇÕES
# ===========================================

status: ## Mostra status do sistema
	@echo "$(YELLOW)Status do DesmentAI:$(NC)"
	@echo "================================"
	@echo "$(YELLOW)Python:$(NC) $(shell $(PYTHON) --version)"
	@echo "$(YELLOW)Pip:$(NC) $(shell $(PIP) --version)"
	@echo "$(YELLOW)Docker:$(NC) $(shell $(DOCKER) --version 2>/dev/null || echo 'Não instalado')"
	@echo "$(YELLOW)Docker Compose:$(NC) $(shell $(DOCKER_COMPOSE) --version 2>/dev/null || echo 'Não instalado')"
	@echo ""
	@echo "$(YELLOW)Verificando Gemini...$(NC)"
	@if [ -f .env ]; then \
		if grep -q "GEMINI_API_KEY=" .env && ! grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then \
			echo "$(GREEN)✅ GEMINI_API_KEY configurada!$(NC)"; \
		else \
			echo "$(RED)❌ GEMINI_API_KEY não configurada!$(NC)"; \
			echo "$(YELLOW)Execute: make config-gemini$(NC)"; \
		fi; \
	else \
		echo "$(RED)❌ Arquivo .env não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute: make config-gemini$(NC)"; \
	fi

show-config: ## Mostra configuração atual
	@echo "$(YELLOW)Configuração atual:$(NC)"
	@echo "========================"
	@if [ -f .env ]; then \
		echo "$(BLUE)Arquivo .env encontrado:$(NC)"; \
		cat .env; \
	else \
		echo "$(RED)Arquivo .env não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute: make config-gemini$(NC)"; \
	fi

show-models: ## Mostra modelos disponíveis
	@echo "$(YELLOW)Modelos disponíveis para DesmentAI:$(NC)"
	@echo "============================================="
	@echo "$(BLUE)Modelos de Linguagem (Gemini):$(NC)"
	@echo "  • gemini-2.0-flash  - Mais recente (recomendado)"
	@echo "  • gemini-1.5-pro    - Melhor qualidade"
	@echo "  • gemini-1.5-flash  - Mais rápido"
	@echo "  • gemini-1.0-pro    - Versão estável"
	@echo ""
	@echo "$(BLUE)Modelos de Embeddings:$(NC)"
	@echo "  • all-MiniLM-L6-v2                    - Rápido (22MB) - RECOMENDADO"
	@echo "  • paraphrase-multilingual-MiniLM-L12-v2 - Multilíngue (118MB)"
	@echo "  • BAAI/bge-small-en-v1.5              - Boa qualidade (33MB)"

# Comando padrão
.DEFAULT_GOAL := help