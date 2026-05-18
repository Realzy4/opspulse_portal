from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DE SEGURANÇA ---
API_TOKEN = "OpsPulse_Super_Secret_2026"

# --- CONFIGURAÇÃO DA BASE DE DATOS DINÂMICA ---
# O os.getenv procura as variáveis que passamos no 'docker run -e'
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "opspulse")
}

def get_db_connection():
    # Esta função agora usa a config dinâmica
    return psycopg2.connect(**DB_CONFIG)

@app.route('/api/preco-kwh', methods=['GET'])
def obter_preco():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT value FROM service_config WHERE key = 'kwh_price';")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return jsonify({"preco": row[0]})
        return jsonify({"preco": "0.15"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/preco-kwh', methods=['POST'])
def atualizar_preco():
    # --- VALIDAÇÃO DO TOKEN ---
    token_recebido = request.headers.get('X-API-KEY')
    if token_recebido != API_TOKEN:
        return jsonify({"status": "erro", "mensagem": "Não autorizado"}), 401

    try:
        dados = request.get_json() or {}
        novo_preco = dados.get('preco') or dados.get('kwhPrice')
        
        if not novo_preco:
            return jsonify({"status": "erro", "mensagem": "Preço não fornecido"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Garante a existência da tabela
        cur.execute("CREATE TABLE IF NOT EXISTS service_config (key TEXT PRIMARY KEY, value TEXT);")
        
        cur.execute(
            "INSERT INTO service_config (key, value) VALUES ('kwh_price', %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;",
            (str(novo_preco),)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"status": "sucesso", "mensagem": f"Preço atualizado para {novo_preco}"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/telemetry', methods=['GET'])
def obter_telemetry():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT value FROM service_config WHERE key = 'kwh_price';")
        row = cur.fetchone()
        kwh_price = float(row[0]) if row and row[0] is not None else 0.15

        cur.execute(
            "SELECT watts, cost_estimated FROM power_consumption "
            "ORDER BY timestamp DESC LIMIT 1;"
        )
        consumo = cur.fetchone()

        current_watts = float(consumo[0]) if consumo and consumo[0] is not None else 0.0
        estimated_cost = float(consumo[1]) if consumo and consumo[1] is not None else 0.0

        return jsonify({
            "status": "success",
            "current_watts": current_watts,
            "estimated_cost": estimated_cost,
            "kwh_price": kwh_price
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # No Docker, o host tem de ser 0.0.0.0 para aceitar ligações externas ao contentor
    app.run(host='0.0.0.0', port=5000)