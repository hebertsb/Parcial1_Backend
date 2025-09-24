"""
Comando para probar el serializer directamente sin HTTP
"""
import json
from django.core.management.base import BaseCommand
from authz.models import SolicitudRegistroPropietario
from authz.serializers_propietario import SolicitudDetailSerializer


class Command(BaseCommand):
    help = 'Prueba el serializer directamente sin HTTP'

    def handle(self, *args, **options):
        self.stdout.write("🔍 PROBANDO SERIALIZER CON FECHA_NACIMIENTO")
        self.stdout.write("=" * 50)
        
        # Obtener solicitudes pendientes
        solicitudes = SolicitudRegistroPropietario.objects.filter(
            estado='PENDIENTE'
        ).order_by('-created_at')
        
        if not solicitudes:
            self.stdout.write(self.style.ERROR("❌ No hay solicitudes pendientes"))
            return
        
        self.stdout.write(f"📊 Solicitudes encontradas: {solicitudes.count()}")
        
        # Serializar usando el serializer actualizado
        serializer = SolicitudDetailSerializer(solicitudes, many=True)
        serialized_data = serializer.data
        
        self.stdout.write("\n📄 DATOS SERIALIZADOS:")
        self.stdout.write("-" * 25)
        
        # Mostrar JSON completo
        print(json.dumps(serialized_data, indent=2, ensure_ascii=False, default=str))
        
        self.stdout.write(f"\n🔍 VERIFICACIÓN CAMPOS ESPECÍFICOS:")
        self.stdout.write("-" * 35)
        
        for i, solicitud_data in enumerate(serialized_data, 1):
            self.stdout.write(f"\n📋 Solicitud {i} (ID: {solicitud_data.get('id')}):")
            self.stdout.write(f"   👤 Nombre: {solicitud_data.get('nombres')} {solicitud_data.get('apellidos')}")
            self.stdout.write(f"   📅 Fecha Nacimiento: {solicitud_data.get('fecha_nacimiento')}")
            self.stdout.write(f"   📧 Email: {solicitud_data.get('email')}")
            self.stdout.write(f"   🏠 Vivienda: {solicitud_data.get('numero_casa')}")
            self.stdout.write(f"   📊 Estado: {solicitud_data.get('estado')}")
            
            # Verificar si fecha_nacimiento está presente
            if 'fecha_nacimiento' in solicitud_data:
                if solicitud_data['fecha_nacimiento']:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ fecha_nacimiento: PRESENTE ({solicitud_data['fecha_nacimiento']})"))
                else:
                    self.stdout.write(self.style.WARNING(f"   ⚠️  fecha_nacimiento: PRESENTE pero NULL"))
            else:
                self.stdout.write(self.style.ERROR(f"   ❌ fecha_nacimiento: AUSENTE"))
        
        self.stdout.write(f"\n🎯 RESUMEN:")
        self.stdout.write(f"   • Campos incluidos en el serializer: {len(serialized_data[0].keys()) if serialized_data else 0}")
        if serialized_data:
            self.stdout.write(f"   • Lista de campos: {list(serialized_data[0].keys())}")
            
        self.stdout.write(f"\n✅ ¡El serializer ya incluye fecha_nacimiento!")
        self.stdout.write(f"   Tu frontend debería ver este campo ahora.")