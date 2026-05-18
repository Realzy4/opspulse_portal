#!/usr/bin/env bash
set -euo pipefail

# Script para inserir dados dummy na base de dados PostgreSQL usada pela aplicação.
# Usa o container Docker opspulse-db e o utilizador/postgres padrão.

DB_CONTAINER="opspulse-db"
DB_NAME="postgres"
DB_USER="postgres"
SQL_FILE="$(dirname "$0")/../db/dummy_data.sql"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker não está instalado ou não disponível no PATH." >&2
  exit 1
fi

if [ ! -f "$SQL_FILE" ]; then
  echo "ERROR: Ficheiro SQL não encontrado: $SQL_FILE" >&2
  exit 1
fi

echo "A inserir dados dummy na bd no container $DB_CONTAINER..."
cat "$SQL_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"

echo "Dados dummy aplicados com sucesso."
