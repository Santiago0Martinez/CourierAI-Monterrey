# 🔐 Especificaciones del Sistema de Autenticación y Telemetría del Repartidor (TimescaleDB)

## 📌 Arquitectura del Módulo de Login
El sistema CourierAI actúa como la **Plataforma del Repartidor en Tiempo Real**, permitiendo a los conductores iniciar sesión, seleccionar su vehículo y visualizar las ofertas de pedidos más rentables según el motor de Inteligencia Artificial.

## 🐯 Características Expertas de TimescaleDB & PostgreSQL

### 1. Autenticación y Perfil del Repartidor
- **Tabla:** epartidores
- **Seguridad:** Encriptación de contraseñas con SHA-256.
- **Campos:** id, 
ombre, email, password_hash, ehiculo_tipo ('Moto', 'Auto', 'Bici'), ating, saldo_acumulado, created_at.

### 2. Telemetría de Series Temporales (Hypertable)
- **Tabla:** epartidor_telemetria
- **TimescaleDB Hypertable:** SELECT create_hypertable('repartidor_telemetria', 'timestamp');
- **Campos:** 	imestamp, epartidor_id, latitud, longitud, elocidad_kmh.

### 3. Vistas Agregadas de Rendimiento (Continuous Aggregates)
- Consultas agregadas por bloques de tiempo (	ime_bucket('1 hour', timestamp)) para analizar la velocidad promedio y ahorro de combustible por turno.
