import pytest
from Backend.Backend_Dev2.auth import hash_password

def test_hash_password():
    p1 = hash_password("secret123")
    p2 = hash_password("secret123")
    p3 = hash_password("different")
    
    assert isinstance(p1, str)
    assert len(p1) == 64  # SHA-256 hex length
    assert p1 == p2
    assert p1 != p3
