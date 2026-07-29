import streamlit as st
import pandas as pd
import os
import json
import base64
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Desenho Técnico Mecânico — SENAI SP",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para visual premium escuro SENAI
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stApp {
        background-color: #0f172a;
    }
    .css-1d3b047, [data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .callout-info {
        background-color: rgba(14, 165, 233, 0.12);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 8px;
        color: #e0f2fe;
        margin: 16px 0;
    }
    .callout-warning {
        background-color: rgba(245, 158, 11, 0.12);
        border-left: 4px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 8px;
        color: #fef3c7;
        margin: 16px 0;
    }
    .callout-success {
        background-color: rgba(34, 197, 94, 0.12);
        border-left: 4px solid #22c55e;
        padding: 14px 18px;
        border-radius: 8px;
        color: #dcfce7;
        margin: 16px 0;
    }
    .badge-card {
        background: #1e293b;
        border: 2px solid #fbbf24;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .module-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        min-height: 230px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .module-card-unlocked {
        border-top: 4px solid #38bdf8;
    }
    .module-card-locked {
        border-top: 4px solid #f59e0b;
        background-color: rgba(245, 158, 11, 0.05);
    }
    .status-badge-unlocked {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-locked {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fde047;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INICIALIZAÇÃO DO ESTADO DA SESSÃO (PERSISTÊNCIA E TRAVAS)
# ============================================================

# Arquivo CSV para salvar os resultados dos alunos (Painel do Instrutor)
DB_FILE = "registro_alunos_senai.csv"

def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Data_Hora", "Aluno_Nome", "Aluno_Matricula", "Modulo", "Nota", "Acertos", "Situacao"])
        df.to_csv(DB_FILE, index=False)

init_db()

def save_result(nome, matricula, modulo, nota, acertos, situacao):
    try:
        df = pd.read_csv(DB_FILE)
        new_row = {
            "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Aluno_Nome": nome,
            "Aluno_Matricula": matricula,
            "Modulo": modulo,
            "Nota": nota,
            "Acertos": f"{acertos}/5",
            "Situacao": situacao
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=False)
        df.to_csv(DB_FILE, index=False)
    except Exception as e:
        st.error(f"Erro ao salvar registro: {e}")

# Chaves secretas de desbloqueio configuráveis pelo professor (não-adivinháveis)
if "passcodes" not in st.session_state:
    st.session_state.passcodes = {
        "mod2": "PROJ-ORT-9482",
        "mod3": "CORTE-MONT-5317",
        "mod4": "TOLER-ISO-8204"
    }

# Estado de liberação dos módulos (True = Liberado, False = Bloqueado)
if "unlocked_modules" not in st.session_state:
    st.session_state.unlocked_modules = {
        "mod1": True,   # Módulo 1 é liberado por padrão
        "mod2": False,  # Módulo 2 bloqueado por padrão
        "mod3": False,  # Módulo 3 bloqueado por padrão
        "mod4": False   # Módulo 4 bloqueado por padrão
    }

if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""
if "student_points" not in st.session_state:
    st.session_state.student_points = 0

# Função para carregar SVG e exibir inline no Streamlit
def load_svg(filename):
    filepath = os.path.join("assets", filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            svg_content = f.read()
        r# ============================================================
# BARRA LATERAL — IDENTIFICAÇÃO DO ALUNO E NAVEGAÇÃO
# ============================================================
banner_path = os.path.join("assets", "banner_curso.jpg")
if os.path.exists(banner_path):
    st.sidebar.image(banner_path, use_container_width=True)
else:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/8/8c/SENAI_L%C3%B3gotipo.svg", width=180)

st.sidebar.title("Leitura e Interpretação de Desenho Técnico Mecânico")

st.sidebar.markdown("---")
st.sidebar.subheader("👤 Identificação do Aluno")
st.session_state.student_name = st.sidebar.text_input("Seu Nome Completo:", value=st.session_state.student_name, placeholder="Ex.: João Silva")
st.session_state.student_id = st.sidebar.text_input("Nº de Matrícula SENAI:", value=st.session_state.student_id, placeholder="Ex.: 2026-9812")

if st.session_state.student_name:
    st.sidebar.success(f"Bem-vindo, **{st.session_state.student_name}**!")
    st.sidebar.markdown(f"🏆 **Pontuação Total:** `{st.session_state.student_points} Pts`")

st.sidebar.markdown("---")

# Opções do Menu
menu_options = [
    "📚 Início & Apresentação",
    "📘 Módulo 1: Fundamentos",
    "📐 Módulo 2: Croquis e Projeção",
    "🔧 Módulo 3: Desenho de Montagem",
    "📏 Módulo 4: Tolerâncias e Acabamento",
    "🔑 Painel do Docente (Área Restrita)"
]

selected_page = st.sidebar.radio("Navegação do Curso:", menu_options)

st.sidebar.markdown("---")
st.sidebar.caption("SENAI SP — Metodologia MSEP | LGPD Privacy by Design")

# ============================================================
# 1. PÁGINA INICIAL & APRESENTAÇÃO
# ============================================================
if selected_page == "📚 Início & Apresentação":
    st.title("🎓 Leitura e Interpretação de Desenho Técnico Mecânico")
    st.subheader("SENAI SP — Formação Profissional")

    st.markdown("""
    <div class="callout-info">
        <strong>Bem-vindo ao material digital interativo do SENAI SP!</strong><br>
        Este aplicativo substitui o caderno e lápis por uma experiência responsiva e interativa de aprendizado individual em computador.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    
    modules_info = [
        {
            "title": "📘 Módulo 1",
            "subtitle": "Fundamentos",
            "desc": "Normas ABNT, Diedros, Folhas ISO, Linhas e Sólidos.",
            "unlocked": st.session_state.unlocked_modules["mod1"]
        },
        {
            "title": "📐 Módulo 2",
            "subtitle": "Croquis e Projeção",
            "desc": "Perspectivas, Vistas Ortogonais e Regras de Cotagem.",
            "unlocked": st.session_state.unlocked_modules["mod2"]
        },
        {
            "title": "🔧 Módulo 3",
            "subtitle": "Montagem & Cortes",
            "desc": "Tipos de Corte, Hachuras, Seções e Balões de Peças.",
            "unlocked": st.session_state.unlocked_modules["mod3"]
        },
        {
            "title": "📏 Módulo 4",
            "subtitle": "Tolerâncias",
            "desc": "Tolerâncias Dimensionais, Geométricas e Rugosidade.",
            "unlocked": st.session_state.unlocked_modules["mod4"]
        }
    ]

    cols = [col1, col2, col3, col4]
    for col, m in zip(cols, modules_info):
        card_class = "module-card-unlocked" if m["unlocked"] else "module-card-locked"
        status_html = '<span class="status-badge-unlocked">✅ Liberado</span>' if m["unlocked"] else '<span class="status-badge-locked">🔒 Bloqueado</span>'
        
        with col:
            st.markdown(f"""
            <div class="module-card {card_class}">
                <div>
                    <h4 style="margin:0 0 4px 0; color:#f8fafc; font-size:1.05rem;">{m['title']}</h4>
                    <div style="font-weight:600; color:#38bdf8; font-size:0.85rem; margin-bottom:8px;">{m['subtitle']}</div>
                    <p style="font-size:0.82rem; color:#94a3b8; margin:0; line-height:1.4;">{m['desc']}</p>
                </div>
                <div style="margin-top:14px;">
                    {status_html}
                </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🎯 Objetivos de Aprendizagem (MSEP SENAI)")
    st.markdown("""
    - Interpretar desenhos técnicos mecânicos conforme as **normas ABNT NBR** (NBR 8403, 10067, 10126, 1101).
    - Identificar projeções no **Primeiro Diedro** (Padrão ABNT / Brasil).
    - Ler e aplicar cotagem, cortes, seções, tolerâncias dimensionais/geométricas e rugosidade superficial.
    """)

# ============================================================
# 2. MÓDULO 1: FUNDAMENTOS
# ============================================================
elif selected_page == "📘 Módulo 1: Fundamentos":
    st.title("📘 Módulo 1: Fundamentos do Desenho Técnico Mecânico")

    tab1, tab2, tab3, tab4, tab_ex, tab_av = st.tabs([
        "SA1: Definição e Normas",
        "SA2: Diedros e Folhas",
        "SA3: Linhas e Escalas",
        "SA4: Sólidos Geométricos",
        "📝 Exercícios",
        "📝 Avaliação Somativa"
    ])

    with tab1:
        st.header("1.1 Definição e Normas Técnicas (ABNT)")
        st.write("O desenho técnico é a linguagem universal da engenharia e da manutenção mecânica.")
        
        st.markdown("""
        <div class="callout-info">
            <strong>Normas ABNT Principais:</strong>
            <ul>
                <li><strong>NBR 8403:</strong> Aplicação de linhas em desenhos.</li>
                <li><strong>NBR 10067:</strong> Princípios gerais de representação em desenho técnico.</li>
                <li><strong>NBR 10126:</strong> Cotagem em desenho técnico.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("1.2 Primeiro Diedro (Símbolo ABNT)")
        svg_diedros = load_svg("fig-diedros.svg")
        if svg_diedros:
            st.components.v1.html(svg_diedros, height=260)

    with tab2:
        st.header("1.3 Formatos de Folhas e Legenda (NBR 10068)")
        df_folhas = pd.DataFrame({
            "Formato ISO": ["A0", "A1", "A2", "A3", "A4"],
            "Dimensões (mm)": ["841 × 1189", "594 × 841", "420 × 594", "297 × 420", "210 × 297"],
            "Aplicação Recomendada": ["Desenhos de grandes conjuntos", "Conjuntos mecânicos", "Subconjuntos", "Detalhes de montagem", "Desenhos de peças individuais"]
        })
        st.table(df_folhas)

    with tab3:
        st.header("1.4 Tipos de Linhas em Desenho Técnico (NBR 8403)")
        svg_linhas = load_svg("fig-linhas.svg")
        if svg_linhas:
            st.components.v1.html(svg_linhas, height=280)

    with tab4:
        st.header("1.5 Sólidos Geométricos Básicos")
        st.write("Cubo, Prisma, Cilindro, Cone, Pirâmide e Esfera formam os elementos básicos das peças usinadas.")

    with tab_ex:
        st.header("Exercícios de Fixação — Módulo 1")
        
        q1 = st.radio("1. Qual é o padrão de projeção ortogonal utilizado obrigatoriamente no Brasil pela ABNT?", 
                      ["Terceiro Diedro", "Primeiro Diedro", "Segundo Diedro", "Quarto Diedro"], key="m1_q1")
        if st.button("Verificar Questão 1"):
            if q1 == "Primeiro Diedro":
                st.success("✅ Correto! No Brasil adota-se o 1º Diedro.")
                st.session_state.student_points += 100
            else:
                st.error("❌ Incorreto. A resposta correta é Primeiro Diedro.")

    with tab_av:
        st.header("Avaliação Somativa — Módulo 1")
        if not st.session_state.student_name or not st.session_state.student_id:
            st.warning("⚠️ Por favor, informe seu **Nome** e **Matrícula** na barra lateral antes de realizar a avaliação.")
        else:
            with st.form("form_av_mod1"):
                av1 = st.radio("1. Qual norma regulamenta o tipo de linha em desenhos técnicos no Brasil?", ["NBR 10067", "NBR 8403", "NBR 10126", "NR 12"])
                av2 = st.radio("2. A escala 2:1 representa:", ["Escala de Redução", "Escala Natural", "Escala de Ampliação", "Escala de Detalhe"])
                av3 = st.radio("3. Qual o formato de folha ISO com dimensões 210 × 297 mm?", ["A3", "A4", "A2", "A1"])
                av4 = st.radio("4. No 1º Diedro, onde é desenhada a Vista Superior?", ["Acima da Vista Frontal", "Abaixo da Vista Frontal", "À direita da Vista Frontal", "Atrás da Vista Frontal"])
                av5 = st.radio("5. A linha de traço e ponto estreita é utilizada para:", ["Contornos visíveis", "Linhas de centro e eixos de simetria", "Hachuras", "Arestas ocultas"])
                
                submitted = st.form_submit_button("Finalizar e Enviar Avaliação Módulo 1")
                if submitted:
                    acertos = 0
                    if av1 == "NBR 8403": acertos += 1
                    if av2 == "Escala de Ampliação": acertos += 1
                    if av3 == "A4": acertos += 1
                    if av4 == "Abaixo da Vista Frontal": acertos += 1
                    if av5 == "Linhas de centro e eixos de simetria": acertos += 1
                    
                    nota = acertos * 2.0
                    situacao = "APROVADO" if nota >= 7.0 else "REPROVADO"
                    
                    save_result(st.session_state.student_name, st.session_state.student_id, "Módulo 1", nota, acertos, situacao)
                    
                    if nota >= 7.0:
                        st.balloons()
                        st.success(f"🎉 **Parabéns, {st.session_state.student_name}!** Você foi APROVADO no Módulo 1 com Nota **{nota:.1f}** ({acertos}/5 acertos).")
                    else:
                        st.error(f"❌ Nota {nota:.1f} (Desempenho abaixo de 7,0). Estude o conteúdo e tente novamente!")

# ============================================================
# 3. MÓDULO 2: CROQUIS E PROJEÇÃO ORTOGONAL (COM TRAVA DE SENHA)
# ============================================================
elif selected_page == "📐 Módulo 2: Croquis e Projeção":
    st.title("📐 Módulo 2: Croquis e Projeção Ortogonal")

    # Verificação de Desbloqueio
    if not st.session_state.unlocked_modules["mod2"]:
        st.warning("🔒 **Este módulo está bloqueado pelo instrutor.**")
        st.markdown("""
        <div class="callout-warning">
            Para acessar este módulo, solicite a <strong>Chave de Acesso da Aula</strong> ao seu professor e digite abaixo.
        </div>
        """, unsafe_allow_html=True)
        
        pass_input = st.text_input("Digite a Chave de Liberação do Módulo 2:", type="password")
        if st.button("Desbloquear Módulo 2"):
            if pass_input == st.session_state.passcodes["mod2"]:
                st.session_state.unlocked_modules["mod2"] = True
                st.success("🔓 **Módulo 2 Desbloqueado com Sucesso!**")
                st.rerun()
            else:
                st.error("❌ Chave de liberação incorreta! Verifique a chave informada pelo professor.")
    else:
        tab1, tab2, tab_ex, tab_av = st.tabs([
            "SA1: Croquis e Perspectivas",
            "SA2: Projeção Ortogonal",
            "📝 Exercícios",
            "📝 Avaliação Somativa"
        ])
        
        with tab1:
            st.header("2.1 Perspectiva Isométrica e Croquis")
            st.write("O croqui é o esboço à mão livre essencial para a comunicação rápida na oficina.")
        
        with tab2:
            st.header("2.2 As 3 Vistas Ortogonais Fundamentais")
            svg_proj = load_svg("fig-projecao-ortogonal.svg")
            if svg_proj:
                st.components.v1.html(svg_proj, height=300)

        with tab_ex:
            st.header("Exercícios — Módulo 2")
            st.info("Responda às questões de projeção ortogonal para praticar.")

        with tab_av:
            st.header("Avaliação Somativa — Módulo 2")
            with st.form("form_av_mod2"):
                av1 = st.radio("1. Qual vista é projetada no Plano Vertical (PV)?", ["Vista Superior", "Vista Frontal", "Vista Lateral Esquerda", "Vista Inferior"])
                av2 = st.radio("2. A representação de arestas não visíveis é feita por qual linha?", ["Contínua grossa", "Traçada estreita", "Traço e ponto", "Ondulada"])
                submitted = st.form_submit_button("Enviar Avaliação Módulo 2")
                if submitted:
                    acertos = 2 if (av1 == "Vista Frontal" and av2 == "Traçada estreita") else 1
                    nota = acertos * 5.0
                    situacao = "APROVADO" if nota >= 7.0 else "REPROVADO"
                    save_result(st.session_state.student_name, st.session_state.student_id, "Módulo 2", nota, acertos, situacao)
                    st.success(f"Avaliação registrada! Sua Nota: {nota:.1f}")

# ============================================================
# 4. MÓDULO 3: DESENHO DE MONTAGEM (COM TRAVA DE SENHA)
# ============================================================
elif selected_page == "🔧 Módulo 3: Desenho de Montagem":
    st.title("🔧 Módulo 3: Desenho de Montagem e Cortes")

    if not st.session_state.unlocked_modules["mod3"]:
        st.warning("🔒 **Este módulo está bloqueado pelo instrutor.**")
        pass_input = st.text_input("Digite a Chave de Liberação do Módulo 3:", type="password")
        if st.button("Desbloquear Módulo 3"):
            if pass_input == st.session_state.passcodes["mod3"]:
                st.session_state.unlocked_modules["mod3"] = True
                st.success("🔓 **Módulo 3 Desbloqueado!**")
                st.rerun()
            else:
                st.error("❌ Chave incorreta!")
    else:
        st.header("3.1 Representação de Cortes e Hachuras (NBR 10067)")
        svg_cortes = load_svg("fig-cortes.svg")
        if svg_cortes:
            st.components.v1.html(svg_cortes, height=260)

# ============================================================
# 5. MÓDULO 4: TOLERÂNCIAS E ACABAMENTO (COM TRAVA DE SENHA)
# ============================================================
elif selected_page == "📏 Módulo 4: Tolerâncias e Acabamento":
    st.title("📏 Módulo 4: Tolerâncias e Acabamento Superficial")

    if not st.session_state.unlocked_modules["mod4"]:
        st.warning("🔒 **Este módulo está bloqueado pelo instrutor.**")
        pass_input = st.text_input("Digite a Chave de Liberação do Módulo 4:", type="password")
        if st.button("Desbloquear Módulo 4"):
            if pass_input == st.session_state.passcodes["mod4"]:
                st.session_state.unlocked_modules["mod4"] = True
                st.success("🔓 **Módulo 4 Desbloqueado!**")
                st.rerun()
            else:
                st.error("❌ Chave incorreta!")
    else:
        st.header("4.1 Tolerâncias Geométricas e Rugosidade Ra (N1-N12)")
        svg_tol = load_svg("fig-tolerancias-simbolo.svg")
        if svg_tol:
            st.components.v1.html(svg_tol, height=270)

# ============================================================
# 6. PAINEL DO DOCENTE (ÁREA RESTRITA DO PROFESSOR)
# ============================================================
elif selected_page == "🔑 Painel do Docente (Área Restrita)":
    st.title("🔑 Painel de Controle do Instrutor — SENAI SP")
    
    admin_pass = st.text_input("Digite a Senha Mestre de Docente:", type="password")
    
    if admin_pass == "SENAI-DOCENTE-2026":
        st.success("🔓 **Autenticado como Instrutor Responsável**")
        
        tab_admin1, tab_admin2 = st.tabs(["📊 Relatório de Desempenho dos Alunos", "⚙️ Gerenciamento de Liberação dos Módulos"])
        
        with tab_admin1:
            st.subheader("Alunos que Realizaram as Avaliações:")
            if os.path.exists(DB_FILE):
                df_results = pd.read_csv(DB_FILE)
                if not df_results.empty:
                    st.dataframe(df_results, use_container_width=True)
                    
                    # Botão para baixar CSV
                    csv = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar Relatório Completo dos Alunos (CSV)",
                        data=csv,
                        file_name=f"relatorio_turma_senai_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Nenhuma avaliação realizada até o momento.")

        with tab_admin2:
            st.subheader("Liberação Direta de Módulos para a Turma:")
            st.write("Alterne as chaves abaixo para liberar ou bloquear o acesso dos alunos instantaneamente:")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.session_state.unlocked_modules["mod2"] = st.checkbox("Liberar Módulo 2 (Projeção)", value=st.session_state.unlocked_modules["mod2"])
                st.info(f"Chave Atual: `{st.session_state.passcodes['mod2']}`")
            with col_b:
                st.session_state.unlocked_modules["mod3"] = st.checkbox("Liberar Módulo 3 (Montagem)", value=st.session_state.unlocked_modules["mod3"])
                st.info(f"Chave Atual: `{st.session_state.passcodes['mod3']}`")
            with col_c:
                st.session_state.unlocked_modules["mod4"] = st.checkbox("Liberar Módulo 4 (Tolerâncias)", value=st.session_state.unlocked_modules["mod4"])
                st.info(f"Chave Atual: `{st.session_state.passcodes['mod4']}`")
                
            st.markdown("---")
            st.subheader("Personalizar Chaves de Acesso dos Módulos:")
            st.session_state.passcodes["mod2"] = st.text_input("Nova Chave Módulo 2:", value=st.session_state.passcodes["mod2"])
            st.session_state.passcodes["mod3"] = st.text_input("Nova Chave Módulo 3:", value=st.session_state.passcodes["mod3"])
            st.session_state.passcodes["mod4"] = st.text_input("Nova Chave Módulo 4:", value=st.session_state.passcodes["mod4"])
            st.success("Chaves atualizadas!")

    elif admin_pass:
        st.error("❌ Senha Mestre de Docente Incorreta!")
