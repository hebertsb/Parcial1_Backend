# GUÍA COMPLETA: PANEL ADMIN - GESTIÓN DE PROPIETARIOS

## 📋 ENDPOINTS DISPONIBLES

### 1. LISTAR PROPIETARIOS CON INFORMACIÓN COMPLETA
```
GET /auth/admin/propietarios/listar/
Authorization: Bearer {admin_token}
```

**RESPONSE PAYLOAD:**
```json
{
  "success": true,
  "data": [
    {
      "usuario_id": 6,
      "copropietario_id": 8,
      "email": "laura.gonzález10@test.com",
      "nombres_completos": "Laura Segundo González Segundo",
      "documento_identidad": "12345010",
      "telefono": "77777777",
      "unidad_residencial": "V010",
      "tipo_residente": "Propietario",
      "foto_perfil_url": "https://dl.dropboxusercontent.com/scl/fi/...",
      "tiene_perfil_copropietario": true,
      "puede_subir_fotos": true,
      "estado_usuario": "ACTIVO",
      "fecha_creacion": "2025-09-28T10:30:00Z",
      "ultimo_login": "2025-09-28T15:45:00Z"
    }
  ],
  "total": 4
}
```

### 2. EDITAR PROPIETARIO
```
PUT /auth/admin/propietarios/{usuario_id}/editar/
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**REQUEST PAYLOAD:**
```json
{
  "nombres": "Nombre Actualizado",
  "apellidos": "Apellido Actualizado", 
  "telefono": "77777777",
  "unidad_residencial": "Casa 101",
  "estado_usuario": "ACTIVO"
}
```

**RESPONSE PAYLOAD:**
```json
{
  "success": true,
  "message": "Propietario actualizado exitosamente",
  "data": {
    "usuario_id": 6,
    "copropietario_id": 8,
    "nombres_completos": "Nombre Actualizado Apellido Actualizado",
    "unidad_residencial": "Casa 101"
  }
}
```

## 🏠 IMPLEMENTACIÓN FRONTEND - LISTA DE PROPIETARIOS

### COMPONENTE: ListaPropietarios.jsx
```jsx
import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, Avatar, Modal, Form, Input, Select, message } from 'antd';
import { UserOutlined, HomeOutlined, CameraOutlined, EditOutlined } from '@ant-design/icons';

const ListaPropietarios = () => {
  const [propietarios, setPropietarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editModal, setEditModal] = useState({ visible: false, propietario: null });

  // Cargar lista de propietarios
  const cargarPropietarios = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/auth/admin/propietarios/listar/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setPropietarios(data.data);
      } else {
        message.error('Error cargando propietarios');
      }
    } catch (error) {
      message.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  // Editar propietario
  const editarPropietario = async (valores) => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/auth/admin/propietarios/${editModal.propietario.usuario_id}/editar/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(valores)
      });
      
      const data = await response.json();
      if (data.success) {
        message.success('Propietario actualizado exitosamente');
        setEditModal({ visible: false, propietario: null });
        cargarPropietarios(); // Recargar lista
      } else {
        message.error(data.message || 'Error actualizando propietario');
      }
    } catch (error) {
      message.error('Error de conexión');
    }
  };

  useEffect(() => {
    cargarPropietarios();
  }, []);

  return (
    <div className="propietarios-container">
      <div className="header-section">
        <h2>Gestión de Propietarios</h2>
        <Button onClick={cargarPropietarios} loading={loading}>
          Actualizar Lista
        </Button>
      </div>

      <div className="propietarios-grid">
        {propietarios.map((prop) => (
          <Card
            key={prop.usuario_id}
            className="propietario-card"
            actions={[
              <Button 
                icon={<EditOutlined />} 
                onClick={() => setEditModal({ visible: true, propietario: prop })}
              >
                Editar
              </Button>
            ]}
          >
            <div className="propietario-header">
              <Avatar 
                size={64}
                icon={<UserOutlined />}
                src={prop.foto_perfil_url}
              />
              <div className="propietario-info">
                <h3>{prop.nombres_completos}</h3>
                <p>{prop.email}</p>
                <Badge 
                  status={prop.estado_usuario === 'ACTIVO' ? 'success' : 'error'}
                  text={prop.estado_usuario}
                />
              </div>
            </div>

            <div className="propietario-details">
              <div className="detail-item">
                <HomeOutlined style={{ color: '#1890ff' }} />
                <span><strong>Unidad:</strong> {prop.unidad_residencial}</span>
              </div>
              
              <div className="detail-item">
                <span><strong>Documento:</strong> {prop.documento_identidad}</span>
              </div>
              
              <div className="detail-item">
                <span><strong>Teléfono:</strong> {prop.telefono || 'No registrado'}</span>
              </div>

              <div className="detail-item">
                <CameraOutlined style={{ 
                  color: prop.puede_subir_fotos ? '#52c41a' : '#ff4d4f' 
                }} />
                <span>
                  <strong>Reconocimiento Facial:</strong> {' '}
                  {prop.puede_subir_fotos ? 'Habilitado' : 'Deshabilitado'}
                </span>
              </div>

              <div className="detail-item">
                <span>
                  <strong>Perfil Copropietario:</strong> {' '}
                  {prop.tiene_perfil_copropietario ? 'Sí' : 'No'}
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Modal de Edición */}
      <Modal
        title="Editar Propietario"
        open={editModal.visible}
        onCancel={() => setEditModal({ visible: false, propietario: null })}
        footer={null}
      >
        {editModal.propietario && (
          <Form
            initialValues={{
              nombres: editModal.propietario.nombres_completos.split(' ')[0],
              apellidos: editModal.propietario.nombres_completos.split(' ').slice(1).join(' '),
              telefono: editModal.propietario.telefono,
              unidad_residencial: editModal.propietario.unidad_residencial,
              estado_usuario: editModal.propietario.estado_usuario
            }}
            onFinish={editarPropietario}
            layout="vertical"
          >
            <Form.Item
              name="nombres"
              label="Nombres"
              rules={[{ required: true, message: 'Ingrese los nombres' }]}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="apellidos"
              label="Apellidos"
              rules={[{ required: true, message: 'Ingrese los apellidos' }]}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="telefono"
              label="Teléfono"
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="unidad_residencial"
              label="Unidad Residencial"
              rules={[{ required: true, message: 'Ingrese la unidad residencial' }]}
            >
              <Input placeholder="Ej: Casa 101, Apto 205" />
            </Form.Item>

            <Form.Item
              name="estado_usuario"
              label="Estado"
              rules={[{ required: true, message: 'Seleccione el estado' }]}
            >
              <Select>
                <Select.Option value="ACTIVO">Activo</Select.Option>
                <Select.Option value="INACTIVO">Inactivo</Select.Option>
                <Select.Option value="SUSPENDIDO">Suspendido</Select.Option>
                <Select.Option value="BLOQUEADO">Bloqueado</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block>
                Guardar Cambios
              </Button>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  );
};

export default ListaPropietarios;
```

### CSS ASOCIADO: propietarios.css
```css
.propietarios-container {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.propietarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.propietario-card {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 12px;
  transition: transform 0.2s;
}

.propietario-card:hover {
  transform: translateY(-4px);
}

.propietario-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.propietario-info h3 {
  margin: 0;
  color: #1890ff;
}

.propietario-info p {
  margin: 4px 0;
  color: #666;
}

.propietario-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.detail-item span {
  font-size: 14px;
}
```

## 🔧 CONFIGURACIÓN DE RUTAS

### En tu router principal:
```jsx
import { Route } from 'react-router-dom';
import ListaPropietarios from './components/admin/ListaPropietarios';

// Dentro de tus rutas admin
<Route path="/admin/propietarios" element={<ListaPropietarios />} />
```

## 📱 MENÚ DE NAVEGACIÓN ADMIN

### Agregar al menú admin:
```jsx
const menuItems = [
  {
    key: 'propietarios',
    icon: <HomeOutlined />,
    label: 'Gestión de Propietarios',
    path: '/admin/propietarios'
  },
  // ... otros items
];
```

## 🔒 AUTENTICACIÓN Y PERMISOS

### Verificar token admin:
```jsx
const verificarTokenAdmin = () => {
  const token = localStorage.getItem('admin_token');
  if (!token) {
    // Redirigir a login admin
    window.location.href = '/admin/login';
    return false;
  }
  return token;
};
```

## 📊 ESTADOS DE LA APLICACIÓN

### Context para propietarios:
```jsx
const PropietariosContext = createContext();

export const PropietariosProvider = ({ children }) => {
  const [propietarios, setPropietarios] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <PropietariosContext.Provider value={{ 
      propietarios, 
      setPropietarios, 
      loading, 
      setLoading 
    }}>
      {children}
    </PropietariosContext.Provider>
  );
};
```

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear componente ListaPropietarios.jsx
- [ ] Agregar estilos CSS
- [ ] Configurar rutas en router
- [ ] Agregar al menú de navegación admin
- [ ] Verificar autenticación admin
- [ ] Probar endpoints con tokens reales
- [ ] Manejar estados de carga y errores
- [ ] Implementar validaciones de formulario
- [ ] Agregar confirmaciones para ediciones
- [ ] Probar responsividad en móviles

## 🚀 FUNCIONALIDADES ADICIONALES RECOMENDADAS

1. **Filtros y búsqueda** por nombre, unidad, estado
2. **Exportar lista** a Excel/PDF
3. **Bulk actions** para cambiar estado de múltiples propietarios
4. **Historial de cambios** por propietario
5. **Notificaciones** cuando se actualiza un propietario