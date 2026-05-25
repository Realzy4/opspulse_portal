-- Cria a tabela se não existir e insere dados dummy para o Grafana.
CREATE TABLE IF NOT EXISTS power_consumption (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    device_name TEXT,
    watts FLOAT,
    cost_estimated FLOAT,
    client_id INTEGER
);

INSERT INTO power_consumption (timestamp, device_name, watts, cost_estimated, client_id) VALUES
(NOW() - INTERVAL '2 hours', 'Main Meter', 450.5, 0.06, (SELECT id FROM clients WHERE name = 'Cliente Default' LIMIT 1)),
(NOW() - INTERVAL '1 hour', 'Main Meter', 520.0, 0.08, (SELECT id FROM clients WHERE name = 'Cliente Default' LIMIT 1)),
(NOW() - INTERVAL '30 minutes', 'Main Meter', 380.2, 0.05, (SELECT id FROM clients WHERE name = 'Cliente Default' LIMIT 1)),
(NOW() - INTERVAL '15 minutes', 'Main Meter', 430.4, 0.06, (SELECT id FROM clients WHERE name = 'Cliente Default' LIMIT 1)),
(NOW(), 'Main Meter', 410.0, 0.06, (SELECT id FROM clients WHERE name = 'Cliente Default' LIMIT 1));
