import pymysql
import pandas as pd
import os
import pymysql
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def conectar_ao_banco():
    """
    Conecta ao banco de dados MySQL usando variáveis de ambiente e retorna a conexão.
    """
    return pymysql.connect(
        charset=os.getenv("DB_CHARSET"),
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor,
        db=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        password=os.getenv("DB_PASSWORD"),
        read_timeout=10,
        port=int(os.getenv("DB_PORT")),  # Porta deve ser convertida para inteiro
        user=os.getenv("DB_USER"),
        write_timeout=10,
    )

def obter_maior_id_edicao():
    """
    Obtém o maior ID de edição do banco de dados.
    """
    query = "SELECT MAX(id_edicao) AS maior_id_edicao FROM edicao;"
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query)
            resultado = cursor.fetchone()
            return resultado['maior_id_edicao']
    finally:
        conexao.close()


def obter_pontuacoes_dos_jogadores():
    """
    Executa a consulta SQL para obter a pontuação dos jogadores e retorna um DataFrame.
    """
    query = """
    WITH ParticipacaoTorneios AS (
        SELECT
            p.id_pessoa,
            COUNT(DISTINCT pa.id_torneio) * 10 AS pontos_participacao
        FROM
            participante pa
        JOIN pessoa p ON p.id_pessoa = pa.id_pessoa
        GROUP BY p.id_pessoa
    ),
    VitoriasEmpates AS (
        SELECT
            pa.id_pessoa,
            COALESCE(SUM(CASE WHEN pa.id_participante = p1.id_participante1 AND p1.resultado = 'vitória' THEN 3 ELSE 0 END), 0) AS pontos_vitoria,
            COALESCE(SUM(CASE WHEN pa.id_participante = p1.id_participante1 AND p1.resultado = 'empate' THEN 1 ELSE 0 END), 0) AS pontos_empate
        FROM
            partida p1
        JOIN participante pa ON pa.id_participante = p1.id_participante1
        GROUP BY pa.id_pessoa
    ),
    PontosTotais AS (
        SELECT
            p.id_pessoa,
            p.nome,
            COALESCE(v.pontos_vitoria, 0) + COALESCE(v.pontos_empate, 0) + COALESCE(pt.pontos_participacao, 0) AS total_pontos
        FROM
            pessoa p
        LEFT JOIN VitoriasEmpates v ON p.id_pessoa = v.id_pessoa
        LEFT JOIN ParticipacaoTorneios pt ON p.id_pessoa = pt.id_pessoa
    )
    SELECT
        nome AS Jogador,
        total_pontos AS Pontos
    FROM
        PontosTotais
    ORDER BY
        total_pontos DESC;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query)
            resultado = cursor.fetchall()
            df = pd.DataFrame(resultado)
    finally:
        conexao.close()
    
    return df

def obter_quantidade_decks_por_edicao(id_edicao=None):
    """
    Obtém a quantidade de decks utilizados em uma edição específica. Se nenhum ID de edição for passado,
    utiliza o maior ID de edição disponível.
    """
    if id_edicao is None:
        id_edicao = obter_maior_id_edicao()
    
    query = """
    SELECT
        d.nome_do_deck AS Deck,
        COUNT(*) AS Quantidade
    FROM
        participante p
    JOIN deck d ON p.id_deck = d.id_deck
    JOIN torneio t ON p.id_torneio = t.id_torneio
    WHERE
        t.id_edicao = %s
    GROUP BY
        d.nome_do_deck
    ORDER BY
        Quantidade DESC;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query, (id_edicao,))
            resultado = cursor.fetchall()
            df = pd.DataFrame(resultado)
    finally:
        conexao.close()
    
    return df

def obter_media_jogadores_por_edicao(id_edicao=None):
    """
    Obtém a média do número de jogadores por edição. Se nenhum ID de edição for passado,
    utiliza o maior ID de edição disponível.
    """
    if id_edicao is None:
        id_edicao = obter_maior_id_edicao()
    
    query = """
    SELECT
        AVG(qnt_players) AS media_jogadores
    FROM
        torneio
    WHERE
        id_edicao = %s;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query, (id_edicao,))
            resultado = cursor.fetchone()
            media_jogadores = resultado['media_jogadores']
            # Arredondar para o número inteiro mais próximo
            media_jogadores = round(media_jogadores) if media_jogadores is not None else None
    finally:
        conexao.close()
    
    return media_jogadores

def calcular_valores_e_quantidade_torneios(id_edicao=None):
    """
    Calcula o valor total arrecadado, o valor arrecadado pelo último torneio e a quantidade de torneios na edição.
    Se nenhum ID de edição for passado, utiliza o maior ID de edição disponível.
    """
    if id_edicao is None:
        id_edicao = obter_maior_id_edicao()
    
    query_total = """
    SELECT
        SUM(valor_arrecadado) AS valor_total
    FROM
        torneio
    WHERE
        id_edicao = %s;
    """
    
    query_ultimo_torneio = """
    SELECT
        valor_arrecadado AS valor_ultimo_torneio
    FROM
        torneio
    WHERE
        id_edicao = %s
    ORDER BY
        id_torneio DESC
    LIMIT 1;
    """
    
    query_quantidade_torneios = """
    SELECT
        COUNT(*) AS quantidade_torneios
    FROM
        torneio
    WHERE
        id_edicao = %s;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            # Obter valor total arrecadado
            cursor.execute(query_total, (id_edicao,))
            resultado_total = cursor.fetchone()
            valor_total = resultado_total['valor_total'] if resultado_total['valor_total'] is not None else 0
            
            # Obter valor arrecadado pelo último torneio
            cursor.execute(query_ultimo_torneio, (id_edicao,))
            resultado_ultimo_torneio = cursor.fetchone()
            valor_ultimo_torneio = resultado_ultimo_torneio['valor_ultimo_torneio'] if resultado_ultimo_torneio['valor_ultimo_torneio'] is not None else 0
            
            # Obter quantidade de torneios
            cursor.execute(query_quantidade_torneios, (id_edicao,))
            resultado_quantidade = cursor.fetchone()
            quantidade_torneios = resultado_quantidade['quantidade_torneios'] if resultado_quantidade['quantidade_torneios'] is not None else 0
            
    finally:
        conexao.close()
    
    return valor_total, valor_ultimo_torneio, quantidade_torneios

def obter_nome_pessoa(id_pessoa):
    """
    Obtém o nome da pessoa com base no ID da pessoa.
    """
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            query = "SELECT nome FROM pessoa WHERE id_pessoa = %s;"
            cursor.execute(query, (id_pessoa,))
            resultado = cursor.fetchone()
            return resultado['nome'] if resultado else 'Nome não encontrado'
    finally:
        conexao.close()


def obter_adversarios_e_resultados(id_pessoa, id_edicao=None):
    """
    Obtém a pessoa com quem o usuário mais perdeu e mais ganhou na edição fornecida ou na mais recente.
    """
    if id_edicao is None:
        id_edicao = obter_maior_id_edicao()
    
    query_resultados = """
    SELECT
        p2.id_pessoa AS id_adversario,
        p2_nome.nome AS nome_adversario,
        SUM(CASE WHEN p1.id_pessoa = %s AND p1.id_participante = p.id_participante1 AND p.resultado = 'vitória' THEN 1 ELSE 0 END) AS vitorias,
        SUM(CASE WHEN p1.id_pessoa = %s AND p1.id_participante = p.id_participante1 AND p.resultado = 'derrota' THEN 1 ELSE 0 END) AS derrotas
    FROM
        partida p
    JOIN participante p1 ON p.id_participante1 = p1.id_participante
    JOIN participante p2 ON p.id_participante2 = p2.id_participante
    JOIN pessoa p2_nome ON p2.id_pessoa = p2_nome.id_pessoa
    WHERE
        p1.id_pessoa = %s
        AND p.id_rodada IN (SELECT id_rodada FROM rodada WHERE id_torneio IN (SELECT id_torneio FROM torneio WHERE id_edicao = %s))
    GROUP BY
        p2.id_pessoa, p2_nome.nome;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            # Obter os adversários e contagem de vitórias e derrotas
            cursor.execute(query_resultados, (id_pessoa, id_pessoa, id_pessoa, id_edicao))
            resultados = cursor.fetchall()

            if not resultados:
                return None, None, None, None

            # Identificar o adversário com mais vitórias e mais derrotas
            df = pd.DataFrame(resultados)
            adversario_mais_vitorias = df.loc[df['vitorias'].idxmax()] if not df['vitorias'].empty else None
            adversario_mais_derrotas = df.loc[df['derrotas'].idxmax()] if not df['derrotas'].empty else None
            
            return (
                obter_nome_pessoa(id_pessoa),
                adversario_mais_vitorias['nome_adversario'] if adversario_mais_vitorias is not None else 'N/A',
                adversario_mais_derrotas['nome_adversario'] if adversario_mais_derrotas is not None else 'N/A'
            )
    finally:
        conexao.close()



def calcular_winrate(id_pessoa, id_edicao=None):
    """
    Calcula o win rate (taxa de vitórias) de uma pessoa na edição fornecida ou na mais recente.
    """
    if id_edicao is None:
        id_edicao = obter_maior_id_edicao()

    query_winrate = """
    SELECT
        SUM(CASE WHEN p.resultado = 'vitória' THEN 1 ELSE 0 END) AS vitorias,
        COUNT(*) AS total_partidas
    FROM
        partida p
    JOIN participante p1 ON p.id_participante1 = p1.id_participante
    WHERE
        p1.id_pessoa = %s
        AND p.id_rodada IN (SELECT id_rodada FROM rodada WHERE id_torneio IN (SELECT id_torneio FROM torneio WHERE id_edicao = %s));
    """

    conexao = conectar_ao_banco()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(query_winrate, (id_pessoa, id_edicao))
            resultado = cursor.fetchone()

            if resultado['total_partidas'] == 0:
                return 0.0  # Caso a pessoa não tenha jogado nenhuma partida, o winrate é 0%

            winrate = (resultado['vitorias'] / resultado['total_partidas']) * 100
            return round(winrate, 2)  # Retorna o winrate com duas casas decimais

    finally:
        conexao.close()


def obter_historico_torneios(id_pessoa, id_edicao=None):
    """
    Retorna o histórico de torneios com o nome do torneio e a posição do participante.
    
    :param id_pessoa: ID da pessoa.
    :param id_edicao: (Opcional) ID da edição. Se não fornecido, será utilizado o maior ID de edição disponível.
    :return: DataFrame com o nome do torneio e a posição do participante.
    """
    # Obtém o maior ID de edição se não for passado
    if not id_edicao:
        id_edicao = obter_maior_id_edicao()

    # Consulta para buscar os torneios e posições
    query = """
    SELECT t.nome_torneio, p.posicao
    FROM participante p
    INNER JOIN torneio t ON p.id_torneio = t.id_torneio
    WHERE p.id_pessoa = %s AND t.id_edicao = %s;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query, (id_pessoa, id_edicao))
            resultados = cursor.fetchall()
            
            # Se não houver registros, retorna um DataFrame vazio
            if not resultados:
                return pd.DataFrame(columns=["Torneio", "Posição"])
            
            # Converte os resultados para um DataFrame
            data = {
                "Torneio": [resultado['nome_torneio'] for resultado in resultados],
                "Posição": [resultado['posicao'] for resultado in resultados]
            }
            df_posicao = pd.DataFrame(data)
            
            return df_posicao
    
    finally:
        conexao.close()

def obter_decks_utilizados(id_pessoa, id_edicao=None):
    """
    Retorna os decks utilizados pela pessoa e quantas vezes foram utilizados em uma determinada edição.
    
    :param id_pessoa: ID da pessoa.
    :param id_edicao: (Opcional) ID da edição. Se não fornecido, será utilizado o maior ID de edição disponível.
    :return: DataFrame com o nome do deck e a quantidade de vezes que foi utilizado.
    """
    # Obtém o maior ID de edição se não for passado
    if not id_edicao:
        id_edicao = obter_maior_id_edicao()

    # Consulta para buscar os decks utilizados e a quantidade de vezes
    query = """
    SELECT d.nome_do_deck, COUNT(*) AS vezes_utilizado
    FROM participante p
    INNER JOIN deck d ON p.id_deck = d.id_deck
    INNER JOIN torneio t ON p.id_torneio = t.id_torneio
    WHERE p.id_pessoa = %s AND t.id_edicao = %s
    GROUP BY d.nome_do_deck;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query, (id_pessoa, id_edicao))
            resultados = cursor.fetchall()
            
            # Se não houver registros, retorna um DataFrame vazio
            if not resultados:
                return pd.DataFrame(columns=["Deck", "Vezes Utilizado"])
            
            # Converte os resultados para um DataFrame
            data = {
                "Deck": [resultado['nome_do_deck'] for resultado in resultados],
                "Vezes Utilizado": [resultado['vezes_utilizado'] for resultado in resultados]
            }
            df_decks = pd.DataFrame(data)
            
            return df_decks
    
    finally:
        conexao.close()



def obter_decks_top(id_edicao=None, top=8):
    """
    Obtém os decks mais utilizados no top (ex: top 2, 4, 6, 8) de uma edição específica. 
    Se nenhum ID de edição for passado, utiliza o maior ID de edição disponível.
    
    :param id_edicao: (Opcional) ID da edição. Se não fornecido, será utilizado o maior ID de edição disponível.
    :param top: Quantidade de jogadores no top a ser considerado (ex: 2, 4, 8). O padrão é 8.
    :return: DataFrame com o nome dos decks e a quantidade de vezes que foram usados no top.
    """
    if id_edicao is None:
        id_edicao = obter_maior_id_edicao()
    
    query = """
    SELECT
        d.nome_do_deck AS Deck,
        COUNT(*) AS Quantidade
    FROM
        participante p
    JOIN deck d ON p.id_deck = d.id_deck
    JOIN torneio t ON p.id_torneio = t.id_torneio
    WHERE
        t.id_edicao = %s
        AND p.posicao <= %s  -- Filtra apenas jogadores que ficaram nas primeiras posições (top)
    GROUP BY
        d.nome_do_deck
    ORDER BY
        Quantidade DESC;
    """
    
    conexao = conectar_ao_banco()
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query, (id_edicao, top))
            resultado = cursor.fetchall()
            df = pd.DataFrame(resultado)
    finally:
        conexao.close()
    
    return df