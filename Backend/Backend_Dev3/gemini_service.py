import os
from google import genai
from google.genai import types
from schemas import SolicitudMediacion

class GeminiMediator:
    def __init__(self):
        # Toma automáticamente la variable GEMINI_API_KEY cargada por load_dotenv()
        self.client = genai.Client()
        self.model_name = "gemini-3.6-flash"

    def evaluar_y_decidir(self, datos: SolicitudMediacion) -> str:
        prompt = f"""
        Eres 'CourierAI'. Compara 2 rutas para un repartidor en Monterrey (Evento: {datos.evento_contexto}):
        
        Opción 1 (Baseline): {datos.opcion_baseline.tiempo_est_min} min, ${datos.opcion_baseline.ganancia_neta_mxn} MXN. Arg: {datos.opcion_baseline.argumento_agente}
        Opción 2 (Smart): {datos.opcion_smart.tiempo_est_min} min, ${datos.opcion_smart.ganancia_neta_mxn} MXN. Arg: {datos.opcion_smart.argumento_agente}

        REGLAS:
        1. Elige objetivamente la mejor opción (Opción 1 u Opción 2) según ganancia, tiempo y riesgo.
        2. Empieza tu respuesta EXACTAMENTE escribiendo 'Opción 1' u 'Opción 2'.
        3. Da la justificación en máximo 2 oraciones directas.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,        # Respuesta determinista e instantánea
                    max_output_tokens=150   # Corta la generación para responder rapidísimo
                )
            )
            return response.text
        except Exception as e:
            return f"Error al generar decisión con Gemini: {str(e)}"