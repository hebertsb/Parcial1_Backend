#!/usr/bin/env python
"""
🏠 SCRIPT PARA POBLAR BASE DE DATOS COMPLETA
Sistema de Reconocimiento Facial - Condominio

Este script crea:
✅ 50 Propietarios con registro completo
✅ 20 Inquilinos 
✅ 2 Administradores
✅ 5 Usuarios de Seguridad
✅ 30 Familiares de Propietarios
✅ 20 Familiares de Inquilinos
✅ Viviendas necesarias
✅ Registros de reconocimiento facial
✅ Solicitudes de registro (algunas aprobadas, otras pendientes)

Ejecutar: python poblar_base_datos_completa.py
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random
from faker import Faker

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

# Configurar Faker para datos en español
fake = Faker('es_ES')
User = get_user_model()

class PobladorBaseDatos:
    """Clase para poblar la base de datos con datos de prueba"""
    
    def __init__(self):
        self.viviendas_creadas = []
        self.propietarios_creados = []
        self.inquilinos_creados = []
        self.admin_creados = []
        self.seguridad_creados = []
        
    def limpiar_datos_anteriores(self):
        """⚠️ CUIDADO: Limpia datos de prueba anteriores"""
        print("🧹 Limpiando datos anteriores...")
        
        try:
            with transaction.atomic():
                # Eliminar en orden correcto para evitar errores de FK
                ReconocimientoFacial.objects.filter(copropietario__nombres__contains='TEST').delete()
                Copropietarios.objects.filter(nombres__contains='TEST').delete()
                FamiliarPropietario.objects.all().delete()
                RelacionesPropietarioInquilino.objects.all().delete()
                SolicitudRegistroPropietario.objects.filter(nombres__contains='TEST').delete()
                Propiedad.objects.all().delete()
                
                # Eliminar usuarios pero mantener superusuarios
                Usuario.objects.filter(is_superuser=False).delete()
                Persona.objects.all().delete()
                
                # Solo eliminar viviendas de prueba
                Vivienda.objects.filter(numero_casa__startswith='CASA-').delete()
                
        except Exception as e:
            print(f"⚠️ Advertencia durante limpieza: {e}")
            
        print("✅ Datos anteriores limpiados")

    def crear_roles_basicos(self):
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

    def crear_viviendas(self, cantidad=100):
        """Crear viviendas para el condominio"""
        print(f"🏠 Creando {cantidad} viviendas...")
        
        tipos_vivienda = ['Casa', 'Departamento']
        bloques = ['A', 'B', 'C', 'D', 'E']
        
        for i in range(1, cantidad + 1):
            tipo = random.choice(tipos_vivienda)
            bloque = random.choice(bloques) if tipo == 'Departamento' else None
            
            vivienda = Vivienda.objects.create(
                numero_casa=f"CASA-{i:03d}",
                bloque=bloque,
                tipo_vivienda='casa' if tipo == 'Casa' else 'departamento',
                metros_cuadrados=Decimal(str(random.randint(80, 200))),
                tarifa_base_expensas=Decimal(str(random.randint(100, 300))),
                tipo_cobranza='por_casa',
                estado='activa'
            )
            self.viviendas_creadas.append(vivienda)
            
        print(f"✅ {len(self.viviendas_creadas)} viviendas creadas")

    def crear_persona_base(self, tipo_persona, incluir_reconocimiento=True):
        """Crear una persona base con datos aleatorios"""
        genero = random.choice(['M', 'F'])
        
        if genero == 'M':
            nombre = fake.first_name_male()
        else:
            nombre = fake.first_name_female()
            
        apellido = fake.last_name()
        documento = fake.unique.random_number(digits=8, fix_len=True)
        
        persona = Persona.objects.create(
            nombre=nombre,
            apellido=apellido,
            documento_identidad=str(documento),
            telefono=fake.phone_number()[:15],
            email=fake.unique.email(),
            fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=80),
            genero=genero,
            tipo_persona=tipo_persona,
            activo=True
        )
        
        return persona

    def crear_usuario_con_rol(self, persona, rol_nombre, password="temporal123"):
        """Crear usuario del sistema con rol específico"""
        rol = Rol.objects.get(nombre=rol_nombre)
        
        usuario = Usuario.objects.create_user(
            email=persona.email,
            password=password,
            persona=persona,
            estado='ACTIVO'
        )
        usuario.roles.add(rol)
        
        return usuario

    def crear_copropietario_seguridad(self, persona, tipo_residente, vivienda=None):
        """Crear registro en seguridad.Copropietarios"""
        unidad = f"Casa {vivienda.numero_casa}" if vivienda else "Administración"
        
        copropietario = Copropietarios.objects.create(
            nombres=persona.nombre,
            apellidos=persona.apellido,
            numero_documento=persona.documento_identidad,
            telefono=persona.telefono,
            email=persona.email,
            unidad_residencial=unidad,
            tipo_residente=tipo_residente,
            activo=True
        )
        
        # Crear reconocimiento facial básico
        ReconocimientoFacial.objects.create(
            copropietario=copropietario,
            proveedor_ia='Local',
            vector_facial="[]",  # Vacío por ahora
            activo=True
        )
        
        return copropietario

    def crear_propietarios(self, cantidad=50):
        """Crear propietarios completos"""
        print(f"👨‍💼 Creando {cantidad} propietarios...")
        
        viviendas_disponibles = self.viviendas_creadas[:cantidad]
        
        for i, vivienda in enumerate(viviendas_disponibles):
            # Crear persona
            persona = self.crear_persona_base('propietario')
            
            # Crear usuario
            usuario = self.crear_usuario_con_rol(persona, 'Propietario')
            
            # Crear propiedad
            Propiedad.objects.create(
                vivienda=vivienda,
                persona=persona,
                tipo_tenencia='propietario',
                porcentaje_propiedad=Decimal('100.00'),
                fecha_inicio_tenencia=fake.date_between(start_date='-5y', end_date='today'),
                activo=True
            )
            
            # Crear copropietario para seguridad
            copropietario = self.crear_copropietario_seguridad(persona, 'Propietario', vivienda)
            copropietario.usuario_sistema = usuario
            copropietario.save()
            
            # Crear algunas solicitudes (mezclando estados)
            if i < 40:  # 40 aprobadas
                estado = 'APROBADA'
                fecha_revision = timezone.make_aware(datetime.combine(fake.date_between(start_date='-1y', end_date='today'), datetime.min.time()))
            elif i < 45:  # 5 pendientes
                estado = 'PENDIENTE'
                fecha_revision = None
            else:  # 5 en revisión
                estado = 'EN_REVISION'
                fecha_revision = timezone.make_aware(datetime.combine(fake.date_between(start_date='-30d', end_date='today'), datetime.min.time()))
                
            SolicitudRegistroPropietario.objects.create(
                nombres=persona.nombre,
                apellidos=persona.apellido,
                documento_identidad=persona.documento_identidad,
                fecha_nacimiento=persona.fecha_nacimiento,
                email=persona.email,
                telefono=persona.telefono,
                numero_casa=vivienda.numero_casa,
                vivienda_validada=vivienda,
                estado=estado,
                fecha_revision=fecha_revision,
                usuario_creado=usuario if estado == 'APROBADA' else None,
                token_seguimiento=fake.uuid4()[:16]
            )
            
            self.propietarios_creados.append(usuario)
            
        print(f"✅ {len(self.propietarios_creados)} propietarios creados")

    def crear_inquilinos(self, cantidad=20):
        """Crear inquilinos con relación a propietarios"""
        print(f"🏠 Creando {cantidad} inquilinos...")
        
        propietarios_disponibles = random.sample(self.propietarios_creados, min(cantidad, len(self.propietarios_creados)))
        
        for propietario in propietarios_disponibles:
            # Crear persona inquilino
            persona = self.crear_persona_base('inquilino')
            
            # Crear usuario
            usuario = self.crear_usuario_con_rol(persona, 'Inquilino')
            
            # Obtener vivienda del propietario
            propiedad_propietario = Propiedad.objects.filter(
                persona=propietario.persona,
                tipo_tenencia='propietario'
            ).first()
            
            if propiedad_propietario:
                # Crear relación propietario-inquilino
                RelacionesPropietarioInquilino.objects.create(
                    propietario=propietario,
                    inquilino=usuario,
                    vivienda=propiedad_propietario.vivienda,
                    fecha_inicio=fake.date_between(start_date='-2y', end_date='today'),
                    fecha_fin=fake.date_between(start_date='today', end_date='+2y'),
                    monto_alquiler=Decimal(str(random.randint(500, 1500))),
                    activo=True
                )
                
                # Crear copropietario para seguridad
                self.crear_copropietario_seguridad(persona, 'Inquilino', propiedad_propietario.vivienda)
                
                self.inquilinos_creados.append(usuario)
                
        print(f"✅ {len(self.inquilinos_creados)} inquilinos creados")

    def crear_administradores(self, cantidad=2):
        """Crear usuarios administradores"""
        print(f"👔 Creando {cantidad} administradores...")
        
        for i in range(cantidad):
            persona = self.crear_persona_base('administrador')
            usuario = self.crear_usuario_con_rol(persona, 'Administrador')
            
            # Hacer staff para acceso a admin
            usuario.is_staff = True
            usuario.save()
            
            # Crear copropietario para seguridad
            self.crear_copropietario_seguridad(persona, 'Administrador')
            
            self.admin_creados.append(usuario)
            
        print(f"✅ {len(self.admin_creados)} administradores creados")

    def crear_personal_seguridad(self, cantidad=5):
        """Crear personal de seguridad"""
        print(f"👮‍♂️ Creando {cantidad} usuarios de seguridad...")
        
        for i in range(cantidad):
            persona = self.crear_persona_base('seguridad')
            usuario = self.crear_usuario_con_rol(persona, 'Seguridad')
            
            # Crear copropietario para seguridad
            self.crear_copropietario_seguridad(persona, 'Seguridad')
            
            self.seguridad_creados.append(usuario)
            
        print(f"✅ {len(self.seguridad_creados)} usuarios de seguridad creados")

    def crear_familiares_propietarios(self, cantidad=30):
        """Crear familiares de propietarios"""
        print(f"👨‍👩‍👧‍👦 Creando {cantidad} familiares de propietarios...")
        
        parentescos = ['conyugue', 'hijo', 'padre', 'hermano', 'abuelo', 'nieto']
        propietarios_con_familiares = random.sample(self.propietarios_creados, min(15, len(self.propietarios_creados)))
        
        familiares_creados = 0
        for propietario in propietarios_con_familiares:
            # Cada propietario puede tener 1-3 familiares
            num_familiares = min(random.randint(1, 3), cantidad - familiares_creados)
            
            for _ in range(num_familiares):
                persona = self.crear_persona_base('familiar')
                
                familiar = FamiliarPropietario.objects.create(
                    propietario=propietario,
                    persona=persona,
                    parentesco=random.choice(parentescos),
                    autorizado_acceso=random.choice([True, False]),
                    puede_autorizar_visitas=random.choice([True, False]),
                    activo=True
                )
                
                # Crear copropietario para seguridad
                propiedad = Propiedad.objects.filter(persona=propietario.persona).first()
                self.crear_copropietario_seguridad(persona, 'Familiar', propiedad.vivienda if propiedad else None)
                
                familiares_creados += 1
                if familiares_creados >= cantidad:
                    break
                    
            if familiares_creados >= cantidad:
                break
                
        print(f"✅ {familiares_creados} familiares de propietarios creados")

    def crear_familiares_inquilinos(self, cantidad=20):
        """Crear familiares de inquilinos"""
        print(f"👨‍👩‍👧‍👦 Creando {cantidad} familiares de inquilinos...")
        
        parentescos = ['conyugue', 'hijo', 'padre', 'hermano']
        inquilinos_con_familiares = random.sample(self.inquilinos_creados, min(10, len(self.inquilinos_creados)))
        
        familiares_creados = 0
        for inquilino in inquilinos_con_familiares:
            # Cada inquilino puede tener 1-2 familiares
            num_familiares = min(random.randint(1, 2), cantidad - familiares_creados)
            
            for _ in range(num_familiares):
                persona = self.crear_persona_base('familiar')
                
                # Para inquilinos, creamos familiares como si fueran del propietario relacionado
                relacion = RelacionesPropietarioInquilino.objects.filter(inquilino=inquilino).first()
                if relacion:
                    familiar = FamiliarPropietario.objects.create(
                        propietario=relacion.propietario,  # Familiar del propietario, no del inquilino directamente
                        persona=persona,
                        parentesco=random.choice(parentescos),
                        autorizado_acceso=True,
                        puede_autorizar_visitas=False,
                        observaciones=f"Familiar del inquilino {inquilino.persona.nombre}",
                        activo=True
                    )
                    
                    # Crear copropietario para seguridad
                    self.crear_copropietario_seguridad(persona, 'Familiar', relacion.vivienda)
                    
                    familiares_creados += 1
                    if familiares_creados >= cantidad:
                        break
                        
            if familiares_creados >= cantidad:
                break
                
        print(f"✅ {familiares_creados} familiares de inquilinos creados")

    def mostrar_resumen(self):
        """Mostrar resumen de datos creados"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE DATOS CREADOS")
        print("="*60)
        
        print(f"🏠 Viviendas creadas: {Vivienda.objects.count()}")
        print(f"👥 Personas totales: {Persona.objects.count()}")
        print(f"👤 Usuarios totales: {Usuario.objects.count()}")
        print("\n📋 Por tipo de usuario:")
        print(f"  👨‍💼 Propietarios: {Usuario.objects.filter(roles__nombre='Propietario').count()}")
        print(f"  🏠 Inquilinos: {Usuario.objects.filter(roles__nombre='Inquilino').count()}")
        print(f"  👔 Administradores: {Usuario.objects.filter(roles__nombre='Administrador').count()}")
        print(f"  👮‍♂️ Seguridad: {Usuario.objects.filter(roles__nombre='Seguridad').count()}")
        print(f"  👨‍👩‍👧‍👦 Familiares: {FamiliarPropietario.objects.count()}")
        
        print("\n🔐 Sistema de Seguridad:")
        print(f"  👥 Copropietarios: {Copropietarios.objects.count()}")
        print(f"  📸 Reconocimientos faciales: {ReconocimientoFacial.objects.count()}")
        
        print("\n📄 Solicitudes:")
        print(f"  ✅ Aprobadas: {SolicitudRegistroPropietario.objects.filter(estado='APROBADA').count()}")
        print(f"  ⏳ Pendientes: {SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').count()}")
        print(f"  🔍 En revisión: {SolicitudRegistroPropietario.objects.filter(estado='EN_REVISION').count()}")
        
        print("\n🔑 Credenciales de prueba:")
        print("  📧 Email: [cualquier email generado]")
        print("  🔒 Password: temporal123")
        
        print("\n" + "="*60)
        print("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        print("="*60)

    def poblar_todo(self):
        """Ejecutar todo el proceso de poblado"""
        print("🚀 INICIANDO POBLADO COMPLETO DE BASE DE DATOS")
        print("="*60)
        
        try:
            with transaction.atomic():
                self.limpiar_datos_anteriores()
                self.crear_roles_basicos()
                self.crear_viviendas(100)
                self.crear_propietarios(50)
                self.crear_inquilinos(20)
                self.crear_administradores(2)
                self.crear_personal_seguridad(5)
                self.crear_familiares_propietarios(30)
                self.crear_familiares_inquilinos(20)
                
            self.mostrar_resumen()
            
        except Exception as e:
            print(f"❌ Error durante el poblado: {e}")
            raise

def main():
    """Función principal"""
    poblador = PobladorBaseDatos()
    poblador.poblar_todo()

if __name__ == "__main__":
    main()