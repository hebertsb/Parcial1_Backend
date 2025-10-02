// 🔧 CORRECCIÓN SIMPLE PARA EL PANEL DE RECONOCIMIENTO FACIAL
// Solo necesitas cambiar UNA LÍNEA en tu código actual

// ❌ PROBLEMA EN TU CÓDIGO ACTUAL (línea ~100):
// fetch('http://127.0.0.1:8000/api/seguridad/dashboard/')

// ✅ SOLUCIÓN - CAMBIAR POR:
// fetch('http://127.0.0.1:8000/api/seguridad/health/')

// 📋 CAMBIOS ESPECÍFICOS NECESARIOS:

/*
BUSCAR en tu archivo panel-reconocimiento-facial.tsx:

LÍNEA ~98-104:
❌ CÓDIGO ACTUAL:
console.log('🔍 Verificando conexión con backend...');
const response = await fetch('http://127.0.0.1:8000/api/seguridad/dashboard/');
console.log('🌐 Test conexión:', response.status);

✅ CAMBIAR POR:
console.log('🔍 Verificando conexión con backend...');
const response = await fetch('http://127.0.0.1:8000/api/seguridad/health/');
console.log('🌐 Test conexión:', response.status);

if (response.ok) {
  const data = await response.json();
  console.log('✅ Backend funcionando:', data.message);
} else {
  console.log('❌ Backend error:', response.status);
}
*/

// 🎯 EXPLICACIÓN DEL CAMBIO:
// 
// 1. /api/seguridad/dashboard/ → Requiere autenticación (JWT token)
// 2. /api/seguridad/health/ → NO requiere autenticación
// 
// El health check devuelve esto:
// {
//   "success": true,
//   "message": "Backend funcionando correctamente",
//   "timestamp": "2025-09-29T22:09:31.544710+00:00",
//   "status": "online",
//   "version": "1.0.0"
// }

// 🔄 ALTERNATIVA: Si NECESITAS el dashboard específicamente
// 
// Entonces necesitas manejar autenticación:

const verificarConexionConAuth = async () => {
  try {
    // Opción 1: Solo verificar que backend existe
    const healthResponse = await fetch('http://127.0.0.1:8000/api/seguridad/health/');
    if (healthResponse.ok) {
      console.log('✅ Backend OK - Sin autenticación necesaria');
      return true;
    }
    
    // Opción 2: Si necesitas dashboard, primero hacer login
    const loginResponse = await fetch('http://127.0.0.1:8000/authz/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'tu_usuario', // Cambiar por credenciales reales
        password: 'tu_password'
      })
    });
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json();
      const token = loginData.access_token || loginData.access;
      
      // Ahora sí puedes acceder al dashboard
      const dashboardResponse = await fetch('http://127.0.0.1:8000/api/seguridad/dashboard/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json();
        console.log('✅ Dashboard accedido con token:', dashboardData);
        return true;
      }
    }
    
  } catch (error) {
    console.error('❌ Error en verificación:', error);
    return false;
  }
};

// 📝 RECOMENDACIÓN:
// 
// Para reconocimiento facial NO necesitas el dashboard
// Solo cambia a /api/seguridad/health/ y listo
// 
// El reconocimiento facial funciona con:
// POST /api/seguridad/verificacion-tiempo-real/
// 
// Que NO requiere autenticación