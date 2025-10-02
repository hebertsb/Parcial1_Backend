// 🔧 CORRECCIÓN PARA EL PANEL DE RECONOCIMIENTO FACIAL
// Archivo: panel-reconocimiento-facial.tsx
// 
// ❌ PROBLEMA: El frontend está usando /api/seguridad/dashboard/ (requiere auth)
// ✅ SOLUCIÓN: Cambiar a /api/seguridad/health/ (sin auth) o manejar autenticación

import React, { useState, useEffect } from 'react';

const PanelReconocimientoFacial = () => {
  const [backendStatus, setBackendStatus] = useState('checking');
  const [foto, setFoto] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);

  // 🔧 CORRECCIÓN 1: Cambiar verificación de conexión
  const verificarConexionBackend = async () => {
    try {
      console.log('🔍 Verificando conexión con backend...');
      
      // ✅ CAMBIAR ESTA LÍNEA:
      // const response = await fetch('http://127.0.0.1:8000/api/seguridad/dashboard/'); // ❌ 401
      
      // ✅ POR ESTA:
      const response = await fetch('http://127.0.0.1:8000/api/seguridad/health/'); // ✅ Sin auth
      
      console.log('🌐 Test conexión:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Backend funcionando:', data.message);
        setBackendStatus('online');
      } else {
        console.log('❌ Backend error:', response.status);
        setBackendStatus('error');
      }
    } catch (error) {
      console.error('💥 Error crítico:', error);
      setBackendStatus('offline');
      throw new Error('Backend no disponible - Verificar que Django esté corriendo en puerto 8000');
    }
  };

  // 🔧 CORRECCIÓN 2: Verificar conexión al montar componente
  useEffect(() => {
    verificarConexionBackend().catch(error => {
      console.error('Error en verificación inicial:', error.message);
    });
  }, []);

  // ✅ FUNCIÓN DE VERIFICACIÓN DE IDENTIDAD (esta está bien)
  const verificarIdentidad = async () => {
    if (!foto) {
      alert('Por favor selecciona una foto primero');
      return;
    }

    setCargando(true);
    setResultado(null);

    try {
      // Verificar conexión antes de procesar
      await verificarConexionBackend();

      const formData = new FormData();
      formData.append('foto_verificacion', foto);
      formData.append('umbral_confianza', '70.0');
      formData.append('buscar_en', 'propietarios');
      formData.append('usar_ia_real', 'false'); // Empezar con simulación

      console.log('📂 Archivo válido:', {
        nombre: foto.name,
        tamaño_mb: (foto.size / 1024 / 1024).toFixed(2),
        tipo: foto.type
      });

      const response = await fetch('http://127.0.0.1:8000/api/seguridad/verificacion-tiempo-real/', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setResultado({
          tipo: data.verificacion.resultado === 'ACEPTADO' ? 'exito' : 'denegado',
          data: data
        });
      } else {
        setResultado({
          tipo: 'error',
          mensaje: data.error || 'Error desconocido'
        });
      }
    } catch (error) {
      console.error('Error en verificación:', error);
      setResultado({
        tipo: 'error',
        mensaje: error.message
      });
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="panel-reconocimiento-facial">
      <h2>Verificación Facial con IA</h2>
      
      {/* Estado del backend */}
      <div className="backend-status">
        {backendStatus === 'checking' && '🔄 Verificando conexión...'}
        {backendStatus === 'online' && '✅ Backend conectado'}
        {backendStatus === 'error' && '⚠️ Backend con errores'}
        {backendStatus === 'offline' && '❌ Backend no disponible'}
      </div>

      {/* Captura de foto */}
      <div className="captura-foto">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFoto(e.target.files[0])}
        />
      </div>

      {/* Botón de verificación */}
      <button
        onClick={verificarIdentidad}
        disabled={!foto || cargando || backendStatus !== 'online'}
      >
        {cargando ? '⏳ Verificando...' : '🔍 Verificar Identidad'}
      </button>

      {/* Resultado */}
      {resultado && (
        <div className={`resultado ${resultado.tipo}`}>
          {resultado.tipo === 'exito' && (
            <div>
              <h3>✅ ACCESO AUTORIZADO</h3>
              <p>👤 {resultado.data.verificacion.persona_identificada.nombre_completo}</p>
              <p>🎯 Confianza: {resultado.data.verificacion.confianza.toFixed(1)}%</p>
            </div>
          )}
          {resultado.tipo === 'denegado' && (
            <div>
              <h3>❌ ACCESO DENEGADO</h3>
              <p>📊 Confianza: {resultado.data.verificacion.confianza.toFixed(1)}%</p>
            </div>
          )}
          {resultado.tipo === 'error' && (
            <div>
              <h3>⚠️ ERROR</h3>
              <p>{resultado.mensaje}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PanelReconocimientoFacial;

// 📋 RESUMEN DE CAMBIOS NECESARIOS:
// 
// 1. ✅ CAMBIAR línea ~100:
//    ❌ fetch('http://127.0.0.1:8000/api/seguridad/dashboard/')
//    ✅ fetch('http://127.0.0.1:8000/api/seguridad/health/')
//
// 2. ✅ AGREGAR manejo de estado del backend
//
// 3. ✅ VERIFICAR conexión antes de cada operación
//
// 4. ✅ MEJORAR manejo de errores
//
// 💡 ALTERNATIVA: Si necesitas el dashboard, primero hacer login:
//    1. POST /authz/login/ con credenciales
//    2. Usar token en header Authorization: Bearer <token>
//    3. Luego acceder a /api/seguridad/dashboard/