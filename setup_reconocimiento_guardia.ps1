# Script para probar el sistema de reconocimiento facial del guardia

Write-Host "🎯 CONFIGURANDO SISTEMA DE RECONOCIMIENTO FACIAL PARA GUARDIA" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Yellow

Write-Host "📋 1. VERIFICANDO CONFIGURACIÓN DEL BACKEND..." -ForegroundColor Cyan

# Verificar si hay usuarios con reconocimiento facial activo
python manage.py shell -c "
from seguridad.models import ReconocimientoFacial
from authz.models import Usuario

print('🔍 VERIFICANDO DATOS EXISTENTES...')
print()

# Contar registros de reconocimiento facial
total_registros = ReconocimientoFacial.objects.count()
registros_activos = ReconocimientoFacial.objects.filter(activo=True).count()

print(f'📊 ESTADÍSTICAS RECONOCIMIENTO FACIAL:')
print(f'   Total registros: {total_registros}')
print(f'   Registros activos: {registros_activos}')
print()

if registros_activos == 0:
    print('⚠️  NO HAY USUARIOS CON RECONOCIMIENTO FACIAL ACTIVO')
    print('   Para probar el sistema, necesitas:')
    print('   1. Aprobar solicitudes de copropietarios')
    print('   2. Activar reconocimiento facial para algunos usuarios')
    print()
else:
    print('✅ HAY USUARIOS CON RECONOCIMIENTO FACIAL ACTIVO')
    
    # Mostrar algunos usuarios activos
    usuarios_activos = ReconocimientoFacial.objects.filter(activo=True).select_related('copropietario', 'inquilino')[:5]
    
    print('👥 USUARIOS CON RECONOCIMIENTO ACTIVO:')
    for registro in usuarios_activos:
        if registro.copropietario:
            print(f'   • {registro.copropietario.nombres} {registro.copropietario.apellidos} (Copropietario)')
        elif registro.inquilino:
            print(f'   • {registro.inquilino.persona.nombre} {registro.inquilino.persona.apellido} (Inquilino)')
"

Write-Host ""
Write-Host "🌐 2. INICIANDO SERVIDOR PARA PRUEBAS..." -ForegroundColor Cyan
Write-Host "   El panel del guardia estará disponible en:" -ForegroundColor White
Write-Host "   http://127.0.0.1:8000/api/seguridad/panel-guardia/" -ForegroundColor Green
Write-Host ""

Write-Host "🔧 3. ENDPOINTS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "   📤 POST /api/seguridad/reconocimiento-facial/" -ForegroundColor White
Write-Host "      (Para reconocimiento facial simulado)" -ForegroundColor Gray
Write-Host ""
Write-Host "   📋 GET /api/seguridad/lista-usuarios-activos/" -ForegroundColor White  
Write-Host "      (Lista completa de usuarios)" -ForegroundColor Gray
Write-Host ""
Write-Host "   🔍 GET /api/seguridad/buscar-usuarios/?q=termino" -ForegroundColor White
Write-Host "      (Búsqueda de usuarios)" -ForegroundColor Gray
Write-Host ""
Write-Host "   📊 GET /api/seguridad/estadisticas/" -ForegroundColor White
Write-Host "      (Estadísticas del sistema)" -ForegroundColor Gray
Write-Host ""

Write-Host "📝 4. PASOS PARA PROBAR:" -ForegroundColor Cyan
Write-Host "   1. Ejecuta: python manage.py runserver" -ForegroundColor White
Write-Host "   2. Abre: http://127.0.0.1:8000/api/seguridad/panel-guardia/" -ForegroundColor White
Write-Host "   3. Ve a la pestaña 'Lista de Residentes' para ver usuarios" -ForegroundColor White
Write-Host "   4. Ve a 'Reconocimiento Facial' para probar subiendo imágenes" -ForegroundColor White
Write-Host "   5. Sube una imagen de un usuario registrado" -ForegroundColor White
Write-Host "   6. El sistema comparará y mostrará si lo reconoce" -ForegroundColor White
Write-Host ""

Write-Host "💡 5. NOTAS IMPORTANTES:" -ForegroundColor Cyan
Write-Host "   ✅ El sistema usa tus modelos existentes (no crea nuevas tablas)" -ForegroundColor Green
Write-Host "   ✅ Reconoce tanto copropietarios como inquilinos" -ForegroundColor Green
Write-Host "   ✅ Las fotos vienen de Dropbox (campo fotos_dropbox_urls)" -ForegroundColor Green
Write-Host "   ✅ Umbral de confianza: 70%" -ForegroundColor Green
Write-Host "   ⚠️  Necesitas tener face_recognition instalado" -ForegroundColor Yellow
Write-Host "   ⚠️  Necesitas usuarios con encoding_facial no vacío" -ForegroundColor Yellow
Write-Host ""

Write-Host "🚀 SISTEMA LISTO PARA USAR!" -ForegroundColor Magenta