import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

function SEInterface() {
  const [isLoading, setIsLoading] = useState(false);
  const [simulationResults, setSimulationResults] = useState(null);
  const [error, setError] = useState('');

  const handleRunSimulation = async () => {
    setIsLoading(true);
    setError('');
    setSimulationResults(null);

    try {
      // The backend /api/piase/run_simulation is a POST request
      // and currently runs a hardcoded scenario, so no body is strictly needed for this version.
      const response = await fetch(`${API_BASE_URL}/api/piase/run_simulation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // Still good practice to send
        },
        // body: JSON.stringify({}), // Send empty JSON object if backend expects it
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }
      
      setSimulationResults(data);

    } catch (err) {
      console.error("Simulation run error:", err);
      setError(err.message);
      setSimulationResults(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  const commonInputStyle = "mt-1 block w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-gray-200";
  const commonTextareaClass = `${commonInputStyle} min-h-[60px]`;
  const commonLabelClass = "block text-sm font-medium text-gray-300";
  const sectionClass = "p-4 bg-slate-800 rounded-lg mb-6 shadow";
  const headingClass = "text-xl font-semibold mb-3 text-sky-400";
  const commonButtonClass = "px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-75 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors";


  return (
    <div className="se-interface p-4">
      <h1 className="text-2xl font-bold mb-6 text-sky-300">PiaSE - Simulation Engine Interface</h1>

      <div className={sectionClass}>
        <h2 className={headingClass}>Run Simulation</h2>
        <p className="text-gray-400 mb-4">
          Click the button below to run a default GridWorld scenario on the backend.
        </p>
        <button
          onClick={handleRunSimulation}
          disabled={isLoading}
          className={commonButtonClass}
        >
          {isLoading ? 'Running Simulation...' : 'Run Default GridWorld Scenario'}
        </button>
      </div>

      {isLoading && (
        <div className="mt-6 text-center">
          <p className="text-lg text-gray-300">Simulation in progress, please wait...</p>
          {/* You could add a spinner here */}
        </div>
      )}

      {error && (
        <div className={`${sectionClass} mt-6 border-red-500/50`}>
          <h2 className={`${headingClass} text-red-400`}>Error</h2>
          <p className="text-red-300 bg-red-900 p-3 rounded">{error}</p>
        </div>
      )}

      {simulationResults && (
        <div className={`${sectionClass} mt-6`}>
          <h2 className={headingClass}>Simulation Results (Run ID: {simulationResults.run_id})</h2>
          
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-300 mb-2">Summary:</h3>
            <p className="text-gray-400">Agent Reached Goal: {simulationResults.summary?.agent_reached_goal ? 'Yes' : 'No'}</p>
            <p className="text-gray-400">Total Steps Taken: {simulationResults.summary?.total_steps_taken}</p>
            <p className="text-gray-400">Final Agent Position: {JSON.stringify(simulationResults.summary?.final_agent_position)}</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-300 mb-2">Text Log:</h3>
            <pre className="p-3 bg-slate-900 text-gray-300 rounded-md max-h-96 overflow-y-auto text-sm">
              {simulationResults.text_log}
            </pre>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-300 mb-3">Generated Images:</h3>
            {simulationResults.image_urls && simulationResults.image_urls.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {simulationResults.image_urls.map((url, index) => (
                  <div key={index} className="p-2 bg-slate-700 rounded shadow">
                    <img 
                      src={`${API_BASE_URL}${url}`} // Assuming URLs are relative to API_BASE_URL/static/...
                      alt={`Simulation step ${index}`} 
                      className="w-full h-auto rounded" 
                    />
                    <p className="text-center text-xs text-gray-400 mt-1">{url.split('/').pop()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400">No images were generated or returned.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Renaming SEPage to SEInterface for clarity, assuming SEPage was the placeholder.
// If SEPage was meant to be distinct, then this component should be SEInterface.jsx
// and App.jsx should route /se to <SEInterface />
export default SEInterface;
