#!/usr/bin/env python3
"""
Exemplo simples de uso do RAGAS Evaluator v2.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

def exemplo_basico():
    """Exemplo básico de uso do avaliador."""
    try:
        from src.evaluation.ragas_evaluator import RAGASEvaluatorV2
        from src.core import DesmentAI
        
        print("🚀 Exemplo de uso do RAGAS Evaluator v2")
        print("=" * 50)
        
        print("1️⃣ Inicializando avaliador...")
        evaluator = RAGASEvaluatorV2()
        print("   ✅ Avaliador criado")
        
        print("2️⃣ Criando dataset de teste...")
        test_dataset = evaluator.create_test_dataset()
        print(f"   ✅ Dataset criado com {len(test_dataset['question'])} perguntas")
        
        print("3️⃣ Perguntas do dataset:")
        for i, question in enumerate(test_dataset['question'][:3], 1):
            print(f"   {i}. {question}")
        print("   ...")
        
        print("4️⃣ Ground truth (primeiras 3):")
        for i, gt in enumerate(test_dataset['ground_truth'][:3], 1):
            print(f"   {i}. {gt[:80]}...")
        print("   ...")
        
        print("5️⃣ Inicializando DesmentAI...")
        desmentai = DesmentAI()
        
        if desmentai.is_initialized:
            print("   ✅ DesmentAI inicializado com sucesso")
            
            print("6️⃣ Executando avaliação rápida...")
            results = evaluator.evaluate_desmentai(desmentai, test_dataset)
            
            if results.get("success", True):
                summary = results.get("summary", {})
                print("   ✅ Avaliação concluída!")
                print(f"   📊 Pontuação geral: {summary.get('overall_score', 0):.3f}")
                print(f"   📈 Melhor métrica: {summary.get('best_performing_metric', 'N/A')}")
                print(f"   📉 Pior métrica: {summary.get('worst_performing_metric', 'N/A')}")
            else:
                print(f"   ❌ Erro: {results.get('error', 'Erro desconhecido')}")
        else:
            print(f"   ❌ DesmentAI não inicializado: {desmentai.initialization_error}")
            print("   💡 Verifique se GEMINI_API_KEY está configurada no arquivo .env")
        
        print("\n🎉 Exemplo concluído!")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Instale as dependências: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_dataset_personalizado():
    """Exemplo com dataset personalizado."""
    try:
        from src.evaluation.ragas_evaluator import RAGASEvaluatorV2
        from datasets import Dataset
        
        print("🔧 Exemplo com dataset personalizado")
        print("=" * 50)
        
        custom_data = {
            "question": [
                "O Bitcoin é uma moeda digital?",
                "A inteligência artificial pode substituir médicos?"
            ],
            "ground_truth": [
                "VERDADEIRO: O Bitcoin é uma criptomoeda digital descentralizada criada em 2009.",
                "PARCIALMENTE VERDADEIRO: A IA pode auxiliar médicos, mas não substituí-los completamente."
            ],
            "source": [
                "Whitepaper do Bitcoin (2009)",
                "Estudos de medicina e IA (2023)"
            ]
        }
        
        custom_dataset = Dataset.from_dict(custom_data)
        
        evaluator = RAGASEvaluatorV2()
        print(f"✅ Dataset personalizado criado com {len(custom_dataset['question'])} perguntas")
        
        for i, question in enumerate(custom_dataset['question'], 1):
            print(f"   {i}. {question}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("🎯 Escolha um exemplo:")
    print("1. Exemplo básico")
    print("2. Dataset personalizado")
    
    escolha = input("Digite sua escolha (1 ou 2): ").strip()
    
    if escolha == "1":
        exemplo_basico()
    elif escolha == "2":
        exemplo_dataset_personalizado()
    else:
        print("❌ Escolha inválida")