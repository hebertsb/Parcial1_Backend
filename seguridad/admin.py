from django.contrib import admin
from .models import Copropietarios, ReconocimientoFacial, BitacoraAcciones


@admin.register(Copropietarios)
class CopropietariosAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'numero_documento', 'tipo_documento', 'unidad_residencial', 'activo']
    list_filter = ['tipo_documento', 'activo', 'fecha_creacion']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'unidad_residencial', 'email']
    ordering = ['apellidos', 'nombres']
    
    @admin.display(description='Nombre Completo')
    def nombre_completo(self, obj):
        return obj.nombre_completo


@admin.register(ReconocimientoFacial)
class ReconocimientoFacialAdmin(admin.ModelAdmin):
    list_display = ['copropietario', 'proveedor_ia', 'activo', 'fecha_enrolamiento', 'intentos_verificacion']
    list_filter = ['proveedor_ia', 'activo', 'fecha_enrolamiento']
    search_fields = ['copropietario__nombres', 'copropietario__apellidos', 'copropietario__numero_documento']
    ordering = ['-fecha_enrolamiento']
    readonly_fields = ['vector_facial', 'fecha_enrolamiento', 'fecha_modificacion']


@admin.register(BitacoraAcciones)
class BitacoraAccionesAdmin(admin.ModelAdmin):
    list_display = ['tipo_accion', 'usuario', 'copropietario', 'proveedor_ia', 'resultado_match', 'fecha_accion']
    list_filter = ['tipo_accion', 'proveedor_ia', 'resultado_match', 'fecha_accion']
    search_fields = ['descripcion', 'usuario__user__username', 'copropietario__nombres', 'copropietario__apellidos']
    ordering = ['-fecha_accion']
    readonly_fields = ['fecha_accion']
    
    def has_add_permission(self, request):
        return False  # No permitir agregar manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # No permitir editar
