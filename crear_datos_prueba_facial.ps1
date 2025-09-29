# Script para crear datos de prueba para el reconocimiento facial

Write-Host "🧪 CREANDO DATOS DE PRUEBA PARA RECONOCIMIENTO FACIAL" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Yellow

python manage.py shell -c "
from seguridad.models import Copropietarios, ReconocimientoFacial
from authz.models import Usuario, SolicitudRegistroPropietario
import json
import random

print('🏗️  CREANDO DATOS DE PRUEBA...')
print()

# Crear algunos copropietarios de prueba si no existen
copropietarios_prueba = [
    {
        'nombres': 'Juan Carlos',
        'apellidos': 'Pérez González',
        'numero_documento': '12345678',
        'tipo_documento': 'CC',
        'telefono': '71234567',
        'email': 'juancarlos@email.com',
        'unidad_residencial': 'Apto 101',
        'tipo_residente': 'Propietario'
    },
    {
        'nombres': 'María Elena',
        'apellidos': 'Rodríguez Silva',
        'numero_documento': '87654321',
        'tipo_documento': 'CC',
        'telefono': '72345678',
        'email': 'maria.elena@email.com',
        'unidad_residencial': 'Casa 5',
        'tipo_residente': 'Propietario'
    },
    {
        'nombres': 'Carlos Alberto',
        'apellidos': 'Mendoza Torres',
        'numero_documento': '11223344',
        'tipo_documento': 'CC',
        'telefono': '73456789',
        'email': 'carlos.mendoza@email.com',
        'unidad_residencial': 'Apto 205',
        'tipo_residente': 'Propietario'
    }
]

copropietarios_creados = []

for datos in copropietarios_prueba:
    copropietario, created = Copropietarios.objects.get_or_create(
        numero_documento=datos['numero_documento'],
        defaults=datos
    )
    
    if created:
        print(f'✅ Copropietario creado: {copropietario.nombres} {copropietario.apellidos}')
    else:
        print(f'ℹ️  Copropietario ya existe: {copropietario.nombres} {copropietario.apellidos}')
    
    copropietarios_creados.append(copropietario)

print()
print('🤖 CREANDO REGISTROS DE RECONOCIMIENTO FACIAL...')

# Crear registros de reconocimiento facial con encodings simulados
for copropietario in copropietarios_creados:
    # Generar encoding facial simulado (normalmente vendría de face_recognition)
    encoding_simulado = json.dumps([random.uniform(-1, 1) for _ in range(128)])
    
    # URLs de fotos simuladas (normalmente vendrían de Dropbox)
    fotos_urls = [
        f'https://dropbox.com/fotos/{copropietario.numero_documento}_1.jpg',
        f'https://dropbox.com/fotos/{copropietario.numero_documento}_2.jpg'
    ]
    
    registro_facial, created = ReconocimientoFacial.objects.get_or_create(
        copropietario=copropietario,
        defaults={
            'encoding_facial': encoding_simulado,
            'fotos_dropbox_urls': fotos_urls,
            'activo': True,
            'confianza_promedio': random.uniform(85, 95)
        }
    )
    
    if created:
        print(f'✅ Reconocimiento facial creado para: {copropietario.nombres} {copropietario.apellidos}')
    else:
        print(f'ℹ️  Reconocimiento facial ya existe para: {copropietario.nombres} {copropietario.apellidos}')

print()
print('📊 ESTADÍSTICAS FINALES:')
total_copropietarios = Copropietarios.objects.count()
registros_facial_activos = ReconocimientoFacial.objects.filter(activo=True).count()

print(f'   👥 Total copropietarios: {total_copropietarios}')
print(f'   🔍 Reconocimiento facial activo: {registros_facial_activos}')
print()

print('✅ DATOS DE PRUEBA CREADOS CORRECTAMENTE')
print()
print('🧪 PARA PROBAR EL SISTEMA:')
print('   1. Ejecuta: python manage.py runserver')
print('   2. Ve a: http://127.0.0.1:8000/api/seguridad/panel-guardia/')
print('   3. En la pestaña \"Lista de Residentes\" verás los usuarios creados')
print('   4. En \"Reconocimiento Facial\" puedes subir cualquier imagen')
print('   5. El sistema simulará la comparación (con encodings aleatorios)')
print()
print('💡 NOTA: Los encodings son simulados, en producción vendrían de face_recognition')
"

Write-Host ""
Write-Host "🚀 DATOS DE PRUEBA LISTOS!" -ForegroundColor Magenta
Write-Host "   Ahora puedes probar el panel del guardia" -ForegroundColor White