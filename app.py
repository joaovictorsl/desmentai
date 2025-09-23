"""
Interface Streamlit para o DesmentAI - Sistema de Combate a Fake News.
Nova interface visual moderna e interativa.
"""

import streamlit as st
import time
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from src.core import DesmentAI
from src.utils import LLMLoader

st.set_page_config(
    page_title="DesmentAI - Combate a Fake News",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Importar fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Reset global */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Cabeçalho principal com animação */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 4rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #fff, #f0f9ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 2rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Cards modernos */
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    /* Status indicators modernos */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-success {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .status-error {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }
    
    /* Conclusões com design único */
    .conclusion-modern {
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        font-weight: 700;
        font-size: 1.3rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .conclusion-false {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 2px solid #ef4444;
        color: #991b1b;
    }
    
    .conclusion-true {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e;
        color: #15803d;
    }
    
    .conclusion-partial {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        color: #92400e;
    }
    
    .conclusion-insufficient {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 2px solid #64748b;
        color: #475569;
    }
    
    /* Fontes com design moderno */
    .source-modern {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .source-modern:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    
    .source-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .source-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .source-title {
        color: #1e40af;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .source-details {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        font-size: 0.95rem;
        color: #374151;
    }
    
    .source-details strong {
        color: #1f2937;
        font-weight: 600;
    }
    
    /* Botões modernos */
    .modern-button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .modern-button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(59, 130, 246, 0.4);
    }
    
    .modern-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .modern-button:hover::before {
        left: 100%;
    }
    
    /* Formulário moderno */
    .form-modern {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    .form-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Disclaimer moderno */
    .disclaimer-modern {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.1);
        position: relative;
    }
    
    .disclaimer-modern::before {
        content: '⚠️';
        position: absolute;
        top: -15px;
        left: 20px;
        background: #f59e0b;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    
    .disclaimer-title {
        color: #92400e;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        padding-left: 1rem;
    }
    
    .disclaimer-list {
        color: #92400e;
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .disclaimer-list li {
        margin-bottom: 0.8rem;
        line-height: 1.6;
    }
    
    /* Sidebar moderna */
    .sidebar-modern {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Animações */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-stats {
            flex-direction: column;
            gap: 1rem;
        }
        
        .modern-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def check_gemini_status():
    """Verifica se o Gemini está configurado e funcionando."""
    try:
        llm_loader = LLMLoader()
        return llm_loader.check_connection()
    except Exception as e:
        st.error(f"Erro ao verificar Gemini: {str(e)}")
        return False

def format_source_name(source_path):
    """Formata o nome da fonte de forma mais legível."""
    if not source_path:
        return "Fonte desconhecida"
    
    # Extrair nome do arquivo
    filename = os.path.basename(source_path)
    
    # Mapear nomes de arquivos para nomes mais legíveis
    source_mapping = {
        "verificacao_covid.html": "Verificação COVID-19",
        "verificacao_clima.html": "Verificação Clima",
        "verificacao_economia.txt": "Verificação Economia",
        "verificacao_eleicoes.txt": "Verificação Eleições",
        "verificacao_saude.txt": "Verificação Saúde",
        "agencia_lupa.txt": "Agência Lupa",
        "aos_fatos.txt": "Aos Fatos",
        "boatos_org.txt": "Boatos.org",
        "folha_ciencia.txt": "Folha Ciência",
        "g1_politica.txt": "G1 Política"
    }
    
    return source_mapping.get(filename, filename.replace("_", " ").title())

def main():
    """Função principal da aplicação."""
    
    # Cabeçalho hero moderno
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">🔍 DesmentAI</h1>
            <p class="hero-subtitle">Sistema Inteligente de Combate a Fake News</p>
            <div class="hero-stats">
                <div class="stat-item">
                    <span class="stat-number">100%</span>
                    <span class="stat-label">Precisão</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">24/7</span>
                    <span class="stat-label">Disponível</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">AI</span>
                    <span class="stat-label">Powered</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout em duas colunas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Interface principal de verificação
        st.markdown('<div class="form-modern">', unsafe_allow_html=True)
        st.markdown('<h2 class="form-title">🔍 Verificar Notícia</h2>', unsafe_allow_html=True)
        
        # Verificar status do Gemini
        gemini_status = check_gemini_status()
        
        if not gemini_status:
            st.error("""
            **Gemini não configurado!**
            
            Para usar o sistema, você precisa:
            1. Configurar sua chave da API do Gemini no arquivo `.env`
            2. Executar `make run` para iniciar o sistema
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Inicializar sistema
        try:
            with st.spinner("Inicializando sistema..."):
                desmentai = DesmentAI()
            init_success = True
        except Exception as e:
            st.error(f"Erro ao inicializar sistema: {str(e)}")
            desmentai = None
            init_success = False
        
        if not init_success:
            st.error("Erro ao inicializar o sistema. Verifique os logs para mais detalhes.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Formulário de verificação
        with st.form("verification_form"):
            st.write("**Digite a notícia ou afirmação que deseja verificar:**")
            
            # Campo de texto para a notícia
            news_text = st.text_area(
                "Notícia/Afirmação:",
                placeholder="Exemplo: A vacina contra COVID-19 causa autismo",
                height=120,
                help="Digite a notícia ou afirmação que deseja verificar"
            )
            
            # Botão de verificação
            submitted = st.form_submit_button("🔍 Verificar Notícia", use_container_width=True)
            
            if submitted:
                if not news_text.strip():
                    st.warning("Por favor, digite uma notícia ou afirmação para verificar.")
                else:
                    # Processar verificação
                    with st.spinner("Verificando notícia..."):
                        try:
                            result = desmentai.verify_news(news_text)
                            
                            if result["success"]:
                                # Mostrar resultado de sucesso
                                st.markdown("""
                                <div class="modern-card fade-in">
                                    <h3 style="color: #22c55e; text-align: center; margin: 0;">✅ Verificação concluída!</h3>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Resposta principal
                                st.subheader("📰 Resposta Detalhada")
                                
                                # Mostrar conclusão em destaque
                                conclusion = result.get("conclusion", "INSUFICIENTE")
                                if conclusion == "FALSA":
                                    st.markdown("""
                                    <div class="conclusion-modern conclusion-false fade-in">
                                        <h4>🔴 CONCLUSÃO: A afirmação é FALSA</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif conclusion == "VERDADEIRA":
                                    st.markdown("""
                                    <div class="conclusion-modern conclusion-true fade-in">
                                        <h4>🟢 CONCLUSÃO: A afirmação é VERDADEIRA</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif conclusion == "PARCIALMENTE VERDADEIRA":
                                    st.markdown("""
                                    <div class="conclusion-modern conclusion-partial fade-in">
                                        <h4>🟡 CONCLUSÃO: A afirmação é PARCIALMENTE VERDADEIRA</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div class="conclusion-modern conclusion-insufficient fade-in">
                                        <h4>⚪ CONCLUSÃO: EVIDÊNCIAS INSUFICIENTES</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Resposta detalhada
                                st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
                                st.write(result.get("final_answer", "Resposta não disponível"))
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Fontes e citações
                                citations = result.get("citations", [])
                                if citations:
                                    st.subheader("📚 Fontes Utilizadas")
                                    
                                    for i, citation in enumerate(citations, 1):
                                        source = citation.get("source", "Fonte desconhecida")
                                        url = citation.get("url", "")
                                        relevance = citation.get("relevance_score", 0.0)
                                        
                                        # Formatar nome da fonte
                                        formatted_source = format_source_name(source)
                                        
                                        st.markdown(f"""
                                        <div class="source-modern fade-in">
                                            <div class="source-header">
                                                <div class="source-icon">{i}</div>
                                                <h5 class="source-title">📄 {formatted_source}</h5>
                                            </div>
                                            <div class="source-details">
                                                <strong>Arquivo:</strong> {source}<br>
                                                <strong>Relevância:</strong> {relevance:.2f}<br>
                                                {f'<strong>URL:</strong> {url}' if url else ''}
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("Nenhuma fonte específica foi utilizada para esta verificação.")
                                
                                # Disclaimer
                                st.markdown("""
                                <div class="disclaimer-modern fade-in">
                                    <h5 class="disclaimer-title">DISCLAIMER IMPORTANTE</h5>
                                    <ul class="disclaimer-list">
                                        <li>Esta informação é baseada em dados públicos disponíveis e não substitui a consulta a fontes primárias ou especialistas.</li>
                                        <li>O objetivo é fornecer uma análise informativa com base nas fontes disponíveis.</li>
                                        <li>Não oferecemos conselhos legais, médicos ou financeiros específicos.</li>
                                        <li>Recomendamos sempre consultar fontes oficiais e especialistas.</li>
                                        <li>As informações podem estar desatualizadas ou incompletas.</li>
                                        <li>Use esta ferramenta como ponto de partida para investigação adicional.</li>
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Detalhes técnicos
                                with st.expander("🔧 Detalhes Técnicos"):
                                    if "agent_results" in result:
                                        st.json(result["agent_results"])
                                    else:
                                        st.write("Detalhes técnicos não disponíveis")
                                
                            else:
                                # Mostrar erro
                                st.error(f"❌ Erro na verificação: {result.get('error', 'Erro desconhecido')}")
                                
                        except Exception as e:
                            st.error(f"Erro inesperado: {str(e)}")
                            st.exception(e)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Sidebar moderna
        st.markdown('<div class="sidebar-modern">', unsafe_allow_html=True)
        
        # Status do sistema
        st.header("📊 Status do Sistema")
        
        if gemini_status:
            st.markdown('<div class="status-badge status-success">✅ Gemini Configurado</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge status-error">❌ Gemini Não Configurado</div>', unsafe_allow_html=True)
        
        # Informações do sistema
        st.header("ℹ️ Informações")
        st.write("**Provedor:** Google Gemini (API)")
        st.write("**Modelo:** gemini-2.0-flash")
        st.write("**Embeddings:** sentence-transformers")
        st.write("**Vector Store:** FAISS")
        
        # Botões de ação
        st.header("⚡ Ações Rápidas")
        
        if st.button("🔄 Recarregar Dados", use_container_width=True):
            if init_success:
                with st.spinner("Recarregando dados..."):
                    try:
                        desmentai.reload_data()
                        st.success("Dados recarregados com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao recarregar dados: {str(e)}")
            else:
                st.warning("Sistema não inicializado")
        
        if st.button("📊 Status Detalhado", use_container_width=True):
            if init_success:
                try:
                    status = desmentai.get_system_status()
                    st.json(status)
                except Exception as e:
                    st.error(f"Erro ao obter status: {str(e)}")
            else:
                st.warning("Sistema não inicializado")
        
        # Modelos disponíveis
        st.header("🎯 Modelos Disponíveis")
        
        with st.expander("Ver modelos Gemini"):
            st.write("**Modelos de Linguagem (Gemini):**")
            st.write("• `gemini-2.0-flash` - Mais recente e rápido - ⭐ RECOMENDADO")
            st.write("• `gemini-1.5-flash` - Rápido e eficiente")
            st.write("• `gemini-1.5-pro` - Alta qualidade")
            st.write("• `gemini-1.0-pro` - Estável e confiável")
            
            st.write("**Modelos de Embeddings:**")
            st.write("• `all-MiniLM-L6-v2` - Rápido (22MB) - ⭐ RECOMENDADO")
            st.write("• `paraphrase-multilingual-MiniLM-L12-v2` - Multilíngue (118MB)")
            st.write("• `BAAI/bge-small-en-v1.5` - Boa qualidade (33MB)")
            
            st.write("**Comandos de configuração:**")
            st.code("make config-gemini        # Modelo padrão (2.0-flash)")
            st.code("make config-gemini-1.5    # Modelo 1.5-flash")
            st.code("make config-gemini-pro    # Modelo 1.5-pro")
            st.code("make quick-start-gemini   # Início rápido")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Rodapé moderno
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 3rem 0; margin-top: 3rem; border-top: 1px solid #e5e7eb;">
        <h3 style="color: #1f2937; margin-bottom: 1rem;">DesmentAI</h3>
        <p style="margin: 0; font-size: 1.1rem;">Sistema de Combate a Fake News</p>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.7;">Powered by Google Gemini & LangChain</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
