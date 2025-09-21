"""
Agente Safety - Revisa respostas finais para garantir segurança e ética.
"""

from typing import Dict, Any, List
from langchain_core.language_models.base import BaseLanguageModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetyAgent:
    """Agente responsável por revisar respostas finais para garantir segurança."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Inicializa o agente safety.
        
        Args:
            llm: Instância do modelo de linguagem
        """
        self.llm = llm
        self.system_prompt = """Você é um agente de segurança especializado em revisar respostas de verificação de notícias.

Sua função é garantir que as respostas sejam seguras, éticas e não ofereçam conselhos perigosos.

CRITÉRIOS DE SEGURANÇA:
1. Não oferecer conselhos legais específicos
2. Não fornecer diagnósticos médicos
3. Não dar conselhos financeiros específicos
4. Não promover violência ou discurso de ódio
5. Incluir disclaimers apropriados
6. Manter neutralidade e objetividade

AÇÕES POSSÍVEIS:
- APPROVE: Resposta aprovada
- MODIFY: Resposta precisa de modificação
- REJECT: Resposta rejeitada por questões de segurança

SEMPRE inclua um disclaimer padrão."""

    def review_response(self, query: str, answer: str, conclusion: str) -> Dict[str, Any]:
        """
        Revisa uma resposta para questões de segurança.
        
        Args:
            query: Consulta original
            answer: Resposta gerada
            conclusion: Conclusão sobre a veracidade
            
        Returns:
            Dicionário com revisão de segurança
        """
        try:
            # Prompt de revisão
            review_prompt = f"""
            Consulte: "{query}"
            Conclusão: {conclusion}
            Resposta: {answer}
            
            Revise esta resposta para questões de segurança e ética.
            
            Verifique se:
            1. A resposta oferece conselhos legais, médicos ou financeiros específicos
            2. A resposta promove violência ou discurso de ódio
            3. A resposta é neutra e objetiva
            4. A resposta inclui disclaimers apropriados
            
            Responda no formato:
            DECISÃO: [APPROVE/MODIFY/REJECT]
            MOTIVO: [explicação da decisão]
            SUGESTÕES: [sugestões de melhoria se MODIFY]
            """
            
            # Fazer chamada para o LLM
            response = self.llm.invoke(review_prompt)
            
            # Processar resposta
            result = self._parse_safety_response(response.content)
            
            # Adicionar disclaimer padrão
            result["disclaimer"] = self._get_standard_disclaimer()
            
            # Adicionar metadados
            result.update({
                "query": query,
                "original_answer": answer,
                "original_conclusion": conclusion,
                "agent": "SAFETY"
            })
            
            logger.info(f"Safety revisou resposta: {result['decision']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro na revisão de segurança: {str(e)}")
            return {
                "decision": "APPROVE",
                "reason": f"Erro na revisão: {str(e)}",
                "suggestions": [],
                "disclaimer": self._get_standard_disclaimer(),
                "query": query,
                "original_answer": answer,
                "original_conclusion": conclusion,
                "agent": "SAFETY"
            }
    
    def _parse_safety_response(self, response: str) -> Dict[str, Any]:
        """
        Processa a resposta do LLM para extrair a revisão de segurança.
        
        Args:
            response: Resposta do LLM
            
        Returns:
            Dicionário com revisão processada
        """
        try:
            lines = response.strip().split('\n')
            decision = "APPROVE"
            reason = "Resposta aprovada"
            suggestions = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("DECISÃO:"):
                    decision = line.split(":", 1)[1].strip().upper()
                elif line.startswith("MOTIVO:"):
                    reason = line.split(":", 1)[1].strip()
                elif line.startswith("SUGESTÕES:"):
                    suggestions_text = line.split(":", 1)[1].strip()
                    if suggestions_text:
                        suggestions = [s.strip() for s in suggestions_text.split(',')]
            
            return {
                "decision": decision,
                "reason": reason,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta de segurança: {str(e)}")
            return {
                "decision": "APPROVE",
                "reason": f"Erro no processamento: {str(e)}",
                "suggestions": []
            }
    
    def _get_standard_disclaimer(self) -> str:
        """
        Retorna o disclaimer padrão do sistema.
        
        Returns:
            Disclaimer padrão
        """
        return """⚠️ **DISCLAIMER IMPORTANTE** ⚠️

Esta informação é baseada em dados públicos disponíveis e não substitui a consulta a fontes primárias ou especialistas. O objetivo é fornecer uma análise informativa com base nas fontes disponíveis.

- Não oferecemos conselhos legais, médicos ou financeiros específicos
- Recomendamos sempre consultar fontes oficiais e especialistas
- As informações podem estar desatualizadas ou incompletas
- Use esta ferramenta como ponto de partida para investigação adicional"""
    
    def check_harmful_content(self, text: str) -> Dict[str, Any]:
        """
        Verifica se o texto contém conteúdo potencialmente prejudicial.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            Dicionário com resultado da verificação
        """
        try:
            # Palavras-chave potencialmente problemáticas
            harmful_keywords = [
                "conselho legal", "advogado", "processo judicial",
                "diagnóstico", "tratamento médico", "medicamento",
                "investimento", "compra de ações", "conselho financeiro",
                "violência", "ódio", "discriminação"
            ]
            
            text_lower = text.lower()
            found_keywords = [keyword for keyword in harmful_keywords if keyword in text_lower]
            
            return {
                "is_harmful": len(found_keywords) > 0,
                "found_keywords": found_keywords,
                "risk_level": "HIGH" if len(found_keywords) > 2 else "MEDIUM" if found_keywords else "LOW"
            }
            
        except Exception as e:
            logger.error(f"Erro na verificação de conteúdo prejudicial: {str(e)}")
            return {
                "is_harmful": False,
                "found_keywords": [],
                "risk_level": "LOW"
            }
    
    def add_safety_measures(self, answer: str) -> str:
        """
        Adiciona medidas de segurança à resposta.
        
        Args:
            answer: Resposta original
            
        Returns:
            Resposta com medidas de segurança adicionadas
        """
        try:
            # Verificar conteúdo prejudicial
            harm_check = self.check_harmful_content(answer)
            
            # Adicionar disclaimer se necessário
            if harm_check["is_harmful"]:
                safety_note = f"\n\n⚠️ **AVISO DE SEGURANÇA**: Esta resposta pode conter informações que requerem consulta a especialistas.\n"
                answer = answer + safety_note
            
            # Adicionar disclaimer padrão
            disclaimer = self._get_standard_disclaimer()
            final_answer = f"{answer}\n\n{disclaimer}"
            
            return final_answer
            
        except Exception as e:
            logger.error(f"Erro ao adicionar medidas de segurança: {str(e)}")
            return answer + f"\n\n{self._get_standard_disclaimer()}"
    
    def process_query(self, query: str, answer: str, conclusion: str) -> Dict[str, Any]:
        """
        Processa uma consulta completa, revisando a resposta final.
        
        Args:
            query: Consulta do usuário
            answer: Resposta gerada pelo AnswerAgent
            conclusion: Conclusão sobre a veracidade
            
        Returns:
            Resultado completo da revisão de segurança
        """
        try:
            # Revisar resposta
            review_result = self.review_response(query, answer, conclusion)
            
            # Adicionar medidas de segurança
            safe_answer = self.add_safety_measures(answer)
            
            # Preparar resultado final
            result = {
                **review_result,
                "final_answer": safe_answer,
                "is_safe": review_result["decision"] in ["APPROVE", "MODIFY"],
                "requires_modification": review_result["decision"] == "MODIFY"
            }
            
            logger.info(f"Safety processou consulta: {result['is_safe']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento da consulta: {str(e)}")
            return {
                "decision": "APPROVE",
                "reason": f"Erro no processamento: {str(e)}",
                "suggestions": [],
                "disclaimer": self._get_standard_disclaimer(),
                "final_answer": answer + f"\n\n{self._get_standard_disclaimer()}",
                "is_safe": True,
                "requires_modification": False,
                "query": query,
                "original_answer": answer,
                "original_conclusion": conclusion,
                "agent": "SAFETY"
            }
