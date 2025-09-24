"""
Comando para actualizar solicitudes con viviendas disponibles
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from authz.models import SolicitudRegistroPropietario
from core.models import Vivienda, Propiedad
from django.db.models import Q

class Command(BaseCommand):
    help = 'Actualiza solicitudes para usar viviendas disponibles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--solicitud-id',
            type=int,
            help='ID específico de solicitud a actualizar'
        )
        parser.add_argument(
            '--todas',
            action='store_true',
            help='Actualizar todas las solicitudes sin vivienda válida'
        )

    def handle(self, **options):
        solicitud_id = options.get('solicitud_id')
        todas = options.get('todas')
        
        if solicitud_id:
            self.actualizar_solicitud_especifica(solicitud_id)
        elif todas:
            self.actualizar_todas_solicitudes()
        else:
            self.mostrar_solicitudes_problema()

    def mostrar_solicitudes_problema(self):
        """Muestra solicitudes que necesitan actualización"""
        self.stdout.write("🔍 BUSCANDO SOLICITUDES CON PROBLEMAS DE VIVIENDA...")
        
        solicitudes_problema = SolicitudRegistroPropietario.objects.filter(
            Q(vivienda_validada__isnull=True) | 
            Q(estado='PENDIENTE')
        )
        
        if not solicitudes_problema:
            self.stdout.write(self.style.SUCCESS("✅ No hay solicitudes con problemas"))
            return
        
        self.stdout.write(f"⚠️ Encontradas {solicitudes_problema.count()} solicitudes con problemas:")
        
        for solicitud in solicitudes_problema:
            vivienda_info = "Sin vivienda asignada"
            if solicitud.vivienda_validada:
                vivienda_info = f"Vivienda {solicitud.vivienda_validada.numero_casa}"
            
            self.stdout.write(
                f"   ID: {solicitud.pk} | {solicitud.nombres} {solicitud.apellidos} | "
                f"Casa solicitada: {solicitud.numero_casa} | {vivienda_info} | Estado: {solicitud.estado}"
            )
        
        # Mostrar viviendas disponibles
        self.mostrar_viviendas_disponibles()
        
        self.stdout.write("\n💡 OPCIONES:")
        self.stdout.write("--solicitud-id=X --nueva-vivienda=CASA para actualizar una específica")
        self.stdout.write("--todas para actualizar todas automáticamente")

    def mostrar_viviendas_disponibles(self):
        """Muestra viviendas disponibles"""
        self.stdout.write("\n🏠 VIVIENDAS DISPONIBLES:")
        
        viviendas_ocupadas = Propiedad.objects.filter(
            tipo_tenencia='propietario',
            activo=True
        ).values_list('vivienda__numero_casa', flat=True)
        
        solicitudes_activas = SolicitudRegistroPropietario.objects.filter(
            estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
        ).values_list('numero_casa', flat=True)
        
        viviendas_disponibles = Vivienda.objects.exclude(
            Q(numero_casa__in=viviendas_ocupadas) |
            Q(numero_casa__in=solicitudes_activas)
        ).order_by('numero_casa')
        
        for i, vivienda in enumerate(viviendas_disponibles[:10]):
            tipo_icon = "🏘️" if vivienda.tipo_vivienda == 'casa' else "🏢"
            self.stdout.write(
                f"   {tipo_icon} {vivienda.numero_casa} - {vivienda.tipo_vivienda.title()} - "
                f"{vivienda.metros_cuadrados}m² - Bloque {vivienda.bloque}"
            )
        
        if viviendas_disponibles.count() > 10:
            self.stdout.write(f"   ... y {viviendas_disponibles.count() - 10} más")

    def actualizar_todas_solicitudes(self):
        """Actualiza todas las solicitudes problemáticas"""
        self.stdout.write("🔄 ACTUALIZANDO TODAS LAS SOLICITUDES PROBLEMÁTICAS...")
        
        # Obtener viviendas disponibles
        viviendas_ocupadas = Propiedad.objects.filter(
            tipo_tenencia='propietario',
            activo=True
        ).values_list('vivienda__numero_casa', flat=True)
        
        solicitudes_activas = SolicitudRegistroPropietario.objects.filter(
            estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
        ).values_list('numero_casa', flat=True)
        
        viviendas_disponibles = list(Vivienda.objects.exclude(
            Q(numero_casa__in=viviendas_ocupadas) |
            Q(numero_casa__in=solicitudes_activas)
        ).order_by('numero_casa'))
        
        if not viviendas_disponibles:
            self.stdout.write(self.style.ERROR("❌ No hay viviendas disponibles"))
            return
        
        # Obtener solicitudes problemáticas
        solicitudes_problema = SolicitudRegistroPropietario.objects.filter(
            vivienda_validada__isnull=True,
            estado='PENDIENTE'
        )
        
        actualizadas = 0
        
        for i, solicitud in enumerate(solicitudes_problema):
            if i >= len(viviendas_disponibles):
                self.stdout.write(
                    self.style.WARNING(f"⚠️ No hay más viviendas disponibles para solicitud ID: {solicitud.pk}")
                )
                break
            
            vivienda_nueva = viviendas_disponibles[i]
            
            try:
                with transaction.atomic():
                    # Actualizar número de casa
                    solicitud.numero_casa = vivienda_nueva.numero_casa
                    
                    # Validar vivienda
                    es_valida, mensaje = solicitud.validar_vivienda()
                    
                    if es_valida:
                        solicitud.save()
                        actualizadas += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ Solicitud ID: {solicitud.pk} actualizada - "
                                f"Nueva vivienda: {vivienda_nueva.numero_casa} "
                                f"({vivienda_nueva.tipo_vivienda})"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Error validando vivienda para solicitud {solicitud.pk}: {mensaje}")
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error actualizando solicitud {solicitud.pk}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"🎉 ¡{actualizadas} solicitudes actualizadas exitosamente!")
        )

    def actualizar_solicitud_especifica(self, solicitud_id):
        """Actualiza una solicitud específica"""
        try:
            solicitud = SolicitudRegistroPropietario.objects.get(id=solicitud_id)
        except SolicitudRegistroPropietario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ No existe solicitud con ID: {solicitud_id}")
            )
            return
        
        self.stdout.write(f"🔍 Solicitud actual: {solicitud.nombres} {solicitud.apellidos} - Casa: {solicitud.numero_casa}")
        
        # Buscar primera vivienda disponible
        viviendas_ocupadas = Propiedad.objects.filter(
            tipo_tenencia='propietario',
            activo=True
        ).values_list('vivienda__numero_casa', flat=True)
        
        solicitudes_activas = SolicitudRegistroPropietario.objects.filter(
            estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
        ).exclude(id=solicitud_id).values_list('numero_casa', flat=True)
        
        vivienda_disponible = Vivienda.objects.exclude(
            Q(numero_casa__in=viviendas_ocupadas) |
            Q(numero_casa__in=solicitudes_activas)
        ).first()
        
        if not vivienda_disponible:
            self.stdout.write(self.style.ERROR("❌ No hay viviendas disponibles"))
            return
        
        try:
            with transaction.atomic():
                solicitud.numero_casa = vivienda_disponible.numero_casa
                es_valida, mensaje = solicitud.validar_vivienda()
                
                if es_valida:
                    solicitud.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Solicitud actualizada - Nueva vivienda: {vivienda_disponible.numero_casa} "
                            f"({vivienda_disponible.tipo_vivienda}, {vivienda_disponible.metros_cuadrados}m²)"
                        )
                    )
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Error: {mensaje}"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error actualizando solicitud: {e}"))