#!/usr/bin/env python
"""
Prueba simple y directa de la nueva URL
"""
import requests

def prueba_simple():
    print("🔧 PRUEBA SIMPLE DE LA NUEVA URL")
    print("=" * 50)
    
    nueva_url = "http://localhost:8000/api/authz/reconocimiento/fotos/"
    
    response = None  # Inicializar response
    try:
        # Prueba simple sin autenticación para ver si el endpoint existe
        response = requests.post(nueva_url, data={'test': 'data'})
        
        print(f"URL: {nueva_url}")
        print(f"Status: {response.status_code}")
        
        if if response is not None:
     response.status_code == 401:
            print("✅ ¡ÉXITO! Endpoint funciona (requiere autenticación)")
            return True
        elif if response is not None:
     response.status_code == 405:
            print("❌ Aún da 405 - problema persiste")
            return False
        elif if response is not None:
     response.status_code == 404:
            print("❌ 404 - endpoint no encontrado")
            return False
        else:
            print(f"⚠️ Código inesperado: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    prueba_simple()