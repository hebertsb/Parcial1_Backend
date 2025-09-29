import requests
import json

print('🧪 PRUEBA FINAL: ENDPOINT GET CORREGIDO')
print('=' * 40)

try:
    # 1. Login
    print('1. 🔐 Login...')
    login_response = requests.post('http://localhost:8000/api/authz/login/', {
        'email': 'seguridad@facial.com',
        'password': 'seguridad123'
    })
    
    if login_response.status_code != 200:
        print(f'   ❌ Error login: {login_response.status_code}')
        print(f'   Response: {login_response.text}')
        exit()
    
    token = login_response.json()['access']
    print('   ✅ Login OK')
    
    # 2. Probar endpoint GET fotos
    print('2. 📸 GET fotos usuario 8...')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(
        'http://localhost:8000/api/authz/reconocimiento/fotos/8/',
        headers=headers
    )
    
    print(f'   Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            fotos_info = data.get('data', {})
            total = fotos_info.get('total_fotos', 0)
            urls = fotos_info.get('fotos_urls', [])
            
            print(f'   ✅ Total fotos: {total}')
            print(f'   ✅ Usuario: {fotos_info.get("usuario_email")}')
            
            if urls:
                print('   📸 Fotos encontradas:')
                for i, url in enumerate(urls):
                    print(f'      {i+1}. {url}')
                print()
                print('🎉 ¡PROBLEMA RESUELTO!')
                print('✅ El endpoint GET ahora devuelve las URLs correctamente')
            else:
                print('   ❌ Lista de URLs vacía')
        else:
            print(f'   ❌ Error: {data.get("error")}')
    else:
        print(f'   ❌ HTTP Error: {response.status_code}')
        print(f'   Response: {response.text[:200]}')

except Exception as e:
    print(f'❌ Error: {e}')