import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np
from dados import obter_pontuacoes_dos_jogadores,obter_quantidade_decks_por_edicao, obter_historico_torneios, obter_maior_id_edicao,obter_decks_utilizados


df_pontos = obter_pontuacoes_dos_jogadores()


df_decks = obter_quantidade_decks_por_edicao()

data = {
    "Torneio": ["Torneio 1", "Torneio 2", "Torneio 3", "Torneio 4", "Torneio 5"],
    "Posição": [3, 2, 5, 1, 3]
}
df_posicao = pd.DataFrame(data)
df_posicao['Posição_com_graus'] = df_posicao['Posição'].astype(str) + "°"

# Gráfico de pizza para a aba 'Visão Geral'
fig_torta = px.pie(df_decks, values='Quantidade', names='Deck', title='Proporção de Decks na Liga')

fig_torta_decks_usados = px.pie(df_decks, values='Quantidade', names='Deck', title='Decks Usados')

# Gráfico de barras 'Proporção de Decks'
fig_decks = px.bar(df_decks, x='Deck', y='Quantidade', title='Proporção de Decks na Liga')

def grafico_historico_jogador(id_usuario, id_edicao=None, grau_regressao=2):
    """
    Gera um gráfico de linha com o histórico de torneios e posições de um jogador,
    incluindo a previsão para o próximo torneio.
    
    :param id_usuario: ID do usuário.
    :param id_edicao: (Opcional) ID da edição. Se não fornecido, será utilizado o maior ID de edição disponível.
    :param grau_regressao: Grau da regressão polinomial (padrão é 2 para quadrático).
    :return: Gráfico Plotly com o histórico e a previsão.
    """
    
    # Obtém o histórico de torneios e posições do participante
    df_posicao = obter_historico_torneios(id_usuario, id_edicao)

    # Verifica se o DataFrame está vazio
    if df_posicao.empty:
        return "Não há histórico de torneios para este jogador."
    
    # Criação do gráfico de linha com a posição em cada torneio
    fig = px.line(
        df_posicao, 
        x="Torneio", 
        y="Posição", 
        title="Histórico do Jogador em Torneios", 
        markers=True, 
        text="Posição"
    )

    # Invertendo o eixo Y para que quanto mais próximo de 0, mais alta a linha
    fig.update_layout(
        yaxis=dict(autorange='reversed', range=[1, df_posicao['Posição'].max() + 1])
    )

    # Atualizando o layout para que os textos apareçam mais visíveis e aumentando o tamanho
    fig.update_traces(
        textposition="top center",
        textfont=dict(size=20)
    )

    # Dados para o ajuste da curva
    x = np.arange(len(df_posicao)).reshape(-1, 1)
    y = df_posicao['Posição'].values

    # Criando características polinomiais de grau específico (ex: quadrático)
    poly = PolynomialFeatures(degree=grau_regressao)
    x_poly = poly.fit_transform(x)

    # Ajustando o modelo de regressão polinomial
    model = LinearRegression()
    model.fit(x_poly, y)

    # Gerando a linha de tendência curva
    trendline = model.predict(x_poly)

    # Adicionando a linha de tendência curva ao gráfico
    fig.add_trace(go.Scatter(
        x=df_posicao['Torneio'], 
        y=trendline, 
        mode='lines', 
        name=f'Linha de Tendência (Grau {grau_regressao})',
        line=dict(color='red', dash='dash')
    ))

    # Prevendo o próximo torneio
    next_tournament_index = len(df_posicao)
    next_tournament_name = f"Torneio {next_tournament_index + 1}"
    next_x = np.array([[next_tournament_index]])
    next_x_poly = poly.transform(next_x)
    next_y = model.predict(next_x_poly)[0]

    # Adicionando a previsão do próximo torneio ao gráfico
    fig.add_trace(go.Scatter(
        x=[next_tournament_name],
        y=[next_y],
        mode='markers+text',
        name='Previsão Próximo Torneio',
        marker=dict(color='blue', size=10),
        text=[f'{next_y:.1f}°'],
        textposition='top center'
    ))

    return fig


def gerar_grafico_pizza_decks_ultilizados(id_pessoa, id_edicao=None):
    # Verifica se o id_edicao foi fornecido, se não, busca o maior
    if id_edicao is None:
        id_edicao = obter_maior_id_edicao()

    # Obtém os decks utilizados e a quantidade de vezes que foram utilizados
    df_decks = obter_decks_utilizados(id_pessoa, id_edicao)

    # Verifica se o DataFrame está vazio
    if df_decks.empty:
        print("Nenhum dado disponível para gerar o gráfico.")
        return

    # Cria um gráfico de pizza com os dados do DataFrame
    fig = px.pie(
        df_decks,
        names='Deck',
        values='Vezes Utilizado',
        title=f"Distribuição de Decks Usados na Edição {id_edicao}"
    )

    return fig


