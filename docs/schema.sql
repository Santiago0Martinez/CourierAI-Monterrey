-- CourierAI TimescaleDB Schema
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    origen_lat DOUBLE PRECISION NOT NULL,
    origen_lon DOUBLE PRECISION NOT NULL,
    destino_lat DOUBLE PRECISION NOT NULL,
    destino_lon DOUBLE PRECISION NOT NULL,
    tarifa_base DOUBLE PRECISION NOT NULL,
    tiempo_limite INT NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDIENTE',
    assigned_agent VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS decisiones (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    agente VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    razon TEXT,
    margen_neto DOUBLE PRECISION,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
