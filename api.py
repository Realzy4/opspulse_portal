from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
# <--- Confirma se é esta a senhasfsf
app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "opspulse" # <--- Confirma se é esta a senha
}

@app.route('/api/preco-kwh', methods=['POST'])
def atualizar_preco():
    dados = request.get_json(force=True, silent=True) or {}
    novo_preco = dados.get('preco') or dados.get('kwhPrice')

    if novo_preco is None:
        return jsonify({"erro": "Dados inválidos"}), 400

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS service_config (
                "key" TEXT PRIMARY KEY,
                "value" TEXT
            );
        """)
        
        cur.execute("""
            INSERT INTO service_config ("key", "value") 
            VALUES ('kwh_price', %s)
            ON CONFLICT ("key") DO UPDATE SET "value" = EXCLUDED.value;
        """, (str(novo_preco),))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"status": "sucesso", "valor": novo_preco}), 200
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)