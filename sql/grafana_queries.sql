-- Grafana PostgreSQL Queries for OpsPulse

-- 1) Último registo de watts por device_name
SELECT device_name, watts, timestamp
FROM (
  SELECT
    device_name,
    watts,
    timestamp,
    ROW_NUMBER() OVER (PARTITION BY device_name ORDER BY timestamp DESC) AS rn
  FROM power_consumption
) AS latest
WHERE rn = 1;

-- 2) Série temporal de watts por device_name
SELECT
  timestamp AS time,
  device_name AS metric,
  watts AS value
FROM power_consumption
WHERE $__timeFilter(timestamp)
ORDER BY timestamp ASC;

-- 3) Total gasto no intervalo de tempo
SELECT
  SUM(cost_estimated) AS "Total Gasto"
FROM power_consumption
WHERE $__timeFilter(timestamp);

-- 4) Distribuição de gasto por divisão (exclui Main Meter)
SELECT
  device_name,
  SUM(cost_estimated) AS value
FROM power_consumption
WHERE $__timeFilter(timestamp)
  AND device_name <> 'Main Meter'
GROUP BY device_name
ORDER BY value DESC;

-- 5) Consumo médio e pico máximo por device_name
SELECT
  device_name,
  AVG(watts) AS "Consumo Médio",
  MAX(watts) AS "Pico Máximo"
FROM power_consumption
WHERE $__timeFilter(timestamp)
GROUP BY device_name
ORDER BY device_name;