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

