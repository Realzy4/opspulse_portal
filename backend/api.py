from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from functools import wraps

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DE SEGURANÇA ---
API_TOKEN = os.getenv("API_TOKEN", "OpsPulse_Super_Secret_2026")
DEFAULT_CLIENT_NAME = os.getenv("DEFAULT_CLIENT_NAME", "Cliente Default")


def require_api_key(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_TOKEN:
            return jsonify({"status": "error", "message": "Não autorizado"}), 401
        return view_func(*args, **kwargs)
    return wrapped

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


def get_default_client_id(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM clients WHERE name = %s LIMIT 1;", (DEFAULT_CLIENT_NAME,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO clients (name) VALUES (%s) RETURNING id;", (DEFAULT_CLIENT_NAME,))
        return cur.fetchone()[0]


@app.route('/api/clients', methods=['GET'])
def listar_clients():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, name FROM clients ORDER BY name ASC;")
        rows = cur.fetchall()
        
        clients = [{"id": row[0], "name": row[1]} for row in rows]
        
        return jsonify(clients)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


@app.route('/api/preco-kwh', methods=['GET'])
def obter_preco():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Obter client_id do query parameter, padrão para 1
        client_id_param = request.args.get('client_id', '1', type=str)
        try:
            client_id = int(client_id_param)
        except (ValueError, TypeError):
            client_id = 1
        
        # Mapear client_id=1 e client_id=2 para IDs reais de clientes
        if client_id == 1:
            # Buscar o primeiro cliente (Default ou mais antigo)
            cur.execute("SELECT id FROM clients ORDER BY id LIMIT 1;")
            row = cur.fetchone()
            actual_client_id = row[0] if row else 1
        elif client_id == 2:
            # Buscar Cliente Beta
            cur.execute("SELECT id FROM clients WHERE name = 'Cliente Beta' LIMIT 1;")
            row = cur.fetchone()
            actual_client_id = row[0] if row else 3  # fallback
        else:
            # Usar diretamente se for um ID de BD válido
            actual_client_id = client_id
        
        cur.execute(
            "SELECT value FROM service_config WHERE key = 'kwh_price' AND client_id = %s;",
            (actual_client_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return jsonify({"preco": row[0]})
        return jsonify({"preco": "0.15"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/preco-kwh', methods=['POST'])
@require_api_key
def atualizar_preco():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Obter client_id do query parameter, padrão para 1
        client_id_param = request.args.get('client_id', '1', type=str)
        try:
            client_id = int(client_id_param)
        except (ValueError, TypeError):
            client_id = 1
        
        # Mapear client_id=1 e client_id=2 para IDs reais de clientes
        if client_id == 1:
            # Buscar o primeiro cliente (Default ou mais antigo)
            cur.execute("SELECT id FROM clients ORDER BY id LIMIT 1;")
            row = cur.fetchone()
            actual_client_id = row[0] if row else 1
        elif client_id == 2:
            # Buscar Cliente Beta
            cur.execute("SELECT id FROM clients WHERE name = 'Cliente Beta' LIMIT 1;")
            row = cur.fetchone()
            actual_client_id = row[0] if row else 3  # fallback
        else:
            # Usar diretamente se for um ID de BD válido
            actual_client_id = client_id
        
        dados = request.get_json() or {}
        novo_preco = dados.get('preco') or dados.get('kwhPrice')
        
        if not novo_preco:
            return jsonify({"status": "erro", "mensagem": "Preço não fornecido"}), 400

        # Garante a existência da tabela
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS service_config (
                client_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                PRIMARY KEY (client_id, key),
                CONSTRAINT service_config_client_id_fkey FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            );
            """
        )
        
        cur.execute(
            "INSERT INTO service_config (client_id, key, value) VALUES (%s, 'kwh_price', %s) "
            "ON CONFLICT (client_id, key) DO UPDATE SET value = EXCLUDED.value;",
            (actual_client_id, str(novo_preco))
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
        
        # Obter client_id do query parameter, padrão para 1 (Cliente Default)
        client_id_param = request.args.get('client_id', '1', type=str)
        try:
            client_id = int(client_id_param)
        except (ValueError, TypeError):
            client_id = 1
        
        # Mapear client_id=1 e client_id=2 para IDs reais de clientes
        # client_id=1 pode ser qualquer um dos primeiros clientes (Default, Alfa, etc.)
        # client_id=2 é Cliente Beta
        # Se for um valor direto de BD (ex: 36-40), usar diretamente
        if client_id == 1:
            # Buscar o primeiro cliente (Default ou mais antigo)
            cur.execute("SELECT id FROM clients ORDER BY id LIMIT 1;")
            row = cur.fetchone()
            actual_client_id = row[0] if row else 1
        elif client_id == 2:
            # Buscar Cliente Beta
            cur.execute("SELECT id FROM clients WHERE name = 'Cliente Beta' LIMIT 1;")
            row = cur.fetchone()
            actual_client_id = row[0] if row else 3  # fallback
        else:
            # Usar diretamente se for um ID de BD válido
            actual_client_id = client_id

        cur.execute(
            "SELECT value FROM service_config WHERE key = 'kwh_price' AND client_id = %s;",
            (actual_client_id,),
        )
        row = cur.fetchone()
        kwh_price = float(row[0]) if row and row[0] is not None else 0.15

        cur.execute(
            "SELECT watts, cost_estimated FROM power_consumption "
            "WHERE client_id = %s "
            "ORDER BY timestamp DESC LIMIT 1;",
            (actual_client_id,),
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