#!/usr/bin/env python3
"""
Script para avaliar o DesmentAI usando RAGAS.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.core import DesmentAI
from src.evaluation import RAGASEvaluator
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Função principal."""
    print("🔍 DesmentAI - Avaliação com RAGAS")
    print("=" * 40)
    
    try:
        # 1. Inicializar DesmentAI
        print("Inicializando DesmentAI...")
        desmentai = DesmentAI()
        success = desmentai.initialize()
        
        if not success:
            print("❌ Falha na inicialização do DesmentAI")
            sys.exit(1)
        
        print("✅ DesmentAI inicializado com sucesso!")
        
        # 2. Inicializar avaliador
        print("Inicializando avaliador RAGAS...")
        evaluator = RAGASEvaluator()
        
        # 3. Executar avaliação
        print("Executando avaliação...")
        print("Isso pode levar alguns minutos...")
        
        # Escolher tipo de avaliação
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "full":
            evaluation_type = "full"
        else:
            evaluation_type = "quick"
        
        print(f"Executando avaliação: {evaluation_type}")
        
        if evaluation_type == "quick":
            results = evaluator.run_quick_evaluation(desmentai)
        else:
            results = evaluator.evaluate_desmentai(desmentai)
        
        # 4. Mostrar resultados
        if results.get("success", True):
            print("\n✅ Avaliação concluída com sucesso!")
            
            summary = results.get("summary", {})
            print(f"\n📊 Resultados:")
            print(f"  - Total de perguntas: {summary.get('total_questions', 0)}")
            print(f"  - Pontuação geral: {summary.get('overall_score', 0):.3f}")
            print(f"  - Questões problemáticas: {summary.get('problematic_questions', 0)}")
            
            print(f"\n📈 Métricas:")
            avg_scores = summary.get('average_scores', {})
            for metric, score in avg_scores.items():
                print(f"  - {metric}: {score:.3f}")
            
            print(f"\n📁 Resultados salvos em: eval/results/")
            
        else:
            print(f"\n❌ Erro na avaliação: {results.get('error', 'Erro desconhecido')}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Avaliação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
