"""
Comando para crear usuarios de prueba para el sistema
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from authz.models import Usuario, Rol, Persona
from core.models import Vivienda, Propiedad
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Crea usuarios de prueba para el sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['admin', 'propietario', 'seguridad', 'todos'],
            default='todos',
            help='Tipo de usuarios a crear'
        )
        parser.add_argument(
            '--cantidad',
            type=int,
            default=5,
            help='Cantidad de usuarios a crear por tipo'
        )

    def handle(self, **options):
        tipo = options['tipo']
        cantidad = options['cantidad']
        
        self.stdout.write("👥 Iniciando creación de usuarios de prueba...")
        
        if tipo == 'todos':
            self.crear_admin(1)
            self.crear_propietarios(cantidad)
            self.crear_seguridad(2)
        elif tipo == 'admin':
            self.crear_admin(cantidad)
        elif tipo == 'propietario':
            self.crear_propietarios(cantidad)
        elif tipo == 'seguridad':
            self.crear_seguridad(cantidad)
        
        self.mostrar_resumen()

    def crear_admin(self, cantidad):
        """Crea usuarios administradores"""
        self.stdout.write(f"🔑 Creando {cantidad} administrador(es)...")
        
        # Asegurar que existe el rol
        rol_admin, created = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={'descripcion': 'Administrador del sistema'}
        )
        
        for i in range(cantidad):
            email = f"admin{i+1}@condominio.com"
            documento = f"1111111{i}"
            
            if Usuario.objects.filter(email=email).exists():
                continue
            
            try:
                with transaction.atomic():
                    # Crear persona
                    persona = Persona.objects.create(
                        nombre=f"Admin",
                        apellido=f"Sistema {i+1}",
                        documento_identidad=documento,
                        email=email,
                        telefono=f"7000000{i}",
                        tipo_persona='administrador'
                    )
                    
                    # Crear usuario
                    usuario = Usuario.objects.create_user(
                        email=email,
                        password='admin123',
                        persona=persona
                    )
                    
                    # Asignar rol
                    usuario.roles.add(rol_admin)
                    
                    self.stdout.write(f"✅ Admin creado: {email} (password: admin123)")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creando admin {email}: {e}")
                )

    def crear_propietarios(self, cantidad):
        """Crea usuarios propietarios"""
        self.stdout.write(f"🏠 Creando {cantidad} propietario(s)...")
        
        # Asegurar que existe el rol
        rol_propietario, created = Rol.objects.get_or_create(
            nombre='Propietario',
            defaults={'descripcion': 'Propietario de vivienda'}
        )
        
        # Obtener viviendas disponibles
        viviendas_disponibles = list(Vivienda.objects.filter(
            propiedad__isnull=True
        )[:cantidad])
        
        if len(viviendas_disponibles) < cantidad:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ Solo hay {len(viviendas_disponibles)} viviendas disponibles, "
                    f"se crearán solo esos propietarios"
                )
            )
        
        nombres = ['Carlos', 'María', 'José', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura']
        apellidos = ['García', 'López', 'Martínez', 'González', 'Rodríguez', 'Fernández']
        
        for i, vivienda in enumerate(viviendas_disponibles):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            email = f"propietario{i+1}@test.com"
            documento = f"2222222{i}"
            
            if Usuario.objects.filter(email=email).exists():
                continue
            
            try:
                with transaction.atomic():
                    # Crear persona
                    persona = Persona.objects.create(
                        nombre=nombre,
                        apellido=apellido,
                        documento_identidad=documento,
                        email=email,
                        telefono=f"7111111{i}",
                        fecha_nacimiento=f"198{random.randint(0, 9)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                        tipo_persona='propietario'
                    )
                    
                    # Crear usuario
                    usuario = Usuario.objects.create_user(
                        email=email,
                        password='propietario123',
                        persona=persona
                    )
                    
                    # Asignar rol
                    usuario.roles.add(rol_propietario)
                    
                    # Asignar vivienda
                    Propiedad.objects.create(
                        vivienda=vivienda,
                        persona=persona,
                        tipo_tenencia='propietario',
                        porcentaje_propiedad=100.00,
                        fecha_inicio_tenencia=timezone.now().date(),
                        activo=True
                    )
                    
                    self.stdout.write(
                        f"✅ Propietario creado: {email} (password: propietario123) "
                        f"- Vivienda: {vivienda.numero_casa}"
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creando propietario {email}: {e}")
                )

    def crear_seguridad(self, cantidad):
        """Crea usuarios de seguridad"""
        self.stdout.write(f"🛡️ Creando {cantidad} guardia(s) de seguridad...")
        
        # Asegurar que existe el rol
        rol_seguridad, created = Rol.objects.get_or_create(
            nombre='Seguridad',
            defaults={'descripcion': 'Personal de seguridad'}
        )
        
        for i in range(cantidad):
            email = f"seguridad{i+1}@condominio.com"
            documento = f"3333333{i}"
            
            if Usuario.objects.filter(email=email).exists():
                continue
            
            try:
                with transaction.atomic():
                    # Crear persona
                    persona = Persona.objects.create(
                        nombre=f"Guardia",
                        apellido=f"Seguridad {i+1}",
                        documento_identidad=documento,
                        email=email,
                        telefono=f"7222222{i}",
                        tipo_persona='seguridad'
                    )
                    
                    # Crear usuario
                    usuario = Usuario.objects.create_user(
                        email=email,
                        password='seguridad123',
                        persona=persona
                    )
                    
                    # Asignar rol
                    usuario.roles.add(rol_seguridad)
                    
                    self.stdout.write(f"✅ Seguridad creado: {email} (password: seguridad123)")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creando seguridad {email}: {e}")
                )

    def mostrar_resumen(self):
        """Muestra un resumen de los usuarios creados"""
        self.stdout.write("\n📊 RESUMEN DE USUARIOS:")
        self.stdout.write("=" * 50)
        
        total_usuarios = Usuario.objects.count()
        self.stdout.write(f"👥 Total usuarios: {total_usuarios}")
        
        # Por rol
        for rol in Rol.objects.all():
            count = Usuario.objects.filter(roles=rol).count()
            self.stdout.write(f"   {rol.nombre}: {count} usuarios")
        
        self.stdout.write("\n🔐 CREDENCIALES DE ACCESO:")
        self.stdout.write("-" * 30)
        
        # Mostrar algunos usuarios de ejemplo
        admins = Usuario.objects.filter(roles__nombre='Administrador')[:2]
        for admin in admins:
            self.stdout.write(f"🔑 Admin: {admin.email} / admin123")
        
        propietarios = Usuario.objects.filter(roles__nombre='Propietario')[:3]
        for prop in propietarios:
            vivienda = "Sin vivienda"
            if hasattr(prop.persona, 'propiedad_set'):
                prop_obj = prop.persona.propiedad_set.filter(activo=True).first()
                if prop_obj:
                    vivienda = prop_obj.vivienda.numero_casa
            self.stdout.write(f"🏠 Propietario: {prop.email} / propietario123 (Vivienda: {vivienda})")
        
        seguridad = Usuario.objects.filter(roles__nombre='Seguridad')[:2]
        for seg in seguridad:
            self.stdout.write(f"🛡️ Seguridad: {seg.email} / seguridad123")
        
        self.stdout.write("\n✅ ¡Usuarios listos para usar en el frontend!")