"""
Interface Streamlit para o DesmentAI - Sistema de Combate a Fake News.
"""

import streamlit as st
import time
import os
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core import DesmentAI
from src.utils import LLMLoader

# Configuração da página
st.set_page_config(
    page_title="DesmentAI - Combate a Fake News",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .citation-box {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .conclusion-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .conclusion-true {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .conclusion-false {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
    .conclusion-partial {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeaa7;
    }
    .conclusion-insufficient {
        background-color: #e2e3e5;
        color: #383d41;
        border: 2px solid #d6d8db;
    }
</style>
""", unsafe_allow_html=True)

# Função para inicializar o sistema
@st.cache_resource
def initialize_desmentai():
    """Inicializa o DesmentAI com cache."""
    try:
        desmentai = DesmentAI()
        success = desmentai.initialize()
        return desmentai, success
    except Exception as e:
        st.error(f"Erro na inicialização: {str(e)}")
        return None, False

# Função para verificar status do Ollama
def check_ollama_status():
    """Verifica se o Ollama está rodando."""
    try:
        llm_loader = LLMLoader()
        return llm_loader.check_ollama_connection()
    except:
        return False

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🔍 DesmentAI</h1>
    <h3>Sistema Inteligente de Combate a Fake News</h3>
    <p>Verifique notícias e informações usando IA e fontes confiáveis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Status do sistema
    st.subheader("Status do Sistema")
    
    # Verificar Ollama
    ollama_status = check_ollama_status()
    if ollama_status:
        st.markdown('<p class="status-success">✅ Ollama Conectado</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-error">❌ Ollama Desconectado</p>', unsafe_allow_html=True)
        st.warning("Para usar o DesmentAI, você precisa ter o Ollama rodando. Execute: `ollama serve`")
    
    # Inicializar sistema
    if ollama_status:
        with st.spinner("Inicializando DesmentAI..."):
            desmentai, init_success = initialize_desmentai()
        
        if init_success:
            st.markdown('<p class="status-success">✅ DesmentAI Inicializado</p>', unsafe_allow_html=True)
            
            # Mostrar informações do sistema
            status = desmentai.get_system_status()
            st.subheader("Informações do Sistema")
            st.write(f"**Modelo LLM:** {status['model_name']}")
            st.write(f"**Modelo Embeddings:** {status['embedding_model']}")
            
            if 'vector_store' in status:
                vector_info = status['vector_store']
                if vector_info.get('status') == 'initialized':
                    st.write(f"**Documentos Indexados:** {vector_info.get('num_documents', 'N/A')}")
                else:
                    st.write("**Vector Store:** Não inicializado")
        else:
            st.markdown('<p class="status-error">❌ Falha na Inicialização</p>', unsafe_allow_html=True)
    else:
        desmentai = None
        init_success = False
    
    # Botões de ação
    st.subheader("Ações")
    if st.button("🔄 Recarregar Dados"):
        if desmentai:
            with st.spinner("Recarregando dados..."):
                success = desmentai.reload_data()
            if success:
                st.success("Dados recarregados com sucesso!")
            else:
                st.error("Erro ao recarregar dados")
        else:
            st.error("Sistema não inicializado")
    
    if st.button("ℹ️ Informações"):
        st.info("""
        **DesmentAI** é um sistema de verificação de notícias que utiliza:
        - **RAG (Retrieval-Augmented Generation)**
        - **Agentes LangGraph**
        - **Modelos de linguagem locais (Ollama)**
        - **Bases de dados confiáveis**
        
        Para verificar uma notícia, digite-a na caixa de texto e clique em "Verificar".
        """)

# Conteúdo principal
if not ollama_status:
    st.error("""
    ## ❌ Ollama não está rodando
    
    Para usar o DesmentAI, você precisa ter o Ollama instalado e rodando.
    
    **Instalação:**
    1. Instale o Ollama: https://ollama.ai/
    2. Execute: `ollama serve`
    3. Baixe um modelo: `ollama pull llama3.1:8b`
    4. Recarregue esta página
    """)
    
elif not init_success:
    st.error("""
    ## ❌ Erro na Inicialização
    
    O DesmentAI não pôde ser inicializado. Verifique:
    1. Se o Ollama está rodando
    2. Se há dados na pasta `data/raw/`
    3. Se as dependências estão instaladas
    """)
    
else:
    # Interface principal
    st.header("🔍 Verificação de Notícias")
    
    # Caixa de entrada
    query = st.text_area(
        "Digite a notícia ou afirmação que deseja verificar:",
        placeholder="Exemplo: 'O governo brasileiro aprovou uma nova lei que proíbe o uso de redes sociais'",
        height=100
    )
    
    # Botão de verificação
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        verify_button = st.button("🔍 Verificar Notícia", type="primary", use_container_width=True)
    
    # Processar verificação
    if verify_button and query.strip():
        with st.spinner("Verificando notícia... Isso pode levar alguns segundos."):
            result = desmentai.verify_news(query)
        
        if result['success']:
            # Mostrar resultado
            st.success("✅ Verificação concluída!")
            
            # Conclusão
            conclusion = result.get('conclusion', 'INSUFICIENTE')
            conclusion_class = f"conclusion-{conclusion.lower()}"
            
            conclusion_text = {
                'VERDADEIRA': '✅ VERDADEIRA',
                'FALSA': '❌ FALSA',
                'PARCIALMENTE VERDADEIRA': '⚠️ PARCIALMENTE VERDADEIRA',
                'INSUFICIENTE': '❓ INFORMAÇÕES INSUFICIENTES',
                'ERRO': '❌ ERRO NO PROCESSAMENTO'
            }.get(conclusion, f'❓ {conclusion}')
            
            st.markdown(f"""
            <div class="conclusion-box {conclusion_class}">
                {conclusion_text}
            </div>
            """, unsafe_allow_html=True)
            
            # Resposta detalhada
            st.subheader("📋 Resposta Detalhada")
            st.write(result.get('final_answer', ''))
            
            # Citações
            citations = result.get('citations', [])
            if citations:
                st.subheader("📚 Fontes e Citações")
                for i, citation in enumerate(citations, 1):
                    with st.expander(f"Fonte {i}: {citation.get('source', 'Fonte desconhecida')}"):
                        st.write(f"**URL:** {citation.get('url', 'N/A')}")
                        st.write(f"**Relevância:** {citation.get('relevance_score', 0.0):.2f}")
            
            # Detalhes dos agentes (expansível)
            with st.expander("🔧 Detalhes Técnicos"):
                agent_results = result.get('agent_results', {})
                
                for agent_name, agent_result in agent_results.items():
                    st.write(f"**{agent_name.upper()}:**")
                    if isinstance(agent_result, dict):
                        for key, value in agent_result.items():
                            if key not in ['documents', 'citations']:  # Evitar mostrar dados muito grandes
                                st.write(f"  - {key}: {value}")
                    else:
                        st.write(f"  - {agent_result}")
        
        else:
            st.error(f"❌ Erro na verificação: {result.get('error', 'Erro desconhecido')}")
    
    elif verify_button and not query.strip():
        st.warning("⚠️ Por favor, digite uma notícia ou afirmação para verificar.")
    
    # Exemplos
    st.subheader("💡 Exemplos de Verificação")
    
    examples = [
        "O Brasil é o maior produtor de café do mundo",
        "A vacina contra COVID-19 causa autismo",
        "O governo brasileiro aprovou uma nova lei de proteção de dados",
        "A Terra é plana",
        "O aquecimento global é uma farsa"
    ]
    
    for example in examples:
        if st.button(f"Verificar: {example}", key=f"example_{example}"):
            st.session_state.example_query = example
            st.rerun()
    
    # Processar exemplo selecionado
    if 'example_query' in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
        
        with st.spinner("Verificando exemplo..."):
            result = desmentai.verify_news(query)
        
        if result['success']:
            st.success("✅ Verificação concluída!")
            
            # Mostrar resultado do exemplo
            conclusion = result.get('conclusion', 'INSUFICIENTE')
            conclusion_class = f"conclusion-{conclusion.lower()}"
            
            conclusion_text = {
                'VERDADEIRA': '✅ VERDADEIRA',
                'FALSA': '❌ FALSA',
                'PARCIALMENTE VERDADEIRA': '⚠️ PARCIALMENTE VERDADEIRA',
                'INSUFICIENTE': '❓ INFORMAÇÕES INSUFICIENTES',
                'ERRO': '❌ ERRO NO PROCESSAMENTO'
            }.get(conclusion, f'❓ {conclusion}')
            
            st.markdown(f"""
            <div class="conclusion-box {conclusion_class}">
                {conclusion_text}
            </div>
            """, unsafe_allow_html=True)
            
            st.write(result.get('final_answer', ''))

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🔍 <strong>DesmentAI</strong> - Sistema de Combate a Fake News</p>
    <p>Desenvolvido com LangChain, LangGraph e Streamlit</p>
    <p>⚠️ Este sistema é para fins educacionais e informativos</p>
</div>
""", unsafe_allow_html=True)
