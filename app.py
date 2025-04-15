import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
from pydantic import BaseModel
from datetime import datetime

# =========================== #
# ===== Configurações ======= #
# =========================== #

st.set_page_config(
    page_title="Dados de Vendas - Fornecedora de Roupas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Habilita tema escuro para Altair
alt.themes.enable("dark")

class UserLogin(BaseModel):
    username: str
    password: str

# Função auxiliar para exibir KPIs em verde
def green_text_kpi(label, value):
    return f"""
    <div style="background-color: #90ee90; padding: 10px; border-radius: 5px;">
        <h4 style="margin: 0; font-weight: bold;">{label}</h4>
        <h2 style="margin: 0; font-weight: bold;">{value}</h2>
    </div>
    """

# Função auxiliar para exibir KPIs em vermelho
def red_text_kpi(label, value):
    return f"""
    <div style="background-color: #ff5555; padding: 10px; border-radius: 5px;">
        <h4 style="margin: 0; font-weight: bold;">{label}</h4>
        <h2 style="margin: 0; font-weight: bold;">{value}</h2>
    </div>
    """

# =========================== #
# ===== Tela de Login ======= #
# =========================== #

def login_screen():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if username == "admin" and password == "admin":
            st.success("Logado com sucesso!")
            st.session_state.logged_in = True
        else:
            st.error("Usuário ou senha inválidos")
            st.session_state.logged_in = False

# =========================== #
# ========== Dados ========== #
# =========================== #

def load_financial_data():
    """
    Tenta carregar o arquivo 'base-copeira.csv'.
    Caso não seja encontrado, gera dados dummy.
    """
    try:
        df = pd.read_csv("base-copeira.csv", sep=",")
        st.sidebar.success("Arquivo 'base-copeira.csv' carregado com sucesso!")
    except Exception as e:
        st.sidebar.error("Erro ao carregar 'base-copeira.csv'. Usando dados dummy.")
        num_registros = 100
        data_inicial = datetime(2024, 1, 1)
        df = pd.DataFrame({
            "Data da Compra": pd.date_range(start=data_inicial, periods=num_registros, freq="D"),
            "Loja": np.random.choice(["Loja A", "Loja B", "Loja C"], size=num_registros),
            "UF": np.random.choice(["SP", "RJ", "MG", "RS"], size=num_registros),
            "Categoria": np.random.choice(["Camiseta", "Calça", "Vestido", "Blusa"], size=num_registros),
            "Tamanho": np.random.choice(["P", "M", "G", "GG"], size=num_registros),
            "Cor": np.random.choice(["Vermelho", "Azul", "Verde", "Preto"], size=num_registros),
            "Preço Unitário": np.random.randint(50, 200, size=num_registros),
            "Quantidade": np.random.randint(1, 10, size=num_registros),
            "Estação": np.random.choice(["Verão", "Inverno", "Outono", "Primavera"], size=num_registros),
            "Cidade": np.random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre"], size=num_registros),
            "Tipo de Lead": np.random.choice(["Online", "Loja Física"], size=num_registros)
        })
        df["Valor Total"] = df["Preço Unitário"] * df["Quantidade"]

    if "Data da Compra" in df.columns:
        if not np.issubdtype(df["Data da Compra"].dtype, np.datetime64):
            df["Data da Compra"] = pd.to_datetime(df["Data da Compra"], errors="coerce")
    else:
        st.error("A coluna 'Data da Compra' não foi encontrada. Verifique o nome das colunas!")

    return df

# =========================== #
# ========== Páginas ======== #
# =========================== #

def page_overview(df):
    st.title("Visão Geral de Vendas")
    
    date_column = "Data da Compra"
    
    # Filtro de datas
    min_date = df[date_column].min()
    max_date = df[date_column].max()
    date_range = st.sidebar.date_input("Selecione o intervalo de datas", [min_date, max_date])
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))]

    # KPIs
    total_sales = df["Valor Total"].sum()
    total_items = df["Quantidade"].sum()
    ticket_medio = total_sales / len(df) if len(df) > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.markdown(green_text_kpi("Vendas Totais", f"R$ {total_sales:,.2f}"), unsafe_allow_html=True)
    col2.markdown(green_text_kpi("Quantidade Vendida", f"{total_items:,.0f}"), unsafe_allow_html=True)
    col3.markdown(green_text_kpi("Ticket Médio", f"R$ {ticket_medio:,.2f}"), unsafe_allow_html=True)

    st.markdown("---")
    
    # Evolução Mensal das Vendas
    df_grouped = df.groupby(pd.Grouper(key=date_column, freq="M"))["Valor Total"].sum().reset_index()
    line_fig = px.line(
        df_grouped, 
        x=date_column, 
        y="Valor Total",
        title="Evolução Mensal das Vendas",
        labels={date_column: "Data", "Valor Total": "Vendas (R$)"},
        template="plotly_dark"
    )
    st.plotly_chart(line_fig, use_container_width=True)

    # Vendas por Loja
    loja_group = df.groupby("Loja")["Valor Total"].sum().reset_index()
    bar_fig = px.bar(
        loja_group, 
        x="Loja", 
        y="Valor Total",
        title="Vendas por Loja",
        labels={"Valor Total": "Vendas (R$)"},
        template="plotly_dark"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

def page_kpis(df):
    st.title("Análise de KPIs de Vendas")
    date_column = "Data da Compra"
    
    # Filtro de datas
    min_date = df[date_column].min()
    max_date = df[date_column].max()
    date_range = st.sidebar.date_input("Selecione o intervalo de datas", [min_date, max_date])
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))]

    # Novos KPIs
    maior_venda = df["Valor Total"].max()
    menor_venda = df["Valor Total"].min()
    media_venda = df["Valor Total"].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.markdown(green_text_kpi("Maior Venda", f"R$ {maior_venda:,.2f}"), unsafe_allow_html=True)
    col2.markdown(red_text_kpi("Menor Venda", f"R$ {menor_venda:,.2f}"), unsafe_allow_html=True)
    col3.markdown(green_text_kpi("Venda Média", f"R$ {media_venda:,.2f}"), unsafe_allow_html=True)

    st.markdown("---")
    
    # Gráfico de Vendas por Categoria
    cat_group = df.groupby("Categoria")["Valor Total"].sum().reset_index()
    cat_fig = px.bar(
        cat_group,
        x="Categoria",
        y="Valor Total",
        title="Vendas por Categoria",
        labels={"Valor Total": "Vendas (R$)"},
        template="plotly_dark"
    )
    st.plotly_chart(cat_fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Mapa de Vendas por UF")

    # Agrega as vendas por UF
    uf_group = df.groupby("UF")["Valor Total"].sum().reset_index()

    # Dicionário com todas as 27 UFs e coordenadas aproximadas
    state_coords = {
        "AC": {"lat": -8.77, "lon": -70.55},
        "AL": {"lat": -9.71, "lon": -35.73},
        "AM": {"lat": -3.07, "lon": -61.66},
        "AP": {"lat": 1.41, "lon": -51.77},
        "BA": {"lat": -12.96, "lon": -38.51},
        "CE": {"lat": -3.71, "lon": -38.54},
        "DF": {"lat": -15.83, "lon": -47.86},
        "ES": {"lat": -19.19, "lon": -40.34},
        "GO": {"lat": -16.64, "lon": -49.31},
        "MA": {"lat": -2.55, "lon": -44.30},
        "MT": {"lat": -12.64, "lon": -55.42},
        "MS": {"lat": -20.51, "lon": -54.54},
        "MG": {"lat": -18.10, "lon": -44.38},
        "PA": {"lat": -5.53, "lon": -52.29},
        "PB": {"lat": -7.06, "lon": -35.55},
        "PR": {"lat": -25.25, "lon": -52.02},
        "PE": {"lat": -8.28, "lon": -35.07},
        "PI": {"lat": -8.28, "lon": -43.68},
        "RJ": {"lat": -22.84, "lon": -43.15},
        "RN": {"lat": -5.22, "lon": -36.52},
        "RS": {"lat": -30.01, "lon": -51.22},
        "RO": {"lat": -11.22, "lon": -62.80},
        "RR": {"lat": 1.89, "lon": -61.22},
        "SC": {"lat": -27.33, "lon": -49.44},
        "SP": {"lat": -23.55, "lon": -46.64},
        "SE": {"lat": -10.90, "lon": -37.07},
        "TO": {"lat": -10.25, "lon": -48.25}
    }

    # Cria DataFrame com todas as UFs e mescla com as vendas
    all_ufs = [{"UF": uf, "lat": coords["lat"], "lon": coords["lon"]} for uf, coords in state_coords.items()]
    df_all_ufs = pd.DataFrame(all_ufs)
    uf_group_merged = pd.merge(df_all_ufs, uf_group, on="UF", how="left")
    uf_group_merged["Valor Total"] = uf_group_merged["Valor Total"].fillna(0)

    # Mapa via scatter_geo
    map_fig = px.scatter_geo(
        uf_group_merged,
        lat="lat",
        lon="lon",
        size="Valor Total",
        hover_name="UF",
        color="UF",
        projection="natural earth",
        title="Distribuição de Vendas por UF",
        template="plotly_dark"
    )
    map_fig.update_layout(height=700)
    map_fig.update_geos(
        scope="south america",
        showcountries=True,
        countrycolor="gray",
        lataxis_range=[-40, 5],
        lonaxis_range=[-80, -30]
    )
    st.plotly_chart(map_fig, use_container_width=True)

def page_ml_prediction(df):
    st.title("Predição de Compras - Machine Learning")
    
    st.markdown("Selecione a loja e a estação para ver as previsões de compra:")
    # Seleção interativa dos filtros
    lojas = sorted(df["Loja"].unique())
    estacoes = sorted(df["Estação"].unique())
    loja_selecionada = st.selectbox("Selecione a Loja", lojas)
    estacao_selecionada = st.selectbox("Selecione a Estação", estacoes)
    
    # Importa os módulos necessários para o treinamento do modelo
    from sklearn.preprocessing import LabelEncoder
    from sklearn.ensemble import RandomForestClassifier
    import numpy as np

    # Treinar o modelo de ML com base nos dados disponíveis
    model_df = df.copy()
    if not all(col in model_df.columns for col in ["Loja", "Estação", "Categoria"]):
        st.error("Colunas necessárias para treinamento não foram encontradas.")
        return
    
    le_loja = LabelEncoder()
    le_estacao = LabelEncoder()
    le_categoria = LabelEncoder()
    
    model_df['Loja_enc'] = le_loja.fit_transform(model_df['Loja'])
    model_df['Estação_enc'] = le_estacao.fit_transform(model_df['Estação'])
    model_df['Categoria_enc'] = le_categoria.fit_transform(model_df['Categoria'])
    
    X = model_df[['Loja_enc', 'Estação_enc']]
    y = model_df['Categoria_enc']
    
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X, y)
    
    # Transformar as seleções do usuário para as codificações usadas pelo modelo
    loja_enc = le_loja.transform([loja_selecionada])[0]
    estacao_enc = le_estacao.transform([estacao_selecionada])[0]
    entrada = np.array([[loja_enc, estacao_enc]])
    
    # Predição das probabilidades para cada categoria
    probs = clf.predict_proba(entrada)[0]
    max_idx = np.argmax(probs)
    predicted_category = le_categoria.inverse_transform([max_idx])[0]
    
    st.markdown(f"### Previsão: *{predicted_category}*")
    st.write(f"A previsão indica que a categoria com maior chance de compra é *{predicted_category}* "
             f"com *{probs[max_idx]*100:.2f}%* de probabilidade.")
    
    # Gráfico de barras exibindo as probabilidades de cada categoria
    prob_df = pd.DataFrame({
        "Categoria": le_categoria.inverse_transform(np.arange(len(probs))),
        "Probabilidade": probs
    })
    fig = px.bar(prob_df, x="Categoria", y="Probabilidade", 
                 text=prob_df["Probabilidade"].apply(lambda x: f"{x*100:.2f}%"),
                 title="Probabilidades de Compra por Categoria", 
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Cálculo do Ticket Médio para a combinação selecionada, utilizando os dados filtrados
    df_filtrado = df[(df["Loja"] == loja_selecionada) & (df["Estação"] == estacao_selecionada)]
    if not df_filtrado.empty:
        total_sales = df_filtrado["Valor Total"].sum()
        num_registros = len(df_filtrado)
        ticket_medio = total_sales / num_registros
        st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    else:
        st.warning("Não há dados para calcular o ticket médio para essa combinação.")

# =========================== #
# ========= Main ============ #
# =========================== #

def main():
    if st.session_state.get("logged_in") is None or not st.session_state.get("logged_in"):
        login_screen()
        return

    df = load_financial_data()
    if df is None or df.empty:
        st.error("Não há dados disponíveis para análise!")
        return

    # Seletor de página via selectbox
    page = st.sidebar.selectbox("Selecione a Página", 
                                ("Visão Geral", "Análise de KPIs", "Predição de Compras"))

    if page == "Visão Geral":
        page_overview(df)
    elif page == "Análise de KPIs":
        page_kpis(df)
    elif page == "Predição de Compras":
        page_ml_prediction(df)

if __name__ == "__main__":
    main()
