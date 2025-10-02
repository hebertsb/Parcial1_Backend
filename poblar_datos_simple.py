#!/usr/bin/env python
"""
🏠 SCRIPT SIMPLE PARA POBLAR BASE DE DATOS
Versión simplificada que funciona correctamente

Ejecutar: python poblar_datos_simple.py
"""

import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Imports después de configurar Django
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from authz.models import (
    Usuario, Persona, Rol, FamiliarPropietario, 
    SolicitudRegistroPropietario, RelacionesPropietarioInquilino
)
from core.models.propiedades_residentes import Vivienda, Propiedad
from seguridad.models import Copropietarios, ReconocimientoFacial

User = get_user_model()

def crear_roles_basicos():
    """Crear roles básicos del sistema"""
    print("👥 Creando roles básicos...")
    
    roles = [
        ('Administrador', 'Administrador del sistema'),
        ('Propietario', 'Propietario de vivienda'),
        ('Inquilino', 'Inquilino de vivienda'),
        ('Seguridad', 'Personal de seguridad'),
        ('Familiar', 'Familiar de residente')
    ]
    
    for nombre, descripcion in roles:
        rol, created = Rol.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"  ✅ Rol creado: {nombre}")
        else:
            print(f"  ℹ️ Rol existente: {nombre}")

def crear_viviendas_basicas():
    """Crear viviendas básicas"""
    print("🏠 Creando viviendas básicas...")
    
    viviendas_data = [
        ("CASA-001", "casa", 120, 250, "A"),
        ("CASA-002", "casa", 100, 220, None),
        ("CASA-003", "departamento", 80, 180, "B"),
        ("CASA-004", "casa", 150, 300, None),
        ("CASA-005", "departamento", 90, 200, "C"),
    ]
    
    for numero, tipo, metros, tarifa, bloque in viviendas_data:
        vivienda, created = Vivienda.objects.get_or_create(
            numero_casa=numero,
            defaults={
                'tipo_vivienda': tipo,
                'metros_cuadrados': Decimal(str(metros)),
                'tarifa_base_expensas': Decimal(str(tarifa)),
                'tipo_cobranza': 'por_casa',
                'estado': 'activa',
                'bloque': bloque
            }
        )
        if created:
            print(f"  ✅ Vivienda creada: {numero}")

def crear_usuarios_basicos():
    """Crear usuarios básicos para pruebas"""
    print("👤 Creando usuarios básicos...")
    
    # Crear administradores
    print("  👔 Creando administradores...")
    admins_data = [
        ("Juan", "Pérez", "12345678", "admin@condominio.com"),
        ("María", "González", "87654321", "admin2@condominio.com"),
    ]
    
    rol_admin = Rol.objects.get(nombre='Administrador')
    
    for nombre, apellido, doc, email in admins_data:
        # Crear persona
        persona, created = Persona.objects.get_or_create(
            documento_identidad=doc,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'telefono': f"555-{doc[:4]}",
                'email': email,
                'fecha_nacimiento': date(1980, 1, 1),
                'genero': 'M',
                'tipo_persona': 'administrador',
                'activo': True
            }
        )
        
        if created:
            # Crear usuario
            usuario = Usuario.objects.create_user(
                email=email,
                password="temporal123",
                persona=persona,
                estado='ACTIVO'
            )
            usuario.roles.add(rol_admin)
            usuario.is_staff = True
            usuario.save()
            
            # Crear copropietario para seguridad
            Copropietarios.objects.create(
                nombres=nombre,
                apellidos=apellido,
                numero_documento=doc,
                telefono=persona.telefono,
                email=email,
                unidad_residencial="Administración",
                tipo_residente='Administrador',
                usuario_sistema=usuario,
                activo=True
            )
            
            print(f"    ✅ Admin creado: {email}")
    
    # Crear usuarios de seguridad
    print("  👮‍♂️ Creando personal de seguridad...")
    seguridad_data = [
        ("Carlos", "Ramírez", "11111111", "seguridad1@condominio.com"),
        ("Ana", "López", "22222222", "seguridad2@condominio.com"),
        ("Pedro", "Martín", "33333333", "seguridad3@condominio.com"),
    ]
    
    rol_seguridad = Rol.objects.get(nombre='Seguridad')
    
    for nombre, apellido, doc, email in seguridad_data:
        persona, created = Persona.objects.get_or_create(
            documento_identidad=doc,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'telefono': f"555-{doc[:4]}",
                'email': email,
                'fecha_nacimiento': date(1985, 1, 1),
                'genero': 'M' if nombre in ['Carlos', 'Pedro'] else 'F',
                'tipo_persona': 'seguridad',
                'activo': True
            }
        )
        
        if created:
            usuario = Usuario.objects.create_user(
                email=email,
                password="temporal123",
                persona=persona,
                estado='ACTIVO'
            )
            usuario.roles.add(rol_seguridad)
            
            Copropietarios.objects.create(
                nombres=nombre,
                apellidos=apellido,
                numero_documento=doc,
                telefono=persona.telefono,
                email=email,
                unidad_residencial="Seguridad",
                tipo_residente='Seguridad',
                usuario_sistema=usuario,
                activo=True
            )
            
            print(f"    ✅ Seguridad creado: {email}")
    
    # Crear propietarios
    print("  👨‍💼 Creando propietarios...")
    propietarios_data = [
        ("Roberto", "Silva", "44444444", "roberto@email.com", "CASA-001"),
        ("Laura", "Torres", "55555555", "laura@email.com", "CASA-002"),
        ("Diego", "Morales", "66666666", "diego@email.com", "CASA-004"),
    ]
    
    rol_propietario = Rol.objects.get(nombre='Propietario')
    
    for nombre, apellido, doc, email, casa in propietarios_data:
        persona, created = Persona.objects.get_or_create(
            documento_identidad=doc,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'telefono': f"555-{doc[:4]}",
                'email': email,
                'fecha_nacimiento': date(1975, 1, 1),
                'genero': 'M' if nombre in ['Roberto', 'Diego'] else 'F',
                'tipo_persona': 'propietario',
                'activo': True
            }
        )
        
        if created:
            usuario = Usuario.objects.create_user(
                email=email,
                password="temporal123",
                persona=persona,
                estado='ACTIVO'
            )
            usuario.roles.add(rol_propietario)
            
            # Crear propiedad
            vivienda = Vivienda.objects.get(numero_casa=casa)
            Propiedad.objects.create(
                vivienda=vivienda,
                persona=persona,
                tipo_tenencia='propietario',
                porcentaje_propiedad=Decimal('100.00'),
                fecha_inicio_tenencia=date(2023, 1, 1),
                activo=True
            )
            
            # Crear copropietario para seguridad
            Copropietarios.objects.create(
                nombres=nombre,
                apellidos=apellido,
                numero_documento=doc,
                telefono=persona.telefono,
                email=email,
                unidad_residencial=f"Casa {casa}",
                tipo_residente='Propietario',
                usuario_sistema=usuario,
                activo=True
            )
            
            print(f"    ✅ Propietario creado: {email} - {casa}")
    
    # Crear inquilinos
    print("  🏠 Creando inquilinos...")
    inquilinos_data = [
        ("Sofia", "Vega", "77777777", "sofia@email.com", "CASA-003"),
        ("Miguel", "Herrera", "88888888", "miguel@email.com", "CASA-005"),
    ]
    
    rol_inquilino = Rol.objects.get(nombre='Inquilino')
    
    for nombre, apellido, doc, email, casa in inquilinos_data:
        persona, created = Persona.objects.get_or_create(
            documento_identidad=doc,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'telefono': f"555-{doc[:4]}",
                'email': email,
                'fecha_nacimiento': date(1990, 1, 1),
                'genero': 'F' if nombre == 'Sofia' else 'M',
                'tipo_persona': 'inquilino',
                'activo': True
            }
        )
        
        if created:
            usuario = Usuario.objects.create_user(
                email=email,
                password="temporal123",
                persona=persona,
                estado='ACTIVO'
            )
            usuario.roles.add(rol_inquilino)
            
            # Crear copropietario para seguridad
            Copropietarios.objects.create(
                nombres=nombre,
                apellidos=apellido,
                numero_documento=doc,
                telefono=persona.telefono,
                email=email,
                unidad_residencial=f"Casa {casa}",
                tipo_residente='Inquilino',
                usuario_sistema=usuario,
                activo=True
            )
            
            print(f"    ✅ Inquilino creado: {email} - {casa}")

def crear_reconocimiento_facial():
    """Crear registros básicos de reconocimiento facial"""
    print("📸 Configurando reconocimiento facial...")
    
    copropietarios_sin_reconocimiento = Copropietarios.objects.filter(reconocimiento_facial__isnull=True)
    
    for copropietario in copropietarios_sin_reconocimiento:
        ReconocimientoFacial.objects.create(
            copropietario=copropietario,
            proveedor_ia='Local',
            vector_facial="[]",  # Vacío por ahora
            activo=True
        )
        print(f"  ✅ Reconocimiento configurado: {copropietario.nombre_completo}")

def crear_solicitudes_ejemplo():
    """Crear algunas solicitudes de ejemplo"""
    print("📄 Creando solicitudes de ejemplo...")
    
    solicitudes_data = [
        ("Luis", "Mendoza", "99999999", "luis@email.com", "CASA-001", "PENDIENTE"),
        ("Carmen", "Ruiz", "10101010", "carmen@email.com", "CASA-002", "EN_REVISION"),
    ]
    
    for nombres, apellidos, doc, email, casa, estado in solicitudes_data:
        vivienda = Vivienda.objects.filter(numero_casa=casa).first()
        
        SolicitudRegistroPropietario.objects.get_or_create(
            documento_identidad=doc,
            defaults={
                'nombres': nombres,
                'apellidos': apellidos,
                'email': email,
                'telefono': f"555-{doc[:4]}",
                'numero_casa': casa,
                'vivienda_validada': vivienda,
                'estado': estado,
                'fecha_nacimiento': date(1980, 1, 1),
                'token_seguimiento': f"TOKEN-{doc}",
            }
        )
        print(f"  ✅ Solicitud creada: {nombres} {apellidos} - {estado}")

def mostrar_resumen():
    """Mostrar resumen de datos creados"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("="*60)
    
    print(f"🏠 Viviendas: {Vivienda.objects.count()}")
    print(f"👥 Personas: {Persona.objects.count()}")
    print(f"👤 Usuarios: {Usuario.objects.count()}")
    
    print("\n📋 Por tipo de usuario:")
    for rol in Rol.objects.all():
        count = Usuario.objects.filter(roles=rol).count()
        emoji = {
            'Administrador': '👔',
            'Propietario': '👨‍💼',
            'Inquilino': '🏠',
            'Seguridad': '👮‍♂️',
            'Familiar': '👨‍👩‍👧‍👦'
        }.get(rol.nombre, '👤')
        print(f"  {emoji} {rol.nombre}: {count}")
    
    print(f"\n🔐 Copropietarios: {Copropietarios.objects.count()}")
    print(f"📸 Reconocimientos: {ReconocimientoFacial.objects.count()}")
    print(f"📄 Solicitudes: {SolicitudRegistroPropietario.objects.count()}")
    
    print("\n🔑 Credenciales:")
    print("  🔒 Contraseña: temporal123")
    print("  🌐 Sistema: http://127.0.0.1:8000/")
    
    print("\n" + "="*60)

def main():
    """Función principal"""
    print("🚀 POBLANDO BASE DE DATOS - VERSIÓN SIMPLE")
    print("="*60)
    
    try:
        with transaction.atomic():
            crear_roles_basicos()
            crear_viviendas_basicas()
            crear_usuarios_basicos()
            crear_reconocimiento_facial()
            crear_solicitudes_ejemplo()
        
        mostrar_resumen()
        print("✅ POBLADO COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error durante el poblado: {e}")
        raise

if __name__ == "__main__":
    main()