# 🛵 CourierAI — Agente Inteligente de Optimización de Entregas & Decisión Multiobjetivo en Monterrey

<div align="center">

![CourierAI Banner](https://img.shields.io/badge/Reto%20Infosys-HackMTY%202026-6366F1?style=for-the-badge&logo=rocket&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT-4285F4?style=for-the-badge&logo=google&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-PostgreSQL-FDB515?style=for-the-badge&logo=postgresql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

<p align="center">
  <b>Sistema Inteligente de Enrutamiento, Mitigación de Fricción Vial y Maximización de Márgenes Netos en la Gig-Economy.</b>
</p>

[📌 Descripción](#-descripción-del-proyecto) •
[🏗️ Arquitectura](#%EF%B8%8F-arquitectura-del-sistema) •
[⚡ Instalación](#-guía-de-instalación-y-ejecución) •
[👥 Equipo](#-estructura-de-equipo--roles) •
[📈 Impacto](#-métricas-de-impacto-y-rendimiento)

---

</div>

## 📌 Descripción del Proyecto

**CourierAI** es un sistema autónomo de decisión multiobjetivo diseñado para resolver las ineficiencias de la logística de entregas (*Gig-Economy*) en áreas metropolitanas complejas como Monterrey.

A diferencia de las aplicaciones tradicionales (DiDi Food, Rappi, UberEats) que asignan órdenes a ciegas basándose en algoritmos **FIFO (First-In, First-Out)** y sufren pérdidas económicas masivas por tráfico, **CourierAI** integra un motor de Programación con Restricciones (**Google OR-Tools CP-SAT**) que:

1. **💰 Evalúa márgenes financieros netos** en tiempo real.
2. **🚦 Esquiva embotellamientos viales** desviando repartidores por calles secundarias y libres.
3. **📦 Agrupa pedidos cercanos (Batching/TSP)** para minimizar consumo de gasolina y tiempo.
4. **🤖 Proporciona explicabilidad transparente (XAI)** a través de **Gemini AI (FastAPI)**.

> [!IMPORTANT]
> **Ventaja Competitiva:** CourierAI genera una ventaja neta promedio de **+ MXN a + MXN por turno** por repartidor en comparación con los métodos tradicionales de ruteo.

---

## 🏗️ Arquitectura del Sistema

`mermaid
graph TD
    A[📡 Ingesta & Streaming de Pedidos] -->|OSMnx Grafo Monterrey| B[(TimescaleDB / PostgreSQL)]
    B -->|Streaming de Órdenes| C[🐯 Tiger Data I/O Layer]
    C --> D[⚙️ Motor Matemático Google OR-Tools CP-SAT]
    D -->|Evaluación Financiera & Tráfico| E{Decision Engine}
    E -->|Ruta Voraz / Tráfico| F[🔴 Agente Baseline - Pérdidas]
    E -->|Ruta Óptima / Libre| G[🟢 Agente Smart - Rentable]
    D -->|Trazabilidad| B
    E -->|Logs Financieros| H[🤖 Microservicio FastAPI + Gemini AI]
    H -->|Explicabilidad XAI| I[🖥️ Dashboard Streamlit + Folium]
`

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Propósito |
| :--- | :--- | :--- |
| **IA & Optimización** | Google OR-Tools (CP-SAT) | Resolver modelo multiobjetivo y problema del agente viajero (TSP). |
| **Explicabilidad (XAI)** | FastAPI + Gemini AI | Traducir métricas frías a veredictos entendibles en español. |
| **Base de Datos** | TimescaleDB (PostgreSQL) | Persistencia de eventos con marca de tiempo y auditoría de decisiones. |
| **Grafo Vial** | OSMnx + NetworkX | Modelado de la red de 29,000+ intersecciones de Monterrey. |
| **Visualización UI** | Streamlit + Folium (Leaflet) | Dashboard oscuro de control en tiempo real. |

---

## ⚡ Guía de Instalación y Ejecución

### 1. Clonar e Instalar
`ash
git clone https://github.com/Santiago0Martinez/CourierAI-Monterrey.git
cd CourierAI-Monterrey
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
pip install -r requirements.txt
`

### 2. Configurar Variables de Entorno (.env)
`env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/courier_db
GEMINI_API_KEY=tu_api_key_de_gemini
`

### 3. Ejecutar los Microservicios
`ash
# 1. Microservicio de IA
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Ingesta y Simulador en Vivo
python Backend/Backend_Dev1/main.py

# 3. Interfaz Visual Streamlit
python -m streamlit run Front-End/main.py
`

---

## 👥 Estructura de Equipo & Roles (HackMTY 2026)

* **Dev 1 (Streaming & DB):** Simulación de eventos viales en Monterrey, Grafo OSMnx y persistencia en TimescaleDB.
* **Dev 2 (Motor Matemático):** Optimización multiobjetivo con Google OR-Tools CP-SAT Solver y TSP Batching.
* **Dev 3 (IA & Explicabilidad):** Microservicio FastAPI e integración con Google Gemini AI para justificaciones (XAI).
* **Dev 4 (Frontend & Dashboard):** Dashboard interactivo en Streamlit, mapa dinámico con Folium y métricas KPI.

---

## 📈 Métricas de Impacto y Rendimiento

* 🟢 **Rentabilidad Neta:** Ventaja promedio de **+ MXN** por turno vs. Baseline.
* 🛡️ **Prevención de Pérdidas:** 100% de evasión de pedidos con margen negativo por embotellamiento.
* ⏱️ **Trazabilidad:** Más de **2,400+ decisiones auditadas** en TimescaleDB.

---

## 📜 Licencia

Publicado bajo la Licencia **MIT**. Desarrollado para el **Reto Infosys — HackMTY 2026**.
