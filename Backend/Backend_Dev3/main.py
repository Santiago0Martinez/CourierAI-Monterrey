from fastapi import FastAPI
from dotenv import load_dotenv
from schemas import SolicitudMediacion, RespuestaMediacion
from gemini_service import GeminiMediator

# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI(
    title="CourierAI - Módulo de IA Mediador",
    description="Microservicio para la evaluación de rutas y generación de explicabilidad con Gemini API"
)

# Instanciamos nuestra clase mediadora
mediador = GeminiMediator()

@app.get("/")
def home():
    return {"status": "ok", "mensaje": "Servidor de CourierAI Mediador activo"}

@app.post("/evaluar-rutas", response_model=RespuestaMediacion)
async def evaluar_rutas(solicitud: SolicitudMediacion):
    veredicto_texto = mediador.evaluar_y_decidir(solicitud)

    # Extrae el agente ganador de lo que Gemini realmente dijo
    texto_lower = veredicto_texto.lower()
    if "opción 1" in texto_lower or "opcion 1" in texto_lower:
        agente_ganador = solicitud.opcion_baseline.agente
    elif "opción 2" in texto_lower or "opcion 2" in texto_lower:
        agente_ganador = solicitud.opcion_smart.agente
    else:
        # Respaldo por métricas si no se detecta el patrón explícito
        agente_ganador = (
            solicitud.opcion_smart.agente
            if solicitud.opcion_smart.ganancia_neta_mxn >= solicitud.opcion_baseline.ganancia_neta_mxn
            else solicitud.opcion_baseline.agente
        )

    return RespuestaMediacion(
        agente_ganador=agente_ganador,
        explicacion_gemini=veredicto_texto,
    )