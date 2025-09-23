"""
Agente Supervisor - Roteador principal que decide qual agente ativar.
"""

from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.language_models.base import BaseLanguageModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Agente supervisor que roteia consultas para outros agentes."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Inicializa o agente supervisor.
        
        Args:
            llm: Instância do modelo de linguagem
        """
        self.llm = llm
        self.system_prompt = """Você é um supervisor inteligente do sistema DesmentAI, responsável por rotear consultas de verificação de notícias.

Sua função é analisar a consulta do usuário e decidir qual agente deve ser ativado primeiro.

AGENTES DISPONÍVEIS:
- RETRIEVER: Para buscar informações relevantes na base de conhecimento
- SELF_CHECK: Para verificar se há evidências suficientes
- ANSWER: Para gerar respostas baseadas em evidências
- SAFETY: Para revisar respostas finais

REGRAS:
1. Para TODAS as consultas de verificação de notícias, sempre comece com RETRIEVER
2. O fluxo padrão é: RETRIEVER -> SELF_CHECK -> ANSWER -> SAFETY
3. Se a consulta não for sobre verificação de notícias, responda educadamente redirecionando

Responda APENAS com o nome do agente (RETRIEVER, SELF_CHECK, ANSWER, SAFETY) ou uma mensagem de redirecionamento."""

    def route_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Roteia uma consulta para o agente apropriado.
        
        Args:
            query: Consulta do usuário
            context: Contexto adicional (opcional)
            
        Returns:
            Nome do agente para ativar ou mensagem de redirecionamento
        """
        try:
            # Criar mensagem para o LLM
            messages = [
                HumanMessage(content=f"Consulta: {query}")
            ]
            
            # Fazer chamada para o LLM
            response = self.llm.invoke(messages)
            
            # Processar resposta
            if hasattr(response, 'content'):
                agent_name = response.content.strip().upper()
            else:
                agent_name = str(response).strip().upper()
            
            # Validar resposta
            valid_agents = ["RETRIEVER", "SELF_CHECK", "ANSWER", "SAFETY"]
            
            if agent_name in valid_agents:
                logger.info(f"Supervisor roteou para: {agent_name}")
                return agent_name
            else:
                # Se não for um agente válido, rotear para RETRIEVER por padrão
                logger.info(f"Supervisor retornou '{agent_name}', roteando para RETRIEVER")
                return "RETRIEVER"
                
        except Exception as e:
            logger.error(f"Erro no supervisor: {str(e)}")
            # Em caso de erro, rotear para RETRIEVER por padrão
            return "RETRIEVER"
    
    def should_continue(self, agent_name: str, result: Dict[str, Any]) -> str:
        """
        Decide se deve continuar para o próximo agente.
        
        Args:
            agent_name: Nome do agente atual
            result: Resultado do agente atual
            
        Returns:
            Nome do próximo agente ou "END" para finalizar
        """
        try:
            # Fluxo padrão: RETRIEVER -> SELF_CHECK -> ANSWER -> SAFETY
            flow = {
                "RETRIEVER": "SELF_CHECK",
                "SELF_CHECK": "ANSWER" if result.get("has_evidence", False) else "END",
                "ANSWER": "SAFETY",
                "SAFETY": "END"
            }
            
            next_agent = flow.get(agent_name, "END")
            logger.info(f"Próximo agente: {next_agent}")
            return next_agent
            
        except Exception as e:
            logger.error(f"Erro na decisão de continuação: {str(e)}")
            return "END"
    
    def get_agent_description(self, agent_name: str) -> str:
        """
        Retorna descrição de um agente.
        
        Args:
            agent_name: Nome do agente
            
        Returns:
            Descrição do agente
        """
        descriptions = {
            "RETRIEVER": "Busca informações relevantes na base de conhecimento",
            "SELF_CHECK": "Verifica se há evidências suficientes para responder",
            "ANSWER": "Gera resposta baseada nas evidências encontradas",
            "SAFETY": "Revisa a resposta final para garantir segurança"
        }
        
        return descriptions.get(agent_name, "Agente desconhecido")

