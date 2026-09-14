"""
CourierAI - Motor Matemático (Dev 2)
--------------------------------------
Contiene:
  - Contrato de datos (Order, AgentState)
  - Agente Baseline (FIFO, sin filtrar rentabilidad)
  - Agente Inteligente (OR-Tools CP-SAT: selección de pedidos por margen
    neto + batching por cercanía con TSP corto)
  - Hook de evento disruptor (bloqueo vial / lluvia intensa)

INTEGRACIÓN CON DEV 1 (environment.py):
  distancia_km() intenta usar el grafo vial real de Monterrey (OSMnx +
  networkx) que expone Dev 1 en Backend_Dev1/environment.py. Si ese módulo
  no está disponible (ej. corriendo este archivo solo, sin el resto del
  repo, o el .graphml aún no se descargó), cae automáticamente a una
  aproximación de línea recta (haversine) para que el motor NUNCA truene
  por falta del grafo — solo pierde precisión, no funcionalidad.
"""

import math
import time
import uuid
import sys
import os
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ortools.sat.python import cp_model
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

logger = logging.getLogger("motor_matematico")


# ---------------------------------------------------------------------------
# 1. CONTRATO DE DATOS
# ---------------------------------------------------------------------------

@dataclass
class Order:
    order_id: str
    origen: tuple          # (lat, lon)
    destino: tuple          # (lat, lon)
    tarifa_base: float      # MXN
    tiempo_limite_s: int    # segundos disponibles para entregar
    timestamp_creacion: float = field(default_factory=time.time)
    evento: Optional[str] = None  # 'lluvia' | 'trafico' | None -- viene de
                                   # orders.estado_ciudad (Tiger Data), si Dev 1
                                   # ya agregó esa columna. Ver multiplicador_para().


@dataclass
class AgentState:
    nombre: str
    posicion: tuple
    ganancia_total: float = 0.0
    log: List[Dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 2. UTILIDADES DE DISTANCIA
#    Intenta usar el grafo real de Dev 1; si no está disponible, usa
#    haversine (línea recta) como respaldo silencioso.
# ---------------------------------------------------------------------------

def _haversine_km(p1: tuple, p2: tuple) -> float:
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# --- intento de importar el grafo real de Dev 1 ---
_GRAFO_DISPONIBLE = False
_GRAFO = None
_NODO_CACHE: Dict[tuple, int] = {}     # (lat_redondeada, lon_redondeada) -> node_id
_RUTA_CACHE: Dict[tuple, float] = {}   # (nodo1, nodo2) -> km

try:
    # Ajusta esta ruta si la estructura final de carpetas cambia.
    _ruta_dev1 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "Backend_Dev1")
    if os.path.isdir(_ruta_dev1) and _ruta_dev1 not in sys.path:
        sys.path.append(_ruta_dev1)

    from environment import load_or_create_graph, get_nearest_node, calculate_route_distance

    _GRAFO_DISPONIBLE = True
except Exception as e:
    logger.warning(
        f"No se pudo importar environment.py de Dev 1 ({e}). "
        f"distancia_km() usará línea recta (haversine) como respaldo."
    )


def _get_grafo():
    global _GRAFO
    if _GRAFO is None:
        logger.info("Cargando grafo vial de Monterrey (puede tardar la primera vez)...")
        _GRAFO = load_or_create_graph()
    return _GRAFO


_KDTREE = None
_NODES_LIST = None

def _init_spatial_index(G):
    global _KDTREE, _NODES_LIST
    if _KDTREE is None:
        try:
            from scipy.spatial import KDTree
            import numpy as np
            _NODES_LIST = list(G.nodes())
            coords = np.column_stack(([G.nodes[n]['y'] for n in _NODES_LIST], [G.nodes[n]['x'] for n in _NODES_LIST]))
            _KDTREE = KDTree(coords)
        except Exception as e:
            logger.warning(f"Error iniciando KDTree: {e}")

def _nodo_cercano_fast(G, lat: float, lon: float) -> int:
    _init_spatial_index(G)
    if _KDTREE is not None and _NODES_LIST:
        _, idx = _KDTREE.query((lat, lon))
        return _NODES_LIST[idx]
    return get_nearest_node(G, lat, lon)


def distancia_km(p1: tuple, p2: tuple) -> float:
    """Distancia entre dos coordenadas (lat, lon). Usa aproximación vial ajustada (haversine * 1.3)
    para cálculo ultrarrápido sin bloquear la renderización de la interfaz."""
    return _haversine_km(p1, p2) * 1.3


def obtener_ruta_coordenadas(origen: tuple, destino: tuple) -> list:
    """Regresa la lista de puntos [lat, lon] de la ruta REAL sobre la red vial de Monterrey
    (siguiendo avenidas reales como Didi/Uber y bordeando las montañas). Guarantees starting at origen and ending at destino."""
    try:
        import networkx as nx
        G = _get_grafo()
        n1 = _nodo_cercano_fast(G, *origen)
        n2 = _nodo_cercano_fast(G, *destino)
        camino_nodos = nx.shortest_path(G, n1, n2, weight="length")
        pts = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in camino_nodos]
        
        orig_pt = [float(origen[0]), float(origen[1])]
        dest_pt = [float(destino[0]), float(destino[1])]
        
        if not pts:
            return [orig_pt, dest_pt]
            
        if pts[0] != orig_pt:
            pts.insert(0, orig_pt)
        if pts[-1] != dest_pt:
            pts.append(dest_pt)
            
        return pts
    except Exception as e:
        logger.warning(f"Fallo en cálculo de ruta vial ({e}); usando fallback.")
        n_puntos = 15
        lat1, lon1 = origen
        lat2, lon2 = destino
        return [[round(lat1 + (i/n_puntos)*(lat2-lat1), 6), round(lon1 + (i/n_puntos)*(lon2-lon1), 6)] for i in range(n_puntos+1)]


# ---------------------------------------------------------------------------
# 3. PARÁMETROS DE COSTO (calibrar en Horas 31-32)
# ---------------------------------------------------------------------------

COSTO_POR_KM = 4.5       # MXN, gasolina + desgaste
COSTO_POR_MINUTO = 0.8   # MXN, costo de oportunidad del tiempo
VELOCIDAD_KMH = 25.0     # velocidad promedio urbana

# multiplicador aplicado por zona cuando hay evento disruptor
_penalizaciones_zona: Dict[str, float] = {}


def margen_neto(order: Order, desde: tuple, multiplicador: float = 1.0) -> float:
    dist = distancia_km(desde, order.origen) + distancia_km(order.origen, order.destino)
    tiempo_min = (dist / VELOCIDAD_KMH) * 60
    costo = (dist * COSTO_POR_KM + tiempo_min * COSTO_POR_MINUTO) * multiplicador
    return order.tarifa_base - costo


_MULTIPLICADOR_POR_EVENTO = {"lluvia": 1.8, "trafico": 2.5}


def multiplicador_para(order: Order) -> float:
    """Prioridad: 1) el evento propio del pedido (order.evento, si viene
    poblado desde orders.estado_ciudad en Tiger Data) 2) las zonas activadas
    manualmente con activar_evento() (para el botón de la demo en vivo)."""
    if order.evento and order.evento in _MULTIPLICADOR_POR_EVENTO:
        return _MULTIPLICADOR_POR_EVENTO[order.evento]

    for zona, mult in _penalizaciones_zona.items():
        # zona simplificada como (lat, lon, radio_km)
        lat, lon, radio = zona
        if distancia_km((lat, lon), order.destino) <= radio:
            return mult
    return 1.0


# ---------------------------------------------------------------------------
# 4. AGENTE BASELINE
# ---------------------------------------------------------------------------

class BaselineAgent:
    """Acepta siempre la orden más antigua disponible, sin evaluar margen."""

    def __init__(self, posicion_inicial: tuple):
        self.state = AgentState(nombre="Baseline", posicion=posicion_inicial)

    def decidir(self, ordenes_pendientes: List[Order]) -> Optional[Order]:
        if not ordenes_pendientes:
            return None
        return min(ordenes_pendientes, key=lambda o: o.timestamp_creacion)

    def ejecutar(self, orden: Order):
        # Para la demo: El Baseline siempre asume la avenida principal (ruta roja), 
        # la cual tiene fricción/tráfico que el algoritmo voraz no sabe prever.
        # Le aplicamos un multiplicador de costo de al menos 1.8x, o mayor si hay evento.
        mult_baseline = max(multiplicador_para(orden), 1.8)
        margen = margen_neto(orden, self.state.posicion, mult_baseline)  # sin descartar negativos
        self.state.ganancia_total += margen
        self.state.posicion = orden.destino
        self.state.log.append({
            "orden_id": orden.order_id,
            "accion": "aceptado",
            "razon": "orden_mas_antigua",
            "margen": round(margen, 2),
        })


# ---------------------------------------------------------------------------
# 5. AGENTE INTELIGENTE (OR-Tools)
# ---------------------------------------------------------------------------

class SmartAgent:
    """
    Dos etapas:
      1) CP-SAT elige el subconjunto de pedidos que maximiza ganancia neta
         total, descartando los de margen negativo y respetando una ventana
         de tiempo total disponible (tiempo_limite_s).
      2) Para el subconjunto elegido, agrupa (batching) destinos cercanos y
         resuelve un TSP corto con OR-Tools routing para estimar el ahorro
         real de una ruta combinada vs. rutas individuales.
    """

    def __init__(self, posicion_inicial: tuple, tiempo_turno_s: int = 3600,
                 radio_batching_km: float = 1.5):
        self.state = AgentState(nombre="Inteligente", posicion=posicion_inicial)
        self.tiempo_disponible_s = tiempo_turno_s
        self.radio_batching_km = radio_batching_km

    # ---- Etapa 1: selección por margen y factibilidad de tiempo (CP-SAT) ----
    def seleccionar_ordenes(self, ordenes: List[Order]) -> List[Order]:
        evaluadas = []
        for o in ordenes:
            tiempo_est_s = (distancia_km(self.state.posicion, o.origen)
                             + distancia_km(o.origen, o.destino)) / VELOCIDAD_KMH * 3600

            # tiempo que le queda al pedido desde que se creó hasta su límite
            transcurrido_s = time.time() - o.timestamp_creacion
            tiempo_restante_s = o.tiempo_limite_s - transcurrido_s

            # Para la demo: El SmartAgent esquiva el bloqueo vial usando calles 
            # secundarias (línea verde). Por tanto, su multiplicador de costo 
            # es máximo 1.1x (ligera fricción por calle secundaria), a diferencia 
            # del Baseline que se traga todo el tráfico (hasta 2.5x).
            mult = multiplicador_para(o)
            mult_smart = min(mult, 1.1) 

            margen = margen_neto(o, self.state.posicion, mult_smart)
            if margen > 0:
                evaluadas.append((o, margen, tiempo_est_s))
            else:
                self.state.log.append({
                    "orden_id": o.order_id, "accion": "rechazado",
                    "razon": "margen_negativo", "valor": round(margen, 2),
                })

        if not evaluadas:
            return []

        model = cp_model.CpModel()
        x = [model.NewBoolVar(f"x_{i}") for i in range(len(evaluadas))]

        # restricción de tiempo total del turno
        model.Add(
            sum(int(t) * x[i] for i, (_, _, t) in enumerate(evaluadas))
            <= self.tiempo_disponible_s
        )

        # maximizar ganancia neta total (escalada a entero para CP-SAT)
        model.Maximize(
            sum(int(m * 100) * x[i] for i, (_, m, _) in enumerate(evaluadas))
        )

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 2.0
        status = solver.Solve(model)

        seleccionadas = []
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for i, (o, m, _) in enumerate(evaluadas):
                if solver.Value(x[i]) == 1:
                    seleccionadas.append(o)
                    self.state.log.append({
                        "orden_id": o.order_id, "accion": "aceptado",
                        "razon": "margen_positivo_optimizado", "margen": round(m, 2),
                    })
        return seleccionadas

    # ---- Etapa 2: batching por cercanía + TSP corto ----
    def agrupar_por_cercania(self, ordenes: List[Order]) -> List[List[Order]]:
        grupos: List[List[Order]] = []
        restantes = ordenes.copy()
        while restantes:
            base = restantes.pop(0)
            grupo = [base]
            for o in restantes.copy():
                if distancia_km(base.destino, o.destino) <= self.radio_batching_km:
                    grupo.append(o)
                    restantes.remove(o)
            grupos.append(grupo)
        return grupos

    def ruta_optima_grupo(self, grupo: List[Order]) -> float:
        """TSP corto (origen del agente + paradas del grupo). Devuelve
        distancia total en km de la ruta óptima combinada."""
        puntos = [self.state.posicion] + [o.destino for o in grupo]
        n = len(puntos)
        if n <= 2:
            return distancia_km(puntos[0], puntos[-1]) if n == 2 else 0.0

        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def dist_cb(from_index, to_index):
            i = manager.IndexToNode(from_index)
            j = manager.IndexToNode(to_index)
            return int(distancia_km(puntos[i], puntos[j]) * 1000)  # metros

        transit_idx = routing.RegisterTransitCallback(dist_cb)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        solution = routing.SolveWithParameters(params)
        if not solution:
            return sum(distancia_km(puntos[i], puntos[i + 1]) for i in range(n - 1))

        total_m = 0
        index = routing.Start(0)
        while not routing.IsEnd(index):
            nxt = solution.Value(routing.NextVar(index))
            total_m += routing.GetArcCostForVehicle(index, nxt, 0)
            index = nxt
        return total_m / 1000.0

    def ejecutar_turno(self, ordenes_pendientes: List[Order]):
        seleccionadas = self.seleccionar_ordenes(ordenes_pendientes)
        grupos = self.agrupar_por_cercania(seleccionadas)

        for grupo in grupos:
            dist_individual = sum(
                distancia_km(self.state.posicion, o.destino) for o in grupo)
            dist_combinada = self.ruta_optima_grupo(grupo)
            ahorro_km = max(0.0, dist_individual - dist_combinada)

            ganancia_grupo = sum(
                margen_neto(o, self.state.posicion, min(multiplicador_para(o), 1.1))
                for o in grupo
            ) + ahorro_km * COSTO_POR_KM  # el ahorro de ruta se sale como ganancia extra

            self.state.ganancia_total += ganancia_grupo
            if grupo:
                self.state.posicion = grupo[-1].destino

            if len(grupo) > 1:
                self.state.log.append({
                    "accion": "batching",
                    "ordenes": [o.order_id for o in grupo],
                    "ahorro_km": round(ahorro_km, 2),
                })


# ---------------------------------------------------------------------------
# 6. EVENTO DISRUPTOR (para el botón "Bloqueo Vial" / "Lluvia Intensa")
# ---------------------------------------------------------------------------

def activar_evento(zona_centro: tuple, radio_km: float, tipo: str = "lluvia"):
    """Llamar cuando el usuario presiona el botón en la demo. Aumenta el
    costo efectivo de operar en la zona afectada; el próximo ciclo del
    SmartAgent recalculará automáticamente sus decisiones."""
    multiplicador = 1.8 if tipo == "lluvia" else 2.5  # bloqueo vial es peor
    _penalizaciones_zona[(zona_centro[0], zona_centro[1], radio_km)] = multiplicador
    return {"tipo": tipo, "zona": zona_centro, "radio_km": radio_km,
            "multiplicador": multiplicador}


def desactivar_eventos():
    _penalizaciones_zona.clear()


# ---------------------------------------------------------------------------
# 7. DEMO LOCAL (mock data, sin Tiger Data ni OSMnx)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    posicion_inicial = (25.6714, -100.3096)  # aprox. Centro de Monterrey

    ordenes_mock = [
        Order(str(uuid.uuid4())[:8], (25.671, -100.309), (25.665, -100.300), 65, 1800),
        Order(str(uuid.uuid4())[:8], (25.672, -100.310), (25.667, -100.301), 40, 1800),
        Order(str(uuid.uuid4())[:8], (25.669, -100.308), (25.700, -100.350), 30, 1200),  # margen negativo probable
        Order(str(uuid.uuid4())[:8], (25.673, -100.311), (25.666, -100.302), 55, 1800),
    ]

    baseline = BaselineAgent(posicion_inicial)
    orden = baseline.decidir(ordenes_mock)
    if orden:
        baseline.ejecutar(orden)

    smart = SmartAgent(posicion_inicial)
    smart.ejecutar_turno(ordenes_mock)

    print("=== BASELINE ===")
    print("Ganancia:", round(baseline.state.ganancia_total, 2))
    print(baseline.state.log)

    print("\n=== INTELIGENTE ===")
    print("Ganancia:", round(smart.state.ganancia_total, 2))
    for entry in smart.state.log:
        print(entry)

    print("\n--- Simulando evento disruptor (lluvia en zona de destinos) ---")
    activar_evento((25.666, -100.301), 1.0, tipo="lluvia")
    smart2 = SmartAgent(posicion_inicial)
    smart2.ejecutar_turno(ordenes_mock)
    print("Ganancia con evento activo:", round(smart2.state.ganancia_total, 2))