import React, { useState } from 'react';
import LogUploader from '../avt/LogUploader'; // Adjust path if needed
import SimpleLogChart from '../avt/SimpleLogChart'; // Adjust path if needed

const STREAMLIT_AVT_URL = 'http://localhost:8501'; // Placeholder URL

function AVTInterface() {
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [analysisError, setAnalysisError] = useState('');

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    // Example: Simulate data if backend isn't ready
    // if (!data && !isLoadingAnalysis && !analysisError) { 
    //   console.log("Simulating analysis data for chart display.");
    //   setAnalysisData({
    //     "AGENT_ACTION": 50,
    //     "AGENT_PERCEPTION": 50,
    //     "STEP_END": 10,
    //     "SIMULATION_START": 1
    //   });
    // }
  };

  const handleAnalysisError = (errorMessage) => {
    setAnalysisError(errorMessage);
  };
  
  const commonInputStyle = "mt-1 block w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-gray-200";
  const commonTextareaClass = `${commonInputStyle} min-h-[60px]`;
  const commonLabelClass = "block text-sm font-medium text-gray-300";
  const sectionClass = "p-4 bg-slate-800 rounded-lg mb-6 shadow";
  const headingClass = "text-xl font-semibold mb-3 text-sky-400";
  const commonButtonClass = "px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-75 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors";


  return (
    <div className="avt-interface p-4">
      <h1 className="text-2xl font-bold mb-6 text-sky-300">PiaAVT - Analysis & Visualization Toolkit</h1>

      <div className={sectionClass}>
        <h2 className={headingClass}>Standalone PiaAVT Streamlit Application</h2>
        <p className="text-gray-400 mb-3">
          For comprehensive analysis and visualization of PiaAGI tool outputs (especially PiaSE simulation logs), 
          PiaAVT is primarily available as a standalone Streamlit application.
        </p>
        <a 
          href={STREAMLIT_AVT_URL} 
          target="_blank" 
          rel="noopener noreferrer"
          className={commonButtonClass}
        >
          Open PiaAVT Streamlit App (localhost:8501)
        </a>
        <p className="text-xs text-gray-500 mt-2">
          (Ensure the Streamlit PiaAVT application is running separately)
        </p>
      </div>

      <div className={sectionClass}>
        <h2 className={headingClass}>Basic Log Analysis (Integrated Feature - Conceptual)</h2>
        <p className="text-gray-400 mb-3">
          Upload a PiaSE log file (JSON/JSONL) for a very basic automated analysis. 
          The backend for this feature is conceptual and not yet implemented.
        </p>
        <LogUploader 
          onAnalysisComplete={handleAnalysisComplete} 
          onError={handleAnalysisError}
          isLoading={isLoadingAnalysis} // Pass isLoading state
          setIsLoading={setIsLoadingAnalysis} // Pass setter for isLoading state
        />
        {isLoadingAnalysis && <p className="text-gray-300 mt-2">Analyzing log, please wait...</p>}
        {analysisError && <p className="text-red-400 bg-red-900 p-3 rounded mt-2">Analysis Error: {analysisError}</p>}
        
        <div className="mt-4">
          <SimpleLogChart analysisData={analysisData} chartTitle="Basic Event Counts from Log" />
        </div>
      </div>
    </div>
  );
}

// Assuming AVTPage.jsx is intended to be this interface.
export default AVTInterface;
