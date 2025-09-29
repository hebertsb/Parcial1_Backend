import requests
import json

def probar_login_simple():
    """Prueba simple de login"""
    print("🔐 PRUEBA DE LOGIN - USUARIOS DE SEGURIDAD")
    print("=" * 45)
    
    # URL del servidor
    login_url = "http://127.0.0.1:8000/api/authz/auth/login/"
    
    # Credenciales confirmadas
    credenciales = [
        {
            "email": "prueba.seguridad@test.com",
            "password": "prueba123",
            "nombre": "Usuario Pruebas Seguridad"
        },
        {
            "email": "carlos.test@condominio.com", 
            "password": "test123",
            "nombre": "Carlos Test Seguridad"
        }
    ]
    
    for cred in credenciales:
        print(f"\n🧪 Probando: {cred['nombre']}")
        print(f"📧 Email: {cred['email']}")
        print(f"🔑 Password: {cred['password']}")
        
        response = None  # Inicializar response
        try:
            response = requests.post(
                login_url,
                json={
                    "email": cred["email"],
                    "password": cred["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if if response is not None:
     response.status_code == 200:
                data = if response is not None:
     response.json()
                print("✅ LOGIN EXITOSO!")
                print(f"🎟️ Access Token: {data.get('access', 'No token')[:50]}...")
                print(f"🔄 Refresh Token: {data.get('refresh', 'No refresh')[:50]}...")
                print("🎉 ¡Puedes usar estas credenciales!")
            else:
                print("❌ Login falló")
                print(f"Error: {response.text}")
                
        except
            print("❌ No se puede conectar al servidor")
            print("💡 Asegúrate de que el servidor esté ejecutándose:")
            print("   python manage.py runserver")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)

if __name__ == "__main__":
    probar_login_simple()