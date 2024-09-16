import streamlit as st
import pandas as pd
import plotly.express as px
from graficos import *
from botoes import redes_socias
from dados import obter_media_jogadores_por_edicao, calcular_valores_e_quantidade_torneios,obter_nome_pessoa,obter_adversarios_e_resultados,calcular_winrate,obter_decks_top
from graficos import *

def tela_usuario_pagante(id):
    # Dashboard
    nome, fregues, carrasco = obter_adversarios_e_resultados(id)
    st.set_page_config(page_title='Liga Yugioh Acre', layout='wide')

    with open("styles.css") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

    # Cabeçalho
    coluna1, coluna2, coluna3 = st.columns(3)
    with coluna1:
        st.markdown('<h1>Liga Yu-gi-oh Acre</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:15px;">Develop by Ladislau Lopes</p>', unsafe_allow_html=True)
        redes_socias()
    with coluna2:
        st.image(r'src/logo.png', width=350)
    with coluna3:
        st.markdown('<h1>Bem-vindo</h1>', unsafe_allow_html=True)
        st.markdown(f'<h1>{obter_nome_pessoa(id)}</h1>', unsafe_allow_html=True)

    # # Sidebar
    # st.sidebar.title('Edição da liga')
    # st.sidebar.selectbox('Escolha a edição', options=['Atual', 1, 2, 3])

    # Abas
    visao_geral, Aba_do_participante, metacall = st.tabs(['Visão Geral', 'Detalhes do player', 'Metacall'])

    with visao_geral:
        valor_total, valor_ultimo_torneio, quantidade_torneios = calcular_valores_e_quantidade_torneios()
        # Ajuste a largura das colunas para que sejam iguais
        with st.container():
            coluna1, coluna2, coluna3 = st.columns(3)

            with coluna1:
                st.metric('Totais de torneios', f'{quantidade_torneios}/10')
            with coluna2:
                st.metric('Média de players por torneio', obter_media_jogadores_por_edicao())
            with coluna3:
                
                st.metric('Valor Arrecadado', f'R$ {valor_total},00', f'R$ {valor_ultimo_torneio},00')

            coluna2_1, coluna2_2, coluna2_3 = st.columns([2, 3, 1])
            with coluna2_1:
                st.markdown('<p style="font-size:15px;margin-left: 1.5rem">Tabela de Pontuação da Liga</p>',unsafe_allow_html=True)
                st.markdown(df_pontos.to_html(classes='dataframe-container', index=False), unsafe_allow_html=True)
            with coluna2_2:
                st.plotly_chart(fig_decks)  # Gráfico de pizza aqui
            with coluna2_3:
                pass
    with Aba_do_participante:
        with st.container():
            coluna1, coluna2, coluna3 = st.columns(3)

            with coluna1:
                st.metric('Carrasco', f'{carrasco}')
            with coluna2:
                st.metric('Freguês', f'{fregues}')
            with coluna3:
                st.metric('Winrate',f'{calcular_winrate(id)}%')
        with st.container():
            coluna1, coluna2 = st.columns([3, 2])
            with coluna1:
                st.plotly_chart(grafico_historico_jogador(id), use_container_width=True)
            with coluna2:
                st.plotly_chart(gerar_grafico_pizza_decks_ultilizados(id))
        with metacall:
            with st.container():
                coluna1, coluna2, coluna3 = st.columns(3)
                with coluna1:
                    st.markdown("<h2>Top Decks Frequentes</h2>", unsafe_allow_html=True)
                
                    # Seleção de filtro para o top
                    top_n = st.number_input("Selecione o Top N para filtrar", 2)


                    # Obtenha os dados dos decks mais frequentes no top N
                    df_decks_top = obter_decks_top(top=top_n)

                    # Gráfico de barras dos decks mais frequentes (ajustando para as colunas corretas)
                    fig = px.pie(df_decks_top, names='Deck', values='Quantidade', title=f'Distribuição dos Decks no Top {top_n}')
                    st.plotly_chart(fig, use_container_width=True)

                with coluna2:
                    st.warning('Em breve mais adições')

