# GUÍA COMPLETA: PANEL PROPIETARIOS - PERFIL CON VIVIENDA

## 🏠 ENDPOINT PARA OBTENER INFORMACIÓN COMPLETA DEL PROPIETARIO

### OBTENER PERFIL CON VIVIENDA
```
GET /api/authz/propietarios/perfil-completo/
Authorization: Bearer {propietario_token}
```

**RESPONSE PAYLOAD:**
```json
{
  "success": true,
  "data": {
    "usuario": {
      "id": 6,
      "email": "laura.gonzález10@test.com",
      "estado": "ACTIVO",
      "fecha_registro": "2025-09-28T10:30:00Z"
    },
    "persona": {
      "nombres": "Laura Segundo",
      "apellidos": "González Segundo", 
      "documento_identidad": "12345010",
      "telefono": "77777777",
      "email": "laura.gonzález10@test.com",
      "foto_perfil_url": "https://dl.dropboxusercontent.com/scl/fi/..."
    },
    "vivienda": {
      "numero_casa": "V010",
      "bloque": "Bloque A",
      "tipo_vivienda": "casa",
      "metros_cuadrados": "120.50",
      "estado": "activa"
    },
    "copropietario": {
      "id": 8,
      "unidad_residencial": "V010",
      "tipo_residente": "Propietario",
      "activo": true,
      "puede_subir_fotos": true
    },
    "solicitud_original": {
      "numero_casa": "V010",
      "fecha_solicitud": "2025-09-20T14:20:00Z",
      "fecha_aprobacion": "2025-09-21T09:15:00Z"
    },
    "reconocimiento_facial": {
      "habilitado": true,
      "total_fotos": 10,
      "ultima_subida": "2025-09-28T16:45:00Z"
    }
  }
}
```

## 📋 IMPLEMENTACIÓN FRONTEND - PERFIL PROPIETARIO

### COMPONENTE: PerfilPropietario.jsx
```jsx
import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Descriptions, 
  Avatar, 
  Button, 
  Badge, 
  Divider, 
  Row, 
  Col,
  Image,
  message,
  Upload,
  Modal
} from 'antd';
import { 
  UserOutlined, 
  HomeOutlined, 
  CameraOutlined, 
  EditOutlined,
  UploadOutlined 
} from '@ant-design/icons';

const PerfilPropietario = () => {
  const [perfil, setPerfil] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fotosModal, setFotosModal] = useState(false);

  // Cargar perfil completo
  const cargarPerfil = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('propietario_token');
      const response = await fetch('/api/authz/propietarios/perfil-completo/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setPerfil(data.data);
      } else {
        message.error('Error cargando perfil');
      }
    } catch (error) {
      message.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarPerfil();
  }, []);

  if (!perfil) {
    return <div>Cargando perfil...</div>;
  }

  return (
    <div className="perfil-propietario-container">
      {/* Header con foto y datos básicos */}
      <Card className="perfil-header-card">
        <Row gutter={24} align="middle">
          <Col xs={24} sm={8} md={6}>
            <div className="avatar-container">
              <Avatar 
                size={120}
                icon={<UserOutlined />}
                src={perfil.persona.foto_perfil_url}
                className="perfil-avatar"
              />
              <Button 
                icon={<CameraOutlined />}
                className="cambiar-foto-btn"
                onClick={() => setFotosModal(true)}
              >
                Gestionar Fotos
              </Button>
            </div>
          </Col>
          
          <Col xs={24} sm={16} md={18}>
            <div className="perfil-info">
              <h1 className="perfil-nombre">
                {perfil.persona.nombres} {perfil.persona.apellidos}
              </h1>
              <p className="perfil-email">{perfil.usuario.email}</p>
              <div className="perfil-badges">
                <Badge 
                  status={perfil.usuario.estado === 'ACTIVO' ? 'success' : 'error'}
                  text={`Usuario ${perfil.usuario.estado}`}
                />
                <Badge 
                  status={perfil.reconocimiento_facial.habilitado ? 'success' : 'warning'}
                  text={`Reconocimiento ${perfil.reconocimiento_facial.habilitado ? 'Activo' : 'Inactivo'}`}
                />
              </div>
            </div>
          </Col>
        </Row>
      </Card>

      <Row gutter={24}>
        {/* Información Personal */}
        <Col xs={24} lg={12}>
          <Card title="Información Personal" className="info-card">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Documento">
                {perfil.persona.documento_identidad}
              </Descriptions.Item>
              <Descriptions.Item label="Teléfono">
                {perfil.persona.telefono || 'No registrado'}
              </Descriptions.Item>
              <Descriptions.Item label="Email">
                {perfil.persona.email}
              </Descriptions.Item>
              <Descriptions.Item label="Fecha de Registro">
                {new Date(perfil.usuario.fecha_registro).toLocaleDateString()}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* Información de Vivienda */}
        <Col xs={24} lg={12}>
          <Card 
            title={
              <span>
                <HomeOutlined style={{ marginRight: 8 }} />
                Mi Vivienda
              </span>
            } 
            className="vivienda-card"
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Número de Casa">
                <strong className="numero-casa">
                  {perfil.vivienda.numero_casa}
                </strong>
              </Descriptions.Item>
              <Descriptions.Item label="Bloque">
                {perfil.vivienda.bloque || 'No especificado'}
              </Descriptions.Item>
              <Descriptions.Item label="Tipo">
                {perfil.vivienda.tipo_vivienda}
              </Descriptions.Item>
              <Descriptions.Item label="Metros Cuadrados">
                {perfil.vivienda.metros_cuadrados} m²
              </Descriptions.Item>
              <Descriptions.Item label="Estado">
                <Badge 
                  status={perfil.vivienda.estado === 'activa' ? 'success' : 'error'}
                  text={perfil.vivienda.estado}
                />
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      {/* Reconocimiento Facial */}
      <Card 
        title={
          <span>
            <CameraOutlined style={{ marginRight: 8 }} />
            Reconocimiento Facial
          </span>
        }
        extra={
          <Button 
            type="primary" 
            icon={<UploadOutlined />}
            onClick={() => setFotosModal(true)}
            disabled={!perfil.reconocimiento_facial.habilitado}
          >
            Subir Fotos
          </Button>
        }
        className="reconocimiento-card"
      >
        <Row gutter={16}>
          <Col span={8}>
            <div className="stat-item">
              <div className="stat-number">
                {perfil.reconocimiento_facial.total_fotos}
              </div>
              <div className="stat-label">Fotos Registradas</div>
            </div>
          </Col>
          <Col span={8}>
            <div className="stat-item">
              <div className="stat-number">
                {perfil.reconocimiento_facial.habilitado ? 'SÍ' : 'NO'}
              </div>
              <div className="stat-label">Habilitado</div>
            </div>
          </Col>
          <Col span={8}>
            <div className="stat-item">
              <div className="stat-number">
                {perfil.reconocimiento_facial.ultima_subida ? 
                  new Date(perfil.reconocimiento_facial.ultima_subida).toLocaleDateString() : 
                  'Nunca'
                }
              </div>
              <div className="stat-label">Última Subida</div>
            </div>
          </Col>
        </Row>

        {!perfil.reconocimiento_facial.habilitado && (
          <div className="warning-message">
            <p>
              ⚠️ El reconocimiento facial no está habilitado para tu cuenta. 
              Contacta al administrador para habilitarlo.
            </p>
          </div>
        )}
      </Card>

      {/* Historial de Solicitud */}
      <Card title="Historial de Registro" className="historial-card">
        <Descriptions column={2} size="small">
          <Descriptions.Item label="Casa Solicitada">
            {perfil.solicitud_original.numero_casa}
          </Descriptions.Item>
          <Descriptions.Item label="Fecha de Solicitud">
            {new Date(perfil.solicitud_original.fecha_solicitud).toLocaleDateString()}
          </Descriptions.Item>
          <Descriptions.Item label="Fecha de Aprobación">
            {new Date(perfil.solicitud_original.fecha_aprobacion).toLocaleDateString()}
          </Descriptions.Item>
          <Descriptions.Item label="Estado Actual">
            <Badge status="success" text="Aprobado y Activo" />
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Modal para gestionar fotos */}
      <Modal
        title="Gestionar Fotos de Reconocimiento"
        open={fotosModal}
        onCancel={() => setFotosModal(false)}
        footer={null}
        width={800}
      >
        <GestionarFotosComponent 
          usuarioId={perfil.usuario.id}
          onActualizar={cargarPerfil}
        />
      </Modal>
    </div>
  );
};

// Componente separado para gestionar fotos
const GestionarFotosComponent = ({ usuarioId, onActualizar }) => {
  // Implementar upload de fotos aquí
  // Usar el endpoint existente: POST /api/authz/reconocimiento/fotos/{usuario_id}/
  
  return (
    <div className="fotos-manager">
      <Upload.Dragger
        name="fotos"
        multiple
        accept="image/*"
        action={`/api/authz/reconocimiento/fotos/${usuarioId}/`}
        headers={{
          'Authorization': `Bearer ${localStorage.getItem('propietario_token')}`
        }}
        onChange={(info) => {
          if (info.file.status === 'done') {
            message.success('Foto subida exitosamente');
            onActualizar();
          } else if (info.file.status === 'error') {
            message.error('Error subiendo foto');
          }
        }}
      >
        <p className="ant-upload-drag-icon">
          <CameraOutlined />
        </p>
        <p className="ant-upload-text">
          Haz clic o arrastra fotos aquí para subirlas
        </p>
        <p className="ant-upload-hint">
          Formatos permitidos: JPG, PNG, JPEG. Máximo 10 fotos.
        </p>
      </Upload.Dragger>
    </div>
  );
};

export default PerfilPropietario;
```

### CSS ASOCIADO: perfil-propietario.css
```css
.perfil-propietario-container {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.perfil-header-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.avatar-container {
  text-align: center;
}

.perfil-avatar {
  border: 4px solid #1890ff;
}

.cambiar-foto-btn {
  margin-top: 12px;
  border-radius: 20px;
}

.perfil-info h1 {
  font-size: 28px;
  color: #1890ff;
  margin-bottom: 8px;
}

.perfil-email {
  font-size: 16px;
  color: #666;
  margin-bottom: 16px;
}

.perfil-badges .ant-badge {
  margin-right: 16px;
}

.info-card, .vivienda-card, .reconocimiento-card, .historial-card {
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.numero-casa {
  font-size: 18px;
  color: #1890ff;
  background: #e6f7ff;
  padding: 4px 8px;
  border-radius: 4px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.warning-message {
  background: #fff7e6;
  border: 1px solid #ffd591;
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
}

.warning-message p {
  margin: 0;
  color: #d46b08;
}

.fotos-manager {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .perfil-propietario-container {
    padding: 16px;
  }
  
  .perfil-info h1 {
    font-size: 24px;
  }
  
  .perfil-badges {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}
```

## 🔧 ENDPOINT ADICIONAL REQUERIDO EN BACKEND

Necesitas crear este endpoint en el backend para obtener la información completa:

```python
# En authz/views_propietarios_panel.py

@extend_schema(
    summary="Obtener perfil completo del propietario",
    description="Obtiene información completa del propietario incluyendo vivienda"
)
class PerfilCompletoPropietarioView(APIView, PropietarioPermissionMixin):
    def get(self, request):
        try:
            usuario = request.user
            
            # Obtener solicitud aprobada
            solicitud = SolicitudRegistroPropietario.objects.filter(
                usuario_creado=usuario,
                estado='APROBADA'
            ).first()
            
            # Obtener copropietario
            copropietario = getattr(usuario, 'copropietario_perfil', None)
            
            # Obtener fotos de reconocimiento
            fotos_count = 0
            ultima_subida = None
            if copropietario:
                from seguridad.models import ReconocimientoFacial
                fotos = ReconocimientoFacial.objects.filter(copropietario=copropietario)
                fotos_count = fotos.count()
                if fotos.exists():
                    ultima_subida = fotos.latest('fecha_enrolamiento').fecha_enrolamiento
            
            data = {
                'usuario': {
                    'id': usuario.id,
                    'email': usuario.email,
                    'estado': usuario.estado,
                    'fecha_registro': usuario.date_joined
                },
                'persona': {
                    'nombres': usuario.persona.nombre if usuario.persona else '',
                    'apellidos': usuario.persona.apellido if usuario.persona else '',
                    'documento_identidad': usuario.persona.documento_identidad if usuario.persona else '',
                    'telefono': usuario.persona.telefono if usuario.persona else '',
                    'email': usuario.persona.email if usuario.persona else usuario.email,
                    'foto_perfil_url': usuario.persona.foto_perfil_url if usuario.persona else None
                },
                'vivienda': None,
                'copropietario': {
                    'id': copropietario.id if copropietario else None,
                    'unidad_residencial': copropietario.unidad_residencial if copropietario else 'No asignada',
                    'tipo_residente': copropietario.tipo_residente if copropietario else 'Propietario',
                    'activo': copropietario.activo if copropietario else False,
                    'puede_subir_fotos': bool(copropietario)
                },
                'solicitud_original': None,
                'reconocimiento_facial': {
                    'habilitado': bool(copropietario),
                    'total_fotos': fotos_count,
                    'ultima_subida': ultima_subida
                }
            }
            
            # Agregar información de vivienda si existe
            if solicitud and solicitud.vivienda_validada:
                vivienda = solicitud.vivienda_validada
                data['vivienda'] = {
                    'numero_casa': vivienda.numero_casa,
                    'bloque': vivienda.bloque,
                    'tipo_vivienda': vivienda.tipo_vivienda,
                    'metros_cuadrados': str(vivienda.metros_cuadrados),
                    'estado': vivienda.estado
                }
                
            # Agregar información de solicitud
            if solicitud:
                data['solicitud_original'] = {
                    'numero_casa': solicitud.numero_casa,
                    'fecha_solicitud': solicitud.created_at,
                    'fecha_aprobacion': solicitud.fecha_aprobacion
                }
            
            return Response({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error obteniendo perfil: {str(e)}'
            }, status=500)
```

## 🔧 RUTA ADICIONAL

Agregar en `urls_propietarios_panel.py`:
```python
path('perfil-completo/', PerfilCompletoPropietarioView.as_view(), name='perfil-completo-propietario'),
```

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear endpoint backend `perfil-completo/`
- [ ] Implementar componente PerfilPropietario.jsx
- [ ] Agregar estilos CSS responsivos
- [ ] Configurar ruta en frontend
- [ ] Integrar con sistema de fotos existente
- [ ] Probar en diferentes dispositivos
- [ ] Validar datos mostrados
- [ ] Manejar casos de error
- [ ] Agregar loading states
- [ ] Probar con diferentes tipos de usuarios