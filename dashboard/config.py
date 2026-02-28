# CONFIGURACIÓN DE SEGURIDAD
import os
from dotenv import load_dotenv

load_dotenv('/root/content-ai/.env')

# Usuario y contraseña para el dashboard
# Puedes cambiar estos valores
DASHBOARD_CONFIG = {
    "username": "admin",
    "password": os.getenv("DASHBOARD_PASSWORD", "ContentAI2024!"),
    "session_timeout": 3600,  # 1 hora en segundos
    "allow_ips": [],  # Lista vacía = todas las IPs permitidas
}

# Configuración de API
API_URL = "http://backend:8000"
