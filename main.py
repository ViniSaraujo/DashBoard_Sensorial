import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- Configurações ---
DB_NAME = 'dados_sensores.db'
TABLE_NAME = 'leituras_sensores'
NUM_DIAS_SIMULADOS = 14  # --------Simular dados de 14 dias para ter mais volume
LEITURAS_POR_HORA = 4  # 4 ----leituras por hora (a cada 15 minutos)


# --- Função para Gerar Dados Simulados ---
def gerar_dados_simulados(num_dias, leituras_por_hora):
    print(f"Gerando dados simulados para {num_dias} dias...")
    data_inicio = datetime.now() - timedelta(days=num_dias)
    intervalo_minutos = 60 / leituras_por_hora

    dados = []
    for i in range(num_dias * 24 * leituras_por_hora):
        timestamp = data_inicio + timedelta(minutes=i * intervalo_minutos)

        # Simular temperatura (entre 20 e 30 graus, com ruído e variação diária, próximo ao que vivemos na realidade)
        temperatura = 25 + 5 * np.sin(i / (leituras_por_hora * 12)) + np.random.normal(0, 0.5)

        # Simular umidade (entre 40 e 70%, com ruído)
        umidade = 55 + 15 * np.cos(i / (leituras_por_hora * 8)) + np.random.normal(0, 1.5)

        # Simular pressão (entre 1000 e 1020 hPa - como a pressão do ar, com ruído e tendência suave)
        pressao = 1010 + 5 * np.sin(i / (leituras_por_hora * 24 * 2)) + np.random.normal(0, 0.2)

        dados.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Formato string para SQLite
            'temperatura': round(temperatura, 2),
            'umidade': round(umidade, 2),
            'pressao': round(pressao, 2)
        })
    print(f"Total de {len(dados)} leituras geradas.")
    return pd.DataFrame(dados)


# --- Função para Criar Tabela no SQLite ---
def criar_tabela(conn):
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperatura REAL,
            umidade REAL,
            pressao REAL
        )
    ''')
    conn.commit()
    print(f"Tabela '{TABLE_NAME}' verificada/criada com sucesso.")


# --- Função para Inserir Dados no SQLite ---
def inserir_dados(conn, df):
    print(f"Inserindo {len(df)} registros na tabela '{TABLE_NAME}'...")
    # Usamos if_exists='replace' para sempre recriar a tabela e os dados
    # Se quiser adicionar dados a uma tabela existente, use 'append'
    df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
    conn.commit()
    print("Dados inseridos com sucesso!")


# --- Execução Principal ---
if __name__ == "__main__":
    # Remove o banco de dados existente para começar do zero toda vez (útil para testes)
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Banco de dados '{DB_NAME}' existente removido para recriação.")

    # Conectar ao banco de dados SQLite (ele será criado se não existir)
    conn = sqlite3.connect(DB_NAME)
    print(f"Conectado ao banco de dados: {DB_NAME}")

    try:
        # Gerar dados
        df_sensores = gerar_dados_simulados(NUM_DIAS_SIMULADOS, LEITURAS_POR_HORA)

        # Criar tabela e inserir dados
        criar_tabela(conn)
        inserir_dados(conn, df_sensores)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Fechar a conexão com o banco de dados
        conn.close()
        print("Conexão com o banco de dados fechada.")
        print(f"\nO arquivo do banco de dados '{DB_NAME}' foi criado/atualizado em: {os.path.abspath(DB_NAME)}")

        print("Agora você pode rodar 'api.py' para iniciar o servidor web.")
