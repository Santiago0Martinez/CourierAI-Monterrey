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
