import React, { useState } from 'react';
import PerceptionInterface from './PerceptionInterface';
import EmotionInterface from './EmotionInterface';
import MotivationalSystemInterface from './MotivationalSystemInterface';
import WorkingMemoryInterface from './WorkingMemoryInterface';

const CMLDashboard = () => {
  const [activeModule, setActiveModule] = useState(null);

  const renderModuleInterface = () => {
    switch (activeModule) {
      case 'perception':
        return <PerceptionInterface />;
      case 'emotion':
        return <EmotionInterface />;
      case 'motivation':
        return <MotivationalSystemInterface />;
      case 'wm':
        return <WorkingMemoryInterface />;
      default:
        return <p>Select a CML module to interact with.</p>;
    }
  };

  const navButtonBaseStyle = "px-4 py-2 m-1 rounded-lg focus:outline-none focus:ring-2 focus:ring-opacity-50";
  const activeButtonStyle = `${navButtonBaseStyle} bg-blue-600 text-white focus:ring-blue-500`;
  const inactiveButtonStyle = `${navButtonBaseStyle} bg-gray-200 hover:bg-gray-300 text-gray-700 focus:ring-gray-400`;


  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1 style={{ borderBottom: '2px solid #eee', paddingBottom: '10px', fontSize: '2em' }}>
        Cognitive Module Library (CML) Interaction Dashboard
      </h1>
      <nav style={{ margin: '20px 0' }}>
        <button
            onClick={() => setActiveModule('perception')}
            className={activeModule === 'perception' ? activeButtonStyle : inactiveButtonStyle}>
            Perception
        </button>
        <button
            onClick={() => setActiveModule('emotion')}
            className={activeModule === 'emotion' ? activeButtonStyle : inactiveButtonStyle}>
            Emotion
        </button>
        <button
            onClick={() => setActiveModule('motivation')}
            className={activeModule === 'motivation' ? activeButtonStyle : inactiveButtonStyle}>
            Motivation
        </button>
        <button
            onClick={() => setActiveModule('wm')}
            className={activeModule === 'wm' ? activeButtonStyle : inactiveButtonStyle}>
            Working Memory
        </button>
      </nav>
      <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
        {renderModuleInterface()}
      </div>
    </div>
  );
};

export default CMLDashboard;
