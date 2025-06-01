import React, { useState, useEffect, useCallback } from 'react';

const EmotionInterface = () => {
  const [status, setStatus] = useState(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [statusError, setStatusError] = useState('');

  const [currentEmotion, setCurrentEmotion] = useState(null);
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(false);
  const [currentError, setCurrentError] = useState('');

  const [eventInfo, setEventInfo] = useState(''); // JSON string
  const [appraisalContext, setAppraisalContext] = useState(''); // JSON string
  const [isAppraising, setIsAppraising] = useState(false);
  const [appraisalResult, setAppraisalResult] = useState(null);
  const [appraisalError, setAppraisalError] = useState('');

  const [expressionResult, setExpressionResult] = useState(null);
  const [isLoadingExpression, setIsLoadingExpression] = useState(false);
  const [expressionError, setExpressionError] = useState('');


  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

  const fetchStatus = useCallback(async () => {
    setIsLoadingStatus(true); setStatusError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/emotion/status`);
      if (!response.ok) throw new Error((await response.json()).error || `HTTP error! status: ${response.status}`);
      setStatus(await response.json());
    } catch (error) { setStatusError(error.message); setStatus(null); }
    finally { setIsLoadingStatus(false); }
  }, [API_BASE_URL]);

  const fetchCurrentEmotion = useCallback(async () => {
    setIsLoadingCurrent(true); setCurrentError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/emotion/current`);
      if (!response.ok) throw new Error((await response.json()).error || `HTTP error! status: ${response.status}`);
      const data = await response.json();
      setCurrentEmotion(data);
      // Also update general status if VAD/categorical is part of it
      if (status && data.vad_state && data.categorical_emotion) {
        setStatus(prevStatus => ({
            ...prevStatus,
            current_vad_state: data.vad_state,
            current_categorical_emotion: data.categorical_emotion
        }));
      }
    } catch (error) { setCurrentError(error.message); setCurrentEmotion(null); }
    finally { setIsLoadingCurrent(false); }
  }, [API_BASE_URL, status]);


  useEffect(() => {
    fetchStatus();
    fetchCurrentEmotion();
  }, [fetchStatus, fetchCurrentEmotion]);

  const handleAppraiseSituation = async (e) => {
    e.preventDefault();
    setIsAppraising(true); setAppraisalResult(null); setAppraisalError('');
    let parsedEventInfo, parsedContext = {};
    try {
      parsedEventInfo = JSON.parse(eventInfo);
      if (appraisalContext.trim()) parsedContext = JSON.parse(appraisalContext);
    } catch (jsonError) {
      setAppraisalError("Event Info or Context is not valid JSON."); setIsAppraising(false); return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/cml/emotion/appraise`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_info: parsedEventInfo, context: parsedContext }),
      });
      const resultData = await response.json();
      if (!response.ok) throw new Error(resultData.error || `HTTP error! status: ${response.status}`);
      setAppraisalResult(resultData);
      fetchCurrentEmotion(); // Refresh current emotion
      fetchStatus(); // Refresh status
    } catch (error) { setAppraisalError(error.message); }
    finally { setIsAppraising(false); }
  };

  const handleExpressEmotion = async () => {
    setIsLoadingExpression(true); setExpressionError(''); setExpressionResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/cml/emotion/express`);
      if (!response.ok) throw new Error((await response.json()).error || `HTTP error! status: ${response.status}`);
      setExpressionResult(await response.json());
    } catch (error) { setExpressionError(error.message); }
    finally { setIsLoadingExpression(false); }
  };

  const commonInputStyle = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
  const commonButtonStyle = "px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50";
  const sectionStyle = "p-4 border border-gray-300 rounded-lg mb-6 bg-white shadow";
  const headingStyle = "text-xl font-semibold mb-3 text-gray-700";
  const resultBoxStyle = "mt-2 p-2 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto";

  return (
    <div>
      <h2 className={headingStyle}>Emotion Module Interface</h2>

      <div className={sectionStyle}>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Module Status</h3>
        <button onClick={fetchStatus} disabled={isLoadingStatus} className={`${commonButtonStyle} mb-2`}>
          {isLoadingStatus ? 'Loading...' : 'Refresh Status'}
        </button>
        {statusError && <p className="text-red-500">Error: {statusError}</p>}
        {status && <pre className={resultBoxStyle}>{JSON.stringify(status, null, 2)}</pre>}
      </div>

      <div className={sectionStyle}>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Current Emotion</h3>
        <button onClick={fetchCurrentEmotion} disabled={isLoadingCurrent} className={`${commonButtonStyle} mb-2`}>
          {isLoadingCurrent ? 'Loading...' : 'Get Current Emotion'}
        </button>
        {currentError && <p className="text-red-500">Error: {currentError}</p>}
        {currentEmotion && <pre className={resultBoxStyle}>{JSON.stringify(currentEmotion, null, 2)}</pre>}
      </div>

      <div className={sectionStyle}>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Appraise Situation</h3>
        <form onSubmit={handleAppraiseSituation}>
          <div className="mb-4">
            <label htmlFor="eventInfo" className="block text-sm font-medium text-gray-700">Event Info (JSON):</label>
            <textarea id="eventInfo" value={eventInfo} onChange={(e) => setEventInfo(e.target.value)} required className={commonInputStyle} rows="3" placeholder='e.g., {"type": "goal_status", "goal_status": "achieved"}'/>
          </div>
          <div className="mb-4">
            <label htmlFor="appraisalContext" className="block text-sm font-medium text-gray-700">Context (JSON, optional):</label>
            <textarea id="appraisalContext" value={appraisalContext} onChange={(e) => setAppraisalContext(e.target.value)} className={commonInputStyle} rows="2" placeholder='e.g., {"perceived_valence": "positive"}'/>
          </div>
          <button type="submit" disabled={isAppraising} className={commonButtonStyle}>
            {isAppraising ? 'Appraising...' : 'Appraise Situation'}
          </button>
        </form>
        {appraisalError && <p className="text-red-500 mt-2">Error: {appraisalError}</p>}
        {appraisalResult && <div className="mt-4"><h4 className="text-md font-medium">Appraisal Result:</h4><pre className={resultBoxStyle}>{JSON.stringify(appraisalResult, null, 2)}</pre></div>}
      </div>

      <div className={sectionStyle}>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Express Emotion</h3>
        <button onClick={handleExpressEmotion} disabled={isLoadingExpression} className={`${commonButtonStyle} mb-2`}>
          {isLoadingExpression ? 'Loading...' : 'Express Emotion (Get Representation)'}
        </button>
        {expressionError && <p className="text-red-500">Error: {expressionError}</p>}
        {expressionResult && <pre className={resultBoxStyle}>{JSON.stringify(expressionResult, null, 2)}</pre>}
      </div>
    </div>
  );
};

export default EmotionInterface;
