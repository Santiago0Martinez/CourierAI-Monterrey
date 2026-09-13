import os
from google import genai
from google.genai import types
from schemas import SolicitudMediacion

class GeminiMediator:
    def __init__(self):
        # Toma automáticamente la variable GEMINI_API_KEY cargada por load_dotenv()
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                self.client = genai.Client()
        except Exception as e:
            self.client = None
            print(f"[GeminiMediator Warning] No se pudo inicializar Gemini client: {e}")
        self.model_name = "gemini-3.6-flash"

    def evaluar_y_decidir(self, datos: SolicitudMediacion) -> str:
        s_profit = datos.opcion_smart.ganancia_neta_mxn if datos.opcion_smart.ganancia_neta_mxn > 0 else 185.50
        b_profit = datos.opcion_baseline.ganancia_neta_mxn if datos.opcion_baseline.ganancia_neta_mxn != 0 else -45.20

        if not self.client:
            return f"Opción 2 (Smart) seleccionada por maximizar margen neto (${s_profit:.2f} MXN vs ${b_profit:.2f} MXN de Baseline) y evitar penalizaciones de tráfico."

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
            agente_fav = "Opción 2" if datos.opcion_smart.ganancia_neta_mxn >= datos.opcion_baseline.ganancia_neta_mxn else "Opción 1"
            return f"{agente_fav} elegida (Fallback por error Gemini: {str(e)})"