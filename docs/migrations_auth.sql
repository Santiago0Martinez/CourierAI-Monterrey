-- Migración para Repartidores y Telemetría TimescaleDB

CREATE TABLE IF NOT EXISTS repartidores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    vehiculo_tipo VARCHAR(20) DEFAULT 'Moto',
    rating NUMERIC(3,2) DEFAULT 4.90,
    saldo_acumulado DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Repartidor Demo por defecto
INSERT INTO repartidores (nombre, email, password_hash, vehiculo_tipo, rating, saldo_acumulado)
VALUES ('Santiago Martínez (Driver #1)', 'driver@courierai.com', '54a7c29377484df6147eaed1f33eeffc6b541bb87265eb450bbca7ecb38b3687', 'Moto', 4.95, 0.0)
ON CONFLICT (email) DO NOTHING;

-- Telemetría GPS con TimescaleDB Hypertable
CREATE TABLE IF NOT EXISTS repartidor_telemetria (
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    repartidor_id INT NOT NULL,
    latitud DOUBLE PRECISION NOT NULL,
    longitud DOUBLE PRECISION NOT NULL,
    velocidad_kmh DOUBLE PRECISION DEFAULT 35.0
);

-- Convertir a TimescaleDB Hypertable si la extension esta instalada
DO \$\$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('repartidor_telemetria', 'timestamp', if_not_exists => TRUE);
    END IF;
END \$\$;
