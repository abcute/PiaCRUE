import React, { useState, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

function LogUploader({ onAnalysisComplete, onError, setIsLoading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.name.endsWith('.json') || file.name.endsWith('.jsonl')) {
        setSelectedFile(file);
        setFileError('');
      } else {
        setSelectedFile(null);
        setFileError('Invalid file type. Please select a .json or .jsonl file.');
      }
    }
  };

  const handleUpload = useCallback(async () => {
    if (!selectedFile) {
      setFileError('Please select a file first.');
      return;
    }
    setIsLoading(true);
    onError(''); // Clear previous errors
    onAnalysisComplete(null); // Clear previous results

    const formData = new FormData();
    formData.append('logFile', selectedFile);

    try {
      // This endpoint doesn't exist yet, this is a conceptual call
      const response = await fetch(`${API_BASE_URL}/api/avt/analyze_log_basic`, {
        method: 'POST',
        body: formData, // FormData sets Content-Type automatically
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }
      
      onAnalysisComplete(data.analysisResults); // Assuming backend returns { analysisResults: ... }

    } catch (err) {
      console.error("Log analysis error:", err);
      onError(err.message);
      onAnalysisComplete(null);
    } finally {
      setIsLoading(false);
    }
  }, [selectedFile, onAnalysisComplete, onError, setIsLoading]);
  
  const commonButtonClass = "px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-75 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors";
  const fileInputClass = "mt-1 block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-100 file:text-sky-700 hover:file:bg-sky-200";


  return (
    <div className="log-uploader my-4 p-4 border border-slate-700 rounded-lg">
      <h3 className="text-md font-semibold text-gray-300 mb-2">Upload Log File for Basic Analysis</h3>
      <input 
        type="file" 
        accept=".json,.jsonl" 
        onChange={handleFileChange} 
        className={fileInputClass}
      />
      {selectedFile && <p className="text-sm text-gray-400 mt-1">Selected file: {selectedFile.name}</p>}
      {fileError && <p className="text-sm text-red-500 mt-1">{fileError}</p>}
      
      <button 
        onClick={handleUpload} 
        disabled={!selectedFile || setIsLoading === null} // setIsLoading will be passed as prop
        className={`${commonButtonClass} mt-3`}
      >
        Analyze Log (Conceptual)
      </button>
      <p className="text-xs text-gray-500 mt-2">
        Note: The backend endpoint for this feature is not yet implemented. 
        This is a UI placeholder.
      </p>
    </div>
  );
}

export default LogUploader;
