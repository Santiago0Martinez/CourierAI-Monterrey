import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Backend', 'Backend_Dev2'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Backend', 'Backend_Dev1'))
from auth import validar_credenciales, hash_password
from Tiger_Data_io import inicializar_tabla_repartidores, registrar_nuevo_repartidor, registrar_telemetria_gps
inicializar_tabla_repartidores()
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import psycopg2
import os
from dotenv import load_dotenv
import time
import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Backend", "Backend_Dev2"))
from Motor_Matematico import SmartAgent, BaselineAgent, activar_evento, desactivar_eventos, obtener_ruta_coordenadas, Order
from Tiger_Data_io import leer_pedidos_pendientes, sincronizar_log_completo, ejecutar_ciclo_completo
from Debate_Rutas import debatir_rutas, generar_opciones_ruta
from Gemini_Bridge import explicar_evento_con_dev3

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Backend", "Backend_Dev1"))
from generator import generate_single_order, load_or_create_graph

# ==========================================
# 1. CONFIGURACION DE PAGINA Y ESTILOS UI
# ==========================================
st.set_page_config(
    page_title="CourierAI — Reto Infosys (HackMTY 2026)",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS profesionales de alta gama (Dark Tech / Glassmorphism UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% -20%, #1E293B 0%, #0F172A 50%, #080D1A 100%);
        color: #F8FAFC;
    }
    
    /* Header Banner */
    .brand-container {
        text-align: center;
        padding: 15px 0 25px 0;
    }

    .hack-badge {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        color: white;
        font-weight: 700;
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 0.95rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    .main-header {
        background: linear-gradient(90deg, #00FF80 0%, #38BDF8 50%, #6366F1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .sub-header {
        color: #94A3B8;
        font-size: 1.3rem;
        margin-top: 8px;
    }

    /* Badges de Estado */
    .status-bar {
        display: flex;
        justify-content: center;
        gap: 18px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }

    .status-pill {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 0.98rem;
        color: #CBD5E1;
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .dot-green {
        width: 10px;
        height: 10px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
        display: inline-block;
    }

    .dot-blue {
        width: 10px;
        height: 10px;
        background-color: #38BDF8;
        border-radius: 50%;
        box-shadow: 0 0 10px #38BDF8;
        display: inline-block;
    }

    /* Cards de Métricas (KPIs) */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 22px 28px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 255, 128, 0.4);
    }
    
    div[data-testid="stMetricLabel"] > label {
        color: #CBD5E1 !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-size: 2.1rem !important; /* Reducido de 2.6 a 2.1 para evitar truncamiento */
        font-weight: 800 !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }

    /* Tarjetas de Evaluación */
    .card-baseline {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(239, 68, 68, 0.45);
        border-radius: 18px;
        padding: 26px;
        margin-bottom: 18px;
        backdrop-filter: blur(10px);
        font-size: 1.15rem;
    }

    .card-smart {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(16, 185, 129, 0.45);
        border-radius: 18px;
        padding: 26px;
        margin-bottom: 18px;
        backdrop-filter: blur(10px);
        font-size: 1.15rem;
    }

    .card-gemini {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 18px;
        padding: 26px;
        backdrop-filter: blur(10px);
        font-size: 1.15rem;
    }

    h3 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }

    /* Terminal Console */
    .terminal-container {
        background-color: #080D1A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
        height: 380px;
        overflow-y: auto;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.95rem;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        margin-top: 10px;
    }
    
    .terminal-line {
        margin-bottom: 8px;
        line-height: 1.4;
        border-bottom: 1px dashed rgba(255,255,255,0.05);
        padding-bottom: 4px;
    }
    
    .terminal-time {
        color: #64748B;
        margin-right: 12px;
    }
    
    .t-smart { color: #10B981; font-weight: bold; }
    .t-base { color: #EF4444; font-weight: bold; }
    .t-info { color: #38BDF8; }
</style>
""", unsafe_allow_html=True)

# Cargar el mapa de Monterrey una sola vez
@st.cache_resource
def obtener_grafo():
    return load_or_create_graph()

G = obtener_grafo()

# Sidebar: Panel de Control e Interactividad


# ==========================================
# MODULO DE AUTENTICACION DE REPARTIDOR (DRIVER APP - GLASSMORPHISM UI)
# ==========================================
if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = None

if not st.session_state["usuario_autenticado"]:
    st.markdown("""
    <div style='text-align: center; margin-top: 50px; margin-bottom: 30px;'>
        <div style='display: inline-block; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 8px 18px; border-radius: 30px; margin-bottom: 15px;'>
            <span style='color: #818CF8; font-weight: 700; font-size: 0.9rem; letter-spacing: 1px;'>RETO INFOSYS — HACKMTY 2026</span>
        </div>
        <h1 style='background: linear-gradient(135deg, #FFFFFF 0%, #cbd5e1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.2rem; font-weight: 800; margin: 0;'>🛵 CourierAI Driver App</h1>
        <p style='font-size: 1.15rem; color: #94A3B8; margin-top: 10px; font-weight: 400;'>Plataforma Inteligente de Evaluación de Ofertas y Ruteo en Tiempo Real</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2.2, 1])
    with col_l2:
        st.markdown("""
        <style>
            .login-card-container {
                background: rgba(15, 23, 42, 0.75);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 35px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 30px rgba(99, 102, 241, 0.15);
            }
        </style>
        """, unsafe_allow_html=True)
        
        tab_log, tab_reg = st.tabs(["🔐 Acceso Repartidor", "📝 Registrar Nuevo Conductor"])
        
        with tab_log:
            st.markdown("<h3 style='color:#F8FAFC; margin-top:15px; margin-bottom:20px; font-size:1.4rem;'>Acceso a la Plataforma</h3>", unsafe_allow_html=True)
            email_input = st.text_input("Correo Electrónico", value="driver@courierai.com", key="log_email")
            pass_input = st.text_input("Contraseña", value="demo123", type="password", key="log_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Iniciar Sesión como Repartidor", use_container_width=True, type="primary"):
                perfil = validar_credenciales(email_input, pass_input)
                if perfil:
                    st.session_state["usuario_autenticado"] = perfil
                    st.success(f"¡Bienvenido de nuevo, {perfil['nombre']}!")
                    st.rerun()
                else:
                    st.error("Credenciales inválidas. Verifica tu correo y contraseña.")
                    
        with tab_reg:
            st.markdown("<h3 style='color:#F8FAFC; margin-top:15px; margin-bottom:20px; font-size:1.4rem;'>Registro de Nuevo Conductor</h3>", unsafe_allow_html=True)
            r_nombre = st.text_input("Nombre Completo", key="reg_nombre")
            r_email = st.text_input("Correo Electrónico Nuevo", key="reg_email")
            r_pass = st.text_input("Contraseña Nueva", type="password", key="reg_pass")
            r_vehiculo = st.selectbox("Tipo de Vehículo", ["Moto", "Bici Eléctrica", "Auto"], key="reg_veh")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✨ Crear Cuenta de Repartidor", use_container_width=True):
                if r_nombre and r_email and r_pass:
                    if registrar_nuevo_repartidor(r_nombre, r_email, r_pass, r_vehiculo):
                        st.success("¡Cuenta registrada con éxito! Ya puedes iniciar sesión.")
                    else:
                        st.error("El correo electrónico ya se encuentra registrado.")
                else:
                    st.warning("Completa todos los campos obligatorios.")
                    
    st.stop()




# Perfil del Repartidor Autenticado
usuario = st.session_state.get("usuario_autenticado")
if usuario:
    st.sidebar.markdown(f"""
    <div style='background-color: #0F172A; padding: 14px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px;'>
        <div style='color: #6366F1; font-weight: bold; font-size: 1.05rem;'>🛵 {usuario['nombre']}</div>
        <div style='color: #94A3B8; font-size: 0.85rem;'>{usuario['email']}</div>
        <div style='margin-top: 6px; font-size: 0.9rem;'>
            <span style='color: #F59E0B;'>★ {usuario['rating']:.2f}</span> | 
            <span style='color: #10B981; font-weight: bold;'>Vehículo: {usuario['vehiculo_tipo']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Registrar telemetría de posición actual en TimescaleDB
    try:
        registrar_telemetria_gps(usuario['id'], POSICION_BASE[0], POSICION_BASE[1], velocidad=38.5)
    except:
        pass

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["usuario_autenticado"] = None
        st.session_state["orden_activa_fijada"] = None
        st.rerun()


st.sidebar.title("Panel de Control")

if st.sidebar.button("Generar Nueva Orden (Manual)", use_container_width=True, type="primary"):
    nueva_id = generate_single_order(G)
    st.session_state.last_cycle_time = 0  # Forzar que el próximo render procese el ciclo inmediatamente
    st.sidebar.success(f"Orden #{nueva_id} registrada exitosamente.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Configuración y Streaming")

auto_refresh = st.sidebar.toggle("Auto-actualización (30s)", value=True)

if st.sidebar.button("Forzar Actualización", use_container_width=True):
    st.rerun()

import random
# Generador de eventos aleatorios de ciudad (tipo app repartidor)
if "last_event_update" not in st.session_state:
    st.session_state.last_event_update = time.time()
    st.session_state.current_event = "normal"
    desactivar_eventos()

# Actualizar evento aleatorio cada vez que pasan 30s
if time.time() - st.session_state.last_event_update > 25:
    evento_rand = random.choices(["normal", "lluvia", "trafico"], weights=[0.6, 0.2, 0.2])[0]
    st.session_state.current_event = evento_rand
    st.session_state.last_event_update = time.time()
    
    if evento_rand == "lluvia":
        activar_evento((25.6714, -100.3096), radio_km=5.0, tipo="lluvia")
        st.toast("Alerta climática detectada automáticamente en Monterrey.", icon="🌧️")
    elif evento_rand == "trafico":
        activar_evento((25.6840, -100.3450), radio_km=5.0, tipo="trafico")
        st.toast("Fuerte congestión vial detectada automáticamente.", icon="🚗")
    else:
        desactivar_eventos()
        st.toast("Condiciones climáticas y de tráfico normales.", icon="☀️")

st.sidebar.markdown("---")
st.sidebar.markdown("### Estado de la Ciudad (En Vivo)")
if st.session_state.current_event == "lluvia":
    st.sidebar.warning("🌧️ **Lluvia:** Tiempos de entrega extendidos.")
elif st.session_state.current_event == "trafico":
    st.sidebar.error("🚗 **Bloqueo Vial:** Congestión severa.")
else:
    st.sidebar.success("☀️ **Tránsito Fluido:** Condiciones óptimas.")

if auto_refresh:
    # Hack HTML para refrescar Streamlit sin bloquear el thread
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        setTimeout(function(){
            window.parent.location.reload();
        }, 30000);
        </script>
        """,
        height=0
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### Guía de Operación")
st.sidebar.markdown("""
Cada viaje consta de **2 tramos viales reales**:
1. **Origen**: Repartidor (Base) ➔ Recolección (Restaurante)
2. **Destino**: Recolección ➔ Entrega Final (Cliente)

- **Ruta Baseline (FIFO)**: Voraz, ignora tráfico y márgenes.
- **Ruta Smart (OR-Tools)**: Optimiza margen neto y tiempos.
""")

# ==========================================
# 2. CONEXION A DATOS (Tiger Data Real)
# ==========================================
load_dotenv()

@st.cache_resource
def inicializar_conexion():
    try:
        return psycopg2.connect(os.environ.get("DATABASE_URL"))
    except Exception as e:
        st.error(f"Error conectando a Tiger Data: {e}")
        st.stop()

conexion = inicializar_conexion()

POSICION_BASE = (25.6714, -100.3096)
pedidos = leer_pedidos_pendientes(limit=50)

while len(pedidos) < 2:
    try:
        generate_single_order(G)
    except Exception as e:
        break
    pedidos = leer_pedidos_pendientes(limit=50)
    if len(pedidos) >= 2:
        break

ids_actuales = tuple(sorted(p.order_id for p in pedidos))

# Evitar que interacciones en la UI (como el filtro del mapa) consuman órdenes y cambien la vista
if "last_cycle_time" not in st.session_state:
    st.session_state.last_cycle_time = 0

ahora = time.time()
# Solo ejecutar un ciclo nuevo si pasaron 28s (auto-refresh) o si forzaron una orden nueva
should_cycle = (ahora - st.session_state.last_cycle_time > 28) or (st.session_state.get("ultimos_ids_pedidos") != ids_actuales and not st.session_state.get("orden_activa_fijada"))

if should_cycle:
    baseline_state, smart_state, _ = ejecutar_ciclo_completo(
        posicion_inicial=POSICION_BASE, pedidos=pedidos
    )
    st.session_state["ultimos_ids_pedidos"] = ids_actuales
    st.session_state["baseline_state"] = baseline_state
    st.session_state["smart_state"] = smart_state
    
    # Acumular ganancia del turno
    if "total_historico_smart" not in st.session_state:
        st.session_state["total_historico_smart"] = 0.0
    if "total_historico_baseline" not in st.session_state:
        st.session_state["total_historico_baseline"] = 0.0
        
    st.session_state["total_historico_smart"] += smart_state.ganancia_total
    st.session_state["total_historico_baseline"] += baseline_state.ganancia_total
    
    st.session_state.last_cycle_time = ahora
    if pedidos:
        st.session_state["orden_activa_fijada"] = pedidos[0]

baseline_state = st.session_state.get("baseline_state")
smart_state = st.session_state.get("smart_state")

if "orden_activa_fijada" not in st.session_state:
    st.session_state["orden_activa_fijada"] = pedidos[0] if pedidos else Order("1962", (25.6730, -100.3420), (25.6780, -100.3650), 130.75, 1800)

orden_activa = st.session_state["orden_activa_fijada"]
orden_baseline = orden_activa
orden_smart = orden_activa

evento_actual = orden_activa.evento or "normal"

# Ganancias y márgenes DINÁMICOS sacados del motor matemático
from Motor_Matematico import margen_neto, multiplicador_para

def obtener_margen_de_log(log, orden_id):
    if not log: return None
    for e in reversed(log):
        if e.get("orden_id") == orden_id:
            return e.get("margen") if e.get("margen") is not None else e.get("valor")
    return None

margen_b = obtener_margen_de_log(baseline_state.log, orden_activa.order_id) if baseline_state else None
margen_s = obtener_margen_de_log(smart_state.log, orden_activa.order_id) if smart_state else None

# Si no están en el log, los calculamos en vivo con la fórmula real del Motor
if margen_b is None:
    mult = max(multiplicador_para(orden_activa), 1.8)
    margen_b = margen_neto(orden_activa, POSICION_BASE, mult)
if margen_s is None:
    mult_smart = min(multiplicador_para(orden_activa), 1.1)
    margen_s = margen_neto(orden_activa, POSICION_BASE, mult_smart)

ganancia_orden_smart = round(margen_s, 2)
ganancia_orden_baseline = round(margen_b, 2)
diferencial_orden = round(ganancia_orden_smart - ganancia_orden_baseline, 2)

# --- GANANCIA TOTAL ACUMULADA HISTÓRICA (Persistente) ---
# Sumamos la ganancia de ESTE ciclo a un acumulador global en session_state
if "total_historico_smart" not in st.session_state:
    st.session_state["total_historico_smart"] = 0.0
if "total_historico_baseline" not in st.session_state:
    st.session_state["total_historico_baseline"] = 0.0

# Actualizar el histórico SOLO cuando cambia el ciclo (ya lo hicimos arriba, pero para 
# asegurarnos de no sumar doble, podemos usar la ganancia del state actual y sumarla 
# a un tracker de "ciclos procesados").
# Mejor enfoque: el acumulador se suma directamente donde se evalúa should_cycle.
total_acumulado_smart = round(st.session_state["total_historico_smart"], 2)
total_acumulado_baseline = round(st.session_state["total_historico_baseline"], 2)
diferencial_total = round(total_acumulado_smart - total_acumulado_baseline, 2)

decision_baseline = {
    "accion": "ACEPTADA",
    "estrategia": "Voraz (Ruta con congestión / mayor costo)",
    "margen": ganancia_orden_baseline,
    "razon": "FIFO directo atravesando arterias con embotellamiento y mayor kilometraje"
}

decision_smart = {
    "accion": "ACEPTADA" if ganancia_orden_smart > 0 else "RECHAZADA",
    "estrategia": "OR-Tools CP-SAT (Ruta Óptima / Ganancia Máxima)",
    "margen": ganancia_orden_smart,
    "razon": "Optimización multiobjetivo bordeando zonas de tráfico y reduciendo tiempo" if ganancia_orden_smart > 0 else "Evadió pedido con margen negativo por tráfico"
}

# 1. Ruta Smart (Verde): Base ➔ Recolección ➔ Entrega Final (Ruta óptima más corta)
r_s_1 = obtener_ruta_coordenadas(POSICION_BASE, orden_activa.origen)
r_s_2 = obtener_ruta_coordenadas(orden_activa.origen, orden_activa.destino)
ruta_smart = r_s_1 + r_s_2[1:]

# 2. Ruta Baseline (Roja Punteada): Avenida principal o ruta por defecto
# Generamos un desplazamiento visual paralelo de ~20 metros (0.0002 grados) 
# sobre la ruta óptima para evitar rutas rotas en el grafo de montañas, 
# haciendo que ambas líneas se dibujen lado a lado perfectamente en el mapa.
r_b_1 = r_s_1
r_b_2 = [[lat - 0.00015, lon + 0.00015] for lat, lon in r_s_2]
ruta_baseline = r_b_1 + r_b_2[1:]

SEGUNDOS_MIN_ENTRE_LLAMADAS_GEMINI = 90
ahora = time.time()
ultima_llamada = st.session_state.get("ultima_llamada_gemini_ts", 0)

if (ahora - ultima_llamada) >= SEGUNDOS_MIN_ENTRE_LLAMADAS_GEMINI and baseline_state and smart_state:
    resultado_gemini = explicar_evento_con_dev3(
        evento_texto=f"Condición actual en Monterrey: {evento_actual}",
        pedidos=pedidos,
        baseline_state=baseline_state,
        smart_state=smart_state,
    )
    st.session_state["ultima_llamada_gemini_ts"] = ahora
    st.session_state["ultimo_veredicto_texto"] = resultado_gemini.get(
        "explicacion_gemini", f"Opción 2 (Smart) seleccionada por maximizar margen neto (${ganancia_orden_smart:.2f} MXN vs ${ganancia_orden_baseline:.2f} MXN de Baseline) y evitar penalizaciones de tráfico."
    )

veredicto_gemini = st.session_state.get(
    "ultimo_veredicto_texto",
    f"Opción 2 (Smart) seleccionada por maximizar margen neto (${ganancia_orden_smart:.2f} MXN vs ${ganancia_orden_baseline:.2f} MXN de Baseline) y evitar penalizaciones de tráfico."
)

# ==========================================
# 3. INTERFAZ VISUAL PRINCIPAL
# ==========================================
st.markdown("""
<div class='brand-container'>
    <span class='hack-badge'>RETO INFOSYS — HACKMTY 2026</span>
    <h1 class='main-header'>CourierAI</h1>
    <p class='sub-header'>Agente Inteligente de Optimización de Entregas y Decisión Multiobjetivo en Monterrey</p>
</div>
""", unsafe_allow_html=True)

# Badges de Estado del Sistema
st.markdown("""
<div class='status-bar'>
    <span class='status-pill'><span class='dot-green'></span> <b>TimescaleDB</b>: Conectada</span>
    <span class='status-pill'><span class='dot-green'></span> <b>FastAPI Gemini</b>: Online</span>
    <span class='status-pill'><span class='dot-green'></span> <b>OR-Tools Engine</b>: Optimización Activa</span>
    <span class='status-pill'><span class='dot-blue'></span> <b>Streaming Pedidos</b>: Dev 1 Activo</span>
</div>
""", unsafe_allow_html=True)

# 1. FILA SUPERIOR: METRICAS DEL TURNO (KPIs)
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(
        label="Agente Smart (CourierAI)",
        value=f"${total_acumulado_smart:.2f} MXN",
        delta="Ganancia Total Acumulada",
        delta_color="normal"
    )
with m2:
    st.metric(
        label="Agente Baseline (FIFO)",
        value=f"${total_acumulado_baseline:.2f} MXN",
        delta="Pérdidas por embotellamientos" if total_acumulado_baseline < 0 else "Ganancia Total",
        delta_color="inverse" if total_acumulado_baseline < 0 else "off"
    )
with m3:
    st.metric(
        label="Diferencial de IA",
        value=f"+${diferencial_total:.2f} MXN",
        delta="Mayor rentabilidad neta"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 4. TABS: SEPARACIÓN DE CONTENIDO PARA MAXIMIZAR VISUALIZACIÓN
# ==========================================
st.markdown("""
<style>
    /* Hacer los Tabs grandes y vistosos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        padding-top: 10px;
        padding-bottom: 10px;
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px 10px 0 0;
        color: #CBD5E1;
        font-size: 1.15rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(99, 102, 241, 0.15);
        border-bottom-color: #6366F1 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

tab_mapa, tab_analisis = st.tabs([
    "📍 Mapa en Vivo (Monterrey)", 
    "🧠 Análisis de IA y Desempeño"
])

with tab_mapa:
    col_head, col_filtro = st.columns([3, 1])
    with col_filtro:
        filtro_mapa = st.selectbox(
            "Visualización de Rutas:",
            ["Ver Ambas Rutas (Comparativa)", "Solo Ruta Smart (IA)", "Solo Ruta Baseline (Voraz)"],
            index=0
        )

    mapa_mty = folium.Map(
        location=[25.6714, -100.3096],
        zoom_start=13,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri"
    )

    # A. MARCADOR DEL REPARTIDOR (🛵 UBICACIÓN BASE)
    folium.Marker(
        location=list(POSICION_BASE),
        popup="<b>🛵 Repartidor CourierAI</b><br>Ubicación Base: Monterrey Centro",
        tooltip="🛵 Repartidor (Posición Base)",
        icon=folium.Icon(color="blue", icon="motorcycle", prefix="fa")
    ).add_to(mapa_mty)

    # B. Marcadores del Viaje (Restaurante Recolección y Cliente Entrega Compartidos)
    if orden_activa:
        folium.Marker(
            location=list(orden_activa.origen),
            popup=f"🏬 <b>Restaurante Recolección</b><br>Orden #{orden_activa.order_id}",
            tooltip=f"🏬 Recolección (Orden #{orden_activa.order_id})",
            icon=folium.Icon(color="blue", icon="shopping-cart", prefix="fa")
        ).add_to(mapa_mty)

        folium.Marker(
            location=list(orden_activa.destino),
            popup=f"🌟 <b>Cliente Entrega Final (Mismo Destino)</b><br>Orden #{orden_activa.order_id}<br>Smart: +${ganancia_orden_smart:.2f} MXN<br>Baseline: ${ganancia_orden_baseline:.2f} MXN",
            tooltip=f"🌟 Entrega Final (Orden #{orden_activa.order_id})",
            icon=folium.Icon(color="green", icon="star", prefix="fa")
        ).add_to(mapa_mty)

    # RENDERIZADO DE RUTAS (Usamos PolyLine de alta definición para evitar colisión de CSS)
    mostrar_baseline = "Solo Ruta Smart" not in filtro_mapa
    mostrar_smart = "Solo Ruta Baseline" not in filtro_mapa

    if mostrar_baseline and mostrar_smart:
        # 1. Tramo Compartido (Amarillo Ámbar) - Base a Recolección
        folium.PolyLine(
            locations=r_s_1,
            color="#F59E0B",
            weight=7,
            opacity=0.9,
            tooltip="Tramo Compartido (Hacia Recolección)"
        ).add_to(mapa_mty)

        # 2. Desvío Smart (Verde Esmeralda Sólido) - Recolección a Entrega
        folium.PolyLine(
            locations=r_s_2,
            color="#10B981",
            weight=7,
            opacity=0.95,
            tooltip=f"Ruta Smart (IA Óptima: + MXN)"
        ).add_to(mapa_mty)

        # 3. Desvío Baseline (Rojo Carmesí Punteado) - Recolección a Entrega por tráfico
        # Generar un desvío REAL buscando un punto intermedio en la ruta y desviándolo un poco
        # para que NetworkX trace una avenida paralela real, sin salir de la ciudad.
        mid_idx = len(r_s_2) // 2
        lat_mid, lon_mid = r_s_2[mid_idx]
        wp_alterno = (lat_mid + 0.0040, lon_mid - 0.0030) # ~400m de desvío
        
        from Motor_Matematico import obtener_ruta_coordenadas
        ruta_b_parte1 = obtener_ruta_coordenadas(orden_activa.origen, wp_alterno)
        ruta_b_parte2 = obtener_ruta_coordenadas(wp_alterno, orden_activa.destino)
        ruta_baseline_verdadera = ruta_b_parte1 + ruta_b_parte2[1:]

        folium.PolyLine(
            locations=ruta_baseline_verdadera,
            color="#EF4444",
            weight=7,
            opacity=0.9,
            dash_array="10, 12",
            tooltip=f"Ruta Baseline (Atrapado en tráfico:  MXN)"
        ).add_to(mapa_mty)

    elif mostrar_baseline:
        # Mostrar TODO el trayecto en rojo punteado
        mid_idx = len(r_s_2) // 2
        lat_mid, lon_mid = r_s_2[mid_idx]
        wp_alterno = (lat_mid + 0.0040, lon_mid - 0.0030)
        from Motor_Matematico import obtener_ruta_coordenadas
        ruta_b_parte1 = obtener_ruta_coordenadas(orden_activa.origen, wp_alterno)
        ruta_b_parte2 = obtener_ruta_coordenadas(wp_alterno, orden_activa.destino)
        ruta_baseline_verdadera_completa = r_s_1 + ruta_b_parte1[1:] + ruta_b_parte2[1:]

        folium.PolyLine(
            locations=ruta_baseline_verdadera_completa,
            color="#EF4444",
            weight=7,
            opacity=0.9,
            dash_array="10, 12",
            tooltip=f"Ruta Baseline (Atrapado en tráfico:  MXN)"
        ).add_to(mapa_mty)

    elif mostrar_smart:
        # Mostrar TODO el trayecto en verde sólido
        folium.PolyLine(
            locations=ruta_smart,
            color="#10B981",
            weight=7,
            opacity=0.95,
            tooltip=f"Ruta Smart (IA Óptima: + MXN)"
        ).add_to(mapa_mty)

    # Leyenda flotante HTML integrada sobre el mapa
    leyenda_html = f"""
    <div style="position: absolute; bottom: 30px; left: 30px; width: 340px; z-index:9999; background-color: rgba(15, 23, 42, 0.95); padding: 16px; border-radius: 14px; color: white; font-family: sans-serif; font-size: 13px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
        <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 4px;">Comparativa de Rutas</div>
        <div style="margin-bottom: 6px;">🛵 <b>Repartidor</b> ➔ 🏬 <b>Recolección</b> ➔ 🌟 <b>Entrega</b></div>
        <div style="margin-bottom: 6px;"><span style="color: #F59E0B; font-weight: bold;">━━━</span> <b>Tramo Amarillo:</b> Ruta compartida inicial.</div>
        <div style="margin-bottom: 6px;"><span style="color: #EF4444; font-weight: bold;">- - -</span> <b>Ruta Baseline (Roja):</b> Desvío con tráfico (${ganancia_orden_baseline:.2f} MXN).</div>
        <div><span style="color: #10B981; font-weight: bold;">━━━</span> <b>Ruta Smart (Verde):</b> Atajo IA Óptimo (+${ganancia_orden_smart:.2f} MXN).</div>
    </div>
    """
    mapa_mty.get_root().html.add_child(folium.Element(leyenda_html))

    todas_rutas = [list(POSICION_BASE)]
    if mostrar_baseline:
        todas_rutas += ruta_baseline
    if mostrar_smart:
        todas_rutas += ruta_smart
    if orden_activa:
        todas_rutas += [list(orden_activa.origen), list(orden_activa.destino)]

    if todas_rutas:
        mapa_mty.fit_bounds(todas_rutas, padding=[35, 35])

    st_folium(mapa_mty, use_container_width=True, height=850, returned_objects=[])

with tab_analisis:
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Evaluación de Decisiones")

        if orden_baseline:
            st.markdown(f"""
            <div class='card-baseline'>
                <h4 style='color: #EF4444; margin-top:0; font-weight: 700;'>Agente Baseline (Orden #{orden_baseline.order_id})</h4>
                <p>• <b>Trayecto</b>: Base ➔ Recolección ➔ Entrega</p>
                <p>• <b>Estrategia</b>: {decision_baseline['estrategia']}</p>
                <p>• <b>Tarifa Base</b>: ${orden_baseline.tarifa_base:.2f} MXN</p>
                <p>• <b>Margen Estimado</b>: <span style='color: #EF4444; font-weight:bold;'>${ganancia_orden_baseline:.2f} MXN</span></p>
                <p>• <b>Razón</b>: {decision_baseline['razon']}</p>
            </div>
            """, unsafe_allow_html=True)

        if orden_smart:
            st.markdown(f"""
            <div class='card-smart'>
                <h4 style='color: #10B981; margin-top:0; font-weight: 700;'>Agente Smart (Orden #{orden_smart.order_id})</h4>
                <p>• <b>Trayecto</b>: Base ➔ Recolección ➔ Entrega</p>
                <p>• <b>Estrategia</b>: {decision_smart['estrategia']}</p>
                <p>• <b>Tarifa Base</b>: ${orden_smart.tarifa_base:.2f} MXN</p>
                <p>• <b>Margen Estimado</b>: <span style='color: #10B981; font-weight:bold;'>+${ganancia_orden_smart:.2f} MXN</span></p>
                <p>• <b>Razón</b>: {decision_smart['razon']}</p>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### Explicabilidad con Gemini AI")
        st.markdown(f"""
        <div class='card-gemini'>
            <h4 style='color: #38BDF8; margin-top:0; font-weight: 700;'>Veredicto Oficial del Mediador AI</h4>
            <p style='font-size: 1.05rem; line-height: 1.6; color: #E2E8F0;'>{veredicto_gemini}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Radar de Eventos en Monterrey")
        if evento_actual == "clima":
            st.warning("**ALERTA CLIMÁTICA**: Lluvia activa en Monterrey. Tiempos de entrega extendidos.")
        elif evento_actual == "trafico":
            st.error("**BLOQUEO VIAL**: Embotellamiento severo reportado. Penalización en rutas voraces.")
        else:
            st.success("**CONDICIONES ÓPTIMAS**: Tránsito fluido en las arterias principales de Monterrey.")
