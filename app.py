import streamlit as st
import pandas as pd
import numpy as np
from pydantic import BaseModel

# Modelo de validação usando Pydantic
class UserLogin(BaseModel):
    username: str
    password: str

# Tela de login
def login_screen():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        # Aqui você pode integrar validação com um banco de dados ou API real se desejar
        if username == "admin" and password == "admin":
            st.success("Logado com sucesso!")
            st.session_state.logged_in = True
        else:
            st.error("Usuário ou senha inválidos")
            st.session_state.logged_in = False

# Página Dashboard: Exibe dados e gráficos básicos
def page_dashboard():
    st.header("Dashboard Principal")
    st.markdown("""
    Bem-vindo ao seu dashboard! Aqui você pode visualizar dados aleatórios e alguns gráficos básicos.
    """)
    
    st.subheader("Dados Aleatórios")
    data = {
        'Coluna A': np.random.randint(1, 100, 10),
        'Coluna B': np.random.randint(1, 100, 10),
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
    
    st.subheader("Gráfico de Linhas")
    st.line_chart(df)

# Página Dados: Sugestões de datasets, upload de arquivo e exploração de dados
def page_dados():
    st.header("Sugestões de Dados")
    st.markdown("""
    Nesta seção, você pode:
    - Visualizar datasets exemplos.
    - Fazer upload do seu próprio arquivo CSV.
    - Explorar dados de forma interativa.
    """)
    
    # Exemplo de dataset fictício
    st.subheader("Dataset Exemplo")
    data = {
        'Nome': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Idade': [25, 30, 35, 28],
        'Salário': [5000, 6000, 5500, 5800]
    }
    df_exemplo = pd.DataFrame(data)
    st.dataframe(df_exemplo)
    
    st.subheader("Upload de CSV")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
    if uploaded_file is not None:
        df_upload = pd.read_csv(uploaded_file)
        st.write("Preview dos dados:")
        st.dataframe(df_upload)

# Página Gráficos: Diversos tipos de visualizações
def page_graficos():
    st.header("Visualizações Gráficas")
    st.markdown("""
    Aqui você pode explorar diferentes tipos de gráficos interativos.
    Use os filtros e selecione as variáveis para personalizar os gráficos.
    """)

    # Exemplo 1: Gráfico de Barras
    st.subheader("Gráfico de Barras")
    data_bar = pd.DataFrame({
        'Categoria': ['A', 'B', 'C', 'D'],
        'Valor': np.random.randint(10, 100, 4)
    })
    st.bar_chart(data_bar.set_index('Categoria'))
    
    # Exemplo 2: Gráfico de Dispersão usando Matplotlib (pode expandir com matplotlib.pyplot)
    st.subheader("Gráfico de Dispersão")
    import matplotlib.pyplot as plt
    x = np.random.rand(50)
    y = np.random.rand(50)
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_title("Scatter Plot Exemplo")
    st.pyplot(fig)

# Página Sobre: Informações e instruções sobre o dashboard
def page_sobre():
    st.header("Sobre o Dashboard")
    st.markdown("""
    ## O que é este dashboard?
    Este é um exemplo de dashboard multipágina construído com Streamlit que integra:
    
    - **Login Seguro:** Acesso restrito com validação.
    - **Sidebar Interativa:** Navegue facilmente entre as seções.
    - **Várias Páginas:** Cada página apresenta recursos e exemplos práticos.
    - **Sugestões de Dados:** Amostras de datasets e ferramenta de upload para análise.
    
    Sinta-se à vontade para modificar e expandir cada seção conforme sua necessidade.  
    """)
    
    st.markdown("### Sugestões de Expansão")
    st.markdown("""
    - Conectar a uma base de dados real (ex: SQL, NoSQL ou APIs REST).
    - Adicionar filtros e interatividade para explorar dados de vendas, tráfego, finanças, etc.
    - Integração com bibliotecas de visualização avançadas como Plotly ou Altair.
    - Criação de dashboards responsivos para relatórios em tempo real.
    """)

# Função para gerenciar a navegação entre páginas usando a sidebar
def main():
    # Se o usuário não estiver logado ainda, mostra a tela de login
    if st.session_state.get("logged_in") is None or st.session_state.get("logged_in") is False:
        login_screen()
        # Para evitar que o conteúdo das páginas apareça na tela de login, retornamos aqui.
        return

    # Sidebar para navegação e logout
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Navegue pelas páginas", 
                            ("Dashboard", "Dados", "Gráficos", "Sobre"))

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.experimental_rerun()  # Atualiza a página para retornar ao login

    # Roteamento das páginas
    if page == "Dashboard":
        page_dashboard()
    elif page == "Dados":
        page_dados()
    elif page == "Gráficos":
        page_graficos()
    elif page == "Sobre":
        page_sobre()

if __name__ == "__main__":
    main()
