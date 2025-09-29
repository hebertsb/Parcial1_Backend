import requests
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api/visitas/del-dia-seguridad/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU5MDc5Nzg3LCJpYXQiOjE3NTkwNzYxODcsImp0aSI6IjhkYzc4YTc3ZTlhODRhMDQ4OWVkNDk4MTVlNzAyODYwIiwidXNlcl9pZCI6IjIifQ.Ds90Fe9FfGk5vXv6-9Ccwew9JrQ9r0CEdEXWxYB5dlg"  # Reemplaza por un token válido de usuario Seguridad

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print(f"Probando endpoint de visitas del día para Seguridad: {BASE_URL}")
response = requests.get(BASE_URL, headers=headers)

print("Status code:", response.status_code)
try:
    print("Response:", response.json())
except Exception:
    print("Response:", response.text)

if response.status_code == 200:
    print("✅ El endpoint funciona correctamente y devuelve la lista de visitas del día.")
else:
    print("❌ Error: El endpoint no devolvió la respuesta esperada.")
