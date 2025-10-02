// src/components/AIButton.jsx - Componente mínimo para tu React
import React, { useState } from 'react';
import aiService from '../services/aiService';

const AIButton = () => {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  const handleTrain = async () => {
    setLoading(true);
    try {
      const result = await aiService.trainModel();
      alert(`Entrenamiento completado! Precisión: ${(result.accuracy * 100).toFixed(1)}%`);
      
      // Actualizar estadísticas
      const newStats = await aiService.getStats();
      setStats(newStats.data);
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const result = await aiService.getStats();
      setStats(result.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  React.useEffect(() => {
    loadStats();
  }, []);

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h3>🧠 Sistema de IA</h3>
      
      {stats && (
        <div style={{ marginBottom: '15px' }}>
          <p>Estado: {stats.model_exists ? '✅ Activo' : '❌ Inactivo'}</p>
          <p>Precisión: {stats.accuracy ? (stats.accuracy * 100).toFixed(1) : 0}%</p>
          <p>Personas: {stats.people_in_model || 0}/{stats.total_people_in_db || 0}</p>
        </div>
      )}
      
      <button 
        onClick={handleTrain}
        disabled={loading}
        style={{
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? '🔄 Entrenando...' : '🧠 Entrenar IA'}
      </button>
    </div>
  );
};

export default AIButton;