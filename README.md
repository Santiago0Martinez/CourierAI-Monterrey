# 🛵 CourierAI — Agente Inteligente de Optimización de Entregas y Decisión Multiobjetivo en Monterrey

> **HackMTY 2026 — Reto Infosys**  
> *Sistema Inteligente de Enrutamiento, Mitigación de Fricción Vial y Maximización de Márgenes Netos en la Gig-Economy.*

---

## 📌 Descripción del Proyecto

**CourierAI** es un sistema autónomo de decisión multiobjetivo diseñado para resolver las ineficiencias de la logística de entregas (*Gig-Economy*) en áreas metropolitanas complejas como Monterrey.

A diferencia de las aplicaciones tradicionales (DiDi Food, Rappi, UberEats) que asignan órdenes a ciegas basándose en algoritmos **FIFO (First-In, First-Out)** y sufren pérdidas económicas masivas por tráfico, **CourierAI** integra un motor de Programación con Restricciones (**Google OR-Tools CP-SAT**) que:

1. **Evalúa márgenes financieros netos** en tiempo real.
2. **Esquiva embotellamientos viales** desviando repartidores por calles secundarias y libres.
3. **Agrupa pedidos cercanos (Batching/TSP)** para minimizar consumo de gasolina y tiempo.
4. **Proporciona explicabilidad transparente (XAI)** a través de **Gemini AI (FastAPI)**.

---

## 🛠️ Stack Tecnológico

* **Backend & IA:** Python 3.10+, Google OR-Tools (CP-SAT Solver), FastAPI, NetworkX, OSMnx.
* **Base de Datos:** TimescaleDB / PostgreSQL (Series temporales y trazabilidad de eventos).
* **LLM & Explicabilidad:** Google Gemini AI Microservice.
* **Frontend & Mapas:** Streamlit, Folium (Leaflet.js), Esri Dark Gray Canvas.



---

## ⚡ Guía de Instalación y Ejecución

### 1. Requisitos Previos
* Python 3.10 o superior.
* Instancia activa de PostgreSQL / TimescaleDB.

### 2. Instalación de Dependencias
`ash
git clone https://github.com/Santiago0Martinez/CourierAI-Monterrey.git
cd CourierAI-Monterrey
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
`

### 3. Configuración de Variables de Entorno (.env)
Crea un archivo .env en la raíz con la siguiente estructura:
`env
DATABASE_URL=postgresql://usuario:password@localhost:5432/courier_db
GEMINI_API_KEY=tu_api_key_de_gemini
`

### 4. Ejecución del Sistema
`ash
# 1. Iniciar Microservicio de IA (FastAPI)
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Iniciar Simulador de Entregas (Dev 1)
python Backend/Backend_Dev1/main.py

# 3. Iniciar Dashboard Interactivo (Frontend)
python -m streamlit run Front-End/main.py
`


---

## 👥 Estructura de Equipo & Roles (HackMTY 2026)

| Rol | Componente | Responsable / Descripción |
| :--- | :--- | :--- |
| **Dev 1** | **Ingesta & Streaming** | Simulación de eventos viales en Monterrey, Grafo OSMnx y persistencia en TimescaleDB. |
| **Dev 2** | **Motor Matemático** | Optimización multiobjetivo con Google OR-Tools CP-SAT Solver y TSP Batching. |
| **Dev 3** | **IA & Explicabilidad** | Microservicio FastAPI e integración con Google Gemini AI para justificaciones (XAI). |
| **Dev 4** | **Frontend & Dashboard** | Dashboard interactivo en Streamlit, mapa dinámico con Folium y métricas KPI. |

---

## 📈 Métricas de Impacto y Rendimiento

En pruebas de estrés simuladas con más de **2,400 decisiones auditadas en TimescaleDB**:

* 🟢 **Incremento en Rentabilidad Neta:** Ventaja promedio de **+ MXN a + MXN** por turno de repartidor en comparación con sistemas FIFO tradicionales.
* 🛡️ **Mitigación de Riesgo por Tráfico:** 100% de evasión de pedidos con margen negativo severo originado por embotellamientos viales o bloqueos climáticos.
* ⏱️ **Trazabilidad:** Tiempo medio de respuesta y decisión < 50ms por orden.

---

## 📜 Licencia

Desarrollado para el **Reto Infosys — HackMTY 2026**.
