import requests

# Configuración
BASE_URL = "http://localhost:8000/api/authz/acceso/listar/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU5MDc1NjY1LCJpYXQiOjE3NTkwNzIwNjUsImp0aSI6ImU2NzY3OWY1MmQ4NTQ4ODRiODAzMGIxODQwNTU3NWE5IiwidXNlcl9pZCI6IjIifQ.fPmfmjDUPhMh0I2TqiPnXmK12rFCDD_srQWG-RfScZg"  # Reemplaza por un token válido de usuario con rol seguridad

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_listar_accesos_condominio():
    response = requests.get(BASE_URL, headers=headers)
    print("Status code:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_listar_accesos_condominio()
