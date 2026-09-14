import pytest
from Backend.Backend_Dev2.Tiger_Data_io import _ACCION_A_STATUS

def test_status_mapping():
    assert _ACCION_A_STATUS["aceptado"] == "ACEPTADA"
    assert _ACCION_A_STATUS["rechazado"] == "RECHAZADA"
