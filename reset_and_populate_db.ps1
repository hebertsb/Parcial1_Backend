# Script para Resetear y Poblar la Base de Datos para Pruebas

# IMPORTANTE: Este script eliminará TODOS los datos existentes

# 1. ELIMINAR BASE DE DATOS
Remove-Item db.sqlite3 -Force -ErrorAction SilentlyContinue

# 2. ELIMINAR MIGRACIONES (mantener __init__.py)
Get-ChildItem -Path "*/migrations" -Recurse | Where-Object { $_.Name -match "^\d+.*\.py$" } | Remove-Item -Force
Write-Host "Migraciones eliminadas" -ForegroundColor Green

# 3. CREAR NUEVAS MIGRACIONES
python manage.py makemigrations
Write-Host "Nuevas migraciones creadas" -ForegroundColor Green

# 4. APLICAR MIGRACIONES
python manage.py migrate
Write-Host "Base de datos creada" -ForegroundColor Green

# 5. CREAR SUPERUSUARIO ADMIN
python manage.py shell -c "
from authz.models import Usuario, Rol, Persona
from django.contrib.auth.hashers import make_password

# Crear persona para admin
persona_admin = Persona.objects.create(
    nombre='Admin',
    apellido='Sistema',
    documento_identidad='00000000',
    telefono='70000000',
    email='admin@condominio.com',
    tipo_persona='administrador'
)

# Crear rol administrador
rol_admin, _ = Rol.objects.get_or_create(
    nombre='Administrador',
    defaults={'descripcion': 'Administrador del sistema'}
)

# Crear usuario admin
admin_user = Usuario.objects.create(
    email='admin@condominio.com',
    password=make_password('admin123'),
    persona=persona_admin,
    estado='ACTIVO',
    is_staff=True,
    is_superuser=True
)
admin_user.roles.add(rol_admin)

print('✅ Admin creado - Email: admin@condominio.com, Password: admin123')
"

# 6. POBLAR CON DATOS DE PRUEBA
python manage.py shell -c "
from core.models import Vivienda
from authz.models import SolicitudRegistroPropietario, Persona, Usuario, Rol
from django.utils import timezone
import random

print('🏠 Creando viviendas...')

# Crear viviendas variadas
viviendas_data = [
    # Apartamentos
    {'numero_casa': 'Apto 101', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 1, 'metros_cuadrados': 80.5},
    {'numero_casa': 'Apto 102', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 1, 'metros_cuadrados': 85.0},
    {'numero_casa': 'Apto 201', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 2, 'metros_cuadrados': 90.0},
    {'numero_casa': 'Apto 202', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 2, 'metros_cuadrados': 87.5},
    {'numero_casa': 'Apto 301', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 3, 'metros_cuadrados': 95.0},
    
    {'numero_casa': 'Apto 101', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 1, 'metros_cuadrados': 75.0},
    {'numero_casa': 'Apto 102', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 1, 'metros_cuadrados': 80.0},
    {'numero_casa': 'Apto 201', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 2, 'metros_cuadrados': 88.0},
    {'numero_casa': 'Apto 202', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 2, 'metros_cuadrados': 82.5},
    
    # Casas
    {'numero_casa': 'Casa 1', 'tipo_vivienda': 'Casa', 'bloque': None, 'piso': None, 'metros_cuadrados': 120.0},
    {'numero_casa': 'Casa 2', 'tipo_vivienda': 'Casa', 'bloque': None, 'piso': None, 'metros_cuadrados': 135.0},
    {'numero_casa': 'Casa 3', 'tipo_vivienda': 'Casa', 'bloque': None, 'piso': None, 'metros_cuadrados': 150.0},
    {'numero_casa': 'Casa 4', 'tipo_vivienda': 'Casa', 'bloque': None, 'piso': None, 'metros_cuadrados': 180.0},
    {'numero_casa': 'Casa 5', 'tipo_vivienda': 'Casa', 'bloque': None, 'piso': None, 'metros_cuadrados': 200.0},
    
    # Penthouses
    {'numero_casa': 'PH 401', 'tipo_vivienda': 'Penthouse', 'bloque': 'A', 'piso': 4, 'metros_cuadrados': 150.0},
    {'numero_casa': 'PH 402', 'tipo_vivienda': 'Penthouse', 'bloque': 'B', 'piso': 4, 'metros_cuadrados': 160.0},
    
    # Dúplex
    {'numero_casa': 'Duplex 1', 'tipo_vivienda': 'Duplex', 'bloque': 'C', 'piso': None, 'metros_cuadrados': 110.0},
    {'numero_casa': 'Duplex 2', 'tipo_vivienda': 'Duplex', 'bloque': 'C', 'piso': None, 'metros_cuadrados': 115.0},
]

for vivienda_data in viviendas_data:
    Vivienda.objects.get_or_create(
        numero_casa=vivienda_data['numero_casa'],
        bloque=vivienda_data['bloque'],
        defaults=vivienda_data
    )

print(f'✅ {len(viviendas_data)} viviendas creadas')

# Crear solicitudes de prueba variadas
print('📝 Creando solicitudes de prueba...')

solicitudes_data = [
    {
        'nombres': 'Carlos Alberto',
        'apellidos': 'Rodríguez Pérez',
        'documento_identidad': '12345678',
        'email': 'carlos.rodriguez@gmail.com',
        'telefono': '71234567',
        'numero_casa': 'Apto 101',
        'bloque': 'A',
        'fecha_nacimiento': '1985-03-15'
    },
    {
        'nombres': 'María Elena',
        'apellidos': 'González López',
        'documento_identidad': '87654321',
        'email': 'maria.gonzalez@hotmail.com',
        'telefono': '72345678',
        'numero_casa': 'Casa 1',
        'bloque': None,
        'fecha_nacimiento': '1978-07-22'
    },
    {
        'nombres': 'José Miguel',
        'apellidos': 'Hernández Torres',
        'documento_identidad': '11223344',
        'email': 'jose.hernandez@yahoo.com',
        'telefono': '73456789',
        'numero_casa': 'Apto 201',
        'bloque': 'B',
        'fecha_nacimiento': '1990-11-08'
    },
    {
        'nombres': 'Ana Sofía',
        'apellidos': 'Martínez Silva',
        'documento_identidad': '44332211',
        'email': 'ana.martinez@gmail.com',
        'telefono': '74567890',
        'numero_casa': 'PH 401',
        'bloque': 'A',
        'fecha_nacimiento': '1982-05-30'
    },
    {
        'nombres': 'Roberto Carlos',
        'apellidos': 'Vásquez Morales',
        'documento_identidad': '55667788',
        'email': 'roberto.vasquez@outlook.com',
        'telefono': '75678901',
        'numero_casa': 'Casa 3',
        'bloque': None,
        'fecha_nacimiento': '1975-12-14'
    },
    {
        'nombres': 'Lucía Fernanda',
        'apellidos': 'Ramírez Castro',
        'documento_identidad': '99887766',
        'email': 'lucia.ramirez@gmail.com',
        'telefono': '76789012',
        'numero_casa': 'Duplex 1',
        'bloque': 'C',
        'fecha_nacimiento': '1988-09-03'
    },
    {
        'nombres': 'Pedro Antonio',
        'apellidos': 'Salazar Mendoza',
        'documento_identidad': '13579246',
        'email': 'pedro.salazar@hotmail.com',
        'telefono': '77890123',
        'numero_casa': 'Apto 102',
        'bloque': 'B',
        'fecha_nacimiento': '1993-01-25'
    },
    {
        'nombres': 'Carmen Rosa',
        'apellidos': 'Delgado Vargas',
        'documento_identidad': '24681357',
        'email': 'carmen.delgado@yahoo.com',
        'telefono': '78901234',
        'numero_casa': 'Casa 5',
        'bloque': None,
        'fecha_nacimiento': '1980-06-18'
    }
]

for solicitud_data in solicitudes_data:
    # Buscar la vivienda correspondiente
    try:
        vivienda = Vivienda.objects.get(
            numero_casa=solicitud_data['numero_casa'],
            bloque=solicitud_data.get('bloque')
        )
        
        solicitud = SolicitudRegistroPropietario.objects.create(
            nombres=solicitud_data['nombres'],
            apellidos=solicitud_data['apellidos'],
            documento_identidad=solicitud_data['documento_identidad'],
            email=solicitud_data['email'],
            telefono=solicitud_data['telefono'],
            numero_casa=solicitud_data['numero_casa'],
            bloque=solicitud_data.get('bloque', ''),
            fecha_nacimiento=solicitud_data['fecha_nacimiento'],
            vivienda_validada=vivienda,
            estado='PENDIENTE',
            fotos_reconocimiento_urls=[],
            token_seguimiento=f'SOL-{random.randint(100000, 999999)}'
        )
        print(f'✅ Solicitud creada: {solicitud.nombres} {solicitud.apellidos} - {solicitud.numero_casa}')
        
    except Vivienda.DoesNotExist:
        print(f'❌ Vivienda no encontrada: {solicitud_data[\"numero_casa\"]} - {solicitud_data.get(\"bloque\", \"Sin bloque\")}')

print('✅ Solicitudes de prueba creadas')
"

Write-Host ""
Write-Host "🎉 BASE DE DATOS POBLADA EXITOSAMENTE" -ForegroundColor Green
Write-Host ""
Write-Host "📊 DATOS CREADOS:" -ForegroundColor Cyan
Write-Host "   👤 Admin: admin@condominio.com / admin123" -ForegroundColor Yellow
Write-Host "   🏠 18 Viviendas (Apartamentos, Casas, Penthouses, Dúplex)" -ForegroundColor Yellow
Write-Host "   📝 8 Solicitudes PENDIENTES para aprobar" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 PARA INICIAR EL SERVIDOR:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "🔗 ENDPOINTS DE PRUEBA:" -ForegroundColor Cyan
Write-Host "   GET /api/authz/propietarios/admin/solicitudes/" -ForegroundColor White
Write-Host "   POST /api/authz/propietarios/admin/solicitudes/{id}/aprobar/" -ForegroundColor White
Write-Host ""