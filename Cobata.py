import streamlit as st
import json
import os
import importlib

st.set_page_config(layout="wide", initial_sidebar_state="auto")

# Caminho do arquivo JSON para armazenar os dados de login
USER_DATA_FILE = "users.json"

# Lista de páginas disponíveis
PAGES = {
    "Página Inicial": "Página_Inicial",
    "Produto": "Produto",
    "Fornecedor": "Fornecedor",
    "Estoque": "Estoque",
    "Validade": "Validade"
}

# Função para carregar dados de usuários do arquivo JSON
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Função para salvar os dados de usuários no arquivo JSON
def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Função para exibir a barra de navegação estilizada na barra lateral
def navigation_bar(selected_page):
    st.markdown("""
                <style>
                /* Barra lateral */
                .sidebar .sidebar-content {
                    background: #ADFF2F;
                    padding: 3rem 0;    
                    width: 50px; /* Largura fixa da barra lateral */
                    
                } 

                .st-emotion-cache-1ibsh2c {
                    width: 100%;
                    padding: 6rem 1rem 10rem;
                    max-width: initial;
                    min-width: auto;
                }

                

                .st-emotion-cache-6qob1r {
                    position: relative;
                    height: 100%;               #Configuração de cores da aba laterral
                    width: 100%;
                    overflow: overlay;
                    background-color: #16181c;
                }

                .st-emotion-cache-jh76sn {
                    display: inline-flex;
                    -webkit-box-align: center;
                    align-items: center;
                    -webkit-box-pack: center;
                    justify-content: center;
                    font-weight: 400;
                    padding: 0.25rem 0.75rem;
                    border-radius: 0.5rem;
                    min-height: 2.5rem;         #Configuração do botão da aba lateral
                    margin: 0px;
                    margiin-left: 30px;
                    margin-height: 30px;
                    line-height: 1.6;
                    text-transform: none;
                    font-size: inherit;
                    font-family: inherit;
                    color: inherit;
                    width: 100%;
                    cursor: pointer;
                    user-select: none;
                    background-color: #16181c;
                    border: 1px solid rgba(250, 250, 250, 0.2);

                    }

                    .st-emotion-cache-1espb9k {
                        font-family: "Source Sans Pro", sans-serif;
                        font-size: 1rem;
                        margin-bottom: -1rem;
                        color: inherit;
                        
                    }

                    .st-emotion-cache-1wqrzgl {
                        position: relative;
                        top: 0.125rem;
                        background-color: rgb(38, 39, 48);
                        z-index: 999991;
                        min-width: 244px;
                        max-width: 200px;
                        transform: none;
                        transition: transform 300ms, min-width 300ms, max-width 300ms;
                    }
                
        
                    .st-emotion-cache-xhkv9f  {
                        position: absolute;
                        left: -4%;
	                    top: %
                        margin-left:-90px;
		                margin-top:-50px;
                        height: fit-content;
                        width: fit-content;
                        max-width: 100%;
                        display: flex;
                        -webkit-box-pack: center;
                        justify-content: center;
                        pointer-events: none
                    }
                
                    
                    .st-emotion-cache-1espb9k h1 {
                        font-size: 2.5rem;
                        font-weight: 600;
                        padding: 1.25rem 0px 1rem;
                        text-align: center;
                        
                    }

                /* Estilos de Botões */
                .sidebar .sidebar-content .nav-button {
                    display: block;
                    width: 100% !important; /* Força a largura do botão para preencher a barra lateral */
                    margin: 8px 0;
                    padding: 20px; /* Aumenta o padding para botões maiores */
                    font-size: 1.2rem; /* Aumenta o tamanho da fonte */
                    color: #ffffff;
                    background: linear-gradient(135deg, #0072ff, #00c6ff);
                    border: none;
                    border-radius: 12px; /* Borda arredondada */
                    text-align: center; /* Centraliza o texto */
                    white-space: nowrap; /* Evita quebras de linha */
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
                    transition: all 0.3s ease-in-out;
                }

                /* Hover nos botões */
                .sidebar .sidebar-content .nav-button:hover {
                    background: linear-gradient(135deg, #0056b3, #0078c9);
                    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.25);
                    transform: scale(1.05);
                }

                /* Botão ativo */
                .sidebar .sidebar-content .nav-button.active {
                    background: linear-gradient(135deg, #003d66, #0066cc);
                    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.35);
                    transform: scale(1.1);
                    border: 2px solid #fff; /* Borda branca no botão ativo */
                }

                /* Responsividade: Para telas menores */
                @media (max-width: 768px) {
                    .sidebar .sidebar-content {
                        width: 110px; /* Ajuste para largura da barra lateral em telas pequenas */
                    }

                    .sidebar .sidebar-content .nav-button {
                        font-size: 1rem; /* Ajusta o tamanho da fonte para telas menores */
                        padding: 15px; /* Ajusta o padding para telas menores */
                        width: 100% !important; /* Ajuste a largura dos botões para preencher a tela */
                    }
                }
                </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.sidebar.image("WhatsApp_Image_2024-11-28_at_10.47.28-removebg-preview.png", width=200 )
    st.sidebar .title("PAINEL")  # Título vazio para não ocupar espaço extra
    for page in PAGES.keys():
        button_class = "nav-button active" if page == selected_page else "nav-button"
        if st.sidebar.button(page, key=page):
            st.session_state.page = page
            

# Função para exibir o formulário de login
def login_page():
    # Exibir imagem no topo da página de login
    st.image("WhatsApp_Image_2024-11-28_at_10.47.28-removebg-preview.png", width=200)  # Coloque o caminho correto da sua imagem

    st.title("Login")
    
    # Campos de login
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")

    # Carregar dados dos usuários
    users_db = load_users()

    # Colunas para os botões lado a lado
    col1, col2 = st.columns([1, 1])  # Dividir a tela em duas colunas

    # Validação do login
    with col1:
        if st.button("Entrar"):
            if username in users_db and users_db[username]["password"] == password:
                # Login bem-sucedido, configurando estado da sessão
                st.session_state.logged_in = True
                st.session_state.page = "Página Inicial"  # Define a página inicial 

            else:
                st.error("Usuário ou senha inválidos. Tente novamente.")



# Função para exibir o formulário de registro de um novo usuário
def register_page():
    st.title("Página de Registro")


    # Carregar dados dos usuários
    users_db = load_users()

# Função para carregar e exibir a página selecionada
def load_page(page_name):
    module_name = PAGES.get(page_name)
    if module_name:
        try:
            page_module = importlib.import_module(module_name)
            page_module.main()  # Presume que cada página tem uma função `main()`
        except ModuleNotFoundError:
            st.error(f"Módulo '{module_name}' não encontrado.")
        except AttributeError:
            st.error(f"O módulo '{module_name}' não possui uma função 'main()'.")

# Função principal que gerencia o fluxo da aplicação
def main():
    # Verifica se a sessão de login existe
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'page' not in st.session_state:
        st.session_state.page = "Login"  # Inicia com a página de login

    # Controle de navegação
    if st.session_state.logged_in:
        # Renderiza a barra de navegação estilizada
        navigation_bar(st.session_state.page)
        load_page(st.session_state.page)
    else:
        # Exibe a página de login ou registro
        if st.session_state.page == "Login":
            login_page()


if __name__ == "__main__":
    main()
