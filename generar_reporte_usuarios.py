#!/usr/bin/env python
"""
📋 GENERADOR DE REPORTE DE USUARIOS Y VIVIENDAS
Sistema de Reconocimiento Facial - Condominio

Este script genera un archivo TXT con:
✅ Todos los usuarios con sus credenciales
✅ Viviendas disponibles y ocupadas
✅ Datos organizados por tipo de usuario
✅ Información para pruebas del sistema

Ejecutar: python generar_reporte_usuarios.py
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Imports después de configurar Django
from django.contrib.auth import get_user_model
from authz.models import (
    Usuario, Persona, Rol, FamiliarPropietario, 
    SolicitudRegistroPropietario, RelacionesPropietarioInquilino
)
from core.models.propiedades_residentes import Vivienda, Propiedad
from seguridad.models import Copropietarios, ReconocimientoFacial

User = get_user_model()

class GeneradorReporte:
    """Clase para generar reporte de usuarios y viviendas"""
    
    def __init__(self):
        self.reporte = []
        self.fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def agregar_seccion(self, titulo, contenido=""):
        """Agregar una sección al reporte"""
        self.reporte.append("=" * 80)
        self.reporte.append(f"📋 {titulo.upper()}")
        self.reporte.append("=" * 80)
        if contenido:
            self.reporte.append(contenido)
        self.reporte.append("")
    
    def agregar_linea(self, texto):
        """Agregar una línea al reporte"""
        self.reporte.append(texto)
    
    def generar_encabezado(self):
        """Generar encabezado del reporte"""
        self.agregar_seccion("REPORTE DE USUARIOS Y VIVIENDAS - SISTEMA DE RECONOCIMIENTO FACIAL")
        self.agregar_linea(f"📅 Fecha de generación: {self.fecha_generacion}")
        self.agregar_linea(f"🏠 Sistema de Condominio con Reconocimiento Facial")
        self.agregar_linea(f"🔐 Contraseña por defecto para todos los usuarios: temporal123")
        self.agregar_linea("")
    
    def generar_estadisticas_generales(self):
        """Generar estadísticas generales del sistema"""
        self.agregar_seccion("ESTADÍSTICAS GENERALES")
        
        total_usuarios = Usuario.objects.count()
        total_personas = Persona.objects.count()
        total_viviendas = Vivienda.objects.count()
        total_solicitudes = SolicitudRegistroPropietario.objects.count()
        
        self.agregar_linea(f"👥 Total de usuarios: {total_usuarios}")
        self.agregar_linea(f"👤 Total de personas: {total_personas}")
        self.agregar_linea(f"🏠 Total de viviendas: {total_viviendas}")
        self.agregar_linea(f"📄 Total de solicitudes: {total_solicitudes}")
        self.agregar_linea("")
        
        # Estadísticas por rol
        for rol in Rol.objects.all():
            count = Usuario.objects.filter(roles=rol).count()
            self.agregar_linea(f"  {self.get_emoji_rol(rol.nombre)} {rol.nombre}: {count} usuarios")
        
        self.agregar_linea("")
    
    def get_emoji_rol(self, rol_nombre):
        """Obtener emoji según el tipo de rol"""
        emojis = {
            'Administrador': '👔',
            'Propietario': '👨‍💼',
            'Inquilino': '🏠',
            'Seguridad': '👮‍♂️',
            'Familiar': '👨‍👩‍👧‍👦'
        }
        return emojis.get(rol_nombre, '👤')
    
    def generar_usuarios_por_rol(self, rol_nombre):
        """Generar lista de usuarios por rol específico"""
        usuarios = Usuario.objects.filter(roles__nombre=rol_nombre).select_related('persona')
        
        if not usuarios.exists():
            self.agregar_linea(f"No hay usuarios con rol {rol_nombre}")
            return
        
        emoji = self.get_emoji_rol(rol_nombre)
        self.agregar_seccion(f"{emoji} USUARIOS {rol_nombre.upper()} ({usuarios.count()} usuarios)")
        
        for i, usuario in enumerate(usuarios, 1):
            persona = usuario.persona
            
            # Información básica
            self.agregar_linea(f"{i:2d}. {persona.nombre} {persona.apellido}")
            self.agregar_linea(f"    📧 Email: {usuario.email}")
            self.agregar_linea(f"    🔐 Password: temporal123")
            self.agregar_linea(f"    🆔 Documento: {persona.documento_identidad}")
            self.agregar_linea(f"    📱 Teléfono: {persona.telefono or 'No registrado'}")
            
            # Información específica según el rol
            if rol_nombre == 'Propietario':
                self.agregar_info_propietario(usuario)
            elif rol_nombre == 'Inquilino':
                self.agregar_info_inquilino(usuario)
            elif rol_nombre == 'Administrador':
                self.agregar_linea(f"    🔧 Permisos: Administrador del sistema")
            elif rol_nombre == 'Seguridad':
                self.agregar_linea(f"    🛡️ Área: Personal de seguridad")
            
            # Información de Copropietario (reconocimiento facial)
            self.agregar_info_copropietario(persona)
            
            self.agregar_linea("")
    
    def agregar_info_propietario(self, usuario):
        """Agregar información específica del propietario"""
        propiedades = Propiedad.objects.filter(persona=usuario.persona, tipo_tenencia='propietario')
        
        if propiedades.exists():
            for propiedad in propiedades:
                self.agregar_linea(f"    🏠 Vivienda: {propiedad.vivienda.numero_casa}")
                self.agregar_linea(f"    📐 Área: {propiedad.vivienda.metros_cuadrados} m²")
                tipo_display = {'casa': 'Casa', 'departamento': 'Departamento', 'local': 'Local'}
                tipo_texto = tipo_display.get(propiedad.vivienda.tipo_vivienda, propiedad.vivienda.tipo_vivienda)
                self.agregar_linea(f"    🏢 Tipo: {tipo_texto}")
                if propiedad.vivienda.bloque:
                    self.agregar_linea(f"    🏗️ Bloque: {propiedad.vivienda.bloque}")
        
        # Verificar si tiene inquilinos
        inquilinos = RelacionesPropietarioInquilino.objects.filter(propietario=usuario, activo=True)
        if inquilinos.exists():
            self.agregar_linea(f"    👥 Inquilinos ({inquilinos.count()}):")
            for relacion in inquilinos:
                self.agregar_linea(f"      - {relacion.inquilino.persona.nombre} {relacion.inquilino.persona.apellido}")
        
        # Verificar familiares registrados
        familiares = FamiliarPropietario.objects.filter(propietario=usuario, activo=True)
        if familiares.exists():
            self.agregar_linea(f"    👨‍👩‍👧‍👦 Familiares ({familiares.count()}):")
            for familiar in familiares:
                parentesco_dict = dict(FamiliarPropietario.PARENTESCO_CHOICES)
                parentesco_display = parentesco_dict.get(familiar.parentesco, familiar.parentesco)
                self.agregar_linea(f"      - {familiar.persona.nombre} {familiar.persona.apellido} ({parentesco_display})")
    
    def agregar_info_inquilino(self, usuario):
        """Agregar información específica del inquilino"""
        relaciones = RelacionesPropietarioInquilino.objects.filter(inquilino=usuario, activo=True)
        
        if relaciones.exists():
            for relacion in relaciones:
                self.agregar_linea(f"    🏠 Vivienda: {relacion.vivienda.numero_casa}")
                self.agregar_linea(f"    👨‍💼 Propietario: {relacion.propietario.persona.nombre} {relacion.propietario.persona.apellido}")
                if relacion.monto_alquiler:
                    self.agregar_linea(f"    💰 Alquiler: ${relacion.monto_alquiler}")
                self.agregar_linea(f"    📅 Desde: {relacion.fecha_inicio}")
                if relacion.fecha_fin:
                    self.agregar_linea(f"    📅 Hasta: {relacion.fecha_fin}")
    
    def agregar_info_copropietario(self, persona):
        """Agregar información del sistema de seguridad"""
        try:
            copropietario = Copropietarios.objects.get(numero_documento=persona.documento_identidad)
            self.agregar_linea(f"    🔐 ID Seguridad: {copropietario.id}")
            self.agregar_linea(f"    🏘️ Unidad: {copropietario.unidad_residencial}")
            
            # Verificar reconocimiento facial
            try:
                reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
                self.agregar_linea(f"    📸 Reconocimiento: Configurado ({reconocimiento.proveedor_ia})")
            except ReconocimientoFacial.DoesNotExist:
                self.agregar_linea(f"    📸 Reconocimiento: No configurado")
                
        except Copropietarios.DoesNotExist:
            self.agregar_linea(f"    ⚠️ No registrado en sistema de seguridad")
    
    def generar_viviendas_disponibles(self):
        """Generar lista de viviendas disponibles y ocupadas"""
        self.agregar_seccion("🏠 ESTADO DE VIVIENDAS")
        
        todas_viviendas = Vivienda.objects.all().order_by('numero_casa')
        viviendas_ocupadas = Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True)
        
        ocupadas = []
        disponibles = []
        
        for vivienda in todas_viviendas:
            if vivienda.pk in viviendas_ocupadas:
                ocupadas.append(vivienda)
            else:
                disponibles.append(vivienda)
        
        # Viviendas ocupadas
        self.agregar_linea(f"🔴 VIVIENDAS OCUPADAS ({len(ocupadas)} de {todas_viviendas.count()})")
        self.agregar_linea("-" * 50)
        
        for vivienda in ocupadas:
            propiedades = Propiedad.objects.filter(vivienda=vivienda, activo=True)
            self.agregar_linea(f"🏠 {vivienda.numero_casa} - {vivienda.get_tipo_vivienda_display()}")
            
            for propiedad in propiedades:
                tipo_residente = "👨‍💼 Propietario" if propiedad.tipo_tenencia == 'propietario' else "🏠 Inquilino"
                self.agregar_linea(f"   {tipo_residente}: {propiedad.persona.nombre} {propiedad.persona.apellido}")
            
            if vivienda.bloque:
                self.agregar_linea(f"   🏗️ Bloque: {vivienda.bloque}")
            self.agregar_linea(f"   📐 Área: {vivienda.metros_cuadrados} m²")
            self.agregar_linea("")
        
        # Viviendas disponibles
        self.agregar_linea(f"🟢 VIVIENDAS DISPONIBLES ({len(disponibles)} de {todas_viviendas.count()})")
        self.agregar_linea("-" * 50)
        
        if disponibles:
            for vivienda in disponibles:
                self.agregar_linea(f"🏠 {vivienda.numero_casa} - {vivienda.get_tipo_vivienda_display()}")
                if vivienda.bloque:
                    self.agregar_linea(f"   🏗️ Bloque: {vivienda.bloque}")
                self.agregar_linea(f"   📐 Área: {vivienda.metros_cuadrados} m²")
                self.agregar_linea(f"   💰 Tarifa base: ${vivienda.tarifa_base_expensas}")
                self.agregar_linea("")
        else:
            self.agregar_linea("No hay viviendas disponibles")
            self.agregar_linea("")
    
    def generar_solicitudes_registro(self):
        """Generar información sobre solicitudes de registro"""
        self.agregar_seccion("📄 SOLICITUDES DE REGISTRO")
        
        solicitudes = SolicitudRegistroPropietario.objects.all().order_by('-created_at')
        
        estados = {}
        for solicitud in solicitudes:
            estado = solicitud.estado
            if estado not in estados:
                estados[estado] = []
            estados[estado].append(solicitud)
        
        for estado, lista_solicitudes in estados.items():
            emoji_estado = {
                'APROBADA': '✅',
                'PENDIENTE': '⏳',
                'EN_REVISION': '🔍',
                'RECHAZADA': '❌',
                'DOCUMENTOS_FALTANTES': '📄',
                'REQUIERE_ACLARACION': '❓'
            }.get(estado, '📋')
            
            self.agregar_linea(f"{emoji_estado} {estado} ({len(lista_solicitudes)} solicitudes)")
            self.agregar_linea("-" * 40)
            
            for solicitud in lista_solicitudes[:10]:  # Mostrar solo las primeras 10
                self.agregar_linea(f"  📋 {solicitud.nombres} {solicitud.apellidos}")
                self.agregar_linea(f"     🏠 Vivienda: {solicitud.numero_casa}")
                self.agregar_linea(f"     📧 Email: {solicitud.email}")
                self.agregar_linea(f"     🆔 Documento: {solicitud.documento_identidad}")
                if solicitud.fecha_revision:
                    self.agregar_linea(f"     📅 Revisado: {solicitud.fecha_revision.strftime('%d/%m/%Y')}")
                self.agregar_linea("")
            
            if len(lista_solicitudes) > 10:
                self.agregar_linea(f"  ... y {len(lista_solicitudes) - 10} solicitudes más")
                self.agregar_linea("")
    
    def generar_credenciales_acceso(self):
        """Generar sección de credenciales de acceso"""
        self.agregar_seccion("🔑 CREDENCIALES DE ACCESO RÁPIDO")
        
        self.agregar_linea("🌐 URLS DEL SISTEMA:")
        self.agregar_linea("  📱 Sistema principal: http://127.0.0.1:8000/")
        self.agregar_linea("  📚 Documentación API: http://127.0.0.1:8000/api/docs/")
        self.agregar_linea("  👔 Panel Admin: http://127.0.0.1:8000/admin/")
        self.agregar_linea("  🧪 Demo básico: http://127.0.0.1:8000/api/demo/")
        self.agregar_linea("")
        
        self.agregar_linea("🔐 CREDENCIALES POR DEFECTO:")
        self.agregar_linea("  🔒 Contraseña universal: temporal123")
        self.agregar_linea("  📧 Email formato: [nombre]@ejemplo.com")
        self.agregar_linea("")
        
        self.agregar_linea("🚀 USUARIOS DE PRUEBA RECOMENDADOS:")
        
        # Algunos usuarios de cada tipo para pruebas rápidas
        admin = Usuario.objects.filter(roles__nombre='Administrador').first()
        if admin:
            self.agregar_linea(f"  👔 Admin: {admin.email} / temporal123")
        
        propietario = Usuario.objects.filter(roles__nombre='Propietario').first()
        if propietario:
            self.agregar_linea(f"  👨‍💼 Propietario: {propietario.email} / temporal123")
        
        inquilino = Usuario.objects.filter(roles__nombre='Inquilino').first()
        if inquilino:
            self.agregar_linea(f"  🏠 Inquilino: {inquilino.email} / temporal123")
        
        seguridad = Usuario.objects.filter(roles__nombre='Seguridad').first()
        if seguridad:
            self.agregar_linea(f"  👮‍♂️ Seguridad: {seguridad.email} / temporal123")
        
        self.agregar_linea("")
    
    def generar_reporte_completo(self):
        """Generar el reporte completo"""
        print("📋 Generando reporte de usuarios y viviendas...")
        
        # Generar todas las secciones
        self.generar_encabezado()
        self.generar_estadisticas_generales()
        self.generar_credenciales_acceso()
        
        # Generar usuarios por rol
        roles = ['Administrador', 'Propietario', 'Inquilino', 'Seguridad', 'Familiar']
        for rol in roles:
            if Usuario.objects.filter(roles__nombre=rol).exists():
                self.generar_usuarios_por_rol(rol)
        
        # Generar información de viviendas
        self.generar_viviendas_disponibles()
        
        # Generar solicitudes
        self.generar_solicitudes_registro()
        
        # Guardar el archivo
        nombre_archivo = f"REPORTE_USUARIOS_VIVIENDAS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write('\n'.join(self.reporte))
        
        print(f"✅ Reporte generado exitosamente: {nombre_archivo}")
        print(f"📄 Total de líneas: {len(self.reporte)}")
        return nombre_archivo

def main():
    """Función principal"""
    try:
        generador = GeneradorReporte()
        nombre_archivo = generador.generar_reporte_completo()
        
        print("\n" + "="*60)
        print("📋 REPORTE GENERADO EXITOSAMENTE")
        print("="*60)
        print(f"📄 Archivo: {nombre_archivo}")
        print(f"📍 Ubicación: Directorio actual del proyecto")
        print(f"🔐 Contraseña universal: temporal123")
        print(f"🌐 Sistema funcionando en: http://127.0.0.1:8000/")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        raise

if __name__ == "__main__":
    main()