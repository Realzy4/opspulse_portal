# 1. Usar uma imagem leve de Python
FROM python:3.10-slim

# 2. Definir a pasta de trabalho dentro do contentor
WORKDIR /app

# 3. Instalar dependências do sistema para o Psycopg2 (Postgres)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiar os ficheiros de requisitos e instalar
# (Vamos criar o requirements.txt já a seguir)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar o resto do código
COPY . .

# 6. Expor a porta que a API usa
EXPOSE 5000

# 7. Comando para arrancar a API
CMD ["python", "api.py"]