from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# --- Configurações da API ---
DB_NAME = 'dados_sensores.db'
TABLE_NAME = 'leituras_sensores'


# --- Rota para a página principal (dashboard) ---
@app.route('/')
def index():
    # ---- > ** Aqui certifique-se de que o template 'index.html' existe na pasta 'templates/' **
    return render_template('index.html')


# --- Rota da API para obter dados dos sensores ---
@app.route('/api/data')
def get_sensor_data():
    if not os.path.exists(DB_NAME):
        return jsonify({"error": f"Banco de dados '{DB_NAME}' não encontrado. Execute 'main.py' primeiro."}), 404

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(
            f"SELECT timestamp, temperatura, umidade, pressao FROM {TABLE_NAME} ORDER BY timestamp ASC", conn)

        # Convertendo DataFrame para um formato JSON amigável para o front-end
        data_for_frontend = {
            "timestamps": df['timestamp'].tolist(),
            "temperaturas": df['temperatura'].tolist(),
            "umidades": df['umidade'].tolist(),
            "pressoes": df['pressao'].tolist(),
        }
        return jsonify(data_for_frontend)
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return jsonify({"error": "Erro ao carregar dados do banco de dados."}), 500
    finally:
        if conn:
            conn.close()


# --- Execução da API ---
if __name__ == '__main__':
    print(f"Verificando se o banco de dados '{DB_NAME}' existe...")
    if not os.path.exists(DB_NAME):
        print(f"ATENÇÃO: O banco de dados '{DB_NAME}' não foi encontrado.")
        print("Por favor, execute 'main.py' primeiro para gerar os dados.")

    print("\nIniciando o servidor Flask...")
    print("Acesse o dashboard em: http://127.0.0.1:5000/")
    app.run(debug=True)  # debug=True permite recarregar o servidor automaticamente em mudanças