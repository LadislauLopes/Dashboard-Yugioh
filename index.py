import streamlit as st
import pymysql
from versao_gratuita import tela_usuario_nao_pagante
from versao_paga import tela_usuario_pagante
from dados import conectar_ao_banco


def verificar_usuario(usuario, senha):
    try:
        connection = conectar_ao_banco()
        cursor = connection.cursor()

        # Convertendo os campos de usuario e senha para lowercase na query
        query = """
            SELECT * FROM pessoa 
            WHERE LOWER(usuario) = LOWER(%s) AND LOWER(senha) = LOWER(%s)
        """
        cursor.execute(query, (usuario, senha))
        resultado = cursor.fetchone()
        return resultado
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None
    finally:
        connection.close()

def tela_login():
    st.title("Tela de Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Entrar"):
            if usuario and senha:
                # Convertendo os campos digitados para minúsculo para garantir que não haja case sensitivity
                usuario = usuario.lower()
                senha = senha.lower()
                
                usuario_info = verificar_usuario(usuario, senha)
                if usuario_info:
                    st.session_state.usuario_info = usuario_info
                    st.session_state.id_usuario = usuario_info['id_pessoa']  # Armazena o ID do usuário
                    st.session_state.logged_in = True
                    st.rerun()  # Atualiza a página para mostrar a nova tela
                else:
                    st.error("Credenciais inválidas.")
            else:
                st.error("Por favor, preencha todos os campos.")
    
    with col2:
        if st.button("Entrar como Convidado"):
            st.session_state.id_usuario = 0  # ID do convidado como 0
            st.session_state.logged_in = True
            st.session_state.usuario_info = {'pagante': False}  # Convidado não pagante
            st.rerun()

def main():
    # Verifica se o usuário está logado
    #st.set_page_config('Liga Yugioh Acre')
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        usuario_info = st.session_state.usuario_info
        if usuario_info['pagante']:
            tela_usuario_pagante(st.session_state.id_usuario)
        else:
            tela_usuario_nao_pagante(st.session_state.id_usuario)
    else:
        tela_login()
        

if __name__ == "__main__":
    main()
