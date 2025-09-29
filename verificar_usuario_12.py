#!/usr/bin/env python
"""
Verificar si usuario 12 aparece en endpoint
"""

import requests

def verificar_usuario_12():
    # Login seguridad
    response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
                            json={'email': 'seguridad@facial.com', 'password': 'seguridad123'})
    
    if response.status_code == 200:
        token = response.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Consultar endpoint
        endpoint_response = requests.get('http://127.0.0.1:8000/seguridad/api/usuarios-reconocimiento/', headers=headers)
        
        if endpoint_response.status_code == 200:
            data = endpoint_response.json()
            usuarios = data['data']
            
            print(f'TOTAL USUARIOS EN ENDPOINT: {len(usuarios)}')
            print('=' * 50)
            
            usuario_12_encontrado = False
            for user in usuarios:
                if user.get('usuario_id') == 12:
                    usuario_12_encontrado = True
                    print('🎉 USUARIO 12 ENCONTRADO EN ENDPOINT!')
                    print(f'   Usuario ID: {user.get("usuario_id")}')
                    print(f'   Email: {user.get("email")}')  
                    print(f'   Nombre: {user.get("nombres_completos")}')
                    print(f'   Copropietario ID: {user.get("copropietario_id")}')
                    if 'reconocimiento_facial' in user:
                        rf = user['reconocimiento_facial']
                        fotos = rf.get('total_fotos', 0)
                        print(f'   Total fotos: {fotos}')
                        fecha = rf.get('fecha_ultimo_enrolamiento', 'N/A')
                        print(f'   Fecha enrolamiento: {fecha}')
                    break
            
            if not usuario_12_encontrado:
                print('❌ Usuario 12 NO encontrado en endpoint')
                print('Usuarios encontrados:')
                for user in usuarios:
                    uid = user.get('usuario_id', 'N/A')
                    email = user.get('email', 'N/A')
                    print(f'  - Usuario ID {uid}: {email}')
                    
        else:
            print(f'Error consultando endpoint: {endpoint_response.status_code}')
            print(endpoint_response.text)
    else:
        print(f'Error login: {response.status_code}')

if __name__ == "__main__":
    verificar_usuario_12()