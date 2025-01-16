import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import locale
import time

# Definir o local para a formatação monetária
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para obter dados do endpoint
@st.cache_data(ttl=300)
def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados da API: {e}")
        return pd.DataFrame()

# Forçar a atualização do cache após o TTL
def atualizar_cache_automaticamente():
    # Usar `st.experimental_rerun()` para forçar a atualização da página, recarregando os dados
    st.rerun()

def calcular_faturamento(data, hoje, ontem, semana_inicial, semana_passada_inicial):
    # Faturamento de hoje e ontem
    faturamento_hoje = data[data['DATA'] == hoje]['VLTOTAL'].sum()
    faturamento_ontem = data[data['DATA'] == ontem]['VLTOTAL'].sum()
    
    # Faturamento semanal atual
    faturamento_semanal_atual = data[(data['DATA'] >= semana_inicial) & (data['DATA'] <= hoje)]['VLTOTAL'].sum()
    
    # Faturamento semanal passada
    faturamento_semanal_passada = data[(data['DATA'] >= semana_passada_inicial) & (data['DATA'] < semana_inicial)]['VLTOTAL'].sum()
    
    return faturamento_hoje, faturamento_ontem, faturamento_semanal_atual, faturamento_semanal_passada

def calcular_quantidade_pedidos(data, hoje, ontem, semana_inicial, semana_passada_inicial):
    # Quantidade de pedidos de hoje e ontem
    pedidos_hoje = data[data['DATA'] == hoje]['NUMPED'].nunique()
    pedidos_ontem = data[data['DATA'] == ontem]['NUMPED'].nunique()
    
    # Quantidade de pedidos semana atual
    pedidos_semanal_atual = data[(data['DATA'] >= semana_inicial) & (data['DATA'] <= hoje)]['NUMPED'].nunique()
    
    # Quantidade de pedidos semana passada
    pedidos_semanal_passada = data[(data['DATA'] >= semana_passada_inicial) & (data['DATA'] < semana_inicial)]['NUMPED'].nunique()
    
    return pedidos_hoje, pedidos_ontem, pedidos_semanal_atual, pedidos_semanal_passada

def calcular_comparativos(data, hoje, mes_atual, ano_atual):
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
    
    # Faturamento e quantidade de pedidos do mês atual
    faturamento_mes_atual = data[(data['DATA'].dt.month == mes_atual) & (data['DATA'].dt.year == ano_atual)]['VLTOTAL'].sum()
    pedidos_mes_atual = data[(data['DATA'].dt.month == mes_atual) & (data['DATA'].dt.year == ano_atual)]['NUMPED'].nunique()
    
    # Faturamento e quantidade de pedidos do mês anterior
    faturamento_mes_anterior = data[(data['DATA'].dt.month == mes_anterior) & (data['DATA'].dt.year == ano_anterior)]['VLTOTAL'].sum()
    pedidos_mes_anterior = data[(data['DATA'].dt.month == mes_anterior) & (data['DATA'].dt.year == ano_anterior)]['NUMPED'].nunique()
    
    return faturamento_mes_atual, faturamento_mes_anterior, pedidos_mes_atual, pedidos_mes_anterior

def calcular_detalhes_vendedores(data, data_inicial, data_final):
    # Remover espaços em branco dos nomes das colunas
    data.columns = data.columns.str.strip()

    # Verificar se as colunas necessárias estão presentes
    required_columns = ['DATA', 'VLTOTAL', 'CODCLI', 'NUMPED', 'NOME']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"A coluna '{col}' não está presente no DataFrame.")

    # Filtrar os dados com base no período selecionado
    data_filtrada = data[(data['DATA'] >= data_inicial) & (data['DATA'] <= data_final)]

    # Verificar se há dados após o filtro
    if data_filtrada.empty:
        return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados

    # Agrupar os dados por vendedor e calcular as métricas
    vendedores = data_filtrada.groupby('NOME').agg(
        total_vendas=('VLTOTAL', 'sum'),
        total_clientes=('CODCLI', 'nunique'),
        total_pedidos=('NUMPED', 'nunique')
    ).reset_index()

    vendedores.rename(columns={
        'total_vendas': 'TOTAL VENDAS',
        'total_clientes': 'TOTAL CLIENTES',
        'total_pedidos': 'TOTAL PEDIDOS'
    }, inplace=True)

    return vendedores

def exibir_detalhes_vendedores(vendedores):
    st.subheader("📈 Detalhes dos Vendedores")
    st.dataframe(vendedores.style.format({
        'TOTAL VENDAS': formatar_valor,
    }), use_container_width=True)

def formatar_valor(valor):
    """Função para formatar valores monetários com separador de milhar e vírgula como decimal"""
    return locale.currency(valor, grouping=True, symbol=True)
    

def main():

     

    # Substitua a URL aqui com o endpoint correto
    url = "http://127.0.0.1:5000/dados_pcpedc?data_inicial=2023-01-01&data_final=2025-12-31&pagina=1&limite=5000000"

    st.title('📊 Dashboard de Faturamento')
    st.markdown("### Resumo de Vendas")

    # Obter dados da API
    data = get_data_from_api(url)
    
    if not data.empty:
        # Garantir que as datas sejam corretamente interpretadas
        data['DATA'] = pd.to_datetime(data['DATA'], errors='coerce')

        # Adicionar uma lista de filiais únicas para o seletor
        filiais_unicas = data['CODFILIAL'].unique().tolist()
        filiais_unicas_sorted = sorted(filiais_unicas)

        # Criar as colunas para a seleção das filiais
        colunas = st.columns(len(filiais_unicas_sorted))

        # Usando st.checkbox para selecionar várias filiais
        filiais_selecionadas = []
        for i, filial in enumerate(filiais_unicas_sorted):
            with colunas[i]:
                if st.checkbox(f"Filial: {filial}", value=True):
                    filiais_selecionadas.append(filial)

        # Filtrar os dados conforme as filiais selecionadas
        data_filtrada = data[data['CODFILIAL'].isin(filiais_selecionadas)]

        # Calcular dados de resumo
        hoje = pd.to_datetime('today').normalize()
        ontem = hoje - timedelta(days=1)
        semana_inicial = hoje - timedelta(days=hoje.weekday())
        semana_passada_inicial = semana_inicial - timedelta(days=7)

        # Calcular faturamento
        faturamento_hoje, faturamento_ontem, faturamento_semanal_atual, faturamento_semanal_passada = calcular_faturamento(data_filtrada, hoje, ontem, semana_inicial, semana_passada_inicial)

        # Calcular quantidade de pedidos
        pedidos_hoje, pedidos_ontem, pedidos_semanal_atual, pedidos_semanal_passada = calcular_quantidade_pedidos(data_filtrada, hoje, ontem, semana_inicial, semana_passada_inicial)

        mes_atual = hoje.month
        ano_atual = hoje.year

        # Calcular comparativos mens ais
        faturamento_mes_atual, faturamento_mes_anterior, pedidos_mes_atual, pedidos_mes_anterior = calcular_comparativos(data_filtrada, hoje, mes_atual, ano_atual)

        # Iniciar o processo de verificação de novos dados
        timestamp_atual = time.time()  # Obtém o timestamp atual
        st.session_state.timestamp = timestamp_atual  # Armazena esse timestamp no session state

        if hasattr(st.session_state, 'last_timestamp') and st.session_state.last_timestamp != st.session_state.timestamp:
            # Caso o timestamp tenha mudado, os dados foram atualizados
            st.session_state.last_timestamp = st.session_state.timestamp
            st.rerun()  # Força o rerun para atualização dos dados

        # Exibir as informações
        col1, col2, col3, col4, col5 = st.columns(5)

        # Caixa de resumo
        with col1:
            st.markdown(f"""
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 2.2px; background-color:#007bff; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">💰 Faturamento Hoje:</span> \n  {formatar_valor(faturamento_hoje)}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 6px; background-color:#FF6347; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">📉 Faturamento Ontem:</span> \n {formatar_valor(faturamento_ontem)}
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 5px; background-color:#FF4500; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">📅 Faturamento Semanal Atual:</span> \n {formatar_valor(faturamento_semanal_atual)}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 8px; background-color:#32CD32; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">📦 Faturamento Semanal Passada:</span> \n {formatar_valor(faturamento_semanal_passada)}
                </div>
            """, unsafe_allow_html=True)

        with col3: 
            st.markdown(f"""
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 12px; background-color:#FFD700; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">📈 Faturamento Mês Atual:</span> \n {formatar_valor(faturamento_mes_atual)}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 16px; background-color:#8A2BE2; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">💳 Faturamento Mês Passado:</span> \n {formatar_valor(faturamento_mes_anterior)}
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 21px; background-color:#FF8C00; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">📦 Pedidos Mês Atual:</span> \n {pedidos_mes_atual}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 19.5px; background-color:#8B0000; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: auto; font-weight: normal;">📦 Pedidos Mês Passado:</span> \n {pedidos_mes_anterior}
                </div> 
            """, unsafe_allow_html=True)

        with col5:
            st.markdown(f"""
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 21px; background-color:#3CB371; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: 16px; font-weight: normal;">📦 Pedidos Hoje:</span> \n {pedidos_hoje}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 21px; background-color:#DAA520; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: auto; margin-bottom: 10px; transition: all 0.3s ease; min-height: 120px;">
                    <span style="font-size: 16px; font-weight: normal;">📦 Pedidos Ontem:</span> \n {pedidos_ontem}
                </div>
            """, unsafe_allow_html=True)

        # Seletor de Data para detalhes dos vendedores
        st.subheader("📅 Seletor de Datas para Vendedores")
        data_inicial = st.date_input("Data Inicial", value=datetime(2023,1,1))
        data_final = st.date_input("Data Final", value=datetime.today())

        # Converter data_inicial e data_final para datetime
        data_inicial = pd.to_datetime(data_inicial)
        data_final = pd.to_datetime(data_final)

        # Calcular detalhes dos vendedores com base nas datas selecionadas
        vendedores = calcular_detalhes_vendedores(data_filtrada, data_inicial, data_final)

        if not vendedores.empty:
            # Exibir os detalhes de vendedores
            exibir_detalhes_vendedores(vendedores)
        else:
            st.warning("Não há dados para o período selecionado.")

       

# Executar o aplicativo Streamlit
if __name__ == "__main__":
    main()
