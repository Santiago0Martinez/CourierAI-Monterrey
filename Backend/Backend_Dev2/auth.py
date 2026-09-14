import hashlib
import os
import logging

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 seguro para la contraseña del repartidor."""
    salt = "courier_ai_monterrey_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def validar_credenciales(email: str, password: str, conn=None) -> dict:
    """Valida el login del repartidor en TimescaleDB y retorna su perfil si es valido."""
    from Tiger_Data_io import get_connection
    p_hash = hash_password(password)
    
    try:
        with get_connection() as c:
            cur = c.cursor()
            cur.execute("""
                SELECT id, nombre, email, vehiculo_tipo, rating, saldo_acumulado 
                FROM repartidores 
                WHERE email = %s AND password_hash = %s;
            """, (email.strip().lower(), p_hash))
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "nombre": row[1],
                    "email": row[2],
                    "vehiculo_tipo": row[3],
                    "rating": float(row[4]),
                    "saldo_acumulado": float(row[5])
                }
    except Exception as e:
        logger.error(f"Error autenticando repartidor: {e}")
    return None
