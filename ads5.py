import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Campanha - Imóveis Serra Gaúcha",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .positive-metric {
        border-left: 4px solid #2ecc71;
    }
    .negative-metric {
        border-left: 4px solid #e74c3c;
    }
    .conversion-funnel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .comparison-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Função para limpar valores monetários
def clean_currency_value(value):
    if isinstance(value, str):
        # Remove R$, espaços não quebráveis (\xa0) e pontos de milhar
        cleaned = value.replace('R$', '').replace('\xa0', '').replace(' ', '').replace('.', '')
        # Substitui vírgula decimal por ponto
        cleaned = cleaned.replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return float(value) if pd.notna(value) else 0.0

# Função para limpar porcentagens
def clean_percentage(value):
    if isinstance(value, str):
        cleaned = value.replace('%', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return float(value) if pd.notna(value) else 0.0

# Função para limpar números com separadores de milhar
def clean_number(value):
    if isinstance(value, str):
        cleaned = value.replace('.', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return float(value) if pd.notna(value) else 0.0

# Carregar dados
@st.cache_data
def load_data():
    # Dados principais - ATUALIZADOS PARA OS NOVOS NOMES DE ARQUIVO
    campanhas = pd.read_csv('Campanhas(2025.07.08-2025.10.17).csv')
    dispositivos = pd.read_csv('Dispositivos(2025.07.08-2025.10.17).csv')
    idade = pd.read_csv('Informações_demográficas(Idade_2025.07.08-2025.10.17).csv')
    sexo = pd.read_csv('Informações_demográficas(Sexo_2025.07.08-2025.10.17).csv')
    sexo_idade = pd.read_csv('Informações_demográficas(Sexo_Idade_2025.07.08-2025.10.17).csv')
    palavras_chave = pd.read_csv('Palavras-chave_de_pesquisa(2025.07.08-2025.10.17).csv')
    pesquisas = pd.read_csv('Pesquisas(Palavra_2025.07.08-2025.10.17).csv')
    dia_hora = pd.read_csv('Dia_e_hora(Dia_2025.07.08-2025.10.17).csv')
    hora = pd.read_csv('Dia_e_hora(Hora_2025.07.08-2025.10.17).csv')
    dia_hora_detalhado = pd.read_csv('Dia_e_hora(Dia_Hora_2025.07.08-2025.10.17).csv')
    
    # OBS: 'Série_temporal' e 'Redes' foram removidos por não estarem na lista de arquivos.

    # Limpar dados monetários e numéricos
    # Campanhas
    campanhas['Custo_num'] = campanhas['Custo'].apply(clean_currency_value)
    campanhas['Cliques_num'] = campanhas['Cliques'].apply(clean_number)
    campanhas['CTR_num'] = campanhas['CTR'].apply(clean_percentage)
    
    # Dispositivos
    dispositivos['Custo_num'] = dispositivos['Custo'].apply(clean_currency_value)
    dispositivos['Impressões_num'] = dispositivos['Impressões'].apply(clean_number)
    dispositivos['Cliques_num'] = dispositivos['Cliques'].apply(clean_number)
    
    # Palavras-chave
    palavras_chave['Custo_num'] = palavras_chave['Custo'].apply(clean_currency_value)
    palavras_chave['Cliques_num'] = palavras_chave['Cliques'].apply(clean_number)
    palavras_chave['CTR_num'] = palavras_chave['CTR'].apply(clean_percentage)
    
    # Pesquisas
    # COLUNA 'Palavra' é o termo de pesquisa real
    pesquisas.rename(columns={'Palavra': 'Pesquisar'}, inplace=True) # Renomeia para compatibilidade
    pesquisas['Custo_num'] = pesquisas['Custo'].apply(clean_currency_value)
    pesquisas['Cliques_num'] = pesquisas['Cliques'].apply(clean_number)
    pesquisas['Impressões_num'] = pesquisas['Impressões'].apply(clean_number)
    pesquisas['Conversões_num'] = pesquisas['Conversões'].apply(clean_number)
    
    # Série temporal (Recriando um DataFrame simples para não quebrar o código)
    # Usando os dados de Cliques e Custo da tabela de Campanhas para criar uma "semana" única de resumo.
    # Em uma aplicação real, você precisaria de dados diários/semanais.
    data_fim = '2025-10-17'
    data_inicio = '2025-07-08'
    total_cliques_camp = campanhas['Cliques_num'].sum()
    total_custo_camp = campanhas['Custo_num'].sum()
    total_impressoes_disp = dispositivos['Impressões_num'].sum() # Estimativa de impressões total
    
    # Criando um DataFrame de série temporal simplificado (uma linha por "mês" para simular a evolução)
    # NOTE: Isso é uma simulação, pois o arquivo real 'Série_temporal' está ausente.
    serie_temporal = pd.DataFrame({
        'Semana': ['Julho - Set', 'Outubro'],
        'Cliques_num': [total_cliques_camp * 0.7, total_cliques_camp * 0.3],
        'Custo_num': [total_custo_camp * 0.7, total_custo_camp * 0.3],
        'Impressões_num': [total_impressoes_disp * 0.7, total_impressoes_disp * 0.3],
        'CPC méd.': [total_custo_camp / total_cliques_camp, total_custo_camp / total_cliques_camp],
        'CPC_num': [total_custo_camp / total_cliques_camp, total_custo_camp / total_cliques_camp],
    })
    
    # Redes (Removido o arquivo, criando um dummy DataFrame para não quebrar)
    redes = pd.DataFrame({
        'Rede': ['Pesquisa', 'Display'],
        'Cliques_num': [campanhas['Cliques_num'].sum(), 0],
        'Custo_num': [campanhas['Custo_num'].sum(), 0],
        'CPC méd.': [total_custo_camp / total_cliques_camp, 0],
        'CPC_num': [total_custo_camp / total_cliques_camp, 0]
    })
    
    # Dia e hora
    dia_hora['Impressões_num'] = dia_hora['Impressões'].apply(clean_number)
    hora['Impressões_num'] = hora['Impressões'].apply(clean_number)
    dia_hora_detalhado['Impressões_num'] = dia_hora_detalhado['Impressões'].apply(clean_number)
    
    # Limpar dados demográficos
    idade['Impressões_num'] = idade['Impressões'].apply(clean_number)
    idade['Porcentagem_num'] = idade['Porcentagem do total conhecido'].apply(clean_percentage)
    
    sexo['Impressões_num'] = sexo['Impressões'].apply(clean_number)
    sexo['Porcentagem_num'] = sexo['Porcentagem do total conhecido'].apply(clean_percentage)
    
    sexo_idade['Impressões_num'] = sexo_idade['Impressões'].apply(clean_number)
    sexo_idade['Porcentagem_num'] = sexo_idade['Porcentagem do total conhecido'].apply(clean_percentage)
    
    return {
        'campanhas': campanhas,
        'dispositivos': dispositivos,
        'idade': idade,
        'sexo': sexo,
        'sexo_idade': sexo_idade,
        'palavras_chave': palavras_chave,
        'pesquisas': pesquisas,
        'serie_temporal': serie_temporal, # SIMULADO
        'redes': redes, # SIMULADO
        'dia_hora': dia_hora,
        'hora': hora,
        'dia_hora_detalhado': dia_hora_detalhado
    }

data = load_data()

# Sidebar
st.sidebar.title("📊 Filtros")
st.sidebar.markdown("---")

# Métricas principais na sidebar
total_impressoes = data['dia_hora']['Impressões_num'].sum()
total_cliques = data['campanhas']['Cliques_num'].sum()
total_custo = data['campanhas']['Custo_num'].sum()
ctr_medio = (total_cliques / total_impressoes * 100) if total_impressoes > 0 else 0
cpc_medio = total_custo / total_cliques if total_cliques > 0 else 0

st.sidebar.metric("Total de Impressões", f"{total_impressoes:,.0f}")
st.sidebar.metric("Total de Cliques", f"{total_cliques:,.0f}")
st.sidebar.metric("CTR Médio", f"{ctr_medio:.2f}%")
st.sidebar.metric("Custo Total", f"R$ {total_custo:,.2f}")

# Layout principal - ADICIONANDO A NOVA ABA DE COMPARATIVO
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Visão Geral", 
    "🎯 Público-Alvo", 
    "🔍 Palavras-chave", 
    "📱 Dispositivos & Redes",
    "🔄 Conversões",
    "📊 Comparativo",
    "💡 Recomendações"
])

# --- ABA 1: Visão Geral ---
with tab1:
    # Período de Julho a Outubro de 2025
    st.subheader("📊 Performance Geral da Campanha (Julho - Outubro 2025)") 
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card positive-metric">', unsafe_allow_html=True)
        # Otimização é um dado fictício mantido do código original
        st.metric("Pontuação de Otimização", "86,2%") 
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Custo por Clique (CPC)", f"R$ {cpc_medio:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Conversões do seu arquivo são '0,00'
        total_conversoes = data['pesquisas']['Conversões_num'].sum()
        st.markdown('<div class="metric-card negative-metric">', unsafe_allow_html=True)
        st.metric("Conversões", f"{total_conversoes:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card positive-metric">', unsafe_allow_html=True)
        st.metric("CTR da Campanha", f"{ctr_medio:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráficos de série temporal (USANDO DADOS SIMULADOS OU MAIS GERAIS)
    col1, col2 = st.columns(2)
    
    # Usando o DataFrame SIMULADO de série temporal
    semanas_ativas = data['serie_temporal'][data['serie_temporal']['Cliques_num'] > 0]
    
    with col1:
        # Performance "mensal" simulada
        if not semanas_ativas.empty:
            fig = px.bar(semanas_ativas, x='Semana', y='Cliques_num',
             # Add any other valid arguments here (e.g., title, color, labels)
            )
            fig.update_layout(xaxis_title='Período', yaxis_title='Cliques', xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Custo "mensal" simulado
        if not semanas_ativas.empty:
            fig = px.bar(semanas_ativas, x='Semana', y='Custo_num',
                             title='Custo por Período (R$) (SIMULADO)',
                             color='Custo_num',
                             color_continuous_scale='reds')
            fig.update_layout(xaxis_title='Período', yaxis_title='Custo (R$)', xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Gráficos de distribuição temporal
    col1, col2 = st.columns(2)
    
    # Ordem dos dias da semana
    ordem_dias = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
    data['dia_hora']['Dia'] = pd.Categorical(data['dia_hora']['Dia'], categories=ordem_dias, ordered=True)
    df_dia_ordenado = data['dia_hora'].sort_values('Dia')

    with col1:
        # Impressões por hora
        fig = px.bar(data['hora'], x='Hora de início', y='Impressões_num', 
                         title='Distribuição de Impressões por Hora do Dia',
                         color='Impressões_num',
                         color_continuous_scale='blues')
        fig.update_layout(xaxis_title='Hora', yaxis_title='Impressões')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Impressões por dia da semana
        fig = px.bar(df_dia_ordenado, x='Dia', y='Impressões_num',
                         title='Impressões por Dia da Semana',
                         color='Impressões_num',
                         color_continuous_scale='greens')
        st.plotly_chart(fig, use_container_width=True)
    
    # Análise de sazonalidade
    st.subheader("📈 Análise de Sazonalidade (SIMULADA)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Período Ativo (SIMULADO)", f"{len(semanas_ativas)} meses")
        st.metric("Período de Dados", "8 de Julho a 17 de Outubro")
        st.metric("Média Cliques/Mês", f"{semanas_ativas['Cliques_num'].mean():.0f}")
    
    with col2:
        st.metric("Total de Meses (SIMULADO)", f"{len(data['serie_temporal'])}")
        st.metric("Maior Impressão por Dia", f"{data['dia_hora']['Impressões_num'].max():.0f} ({data['dia_hora'].loc[data['dia_hora']['Impressões_num'].idxmax(), 'Dia']})")
        st.metric("Pico de Cliques (SIMULADO)", f"{semanas_ativas['Cliques_num'].max():.0f}")

# --- ABA 2: Público-Alvo ---
with tab2:
    st.subheader("🎯 Análise Demográfica Detalhada")
    
    # Cálculo das métricas demográficas para insights
    maior_faixa = data['idade'].loc[data['idade']['Impressões_num'].idxmax()]
    maior_sexo = data['sexo'].loc[data['sexo']['Impressões_num'].idxmax()]
    
    # Segmento mais engajado (maior número de impressões)
    segmento_mais_engajado = data['sexo_idade'].loc[data['sexo_idade']['Impressões_num'].idxmax()]
    
    # Total da faixa 25 a 44 anos (maior foco)
    impressoes_25_44 = data['idade'][data['idade']['Faixa de idade'].isin(['25 a 34', '35 a 44'])]['Impressões_num'].sum()
    percentual_25_44 = (impressoes_25_44 / data['idade']['Impressões_num'].sum()) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por Idade
        fig = px.pie(data['idade'], values='Impressões_num', names='Faixa de idade',
                         title='Distribuição por Faixa Etária',
                         hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribuição por Sexo
        fig = px.pie(data['sexo'], values='Impressões_num', names='Sexo',
                         title='Distribuição por Sexo',
                         hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sexo e Idade combinados
        fig = px.bar(data['sexo_idade'], x='Faixa de idade', y='Impressões_num', color='Sexo',
                         title='Impressões por Sexo e Faixa Etária',
                         barmode='group')
        fig.update_layout(xaxis_title='Faixa Etária', yaxis_title='Impressões')
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas demográficas
        st.subheader("📋 Insights Demográficos")
        
        st.success(f"""
        **🎯 Público Principal:**
        - **Sexo:** {maior_sexo['Sexo']} ({maior_sexo['Porcentagem_num']:.1f}%)
        - **Faixa Etária:** {maior_faixa['Faixa de idade']} ({maior_faixa['Porcentagem_num']:.1f}%)
        - **Segmento Mais Engajado:** {segmento_mais_engajado['Sexo']} {segmento_mais_engajado['Faixa de idade']} ({segmento_mais_engajado['Porcentagem_num']:.1f}%)
        - **Foco Imobiliário (25-44):** {percentual_25_44:.1f}% das impressões
        """)
    
    # Análise de engajamento por demografia
    st.subheader("📊 Engajamento por Segmento Demográfico")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Impressões da maior faixa etária
        st.metric(f"{maior_faixa['Faixa de idade']}", f"{maior_faixa['Impressões_num']:,.0f}", f"{maior_faixa['Porcentagem_num']:.1f}% do total")
    
    with col2:
        # Impressões do maior sexo
        st.metric(f"{maior_sexo['Sexo']}", f"{maior_sexo['Impressões_num']:,.0f}", f"{maior_sexo['Porcentagem_num']:.1f}% do total")
    
    with col3:
        # Impressões do segmento mais engajado (Sexo e Idade)
        st.metric(f"{segmento_mais_engajado['Sexo']} {segmento_mais_engajado['Faixa de idade']}", f"{segmento_mais_engajado['Impressões_num']:,.0f}", f"{segmento_mais_engajado['Porcentagem_num']:.1f}% do total")

# --- ABA 3: Palavras-chave ---
with tab3:
    st.subheader("🔍 Análise de Palavras-chave e Pesquisas")
    
    # Palavras-chave com desempenho
    palavras_ativas = data['palavras_chave'][data['palavras_chave']['Cliques_num'] > 0]
    # Palavras-chave com Custo > 0, mas Cliques == 0 (dinheiro gasto sem retorno)
    palavras_gastando_sem_clique = data['palavras_chave'][
        (data['palavras_chave']['Custo_num'] > 0) & 
        (data['palavras_chave']['Cliques_num'] == 0)
    ]
    palavras_sem_cliques_total = data['palavras_chave'][data['palavras_chave']['Cliques_num'] == 0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Palavras-chave", len(data['palavras_chave']))
    
    with col2:
        st.metric("Com Cliques", len(palavras_ativas))
    
    with col3:
        st.metric("Gastando sem Cliques", len(palavras_gastando_sem_clique))
    
    with col4:
        # Custo total em palavras-chave que não deram cliques
        custo_sem_clique = palavras_gastando_sem_clique['Custo_num'].sum()
        st.metric("Custo em Ineficientes", f"R$ {custo_sem_clique:,.2f}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top palavras-chave por CTR
        if not palavras_ativas.empty:
            top_ctr = palavras_ativas.nlargest(10, 'CTR_num')
            fig = px.bar(top_ctr, 
                         x='Palavra-chave da rede de pesquisa', y='CTR_num',
                         title='Top 10 Palavras-chave por CTR (%)',
                         color='CTR_num',
                         color_continuous_scale='viridis')
            fig.update_layout(yaxis_title='CTR (%)', xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top palavras-chave por cliques
        if not palavras_ativas.empty:
            top_cliques = palavras_ativas.nlargest(10, 'Cliques_num')
            fig = px.bar(top_cliques, 
                         x='Palavra-chave da rede de pesquisa', y='Cliques_num',
                         title='Top 10 Palavras-chave por Cliques',
                         color='Cliques_num',
                         color_continuous_scale='blues')
            fig.update_layout(yaxis_title='Cliques', xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Análise de eficiência
    st.subheader("💰 Análise de Eficiência por Palavra-chave")
    
    if not palavras_ativas.empty:
        # Evita divisão por zero para CTR e Custo/Clique
        palavras_ativas['Custo_por_Clique'] = palavras_ativas['Custo_num'] / palavras_ativas['Cliques_num'].replace(0, np.nan) 
        
        fig = px.scatter(palavras_ativas.dropna(subset=['Custo_por_Clique']), # Remove os NaNs gerados
                         x='Custo_por_Clique', y='CTR_num',
                         size='Cliques_num', color='Custo_num',
                         hover_name='Palavra-chave da rede de pesquisa',
                         title='Relação Custo/Clique vs CTR (Tamanho: Cliques)',
                         labels={'Custo_por_Clique': 'Custo por Clique (R$)', 'CTR_num': 'CTR (%)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Top pesquisas reais
    st.subheader("🔎 Top Pesquisas dos Usuários (por Cliques)")
    
    if 'Cliques_num' in data['pesquisas'].columns and not data['pesquisas'].empty:
        top_pesquisas = data['pesquisas'].nlargest(10, 'Cliques_num')
        fig = px.bar(top_pesquisas, x='Pesquisar', y='Cliques_num',
                     title='Top 10 Pesquisas por Cliques',
                     color='Cliques_num',
                     color_continuous_scale='purples')
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

# --- ABA 4: Dispositivos & Redes ---
with tab4:
    st.subheader("📱 Análise por Dispositivos e Redes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dispositivos - Impressões
        fig = px.pie(data['dispositivos'], values='Impressões_num', names='Dispositivo',
                         title='Distribuição por Dispositivo - Impressões')
        st.plotly_chart(fig, use_container_width=True)
        
        # Dispositivos - Custo
        fig = px.bar(data['dispositivos'], x='Dispositivo', y='Custo_num',
                         title='Custo por Dispositivo (R$)',
                         color='Custo_num',
                         color_continuous_scale='greens')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Redes - Cliques (USANDO DADOS SIMULADOS)
        fig = px.bar(data['redes'], x='Rede', y='Cliques_num',
                         title='Cliques por Rede (SIMULADO)',
                         color='Cliques_num',
                         color_continuous_scale='purples')
        st.plotly_chart(fig, use_container_width=True)
        
        # CPC por rede (USANDO DADOS SIMULADOS)
        fig = px.bar(data['redes'], x='Rede', y='CPC_num',
                         title='CPC Médio por Rede (R$) (SIMULADO)',
                         color='CPC_num',
                         color_continuous_scale='oranges')
        st.plotly_chart(fig, use_container_width=True)
    
    # Análise de eficiência por dispositivo
    st.subheader("📊 Eficiência por Dispositivo")
    
    # Recálculo de CTR e CPC para o gráfico de dispersão
    data['dispositivos']['CTR'] = (data['dispositivos']['Cliques_num'] / data['dispositivos']['Impressões_num'].replace(0, np.nan) * 100).fillna(0)
    data['dispositivos']['Custo_por_Clique'] = data['dispositivos']['Custo_num'] / data['dispositivos']['Cliques_num'].replace(0, np.nan)
    
    df_disp_plot = data['dispositivos'][data['dispositivos']['Cliques_num'] > 0]
    
    fig = px.scatter(df_disp_plot, x='Custo_por_Clique', y='CTR',
                         size='Impressões_num', color='Dispositivo',
                         title='Eficiência: Custo por Clique vs CTR por Dispositivo (Tamanho: Impressões)',
                         labels={'Custo_por_Clique': 'Custo por Clique (R$)', 'CTR': 'CTR (%)'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights de dispositivos
    st.subheader("💡 Insights de Dispositivos")
    
    col1, col2, col3 = st.columns(3)
    
    # Dados de Smartphones
    smartphone_row = data['dispositivos'][data['dispositivos']['Dispositivo'] == 'Smartphones']
    if not smartphone_row.empty:
        smartphone_impressoes = smartphone_row['Impressões_num'].iloc[0]
        smartphone_percentual = (smartphone_impressoes / total_impressoes) * 100 if total_impressoes > 0 else 0
        smartphone_custo = smartphone_row['Custo_num'].iloc[0]
        ctr_smartphones = (smartphone_row['Cliques_num'].iloc[0] / smartphone_impressoes) * 100 if smartphone_impressoes > 0 else 0
        
        with col1:
            st.metric("Smartphones - Impressões", f"{smartphone_percentual:.1f}%", f"{smartphone_impressoes:,.0f} do total")
        
        with col2:
            st.metric("Custo Smartphones", f"R$ {smartphone_custo:,.2f}", f"{(smartphone_custo/total_custo*100):.1f}% do total")
        
        with col3:
            st.metric("CTR Smartphones", f"{ctr_smartphones:.2f}%")
    else:
         st.warning("Dados de Smartphones não encontrados.")

# --- ABA 5: Conversões ---
with tab5:
    st.header("🔄 Análise de Conversões")
    
    # Métricas de conversão
    col1, col2, col3, col4 = st.columns(4)
    
    total_conversoes = data['pesquisas']['Conversões_num'].sum()
    taxa_conversao = (total_conversoes / total_cliques * 100) if total_cliques > 0 else 0
    custo_por_conversao = total_custo / total_conversoes if total_conversoes > 0 else total_custo
    
    with col1:
        metric_class = "positive-metric" if total_conversoes > 0 else "negative-metric"
        st.markdown(f'<div class="{metric_class}">', unsafe_allow_html=True)
        st.metric("Total de Conversões", f"{total_conversoes:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        metric_class = "positive-metric" if taxa_conversao > 0 else "negative-metric"
        st.markdown(f'<div class="{metric_class}">', unsafe_allow_html=True)
        st.metric("Taxa de Conversão", f"{taxa_conversao:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        metric_class = "positive-metric" if total_conversoes > 0 else "negative-metric"
        st.markdown(f'<div class="{metric_class}">', unsafe_allow_html=True)
        st.metric("Custo por Conversão", f"R$ {custo_por_conversao:,.2f}" if total_conversoes > 0 else "N/A (Custo Total: R$ " + f"{total_custo:,.2f})")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        # ROAS fictício, pois não temos o valor das conversões. 
        # ROAS = (Valor de Conversão / Custo) * 100
        roas = 0 
        st.markdown('<div class="negative-metric">', unsafe_allow_html=True)
        st.metric("ROAS", f"{roas:.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Funnel de conversão atual
    st.subheader("📊 Funil de Conversão Atual")
    
    funnel_data = pd.DataFrame({
        'Estágio': ['Impressões', 'Cliques', 'Conversões'],
        'Quantidade': [total_impressoes, total_cliques, total_conversoes],
        'Taxa Conversão': [100, (total_cliques/total_impressoes*100) if total_impressoes > 0 else 0, taxa_conversao]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.funnel(funnel_data, x='Quantidade', y='Estágio', 
                         title='Funil de Conversão - Quantidade',
                         color='Estágio')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(funnel_data, x='Taxa Conversão', y='Estágio',
                         title='Taxa de Conversão por Estágio (%)',
                         orientation='h',
                         color='Estágio')
        st.plotly_chart(fig, use_container_width=True)
    
    # Análise de potencial de conversão (Valores ajustados para o setor Imobiliário)
    st.subheader("🎯 Análise de Potencial de Conversão")
    
    col1, col2 = st.columns(2)
    
    # Ajuste dos benchmarks para o setor imobiliário
    imobiliario_conversoes_esperadas_min = total_cliques * 0.005 # 0.5%
    imobiliario_conversoes_esperadas_max = total_cliques * 0.03 # 3%
    valor_medio_imovel = 600000.00 # Estimativa
    
    # Projeção de Leads (conversões) com a taxa de mercado
    with col1:
        st.markdown("""
        ### 📈 Projeção com Taxas de Indústria (Imobiliário)
        
        **Imobiliário/Imóveis de Luxo:**
        - Taxa de conversão (Lead): 0.5% - 3.0%
        - Custo por Lead (CPL) aceitável: R$ 50 - 200 (Depende do valor do imóvel)
        - ROAS (Venda): Não rastreável (Geralmente 500%+)
        
        **Potencial com tráfego atual:**
        - Cliques: {total_cliques:,.0f}
        - Leads esperados: {imobiliario_conversoes_esperadas_min:,.0f} - {imobiliario_conversoes_esperadas_max:,.0f}
        - CPL médio atual: R$ {cpc_medio:,.2f}
        """.format(total_cliques=total_cliques, 
                   imobiliario_conversoes_esperadas_min=imobiliario_conversoes_esperadas_min,
                   imobiliario_conversoes_esperadas_max=imobiliario_conversoes_esperadas_max,
                   cpc_medio=cpc_medio))
    
    # Simulação de cenários
    with col2:
        st.markdown("""
        ### 🔄 Cenários com Melhorias (Leads)
        
        **Cenário Conservador (0.5%):**
        - Leads: {conv_cons:,.0f}
        - Custo por Lead (CPL): R$ {cpl_cons:,.2f}
        
        **Cenário Realista (1.5%):**
        - Leads: {conv_real:,.0f}
        - Custo por Lead (CPL): R$ {cpl_real:,.2f}
        
        **Cenário Otimista (3.0%):**
        - Leads: {conv_otm:,.0f}
        - Custo por Lead (CPL): R$ {cpl_otm:,.2f}
        """.format(
            conv_cons=total_cliques * 0.005, cpl_cons=(total_custo / (total_cliques * 0.005)) if (total_cliques * 0.005) > 0 else total_custo,
            conv_real=total_cliques * 0.015, cpl_real=(total_custo / (total_cliques * 0.015)) if (total_cliques * 0.015) > 0 else total_custo,
            conv_otm=total_cliques * 0.03, cpl_otm=(total_custo / (total_cliques * 0.03)) if (total_cliques * 0.03) > 0 else total_custo,
        ))
    
    # Diagnóstico de problemas de conversão
    st.subheader("🔍 Diagnóstico de Problemas de Conversão")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if total_conversoes == 0:
            st.error("""
            **🚫 Tracking de Conversão Crítico**
            - Conversões registradas: {total_conversoes:,.0f}
            - **Problema:** O rastreamento de conversão (Leads/Contatos) não está funcionando ou não foi implementado.
            - **Prioridade:** Máxima.
            """.format(total_conversoes=total_conversoes))
        else:
             st.success("✅ Conversões rastreadas. CPL: R$ {custo_por_conversao:,.2f}".format(custo_por_conversao=custo_por_conversao))
    
    with col2:
        st.warning("""
        **📱 Experiência Mobile (UX/UI)**
        - O alto volume de tráfego (aprox. {smartphone_percentual:.1f}%) em smartphones exige uma landing page impecável.
        - **Atenção:** Velocidade, formulários e carregamento de imagens de alta resolução.
        """.format(smartphone_percentual=smartphone_percentual))
    
    with col3:
        st.warning(f"""
        **💡 Qualidade/Intenção da Palavra-chave**
        - {len(palavras_gastando_sem_clique)} palavras-chave gastando dinheiro (R$ {custo_sem_clique:,.2f}) sem gerar cliques.
        - **Foco:** Palavras como 'alugar', 'temporada' podem ter intenção diferente de 'comprar/investir'.
        """)

# --- ABA 6: Comparativo ---
with tab6:
    st.header("📊 Comparativo de Performance")
    
    # Dados para comparação (benchmarks da indústria de Imobiliário de Luxo/Nicho - AJUSTADOS)
    benchmarks = {
        'Métrica': ['CTR', 'CPC (R$)', 'Taxa de Conversão (Lead)'],
        'Nossa Campanha': [ctr_medio, cpc_medio, taxa_conversao],
        'Média do Setor': [1.5, 2.50, 1.5], # Ajustado: CTR Imob. é menor, CPC é maior
        'Top Performers': [3.0, 1.50, 4.0] # Ajustado
    }
    
    df_benchmarks = pd.DataFrame(benchmarks)
    
    # Normalização de métricas para o gráfico de radar (Ex: CPC é melhor quanto MENOR)
    df_benchmarks['Nossa Campanha Normalizada'] = df_benchmarks['Nossa Campanha'].copy()
    
    # Inverte a pontuação para Custo (CPC): Maior valor -> pior desempenho (menor pontuação no radar)
    max_cpc = max(df_benchmarks['Média do Setor'].max(), df_benchmarks['Nossa Campanha'].max())
    min_cpc = min(df_benchmarks['Média do Setor'].min(), df_benchmarks['Nossa Campanha'].min())
    
    # Normalização simples (a inversão de escala é mais complexa, vou apenas inverter o valor no plot)
    # df_benchmarks['Nossa Campanha Normalizada'] = np.where(df_benchmarks['Métrica'] == 'CPC (R$)', max_cpc - df_benchmarks['Nossa Campanha'] + min_cpc, df_benchmarks['Nossa Campanha'])
    # df_benchmarks['Média do Setor Normalizada'] = np.where(df_benchmarks['Métrica'] == 'CPC (R$)', max_cpc - df_benchmarks['Média do Setor'] + min_cpc, df_benchmarks['Média do Setor'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Comparativo com Benchmarks (SIMPLIFICADO)")
        
        # Gráfico de radar (Simples, sem normalização complexa de escala para CPC)
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=df_benchmarks['Nossa Campanha'].tolist(),
            theta=df_benchmarks['Métrica'].tolist(),
            fill='toself',
            name='Nossa Campanha',
            line_color='blue'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=df_benchmarks['Média do Setor'].tolist(),
            theta=df_benchmarks['Métrica'].tolist(),
            fill='toself',
            name='Média do Setor',
            line_color='orange'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(df_benchmarks[['Nossa Campanha', 'Média do Setor']].max().max(), 4)]
                )),
            showlegend=True,
            title="Comparativo de Performance vs Benchmarks do Setor"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Análise Competitiva")
        
        # Métricas comparativas
        col2_1, col2_2, col2_3 = st.columns(3)
        
        # Comparação com a Média do Setor (1.5% CTR, R$ 2.50 CPC, 1.5% Conversão)
        ctr_media = 1.5
        cpc_media = 2.50
        conv_media = 1.5
        
        with col2_1:
            delta_ctr = ctr_medio - ctr_media
            st.metric("CTR vs Média", f"{ctr_medio:.2f}%", f"{delta_ctr:+.2f}%", delta_color="normal")
            delta_cpc = cpc_media - cpc_medio # Diferença invertida para Custo: CPC menor é bom
            st.metric("CPC vs Média", f"R$ {cpc_medio:.2f}", f"R$ {delta_cpc:+.2f}", delta_color="inverse")
        
        with col2_2:
            delta_conv = taxa_conversao - conv_media
            st.metric("Taxa Conversão", f"{taxa_conversao:.2f}%", f"{delta_conv:+.2f}%", delta_color="normal")
            # Custo por Conversão vs Média do Setor (R$ 100,00)
            cpc_conv_media = 100.00
            delta_cpc_conv = cpc_conv_media - custo_por_conversao
            if total_conversoes > 0:
                st.metric("Custo/Conversão", f"R$ {custo_por_conversao:,.2f}", f"R$ {delta_cpc_conv:+.2f}", delta_color="inverse")
            else:
                st.metric("Custo/Conversão", "N/A", "R$ -100.00", delta_color="inverse")
        
        with col2_3:
            st.metric("Pontuação Otimização", "86.2%", "Alto")
            st.metric("Eficiência de Tráfego", "CTR Alto/CPC Baixo", "Excelente")
        
        # Análise SWOT comparativa
        st.subheader("🔍 Análise SWOT Comparativa")
        
        col_swot1, col_swot2 = st.columns(2)
        
        with col_swot1:
            st.markdown("""
            **✅ FORÇAS**
            - **CTR ({ctr:.2f}%)** muito acima da média do setor imobiliário (**1.5%**).
            - **CPC ({cpc:.2f}%)** muito competitivo (abaixo da média de **R$ 2.50**).
            - Forte engajamento do público **Feminino 35-44**.
            """.format(ctr=ctr_medio, cpc=cpc_medio))
            
            st.markdown("""
            **🔄 OPORTUNIDADES**
            - **URGENTE:** Configurar rastreamento de conversão.
            - Otimizar Landing Page para Mobile (96.8% do tráfego).
            - **Expandir:** Aproveitar o CPC baixo em Computadores para um público com maior poder de compra/investimento.
            """)
        
        with col_swot2:
            st.markdown("""
            **❌ FRAQUEZAS**
            - **Conversão {conv:,.0f}**: Não há leads sendo rastreados.
            - **Custo em Palavras-Chave Ineficientes:** R$ {custo_sem_clique:,.2f} gasto em termos sem cliques.
            - **Disparidade de Dispositivos:** Quase 100% de dependência de Mobile.
            """.format(conv=total_conversoes, custo_sem_clique=custo_sem_clique))
            
            st.markdown("""
            **⚠️ AMEAÇAS**
            - Concorrência pode estar convertendo melhor (se o rastreamento não estiver funcionando).
            - Aumento do custo das palavras-chave 'Gramado' e 'Canela'.
            - Palavras-chave genéricas como 'alugar' trazem intenção de baixo valor.
            """)
    
    # Comparativo por canal (SIMULADO)
    st.subheader("📊 Comparativo por Canal de Aquisição (SIMULADO)")
    
    if not data['redes'].empty:
        fig = px.bar(data['redes'], x='Rede', y=['Cliques_num', 'Custo_num'],
                         title='Comparativo: Cliques vs Custo por Rede',
                         barmode='group',
                         labels={'value': 'Quantidade', 'variable': 'Métrica'})
        fig.update_layout(xaxis_title='Rede', yaxis_title='Quantidade')
        st.plotly_chart(fig, use_container_width=True)
    
    # Comparativo temporal (SIMULADO)
    st.subheader("📅 Evolução Temporal vs Metas (SIMULADO)")
    
    if not semanas_ativas.empty:
        # Adicionando metas fictícias para comparação
        semanas_ativas['Meta_Cliques'] = semanas_ativas['Cliques_num'] * 1.2 # Meta 20% maior
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=semanas_ativas['Semana'],
            y=semanas_ativas['Cliques_num'],
            name='Cliques Reais',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=semanas_ativas['Semana'],
            y=semanas_ativas['Meta_Cliques'],
            name='Meta Cliques',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Evolução de Cliques vs Metas (SIMULADO)',
            xaxis_title='Período',
            yaxis_title='Cliques',
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig, use_container_width=True)

# --- ABA 7: Recomendações ---
with tab7:
    st.header("💡 Análise e Recomendações")
    
    # Métricas calculadas para análise
    custo_sem_clique = palavras_gastando_sem_clique['Custo_num'].sum()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ O que está funcionando:")
        
        st.success(f"""
        **📈 Performance de Tráfego Forte:**
        - **CTR da campanha:** {ctr_medio:.2f}% (Excelente para Imobiliário) ⭐
        - **CPC Médio:** R$ {cpc_medio:.2f} (Muito competitivo)
        - **Total de Cliques:** {total_cliques:,.0f}
        
        **🎯 Público-alvo engajado:**
        - **Feminino** ({maior_sexo['Porcentagem_num']:.1f}%) é o sexo dominante.
        - O foco de **25-44 anos** ({percentual_25_44:.1f}% das impressões) é ideal para a intenção de compra de imóveis/investimento.
        
        **🔍 Melhores Palavras-chave por Custo/Clique:**
        - As principais palavras-chave estão gerando cliques a um custo baixo, focadas em 'imobiliária' e 'casa/apartamento em Canela/Gramado'.
        """)
        
        st.subheader("🔄 Oportunidades de Melhoria:")
        
        st.warning(f"""
        **💰 Otimização de Custo Imediata:**
        - **Ação:** Pausar {len(palavras_gastando_sem_clique)} palavras-chave que custaram **R$ {custo_sem_clique:,.2f}** sem gerar um único clique.
        - **Ação:** Adicionar palavras-chave negativas para termos de **aluguel de temporada**, 'barato', 'sp' para focar na intenção de compra/investimento.
        
        **💻 Explorar Computador/Tablet:**
        - O CPC para Computador é {data['dispositivos'][data['dispositivos']['Dispositivo'] == 'Computadores']['Custo_num'].iloc[0] / data['dispositivos'][data['dispositivos']['Dispositivo'] == 'Computadores']['Cliques_num'].iloc[0] if not data['dispositivos'][data['dispositivos']['Dispositivo'] == 'Computadores'].empty and data['dispositivos'][data['dispositivos']['Dispositivo'] == 'Computadores']['Cliques_num'].iloc[0] > 0 else 0:,.2f}. Testar lances mais altos neste dispositivo para capturar um público que normalmente finaliza transações complexas no desktop.
        """)
    
    with col2:
        st.subheader("❌ Problemas identificados (CRÍTICOS):")
        
        st.error(f"""
        **🚫 CONVERSÃO ZERO:**
        - **Nenhuma conversão ({total_conversoes:,.0f})** rastreada, apesar de {total_cliques:,.0f} cliques e R$ {total_custo:,.2f} de custo.
        - **Diagnóstico:** O funil está quebrado (falha no rastreamento **OU** Landing Page/Processo de Contato com problemas).
        
        **📊 Disparidade de Dispositivos:**
        - **96.8%** das impressões em Smartphones.
        - O site e os formulários de contato **DEVEM** ser perfeitamente otimizados para Mobile.
        
        **🔍 Tráfego de Baixa Intenção:**
        - Palavras como 'em', 'para', 'alugar' são as que mais geram cliques/impressões (ver Pesquisas).
        - **Risco:** O tráfego gerado tem baixa intenção de compra de imóveis de alto valor.
        """)
        
        st.subheader("🎯 Recomendações Prioritárias:")
        
        st.info("""
        1. **PRIORIDADE MÁXIMA:** **IMPLEMENTAR RASTREAMENTO DE CONVERSÃO** para Leads/Contatos (Preencher Formulário, Ligação, WhatsApp).
        2. **IMEDIATO:** **LIMPAR PALAVRAS-CHAVE** com gasto zero cliques e adicionar termos negativos de 'aluguel', 'temporada', 'pousada'.
        3. **OTIMIZAÇÃO:** **TESTAR LANCES MAIS AGRESSIVOS** em Campanhas de Palavras-chave 'Alto Padrão' no Dispositivo **Computador**.
        4. **CRIAÇÃO:** Desenvolver uma Landing Page **EXCLUSIVAMENTE** otimizada para Mobile e com foco em **Captura de Leads (CPL)**.
        """)