# OpsPulse Portal

Estrutura do projecto e instruções para arrancar o ambiente.

## Estrutura de ficheiros

- `backend/`
  - `api.py` - API Flask principal
  - `data_generator.py` - serviço de geração de dados random em background
  - `requirements.txt` - dependências Python
  - `Dockerfile` - imagem Docker para backend/API

- `frontend/`
  - `index.html` - dashboard principal
  - `settings.html` - página de configurações
  - `style.css` - estilos do frontend
  - `nginx.conf` - configuração do proxy Nginx
  - `Dockerfile.portal` - imagem Docker para o portal web

- `db/`
  - `rebuild_db.sql` - script de criação/reset da base de dados
  - `dummy_data.sql` - dados dummy de exemplo para `power_consumption`

- `sql/`
  - `grafana_queries.sql` - queries SQL para Grafana/PostgreSQL

- `scripts/`
  - `insert_dummy_data.sh` - script para inserir dados dummy no PostgreSQL

- `docker-compose.yml` - orquestração dos serviços Docker

## Serviços

- `db` - PostgreSQL
- `api` - Flask API do OpsPulse
- `portal` - frontend Nginx
- `grafana` - Grafana para dashboards
- `data-generator` - serviço de inserção contínua de dados

## Comandos principais

Abrir o projecto:

```bash
cd /home/opspulse/opspulse_portal
```

Arrancar tudo:

```bash
docker-compose up -d
```

Ver logs dos serviços:

```bash
docker-compose logs -f
```

Recriar um serviço específico:

```bash
docker-compose up -d --force-recreate portal
```

Inserir dados dummy na base de dados:

```bash
./scripts/insert_dummy_data.sh
```

## Notes

- O portal web está exposto em `http://127.0.0.1:8081`
- O Grafana está exposto em `http://127.0.0.1:3000`
- A API Flask responde em `http://127.0.0.1:8081/api/...` através do proxy Nginx
- O serviço `data-generator` insere dados na tabela `power_consumption` a cada 10 segundos

## Actualizações recentes

- Reorganizei a pasta em `backend/`, `frontend/`, `db/`, `sql/` e `scripts/`
- Atualizei o `docker-compose.yml` para usar os novos contextos de build
- Ajustei `insert_dummy_data.sh` para apontar para `db/dummy_data.sql`
