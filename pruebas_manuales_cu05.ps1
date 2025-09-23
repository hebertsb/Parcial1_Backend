# Script de PowerShell para Pruebas Manuales del API CU05
# Gestionar Unidades Habitacionales

Write-Host "🏠 === PRUEBAS MANUALES API CU05 - Gestionar Unidades Habitacionales ===" -ForegroundColor Green
Write-Host ""

# Configuración base
$baseUrl = "http://127.0.0.1:8000"
$headers = @{"Content-Type" = "application/json"}

Write-Host "🔐 PASO 1: Obtener Token JWT" -ForegroundColor Yellow
Write-Host "URL: POST $baseUrl/api/auth/login/" -ForegroundColor Cyan

try {
    $loginBody = @{
        email = "admin@condominio.com"
        password = "admin123"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access
    $authHeaders = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $token"
    }
    
    Write-Host "✅ Token obtenido exitosamente!" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0,50))..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ Error obteniendo token: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "🏠 PASO 2: PRUEBAS DE VIVIENDAS" -ForegroundColor Yellow
Write-Host ""

# 1. Listar Viviendas
Write-Host "📋 1. Listar Viviendas" -ForegroundColor Cyan
Write-Host "URL: GET $baseUrl/api/viviendas/" -ForegroundColor Gray
try {
    $viviendas = Invoke-RestMethod -Uri "$baseUrl/api/viviendas/" -Method GET -Headers $authHeaders
    Write-Host "✅ Viviendas encontradas: $($viviendas.Count)" -ForegroundColor Green
    
    if ($viviendas.Count -gt 0) {
        Write-Host "📋 Primeras 3 viviendas:" -ForegroundColor Gray
        $viviendas[0..2] | ForEach-Object {
            Write-Host "  🏠 ID: $($_.id) | Casa: $($_.numero_casa) | Tipo: $($_.tipo_vivienda) | Estado: $($_.estado)" -ForegroundColor White
        }
        $primeraVivienda = $viviendas[0].id
    }
    Write-Host ""
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Crear Nueva Vivienda
Write-Host "🆕 2. Crear Nueva Vivienda" -ForegroundColor Cyan
Write-Host "URL: POST $baseUrl/api/viviendas/" -ForegroundColor Gray
try {
    $nuevaViviendaBody = @{
        numero_casa = "999Z"
        bloque = "Z"
        tipo_vivienda = "casa"
        metros_cuadrados = "120.00"
        tarifa_base_expensas = "350.00"
        tipo_cobranza = "por_casa"
        estado = "activa"
    } | ConvertTo-Json

    $nuevaVivienda = Invoke-RestMethod -Uri "$baseUrl/api/viviendas/" -Method POST -Body $nuevaViviendaBody -Headers $authHeaders
    Write-Host "✅ Vivienda creada exitosamente!" -ForegroundColor Green
    Write-Host "  🏠 ID: $($nuevaVivienda.id) | Casa: $($nuevaVivienda.numero_casa) | Tipo: $($nuevaVivienda.tipo_vivienda)" -ForegroundColor White
    $viviendaCreada = $nuevaVivienda.id
    Write-Host ""
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Obtener Vivienda Específica
if ($primeraVivienda) {
    Write-Host "🔍 3. Obtener Vivienda Específica (ID: $primeraVivienda)" -ForegroundColor Cyan
    Write-Host "URL: GET $baseUrl/api/viviendas/$primeraVivienda/" -ForegroundColor Gray
    try {
        $viviendaDetalle = Invoke-RestMethod -Uri "$baseUrl/api/viviendas/$primeraVivienda/" -Method GET -Headers $authHeaders
        Write-Host "✅ Vivienda obtenida exitosamente!" -ForegroundColor Green
        Write-Host "  🏠 Casa: $($viviendaDetalle.numero_casa)" -ForegroundColor White
        Write-Host "  📐 Metros²: $($viviendaDetalle.metros_cuadrados)" -ForegroundColor White
        Write-Host "  💰 Tarifa: $($viviendaDetalle.tarifa_base_expensas)" -ForegroundColor White
        Write-Host "  📊 Estado: $($viviendaDetalle.estado)" -ForegroundColor White
        Write-Host ""
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 4. Actualizar Vivienda (PATCH)
if ($viviendaCreada) {
    Write-Host "✏️ 4. Actualizar Vivienda Parcial (ID: $viviendaCreada)" -ForegroundColor Cyan
    Write-Host "URL: PATCH $baseUrl/api/viviendas/$viviendaCreada/" -ForegroundColor Gray
    try {
        $updateBody = @{
            tarifa_base_expensas = "380.00"
        } | ConvertTo-Json

        $viviendaActualizada = Invoke-RestMethod -Uri "$baseUrl/api/viviendas/$viviendaCreada/" -Method PATCH -Body $updateBody -Headers $authHeaders
        Write-Host "✅ Vivienda actualizada exitosamente!" -ForegroundColor Green
        Write-Host "  💰 Nueva tarifa: $($viviendaActualizada.tarifa_base_expensas)" -ForegroundColor White
        Write-Host ""
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 5. Estadísticas del Condominio
Write-Host "📊 5. Estadísticas del Condominio" -ForegroundColor Cyan
Write-Host "URL: GET $baseUrl/api/viviendas/estadisticas/" -ForegroundColor Gray
try {
    $estadisticas = Invoke-RestMethod -Uri "$baseUrl/api/viviendas/estadisticas/" -Method GET -Headers $authHeaders
    Write-Host "✅ Estadísticas obtenidas exitosamente!" -ForegroundColor Green
    Write-Host "  📊 Total Viviendas: $($estadisticas.total_viviendas)" -ForegroundColor White
    Write-Host "  📈 Por Estado:" -ForegroundColor White
    $estadisticas.por_estado.PSObject.Properties | ForEach-Object {
        Write-Host "    $($_.Name): $($_.Value)" -ForegroundColor Gray
    }
    Write-Host "  🏠 Por Tipo:" -ForegroundColor White
    $estadisticas.por_tipo.PSObject.Properties | ForEach-Object {
        Write-Host "    $($_.Name): $($_.Value)" -ForegroundColor Gray
    }
    Write-Host ""
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Buscar Viviendas con Filtros
Write-Host "🔍 6. Buscar Viviendas con Filtros" -ForegroundColor Cyan
Write-Host "URL: GET $baseUrl/api/viviendas/?estado=activa&tipo_vivienda=casa" -ForegroundColor Gray
try {
    $viviendasFiltradas = Invoke-RestMethod -Uri "$baseUrl/api/viviendas/?estado=activa&tipo_vivienda=casa" -Method GET -Headers $authHeaders
    Write-Host "✅ Búsqueda exitosa!" -ForegroundColor Green
    Write-Host "  🏠 Casas activas encontradas: $($viviendasFiltradas.Count)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Propiedades de una Vivienda
if ($primeraVivienda) {
    Write-Host "👥 7. Propiedades de una Vivienda (ID: $primeraVivienda)" -ForegroundColor Cyan
    Write-Host "URL: GET $baseUrl/api/viviendas/$primeraVivienda/propiedades/" -ForegroundColor Gray
    try {
        $propiedades = Invoke-RestMethod -Uri "$baseUrl/api/viviendas/$primeraVivienda/propiedades/" -Method GET -Headers $authHeaders
        Write-Host "✅ Propiedades obtenidas exitosamente!" -ForegroundColor Green
        Write-Host "  👥 Propiedades encontradas: $($propiedades.Count)" -ForegroundColor White
        if ($propiedades.Count -gt 0) {
            $propiedades | ForEach-Object {
                Write-Host "    👤 $($_.persona_nombre) - $($_.tipo_tenencia) ($($_.porcentaje_propiedad)%)" -ForegroundColor Gray
            }
        }
        Write-Host ""
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "🎉 === PRUEBAS COMPLETADAS ===" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Otros endpoints disponibles:" -ForegroundColor Yellow
Write-Host "  📋 GET  /api/propiedades/           - Listar todas las propiedades" -ForegroundColor Gray
Write-Host "  👥 GET  /api/personas/              - Listar todas las personas" -ForegroundColor Gray
Write-Host "  🏠 GET  /api/personas/propietarios/ - Solo propietarios" -ForegroundColor Gray
Write-Host "  🔑 POST /api/propiedades/           - Asignar propiedad" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 Para probar otros endpoints, modifica este script o usa Postman" -ForegroundColor Cyan