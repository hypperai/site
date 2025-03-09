import pandas as pd
import numpy as np
import streamlit as st
import random
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations, product
from scipy.optimize import minimize

# Configuração do Dashboard
st.set_page_config(page_title="Einstein 2.0", layout="wide")

# Custom CSS para fundo branco
st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
    }
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #e0e0e0;
    }
    .sidebar .sidebar-content {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Menu lateral com logo
with st.sidebar:
    # Logo da Hyper (substituir pela URL real)
    st.image("logo write color.png",  # ← URL do logo aqui
             width=210,
             output_format="PNG")
    
    st.title("Menu Einstein 2.0")
    opcao = st.radio("Selecione uma opção:", [
        "Visão Geral", "Combinações de Materiais", "Simulação de Degradação", 
        "Modelagem de Manufatura", "Novos Materiais"
    ])
    st.divider()
    st.write("**Configurações Avançadas**")
    debug_mode = st.checkbox("Modo Debug")

# Conteúdo principal
st.title("Einstein 2.0 - Plataforma Avançada de Simulação de Baterias")
st.write("""
Bem-vindo ao **Einstein 2.0**! Esta plataforma usa **Inteligência Artificial** para simular e otimizar baterias, 
considerando eficiência, custo, sustentabilidade e processos de manufatura.
""")

# Banco de dados de materiais (exemplo inicial)
if 'materiais' not in st.session_state:
    st.session_state.materiais = pd.DataFrame({
        "Material": ["Lítio", "Íon de Lítio", "Grafeno", "Níquel", "Cobalto", "Magnésio"],
        "Eficiencia": [85, 90, 95, 70, 75, 80],  # Eficiência (%)
        "Custo": [100, 120, 200, 80, 90, 70],  # Custo (USD/kg)
        "Sustentabilidade": [3, 4, 5, 2, 3, 4],  # Escala de 1 a 5 (5 = mais sustentável)
        "Densidade Energética": [200, 250, 300, 150, 180, 220]  # Wh/kg
    })

# Função para gerar novos materiais
def gerar_novo_material():
    nome_material = f"Material_{len(st.session_state.materiais) + 1}"
    if nome_material in st.session_state.materiais['Material'].values:
        st.error("Material já existe no banco de dados!")
        return
    
    novo_material_df = pd.DataFrame([{
        "Material": nome_material,
        "Eficiencia": random.randint(70, 100),
        "Custo": random.randint(50, 250),
        "Sustentabilidade": random.randint(1, 5),
        "Densidade Energética": random.randint(150, 350)
    }])

    st.session_state.materiais = pd.concat(
        [st.session_state.materiais, novo_material_df],
        ignore_index=True
    )

# Função para calcular combinações
def calcular_combinacoes_completas(materiais, num_combinacoes):
    resultados = []
    cols = ["Eficiencia", "Custo", "Sustentabilidade", "Densidade Energética"]
    
    for combo in combinations(materiais["Material"], num_combinacoes):
        mascara = materiais["Material"].isin(combo)
        dados = materiais[mascara][cols].values
        
        percentuais = np.arange(1, 100)
        for pesos in product(percentuais, repeat=num_combinacoes):
            if sum(pesos) == 100:
                pesos_normalizados = np.array(pesos) / 100
                media_ponderada = np.sum(dados * pesos_normalizados[:, None], axis=0)
                
                resultados.append({
                    "Combinação": combo,
                    "Percentuais": pesos_normalizados,
                    "Eficiência": round(media_ponderada[0], 2),
                    "Custo": round(media_ponderada[1], 2),
                    "Sustentabilidade": round(media_ponderada[2], 2),
                    "Densidade Energética": round(media_ponderada[3], 2)
                })
    
    return pd.DataFrame(resultados)

# Função de otimização
def otimizar_combinacao(materiais, num_combinacoes):
    def objetivo(pesos):
        mascara = materiais["Material"].isin(combinacao)
        dados = materiais[mascara][["Eficiencia", "Custo", "Sustentabilidade"]].values
        media_ponderada = np.sum(dados * pesos[:, None], axis=0)
        return -media_ponderada[0] + media_ponderada[1] - media_ponderada[2]
    
    combinacao = random.sample(list(materiais["Material"]), num_combinacoes)
    pesos_iniciais = np.ones(num_combinacoes) / num_combinacoes
    resultado = minimize(objetivo, pesos_iniciais, bounds=[(0, 1)] * num_combinacoes)
    
    return combinacao, resultado.x

# Seções do dashboard
if opcao == "Visão Geral":
    col1, col2 = st.columns(2)
    with col1:
        st.write("""
        ### Recursos Principais:
        - Combinações Inteligentes
        - Degradação Preditiva
        - Sustentabilidade (LCA)
        """)
    with col2:
        stats = {
            "Materiais Cadastrados": len(st.session_state.materiais),
            "Combinações Possíveis": 2**len(st.session_state.materiais),
            "Última Atualização": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
        }
        st.json(stats)

elif opcao == "Combinações de Materiais":
    with st.expander("Configurações"):
        num_combinacoes = st.slider("Materiais por Combinação", 2, 6, 2)
        filtro_eficiencia = st.slider("Eficiência Mínima (%)", 0, 100, 70)
        filtro_custo = st.slider("Custo Máximo (USD)", 0, 500, 200)
    
    if st.button("Calcular"):
        with st.spinner("Processando..."):
            resultados = calcular_combinacoes_completas(st.session_state.materiais, num_combinacoes)
            resultados_filtrados = resultados[
                (resultados["Eficiência"] >= filtro_eficiencia) &
                (resultados["Custo"] <= filtro_custo)
            ]
            
            tab1, tab2 = st.tabs(["Resultados", "Gráficos"])
            with tab1:
                st.dataframe(resultados_filtrados.style.background_gradient(cmap="viridis"))
            with tab2:
                fig, ax = plt.subplots()
                sns.scatterplot(data=resultados_filtrados, x="Eficiência", y="Custo", 
                                hue="Sustentabilidade", size="Densidade Energética", ax=ax)
                st.pyplot(fig)

elif opcao == "Simulação de Degradação":
    ciclos = st.slider("Ciclos de Carga", 1, 1000, 100)
    temp = st.slider("Temperatura (°C)", 0, 100, 25)
    if st.button("Simular"):
        degradacao = 100 * np.exp(-0.001 * ciclos) * (1 - 0.01 * (temp - 25))
        st.metric("Eficiência Residual", f"{degradacao:.2f}%")

elif opcao == "Modelagem de Manufatura":
    custo = st.slider("Custo Base (USD/kg)", 50, 500, 100)
    tempo = st.slider("Tempo Produção (h)", 1, 100, 10)
    sustent = st.slider("Sustentabilidade", 1, 5, 3)
    if st.button("Calcular"):
        custo_total = custo * tempo * (6 - sustent)
        st.metric("Custo Total Estimado", f"${custo_total:.2f}")

elif opcao == "Novos Materiais":
    with st.form("Novo Material"):
        qtd = st.number_input("Número de Materiais", 1, 10, 1)
        if st.form_submit_button("Gerar"):
            for _ in range(qtd):
                gerar_novo_material()
            st.success(f"{qtd} novos materiais gerados!")
    
    st.dataframe(st.session_state.materiais.style.format(precision=2))

if debug_mode:
    st.sidebar.write("### Debug Info")
    st.sidebar.write(st.session_state.materiais.describe())