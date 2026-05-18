-- 1. Limpar tabelas antigas (se existirem)
DROP TABLE IF EXISTS service_config;
DROP TABLE IF EXISTS power_consumption;

-- 2. Tabela de Configurações (Preço kWh)
CREATE TABLE service_config (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Inserir o teu preço padrão
INSERT INTO service_config (key, value) VALUES ('kwh_price', '0.15');

-- 3. Tabela de Consumos (Para o Grafana)
CREATE TABLE power_consumption (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    device_name TEXT,
    watts FLOAT,
    cost_estimated FLOAT
);

-- 4. Dados Dummy para teste (últimas 2 horas)
INSERT INTO power_consumption (timestamp, device_name, watts, cost_estimated) VALUES 
(NOW() - INTERVAL '2 hours', 'Main Meter', 450.5, 0.06),
(NOW() - INTERVAL '1 hour', 'Main Meter', 520.0, 0.08),
(NOW() - INTERVAL '30 minutes', 'Main Meter', 380.2, 0.05),
(NOW(), 'Main Meter', 410.0, 0.06);

