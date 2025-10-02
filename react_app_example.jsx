// src/App.jsx - Ejemplo de integración en tu React
import React from 'react';
import AIButton from './components/AIButton';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Sistema de Seguridad</h1>
      </header>
      
      <main>
        {/* Tu contenido existente */}
        <div>
          <h2>Panel de Seguridad</h2>
          {/* Tus componentes existentes */}
        </div>
        
        {/* Agregar componente IA */}
        <div style={{ marginTop: '20px' }}>
          <AIButton />
        </div>
      </main>
    </div>
  );
}

export default App;