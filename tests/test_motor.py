import pytest
from Backend.Backend_Dev2.Motor_Matematico import margen_neto, Order

def test_margen_neto_calculo():
    o = Order("999", (25.67, -100.30), (25.68, -100.31), 100.0, 1800)
    pos_base = (25.67, -100.30)
    m = margen_neto(o, pos_base, multiplicador_friccion=1.0)
    assert isinstance(m, float)
