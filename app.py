import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
from pydantic import BaseModel
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dados de Vendas - Fornecedora de Roupas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Habilita o tema escuro para Altair (opcional)
alt.themes.enable("dark")

# Modelo para validação do login
class UserLogin(BaseModel):
    username: str
    password: str

# Tela de login simples
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

# Função para carregar os dados financeiros do arquivo "base-copeira.csv"
def load_financial_data():
    try:
        # Tenta ler o CSV com as colunas esperadas
        df = pd.read_csv("base-copeira.csv", sep=",")
        st.sidebar.success("Arquivo 'base-copeira.csv' carregado com sucesso!")
    except Exception as e:
        st.sidebar.error("Erro ao carregar 'base-copeira.csv'. Usando dados dummy.")
        # Dados dummy: criação de um DataFrame com as mesmas colunas
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
        # Calcula o Valor Total se não existir no dummy
        df["Valor Total"] = df["Preço Unitário"] * df["Quantidade"]
    # Converter a coluna de data para datetime (mesmo que o CSV venha com a formatação correta)
    if "Data da Compra" in df.columns:
        if not np.issubdtype(df["Data da Compra"].dtype, np.datetime64):
            df["Data da Compra"] = pd.to_datetime(df["Data da Compra"], errors="coerce")
    else:
        st.error("A coluna 'Data da Compra' não foi encontrada no arquivo. Verifique os nomes das colunas!")
    return df

# Página: Visão Geral
def page_overview(df):
    st.title("Visão Geral de Vendas")

    # Definir a coluna de data de acordo com o CSV
    date_column = "Data da Compra"
    
    # Filtros de data: selecionar intervalo no sidebar
    min_date = df[date_column].min()
    max_date = df[date_column].max()
    date_range = st.sidebar.date_input("Selecione o intervalo de datas", [min_date, max_date])
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))]
    
    # KPIs principais
    total_sales = df["Valor Total"].sum()
    total_items = df["Quantidade"].sum()
    ticket_medio = total_sales / len(df) if len(df) > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Vendas Totais", f"R$ {total_sales:,.2f}")
    col2.metric("Quantidade Vendida", f"{total_items:,.0f}")
    col3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("---")
    
    # Gráfico de linha: Evolução das Vendas (agregando por mês)
    df_grouped = df.groupby(pd.Grouper(key=date_column, freq="M"))["Valor Total"].sum().reset_index()
    line_fig = px.line(df_grouped, x=date_column, y="Valor Total",
                       title="Evolução Mensal das Vendas",
                       labels={date_column: "Data", "Valor Total": "Vendas (R$)"},
                       template="plotly_dark")
    st.plotly_chart(line_fig, use_container_width=True)
    
    # Gráfico de barras: Vendas por Loja
    loja_group = df.groupby("Loja")["Valor Total"].sum().reset_index()
    bar_fig = px.bar(loja_group, x="Loja", y="Valor Total",
                     title="Vendas por Loja",
                     labels={"Valor Total": "Vendas (R$)"},
                     template="plotly_dark")
    st.plotly_chart(bar_fig, use_container_width=True)

# Página: Análise Financeira Detalhada
def page_financial_analysis(df):
    st.title("Análise Detalhada de Vendas")
    
    # Gráfico Altair: Quantidade Vendida ao Longo do Tempo
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Data da Compra:T', title='Data'),
        y=alt.Y('Quantidade:Q', title='Quantidade Vendida', scale=alt.Scale(zero=False))
    ).properties(width=600, height=300, title="Evolução da Quantidade Vendida")
    st.altair_chart(chart, use_container_width=True)
    
    # Gráfico de barras: Vendas por Categoria
    cat_group = df.groupby("Categoria")["Valor Total"].sum().reset_index()
    bar_fig = px.bar(cat_group, x="Categoria", y="Valor Total",
                     title="Vendas por Categoria",
                     labels={"Valor Total": "Vendas (R$)"},
                     template="plotly_dark")
    st.plotly_chart(bar_fig, use_container_width=True)
    
    # Gráfico de dispersão: Relação entre Preço Unitário e Quantidade (análise por Categoria)
    scatter_fig = px.scatter(df, x="Preço Unitário", y="Quantidade", color="Categoria",
                             title="Relação entre Preço Unitário e Quantidade",
                             template="plotly_dark",
                             hover_data=["Loja", "Cidade"])
    st.plotly_chart(scatter_fig, use_container_width=True)
    
    st.markdown("### Insights")
    st.write("""
    - Observe a evolução da quantidade vendida ao longo do tempo para identificar tendências.
    - Compare as vendas por categoria para verificar quais produtos têm melhor desempenho.
    - Analise a relação entre o preço unitário e a quantidade vendida para identificar padrões de compra.
    """)

# Página: Sobre o Dashboard
def page_about():
    st.title("Sobre o Dashboard")
    st.write("""
    **Dashboard de Vendas para Fornecedora de Roupas**

    Este dashboard permite visualizar e analisar os dados de vendas a partir de um arquivo CSV chamado **base-copeira.csv**.  
    O arquivo deve conter as seguintes colunas:
    
    - **Data da Compra**
    - **Loja**
    - **UF**
    - **Categoria**
    - **Tamanho**
    - **Cor**
    - **Preço Unitário**
    - **Quantidade**
    - **Valor Total**
    - **Estação**
    - **Cidade**
    - **Tipo de Lead**

    **Recursos do Dashboard:**
    - **Leitura dos Dados:** O arquivo "base-copeira.csv" deve estar na pasta raiz do projeto. Se não for encontrado, são utilizados dados dummy.
    - **Filtros de Data:** Permite selecionar um intervalo para análise.
    - **Visualizações Interativas:** Gráficos de linha, barras e dispersão para detalhar a evolução das vendas, analisar as categorias de produtos e relações de preço/quantidade.
    
    **Instruções de Uso:**
    1. Faça login utilizando o usuário: **admin** e senha: **admin**.
    2. Certifique-se de que o arquivo **base-copeira.csv** está disponível.  
       Caso contrário, serão utilizados dados simulados.
       
    Este dashboard foi desenvolvido com [Streamlit](https://streamlit.io/) e utiliza bibliotecas como [Pandas](https://pandas.pydata.org/), [Plotly](https://plotly.com/python/) e [Altair](https://altair-viz.github.io/).
    """)

# Função principal que gerencia o fluxo do dashboard
def main():
    if st.session_state.get("logged_in") is None or not st.session_state.get("logged_in"):
        login_screen()
        return

    # Carregar os dados a partir do arquivo "base-copeira.csv"
    df = load_financial_data()
    if df is None or df.empty:
        st.error("Não há dados disponíveis para análise!")
        return

    # Sidebar de navegação (multipágina)
    st.sidebar.markdown("## Navegação")
    page = st.sidebar.radio("Selecione a Página", ("Visão Geral", "Análise Detalhada", "Sobre"))

    if page == "Visão Geral":
        page_overview(df)
    elif page == "Análise Detalhada":
        page_financial_analysis(df)
    elif page == "Sobre":
        page_about()

if __name__ == "__main__":
    main()
