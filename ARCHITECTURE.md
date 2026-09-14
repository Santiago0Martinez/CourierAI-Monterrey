# 🏛️ Especificaciones de Arquitectura Técnica — CourierAI

## 1. Módulo de Streaming e Ingesta (Dev 1)
- **Grafo de Red Vial:** Carga del modelo en formato GraphML (monterrey_drive.graphml) utilizando OSMnx y NetworkX con 29,054 nodos y 72,910 aristas.
- **Generador de Eventos:** Emisión periódica de solicitudes de entrega con coordenadas geográficas reales dentro del municipio de Monterrey.
- **Base de Datos:** Persistencia en TimescaleDB / PostgreSQL sobre la tabla orders con estados transicionales (PENDIENTE, ACEPTADA, RECHAZADA, COMPLETADA).

## 2. Motor de Optimización Multiobjetivo (Dev 2)
- **CP-SAT Solver:** Formulación de modelo de optimización lineal y de restricciones de Google OR-Tools.
- **Ecuaciones de Márgen:** Evaluación de tarifa base $, consumo estimado de gasolina $, costo por minuto $, y fricción vial  \in [1.0, 2.5]$.
- **Batching:** Agrupamiento de pedidos concurrentes resolviendo el problema del agente viajero (TSP).

## 3. Microservicio de Explicabilidad (Dev 3)
- **FastAPI Endpoint:** Exposición del puerto 8000 para consultas de veredicto.
- **Prompting Estructurado:** Generación de resúmenes amigables en lenguaje natural mediante el modelo Gemini AI de Google.

## 4. Frontend & Live Analytics (Dev 4)
- **Dashboard UI:** Construido sobre Streamlit con soporte de estados de sesión (st.session_state).
- **Renderizado Cartográfico:** Implementación de mapas Folium (Leaflet.js) con mosaico Esri Dark Gray.
