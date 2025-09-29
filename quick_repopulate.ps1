# Script Rápido - Solo Eliminar y Repoblar Datos (Mantiene Estructura DB)

Write-Host "🗑️ ELIMINANDO DATOS EXISTENTES..." -ForegroundColor Yellow

python manage.py shell -c "
from authz.models import *
from core.models import *
from seguridad.models import *
from expensas_multas.models import *

# Eliminar datos pero mantener estructura
print('Eliminando usuarios...')
Usuario.objects.all().delete()

print('Eliminando personas...')
Persona.objects.all().delete()

print('Eliminando solicitudes...')
SolicitudRegistroPropietario.objects.all().delete()

print('Eliminando viviendas...')
Vivienda.objects.all().delete()

print('Eliminando reconocimiento facial...')
ReconocimientoFacial.objects.all().delete()

print('✅ Datos eliminados, estructura preservada')
"

Write-Host "📊 POBLANDO CON DATOS FRESCOS..." -ForegroundColor Green

# Ejecutar el mismo script de población
python manage.py shell -c "
from core.models import Vivienda
from authz.models import SolicitudRegistroPropietario, Persona, Usuario, Rol
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import random

print('👤 Creando admin...')

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

print('✅ Admin creado')

print('🏠 Creando viviendas...')

# Viviendas variadas
viviendas_data = [
    # Apartamentos Bloque A
    {'numero_casa': 'Apto 101', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 1, 'metros_cuadrados': 80.5},
    {'numero_casa': 'Apto 102', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 1, 'metros_cuadrados': 85.0},
    {'numero_casa': 'Apto 201', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 2, 'metros_cuadrados': 90.0},
    {'numero_casa': 'Apto 202', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 2, 'metros_cuadrados': 87.5},
    {'numero_casa': 'Apto 301', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 3, 'metros_cuadrados': 95.0},
    {'numero_casa': 'Apto 302', 'tipo_vivienda': 'Apartamento', 'bloque': 'A', 'piso': 3, 'metros_cuadrados': 92.0},
    
    # Apartamentos Bloque B
    {'numero_casa': 'Apto 101', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 1, 'metros_cuadrados': 75.0},
    {'numero_casa': 'Apto 102', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 1, 'metros_cuadrados': 80.0},
    {'numero_casa': 'Apto 201', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 2, 'metros_cuadrados': 88.0},
    {'numero_casa': 'Apto 202', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 2, 'metros_cuadrados': 82.5},
    {'numero_casa': 'Apto 301', 'tipo_vivienda': 'Apartamento', 'bloque': 'B', 'piso': 3, 'metros_cuadrados': 89.0},
    
    # Apartamentos Bloque C
    {'numero_casa': 'Apto 101', 'tipo_vivienda': 'Apartamento', 'bloque': 'C', 'piso': 1, 'metros_cuadrados': 78.5},
    {'numero_casa': 'Apto 102', 'tipo_vivienda': 'Apartamento', 'bloque': 'C', 'piso': 1, 'metros_cuadrados': 83.0},
    {'numero_casa': 'Apto 201', 'tipo_vivienda': 'Apartamento', 'bloque': 'C', 'piso': 2, 'metros_cuadrados': 86.0},
    {'numero_casa': 'Apto 202', 'tipo_vivienda': 'Apartamento', 'bloque': 'C', 'piso': 2, 'metros_cuadrados': 91.5},
    
    # Casas
    {'numero_casa': 'Casa 1', 'tipo_vivienda': 'Casa', 'bloque': '', 'piso': None, 'metros_cuadrados': 120.0},
    {'numero_casa': 'Casa 2', 'tipo_vivienda': 'Casa', 'bloque': '', 'piso': None, 'metros_cuadrados': 135.0},
    {'numero_casa': 'Casa 3', 'tipo_vivienda': 'Casa', 'bloque': '', 'piso': None, 'metros_cuadrados': 150.0},
    {'numero_casa': 'Casa 4', 'tipo_vivienda': 'Casa', 'bloque': '', 'piso': None, 'metros_cuadrados': 180.0},
    {'numero_casa': 'Casa 5', 'tipo_vivienda': 'Casa', 'bloque': '', 'piso': None, 'metros_cuadrados': 200.0},
    {'numero_casa': 'Casa 6', 'tipo_vivienda': 'Casa', 'bloque': '', 'piso': None, 'metros_cuadrados': 165.0},
    
    # Penthouses
    {'numero_casa': 'PH 401', 'tipo_vivienda': 'Penthouse', 'bloque': 'A', 'piso': 4, 'metros_cuadrados': 150.0},
    {'numero_casa': 'PH 402', 'tipo_vivienda': 'Penthouse', 'bloque': 'B', 'piso': 4, 'metros_cuadrados': 160.0},
    {'numero_casa': 'PH 403', 'tipo_vivienda': 'Penthouse', 'bloque': 'C', 'piso': 4, 'metros_cuadrados': 155.0},
    
    # Dúplex
    {'numero_casa': 'Duplex 1A', 'tipo_vivienda': 'Duplex', 'bloque': 'D', 'piso': None, 'metros_cuadrados': 110.0},
    {'numero_casa': 'Duplex 1B', 'tipo_vivienda': 'Duplex', 'bloque': 'D', 'piso': None, 'metros_cuadrados': 115.0},
    {'numero_casa': 'Duplex 2A', 'tipo_vivienda': 'Duplex', 'bloque': 'D', 'piso': None, 'metros_cuadrados': 108.0},
    {'numero_casa': 'Duplex 2B', 'tipo_vivienda': 'Duplex', 'bloque': 'D', 'piso': None, 'metros_cuadrados': 112.0},
]

for vivienda_data in viviendas_data:
    Vivienda.objects.create(**vivienda_data)

print(f'✅ {len(viviendas_data)} viviendas creadas')

print('📝 Creando solicitudes de prueba...')

# Solicitudes variadas con diferentes estados
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
        'bloque': '',
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
        'bloque': '',
        'fecha_nacimiento': '1975-12-14'
    },
    {
        'nombres': 'Lucía Fernanda',
        'apellidos': 'Ramírez Castro',
        'documento_identidad': '99887766',
        'email': 'lucia.ramirez@gmail.com',
        'telefono': '76789012',
        'numero_casa': 'Duplex 1A',
        'bloque': 'D',
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
        'bloque': '',
        'fecha_nacimiento': '1980-06-18'
    },
    {
        'nombres': 'Diego Fernando',
        'apellidos': 'Morales Jiménez',
        'documento_identidad': '36925814',
        'email': 'diego.morales@gmail.com',
        'telefono': '79012345',
        'numero_casa': 'Apto 301',
        'bloque': 'C',
        'fecha_nacimiento': '1987-04-12'
    },
    {
        'nombres': 'Valentina Isabel',
        'apellidos': 'Cruz Mendoza',
        'documento_identidad': '14785236',
        'email': 'valentina.cruz@outlook.com',
        'telefono': '70123456',
        'numero_casa': 'PH 402',
        'bloque': 'B',
        'fecha_nacimiento': '1991-08-27'
    }
]

for solicitud_data in solicitudes_data:
    try:
        vivienda = Vivienda.objects.get(
            numero_casa=solicitud_data['numero_casa'],
            bloque=solicitud_data['bloque']
        )
        
        solicitud = SolicitudRegistroPropietario.objects.create(
            nombres=solicitud_data['nombres'],
            apellidos=solicitud_data['apellidos'],
            documento_identidad=solicitud_data['documento_identidad'],
            email=solicitud_data['email'],
            telefono=solicitud_data['telefono'],
            numero_casa=solicitud_data['numero_casa'],
            bloque=solicitud_data['bloque'],
            fecha_nacimiento=solicitud_data['fecha_nacimiento'],
            vivienda_validada=vivienda,
            estado='PENDIENTE',
            fotos_reconocimiento_urls=[],
            token_seguimiento=f'SOL-{random.randint(100000, 999999)}'
        )
        print(f'✅ {solicitud.nombres} {solicitud.apellidos} - {solicitud.numero_casa}')
        
    except Vivienda.DoesNotExist:
        print(f'❌ Vivienda no encontrada: {solicitud_data[\"numero_casa\"]} - {solicitud_data[\"bloque\"]}')

print('✅ Datos poblados correctamente')
"

Write-Host ""
Write-Host "🎉 BASE DE DATOS REPOBLADA EXITOSAMENTE" -ForegroundColor Green
Write-Host ""
Write-Host "📊 DATOS FRESCOS CREADOS:" -ForegroundColor Cyan
Write-Host "   👤 Admin: admin@condominio.com / admin123" -ForegroundColor Yellow
Write-Host "   🏠 27 Viviendas disponibles (Apartamentos A,B,C + Casas + Penthouses + Dúplex)" -ForegroundColor Yellow
Write-Host "   📝 10 Solicitudes PENDIENTES para aprobar" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔥 LISTO PARA PRUEBAS DEL FRONTEND!" -ForegroundColor Magenta