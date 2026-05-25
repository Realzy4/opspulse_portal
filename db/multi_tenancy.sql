-- Migração de esquema para suportar multi-tenancy no OpsPulse
-- 1. Cria tabela de clientes
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Atualiza power_consumption para associar consumo a um cliente
ALTER TABLE power_consumption
    ADD COLUMN IF NOT EXISTS client_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'power_consumption_client_id_fkey'
    ) THEN
        ALTER TABLE power_consumption
            ADD CONSTRAINT power_consumption_client_id_fkey
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
    END IF;
END$$;

-- 3. Atualiza service_config para associar configurações a um cliente
ALTER TABLE service_config
    ADD COLUMN IF NOT EXISTS client_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'service_config_client_id_fkey'
    ) THEN
        ALTER TABLE service_config
            ADD CONSTRAINT service_config_client_id_fkey
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
    END IF;
END$$;

-- 4. Ajusta a unicidade de service_config para ser por cliente em vez de global
INSERT INTO clients (name)
SELECT 'Cliente Default'
WHERE NOT EXISTS (SELECT 1 FROM clients WHERE name = 'Cliente Default');

UPDATE service_config
SET client_id = (SELECT id FROM clients WHERE name = 'Cliente Default' ORDER BY id LIMIT 1)
WHERE client_id IS NULL;

UPDATE power_consumption
SET client_id = (SELECT id FROM clients WHERE name = 'Cliente Default' ORDER BY id LIMIT 1)
WHERE client_id IS NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'service_config_client_key_pkey'
    ) THEN
        ALTER TABLE service_config
            DROP CONSTRAINT IF EXISTS service_config_pkey;
        ALTER TABLE service_config
            ADD CONSTRAINT service_config_client_key_pkey PRIMARY KEY (client_id, key);
    END IF;
END$$;

INSERT INTO clients (name)
SELECT 'Cliente Alfa'
WHERE NOT EXISTS (SELECT 1 FROM clients WHERE name = 'Cliente Alfa');

INSERT INTO clients (name)
SELECT 'Cliente Beta'
WHERE NOT EXISTS (SELECT 1 FROM clients WHERE name = 'Cliente Beta');
