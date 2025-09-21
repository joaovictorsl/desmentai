"""
Grafo LangGraph para orquestração dos agentes do DesmentAI.
"""

from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DesmentAIState(TypedDict):
    """Estado do grafo DesmentAI."""
    query: str
    documents: List[Dict[str, Any]]
    key_claims: List[str]
    evidence_quality: str
    has_evidence: bool
    answer: str
    conclusion: str
    citations: List[Dict[str, Any]]
    final_answer: str
    agent_results: Dict[str, Any]
    current_agent: str
    error: str


class DesmentAIGraph:
    """Grafo LangGraph para orquestração dos agentes."""
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Inicializa o grafo DesmentAI.
        
        Args:
            agents: Dicionário com instâncias dos agentes
        """
        self.agents = agents
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo LangGraph."""
        try:
            # Criar grafo
            workflow = StateGraph(DesmentAIState)
            
            # Adicionar nós
            workflow.add_node("supervisor", self._supervisor_node)
            workflow.add_node("retriever", self._retriever_node)
            workflow.add_node("self_check", self._self_check_node)
            workflow.add_node("answer", self._answer_node)
            workflow.add_node("safety", self._safety_node)
            workflow.add_node("error_handler", self._error_handler_node)
            
            # Definir ponto de entrada
            workflow.set_entry_point("supervisor")
            
            # Adicionar arestas condicionais
            workflow.add_conditional_edges(
                "supervisor",
                self._supervisor_router,
                {
                    "retriever": "retriever",
                    "error_handler": "error_handler",
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "retriever",
                self._retriever_router,
                {
                    "self_check": "self_check",
                    "error_handler": "error_handler",
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "self_check",
                self._self_check_router,
                {
                    "answer": "answer",
                    "error_handler": "error_handler",
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "answer",
                self._answer_router,
                {
                    "safety": "safety",
                    "error_handler": "error_handler",
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "safety",
                self._safety_router,
                {
                    "end": END,
                    "error_handler": "error_handler"
                }
            )
            
            workflow.add_edge("error_handler", END)
            
            # Compilar grafo
            return workflow.compile()
            
        except Exception as e:
            logger.error(f"Erro ao construir grafo: {str(e)}")
            raise
    
    def _supervisor_node(self, state: DesmentAIState) -> DesmentAIState:
        """Nó do supervisor."""
        try:
            query = state.get("query", "")
            if not query:
                state["error"] = "Consulta vazia"
                return state
            
            # Rotear consulta
            agent_name = self.agents["supervisor"].route_query(query)
            
            if agent_name == "RETRIEVER":
                state["current_agent"] = "retriever"
                state["agent_results"] = {"supervisor": {"routed_to": "retriever"}}
            else:
                # Mensagem de redirecionamento
                state["final_answer"] = agent_name
                state["current_agent"] = "end"
            
            return state
            
        except Exception as e:
            logger.error(f"Erro no supervisor: {str(e)}")
            state["error"] = str(e)
            return state
    
    def _retriever_node(self, state: DesmentAIState) -> DesmentAIState:
        """Nó do retriever."""
        try:
            query = state.get("query", "")
            result = self.agents["retriever"].process_query(query)
            
            state["documents"] = result.get("documents", [])
            state["key_claims"] = result.get("key_claims", [])
            state["agent_results"] = state.get("agent_results", {})
            state["agent_results"]["retriever"] = result
            
            return state
            
        except Exception as e:
            logger.error(f"Erro no retriever: {str(e)}")
            state["error"] = str(e)
            return state
    
    def _self_check_node(self, state: DesmentAIState) -> DesmentAIState:
        """Nó do self-check."""
        try:
            query = state.get("query", "")
            documents = state.get("documents", [])
            
            result = self.agents["self_check"].process_query(query, documents)
            
            state["evidence_quality"] = result.get("evidence_quality", "INSUFFICIENT")
            state["has_evidence"] = result.get("has_evidence", False)
            state["agent_results"] = state.get("agent_results", {})
            state["agent_results"]["self_check"] = result
            
            return state
            
        except Exception as e:
            logger.error(f"Erro no self-check: {str(e)}")
            state["error"] = str(e)
            return state
    
    def _answer_node(self, state: DesmentAIState) -> DesmentAIState:
        """Nó do answer."""
        try:
            query = state.get("query", "")
            documents = state.get("documents", [])
            evidence_quality = state.get("evidence_quality", "INSUFFICIENT")
            
            result = self.agents["answer"].process_query(query, documents, evidence_quality)
            
            state["answer"] = result.get("answer", "")
            state["conclusion"] = result.get("conclusion", "INSUFICIENTE")
            state["citations"] = result.get("citations", [])
            state["agent_results"] = state.get("agent_results", {})
            state["agent_results"]["answer"] = result
            
            return state
            
        except Exception as e:
            logger.error(f"Erro no answer: {str(e)}")
            state["error"] = str(e)
            return state
    
    def _safety_node(self, state: DesmentAIState) -> DesmentAIState:
        """Nó do safety."""
        try:
            query = state.get("query", "")
            answer = state.get("answer", "")
            conclusion = state.get("conclusion", "")
            
            result = self.agents["safety"].process_query(query, answer, conclusion)
            
            state["final_answer"] = result.get("final_answer", answer)
            state["agent_results"] = state.get("agent_results", {})
            state["agent_results"]["safety"] = result
            
            return state
            
        except Exception as e:
            logger.error(f"Erro no safety: {str(e)}")
            state["error"] = str(e)
            return state
    
    def _error_handler_node(self, state: DesmentAIState) -> DesmentAIState:
        """Nó de tratamento de erros."""
        error = state.get("error", "Erro desconhecido")
        state["final_answer"] = f"❌ Erro no processamento: {error}"
        return state
    
    def _supervisor_router(self, state: DesmentAIState) -> str:
        """Roteador do supervisor."""
        if state.get("error"):
            return "error_handler"
        elif state.get("current_agent") == "retriever":
            return "retriever"
        else:
            return "end"
    
    def _retriever_router(self, state: DesmentAIState) -> str:
        """Roteador do retriever."""
        if state.get("error"):
            return "error_handler"
        elif state.get("documents"):
            return "self_check"
        else:
            return "error_handler"
    
    def _self_check_router(self, state: DesmentAIState) -> str:
        """Roteador do self-check."""
        if state.get("error"):
            return "error_handler"
        elif state.get("has_evidence"):
            return "answer"
        else:
            return "end"
    
    def _answer_router(self, state: DesmentAIState) -> str:
        """Roteador do answer."""
        if state.get("error"):
            return "error_handler"
        else:
            return "safety"
    
    def _safety_router(self, state: DesmentAIState) -> str:
        """Roteador do safety."""
        if state.get("error"):
            return "error_handler"
        else:
            return "end"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processa uma consulta através do grafo.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Resultado do processamento
        """
        try:
            # Estado inicial
            initial_state = DesmentAIState(
                query=query,
                documents=[],
                key_claims=[],
                evidence_quality="",
                has_evidence=False,
                answer="",
                conclusion="",
                citations=[],
                final_answer="",
                agent_results={},
                current_agent="",
                error=""
            )
            
            # Executar grafo
            result = self.graph.invoke(initial_state)
            
            # Preparar resultado final
            return {
                "query": query,
                "final_answer": result.get("final_answer", ""),
                "conclusion": result.get("conclusion", ""),
                "citations": result.get("citations", []),
                "agent_results": result.get("agent_results", {}),
                "error": result.get("error", ""),
                "success": not bool(result.get("error", ""))
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento da consulta: {str(e)}")
            return {
                "query": query,
                "final_answer": f"❌ Erro no processamento: {str(e)}",
                "conclusion": "ERRO",
                "citations": [],
                "agent_results": {},
                "error": str(e),
                "success": False
            }
