================================================================================
⚠️ DETALLES CRÍTICOS PARA IMPLEMENTACIÓN FRONTEND - RECONOCIMIENTO FACIAL
================================================================================

🔍 PROBLEMAS IDENTIFICADOS EN LA IMPLEMENTACIÓN ANTERIOR DE SEGURIDAD:

1. 🚨 ERROR DE PROXY/CONEXIÓN:
   - El frontend puede tener problemas de proxy configurado
   - Error típico: "Unable to connect to proxy"
   - SOLUCIÓN: Configurar correctamente las URLs del API

2. 🔗 URL DEL ENDPOINT CORRECTO:
   ✅ URL COMPLETA: http://127.0.0.1:8000/api/seguridad/verificacion-tiempo-real/
   ❌ NO usar: /seguridad/verificacion-tiempo-real/
   ❌ NO usar: /api/verificacion-tiempo-real/

3. 🌐 CONFIGURACIÓN CORS:
   - El backend tiene CORS habilitado para todas las origins (desarrollo)
   - CORS_ALLOW_ALL_ORIGINS = True
   - CORS_ALLOW_CREDENTIALS = True
   - Headers permitidos: Authorization, Content-Type, etc.

================================================================================
🔧 CONFIGURACIÓN ESPECÍFICA PARA EL FRONTEND
================================================================================

1. 📡 CONFIGURACIÓN DE AXIOS/FETCH:

```javascript
// Configuración base para requests
const API_CONFIG = {
  baseURL: 'http://127.0.0.1:8000',
  timeout: 30000, // 30 segundos para IA
  headers: {
    'Content-Type': 'multipart/form-data', // Para subida de archivos
  }
};

// NO usar proxy en desarrollo local
const axiosInstance = axios.create({
  ...API_CONFIG,
  proxy: false // IMPORTANTE: Desactivar proxy
});
```

2. 🔒 MANEJO DE AUTENTICACIÓN (SI ES NECESARIO):

```javascript
// Si tu frontend maneja JWT, incluir headers
const headers = {
  'Authorization': `Bearer ${token}`, // Solo si tienes autenticación
  // NO incluir Content-Type para FormData - se auto-genera
};
```

3. 📤 ENVÍO CORRECTO DE FORMDATA:

```javascript
const formData = new FormData();
formData.append('foto_verificacion', file);
formData.append('umbral_confianza', '70.0');
formData.append('buscar_en', 'propietarios');
formData.append('usar_ia_real', 'true');

// NO hacer JSON.stringify en FormData
// NO set Content-Type manualmente para FormData
```

4. 🎯 FETCH CORRECTO:

```javascript
const response = await fetch('http://127.0.0.1:8000/api/seguridad/verificacion-tiempo-real/', {
  method: 'POST',
  body: formData, // Directamente FormData
  // NO incluir Content-Type header
});
```

================================================================================
🐛 ERRORES COMUNES Y SOLUCIONES
================================================================================

1. ❌ ERROR: "Mixed Content" (HTTPS/HTTP):
   SOLUCIÓN: Usar HTTP tanto en frontend como backend en desarrollo

2. ❌ ERROR: "CORS Policy":
   SOLUCIÓN: Verificar que el backend esté en http://127.0.0.1:8000
   NO usar localhost (puede causar problemas de CORS)

3. ❌ ERROR: "Network Error":
   CAUSAS:
   - Servidor backend no está corriendo
   - URL incorrecta
   - Proxy mal configurado

4. ❌ ERROR: "Content-Type multipart/form-data":
   SOLUCIÓN: NO establecer Content-Type manualmente para FormData

5. ❌ ERROR: "Request timeout":
   SOLUCIÓN: Aumentar timeout a 30+ segundos para IA real

6. ❌ ERROR: "400 Bad Request":
   CAUSAS:
   - Archivo muy grande (>5MB)
   - Formato de imagen no válido
   - Parámetros mal formateados

================================================================================
🔍 DEBUGGING FRONTEND
================================================================================

1. 🕵️ VERIFICAR CONEXIÓN:

```javascript
// Test básico de conexión
fetch('http://127.0.0.1:8000/api/seguridad/dashboard/')
  .then(r => console.log('Backend OK:', r.status))
  .catch(e => console.error('Backend Error:', e));
```

2. 📊 LOGGING DEL REQUEST:

```javascript
console.log('Enviando request a:', 'http://127.0.0.1:8000/api/seguridad/verificacion-tiempo-real/');
console.log('FormData contents:');
for (let [key, value] of formData.entries()) {
  console.log(key, value);
}
```

3. 🔍 INSPECCIONAR NETWORK TAB:
   - Verificar que el request sea POST
   - Content-Type debe ser multipart/form-data con boundary
   - Status code esperado: 200
   - Response debe tener JSON con success: true/false

================================================================================
🎨 CONFIGURACIÓN POR FRAMEWORK
================================================================================

📱 REACT:
```javascript
// .env file
REACT_APP_API_URL=http://127.0.0.1:8000

// En el componente
const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
```

🟢 VUE.js:
```javascript
// vue.config.js
module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
}
```

⚡ VITE:
```javascript
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
}
```

================================================================================
🚀 ENDPOINTS DISPONIBLES PARA EL FRONTEND
================================================================================

✅ ENDPOINT PRINCIPAL:
POST http://127.0.0.1:8000/api/seguridad/verificacion-tiempo-real/

✅ ENDPOINTS ADICIONALES:
- GET /api/seguridad/propietarios-reconocimiento/ (lista propietarios)
- GET /api/seguridad/usuarios-reconocimiento/ (lista usuarios)
- GET /api/seguridad/dashboard/ (estadísticas)

================================================================================
⚡ RESPUESTAS ESPERADAS DEL API
================================================================================

🟢 ÉXITO (Status 200):
```json
{
  "success": true,
  "verificacion": {
    "resultado": "ACEPTADO",
    "persona_identificada": {
      "id": 1,
      "nombre_completo": "Luis García",
      "documento": "12345678",
      "unidad": "Apto 101",
      "tipo_residente": "Propietario"
    },
    "confianza": 85.7,
    "umbral_usado": "70.0"
  },
  "estadisticas": {
    "total_comparaciones": 10,
    "tiempo_procesamiento_ms": 2340.5
  }
}
```

🔴 DENEGADO (Status 200):
```json
{
  "success": true,
  "verificacion": {
    "resultado": "DENEGADO",
    "confianza": 45.2,
    "umbral_usado": "70.0"
  }
}
```

❌ ERROR (Status 400/500):
```json
{
  "success": false,
  "error": "Descripción del error"
}
```

================================================================================
🔥 CHECKLIST FINAL ANTES DE IMPLEMENTAR
================================================================================

☑️ Backend Django corriendo en http://127.0.0.1:8000
☑️ Endpoint verificacion-tiempo-real disponible
☑️ CORS configurado correctamente
☑️ Frontend configurado sin proxy para desarrollo local
☑️ Timeout aumentado a 30+ segundos
☑️ FormData enviado sin Content-Type manual
☑️ Manejo de errores implementado
☑️ Loading states para UX
☑️ Validación de archivos (tamaño, formato)
☑️ Preview de imagen funcional

================================================================================
🚨 PROBLEMAS ESPECÍFICOS ENCONTRADOS EN TU IMPLEMENTACIÓN ANTERIOR
================================================================================

1. 🔍 PROBLEMA DE PROXY:
   - Error: "Unable to connect to proxy"
   - Tu sistema tiene configurado un proxy que interfiere
   - SOLUCIÓN: Desactivar proxy para localhost/127.0.0.1

2. 🔗 URL STRUCTURE:
   - El endpoint está en: /api/seguridad/verificacion-tiempo-real/
   - NO en: /seguridad/ o /reconocimiento-facial/

3. 🎯 CONFIGURACIÓN ESPECIAL PARA TU ENTORNO:
   - Usar 127.0.0.1 en lugar de localhost
   - Verificar que no haya variables de entorno de proxy
   - El servidor está corriendo correctamente (puerto 8000)

🔥 ¡LISTO PARA IMPLEMENTACIÓN SIN ERRORES! 🔥