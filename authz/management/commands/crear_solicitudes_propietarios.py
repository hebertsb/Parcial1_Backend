from django.core.management.base import BaseCommand
from authz.models import SolicitudRegistroPropietario, Rol
from authz.serializers_propietario import SolicitudRegistroPropietarioSerializer
from datetime import date


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de registro de propietarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=5,
            help='Cantidad de solicitudes de prueba a crear'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        self.stdout.write('🏠 Creando datos de prueba para registro de propietarios...')
        
        # Asegurar que existe rol de Administrador
        rol_admin, created = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={
                'descripcion': 'Administrador del sistema',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write('✅ Rol Administrador creado')
        
        # Datos de prueba para solicitudes
        solicitudes_data = [
            {
                'nombres': 'Juan Carlos',
                'apellidos': 'García López',
                'documento_identidad': 'PROP001',
                'fecha_nacimiento': date(1985, 3, 15),
                'email': 'juan.garcia@ejemplo.com',
                'telefono': '+591-70123456',
                'numero_vivienda': 'A-101',
                'bloque_torre': 'Torre A',
                'password': 'PropietarioPass123!',
                'password_confirm': 'PropietarioPass123!',
                'acepta_terminos': True,
                'acepta_tratamiento_datos': True,
                'familiares': [
                    {
                        'nombres': 'María Elena',
                        'apellidos': 'López de García',
                        'documento_identidad': 'FAM001',
                        'fecha_nacimiento': date(1990, 7, 20),
                        'telefono': '+591-70654321',
                        'email': 'maria.lopez@ejemplo.com',
                        'parentesco': 'conyugue',
                        'autorizado_acceso': True,
                        'puede_autorizar_visitas': True
                    },
                    {
                        'nombres': 'Carlos Andrés',
                        'apellidos': 'García López',
                        'documento_identidad': 'FAM002',
                        'fecha_nacimiento': date(2010, 12, 5),
                        'telefono': '',
                        'email': '',
                        'parentesco': 'hijo',
                        'autorizado_acceso': True,
                        'puede_autorizar_visitas': False
                    }
                ]
            },
            {
                'nombres': 'Ana Patricia',
                'apellidos': 'Rodríguez Mendoza',
                'documento_identidad': 'PROP002',
                'fecha_nacimiento': date(1978, 11, 8),
                'email': 'ana.rodriguez@ejemplo.com',
                'telefono': '+591-70987654',
                'numero_vivienda': 'B-205',
                'bloque_torre': 'Torre B',
                'password': 'PropietarioPass123!',
                'password_confirm': 'PropietarioPass123!',
                'acepta_terminos': True,
                'acepta_tratamiento_datos': True,
                'familiares': [
                    {
                        'nombres': 'Luis Fernando',
                        'apellidos': 'Mendoza Vega',
                        'documento_identidad': 'FAM003',
                        'fecha_nacimiento': date(1975, 4, 22),
                        'telefono': '+591-70456789',
                        'email': 'luis.mendoza@ejemplo.com',
                        'parentesco': 'conyugue',
                        'autorizado_acceso': True,
                        'puede_autorizar_visitas': True
                    }
                ]
            },
            {
                'nombres': 'Roberto',
                'apellidos': 'Silva Paz',
                'documento_identidad': 'PROP003',
                'fecha_nacimiento': date(1982, 6, 30),
                'email': 'roberto.silva@ejemplo.com',
                'telefono': '+591-70147258',
                'numero_vivienda': 'C-310',
                'bloque_torre': 'Torre C',
                'password': 'PropietarioPass123!',
                'password_confirm': 'PropietarioPass123!',
                'acepta_terminos': True,
                'acepta_tratamiento_datos': True,
                'familiares': []
            },
            {
                'nombres': 'Carmen Rosa',
                'apellidos': 'Vargas Flores',
                'documento_identidad': 'PROP004',
                'fecha_nacimiento': date(1970, 9, 14),
                'email': 'carmen.vargas@ejemplo.com',
                'telefono': '+591-70369852',
                'numero_vivienda': 'D-150',
                'bloque_torre': 'Torre D',
                'password': 'PropietarioPass123!',
                'password_confirm': 'PropietarioPass123!',
                'acepta_terminos': True,
                'acepta_tratamiento_datos': True,
                'familiares': [
                    {
                        'nombres': 'Pedro José',
                        'apellidos': 'Vargas Montenegro',
                        'documento_identidad': 'FAM004',
                        'fecha_nacimiento': date(1995, 2, 28),
                        'telefono': '+591-70741852',
                        'email': 'pedro.vargas@ejemplo.com',
                        'parentesco': 'hijo',
                        'autorizado_acceso': True,
                        'puede_autorizar_visitas': False
                    },
                    {
                        'nombres': 'Isabella',
                        'apellidos': 'Vargas Montenegro',
                        'documento_identidad': 'FAM005',
                        'fecha_nacimiento': date(1998, 8, 10),
                        'telefono': '+591-70852963',
                        'email': 'isabella.vargas@ejemplo.com',
                        'parentesco': 'hijo',
                        'autorizado_acceso': True,
                        'puede_autorizar_visitas': False
                    }
                ]
            },
            {
                'nombres': 'Miguel Ángel',
                'apellidos': 'Torres Ramos',
                'documento_identidad': 'PROP005',
                'fecha_nacimiento': date(1988, 12, 3),
                'email': 'miguel.torres@ejemplo.com',
                'telefono': '+591-70159753',
                'numero_vivienda': 'E-075',
                'bloque_torre': 'Torre E',
                'password': 'PropietarioPass123!',
                'password_confirm': 'PropietarioPass123!',
                'acepta_terminos': True,
                'acepta_tratamiento_datos': True,
                'familiares': [
                    {
                        'nombres': 'Sofía Alejandra',
                        'apellidos': 'Ramos de Torres',
                        'documento_identidad': 'FAM006',
                        'fecha_nacimiento': date(1992, 5, 17),
                        'telefono': '+591-70753159',
                        'email': 'sofia.ramos@ejemplo.com',
                        'parentesco': 'conyugue',
                        'autorizado_acceso': True,
                        'puede_autorizar_visitas': True
                    },
                    {
                        'nombres': 'Mateo Sebastián',
                        'apellidos': 'Torres Ramos',
                        'documento_identidad': 'FAM007',
                        'fecha_nacimiento': date(2015, 11, 25),
                        'telefono': '',
                        'email': '',
                        'parentesco': 'hijo',
                        'autorizado_acceso': True,
                        'puede_autorizar_visitas': False
                    }
                ]
            }
        ]
        
        created_count = 0
        
        for i, solicitud_data in enumerate(solicitudes_data[:cantidad]):
            try:
                # Verificar si ya existe
                if SolicitudRegistroPropietario.objects.filter(
                    documento_identidad=solicitud_data['documento_identidad']
                ).exists():
                    self.stdout.write(f'ℹ️ Solicitud {solicitud_data["documento_identidad"]} ya existe')
                    continue
                
                # Crear solicitud usando el serializer
                serializer = SolicitudRegistroPropietarioSerializer(data=solicitud_data)
                
                if serializer.is_valid():
                    solicitud = serializer.save()
                    created_count += 1
                    
                    # Establecer estado variado para testing
                    if i == 0:
                        solicitud.estado = 'PENDIENTE'
                    elif i == 1:
                        solicitud.estado = 'EN_REVISION'
                    elif i == 2:
                        solicitud.estado = 'APROBADA'
                    elif i == 3:
                        solicitud.estado = 'DOCUMENTOS_FALTANTES'
                        solicitud.comentarios_admin = 'Favor enviar copia de escritura de la propiedad'
                    else:
                        solicitud.estado = 'PENDIENTE'
                    
                    solicitud.save()
                    
                    self.stdout.write(f'✅ Solicitud creada: {solicitud.nombres} {solicitud.apellidos} - {solicitud.estado}')
                    
                else:
                    self.stdout.write(f'❌ Error en solicitud {i+1}: {serializer.errors}')
                    
            except Exception as e:
                self.stdout.write(f'❌ Error creando solicitud {i+1}: {str(e)}')
        
        # Mostrar resumen
        self.stdout.write('\n📊 RESUMEN:')
        self.stdout.write(f'- Solicitudes creadas: {created_count}')
        self.stdout.write(f'- Total solicitudes: {SolicitudRegistroPropietario.objects.count()}')
        
        # Mostrar estadísticas por estado
        self.stdout.write('\n📈 SOLICITUDES POR ESTADO:')
        estados = SolicitudRegistroPropietario.objects.values_list('estado', flat=True)
        for estado in set(estados):
            count = estados.filter(estado=estado).count() if hasattr(estados, 'filter') else len([e for e in estados if e == estado])
            self.stdout.write(f'- {estado}: {count}')
        
        self.stdout.write('\n🌐 ENDPOINTS DISPONIBLES:')
        self.stdout.write('📍 Solicitar registro: POST /api/auth/propietarios/registro/solicitar/')
        self.stdout.write('📍 Consultar estado: GET /api/auth/propietarios/registro/consultar-estado/')
        self.stdout.write('📍 Admin - Listar: GET /api/auth/propietarios/admin/solicitudes/')
        
        self.stdout.write('\n✅ Datos de prueba para propietarios creados exitosamente!')