import React, { useState, useEffect, useCallback } from 'react';

const PerceptionInterface = () => {
  const [status, setStatus] = useState(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [statusError, setStatusError] = useState('');

  const [rawInput, setRawInput] = useState('');
  const [modality, setModality] = useState('text');
  const [contextInput, setContextInput] = useState(''); // JSON string
  const [isProcessing, setIsProcessing] = useState(false);
  const [processResult, setProcessResult] = useState(null);
  const [processError, setProcessError] = useState('');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

  const fetchStatus = useCallback(async () => {
    setIsLoadingStatus(true);
    setStatusError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/perception/status`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error("Failed to fetch perception status:", error);
      setStatusError(error.message);
      setStatus(null);
    } finally {
      setIsLoadingStatus(false);
    }
  }, [API_BASE_URL]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const handleProcessInput = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setProcessResult(null);
    setProcessError('');

    let parsedContext = {};
    if (contextInput.trim()) {
      try {
        parsedContext = JSON.parse(contextInput);
      } catch (jsonError) {
        setProcessError("Context is not valid JSON.");
        setIsProcessing(false);
        return;
      }
    }

    try {
      const response = await fetch(`${API_BASE_URL}/cml/perception/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_input: rawInput, modality, context: parsedContext }),
      });
      const resultData = await response.json();
      if (!response.ok) {
        throw new Error(resultData.error || `HTTP error! status: ${response.status}`);
      }
      setProcessResult(resultData);
      fetchStatus(); // Refresh status after processing
    } catch (error) {
      console.error("Failed to process input:", error);
      setProcessError(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const commonInputStyle = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
  const commonButtonStyle = "px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50";
  const sectionStyle = "p-4 border border-gray-300 rounded-lg mb-6 bg-white shadow";
  const headingStyle = "text-xl font-semibold mb-3 text-gray-700";
  const resultBoxStyle = "mt-2 p-2 border border-gray-200 rounded bg-gray-50 max-h-96 overflow-y-auto";


  return (
    <div>
      <h2 className={headingStyle}>Perception Module Interface</h2>

      <div className={sectionStyle}>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Module Status</h3>
        <button onClick={fetchStatus} disabled={isLoadingStatus} className={`${commonButtonStyle} mb-2`}>
          {isLoadingStatus ? 'Loading...' : 'Refresh Status'}
        </button>
        {statusError && <p className="text-red-500">Error: {statusError}</p>}
        {status && <pre className={resultBoxStyle}>{JSON.stringify(status, null, 2)}</pre>}
      </div>

      <div className={sectionStyle}>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Process Sensory Input</h3>
        <form onSubmit={handleProcessInput}>
          <div className="mb-4">
            <label htmlFor="rawInput" className="block text-sm font-medium text-gray-700">Raw Input:</label>
            <textarea
              id="rawInput"
              value={rawInput}
              onChange={(e) => setRawInput(e.target.value)}
              required
              className={commonInputStyle}
              rows="3"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="modality" className="block text-sm font-medium text-gray-700">Modality:</label>
            <select
              id="modality"
              value={modality}
              onChange={(e) => setModality(e.target.value)}
              className={commonInputStyle}
            >
              <option value="text">Text</option>
              <option value="dict_mock">Dictionary Mock</option>
              {/* Add other supported modalities as needed */}
            </select>
          </div>
          <div className="mb-4">
            <label htmlFor="contextInput" className="block text-sm font-medium text-gray-700">Context (JSON string, optional):</label>
            <textarea
              id="contextInput"
              value={contextInput}
              onChange={(e) => setContextInput(e.target.value)}
              className={commonInputStyle}
              rows="2"
              placeholder='e.g., {"source_id": "user_xyz"}'
            />
          </div>
          <button type="submit" disabled={isProcessing} className={commonButtonStyle}>
            {isProcessing ? 'Processing...' : 'Process Input'}
          </button>
        </form>
        {processError && <p className="text-red-500 mt-2">Error: {processError}</p>}
        {processResult && (
          <div className="mt-4">
            <h4 className="text-md font-medium text-gray-800">Processing Result:</h4>
            <pre className={resultBoxStyle}>{JSON.stringify(processResult, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default PerceptionInterface;
