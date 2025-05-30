import React, { useState, useEffect, useCallback } from 'react';

const MotivationalSystemInterface = () => {
  const [status, setStatus] = useState(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [statusError, setStatusError] = useState('');

  // Manage Goals state
  const [manageAction, setManageAction] = useState('add');
  const [goalId, setGoalId] = useState('');
  const [goalDescription, setGoalDescription] = useState('');
  const [goalType, setGoalType] = useState('intrinsic');
  const [goalPriority, setGoalPriority] = useState(0.5);
  const [goalSource, setGoalSource] = useState('');
  const [goalDetails, setGoalDetails] = useState(''); // JSON string
  const [goalNewStatus, setGoalNewStatus] = useState('pending');
  const [isManagingGoal, setIsManagingGoal] = useState(false);
  const [manageResult, setManageResult] = useState(null);
  const [manageError, setManageError] = useState('');

  // Get Active Goals state
  const [activeN, setActiveN] = useState(0);
  const [activeMinPriority, setActiveMinPriority] = useState(0.0);
  const [isLoadingActiveGoals, setIsLoadingActiveGoals] = useState(false);
  const [activeGoalsResult, setActiveGoalsResult] = useState(null);
  const [activeGoalsError, setActiveGoalsError] = useState('');

  // Update Motivation State
  const [newStateInfo, setNewStateInfo] = useState(''); // JSON string
  const [isUpdatingState, setIsUpdatingState] = useState(false);
  const [updateStateResult, setUpdateStateResult] = useState(null);
  const [updateStateError, setUpdateStateError] = useState('');


  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

  const fetchStatus = useCallback(async () => {
    setIsLoadingStatus(true); setStatusError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/motivation/status`);
      if (!response.ok) throw new Error((await response.json()).error || `HTTP error! status: ${response.status}`);
      setStatus(await response.json());
    } catch (error) { setStatusError(error.message); setStatus(null); }
    finally { setIsLoadingStatus(false); }
  }, [API_BASE_URL]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const handleManageGoal = async (e) => {
    e.preventDefault();
    setIsManagingGoal(true); setManageResult(null); setManageError('');
    let payloadGoalData = {};
    try {
      if (manageAction === 'add') {
        payloadGoalData = { description: goalDescription, type: goalType, priority: parseFloat(goalPriority), source: goalSource, details: goalDetails ? JSON.parse(goalDetails) : {} };
      } else if (manageAction === 'update_status') {
        payloadGoalData = { id: goalId, status: goalNewStatus };
      } else if (manageAction === 'remove') {
        payloadGoalData = { id: goalId };
      }
    } catch(jsonError) {
      setManageError("Goal Details is not valid JSON."); setIsManagingGoal(false); return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/cml/motivation/manage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: manageAction, goal_data: payloadGoalData }),
      });
      const resultData = await response.json();
      if (!response.ok && !(response.status === 200 && resultData === null) ) { // Allow null for "ok_no_return"
         throw new Error(resultData.error || resultData.message || `HTTP error! status: ${response.status}`);
      }
      setManageResult(resultData);
      fetchStatus(); // Refresh status
    } catch (error) { setManageError(error.message); }
    finally { setIsManagingGoal(false); }
  };

  const handleGetActiveGoals = async (e) => {
    e.preventDefault();
    setIsLoadingActiveGoals(true); setActiveGoalsResult(null); setActiveGoalsError('');
    try {
      const params = new URLSearchParams();
      if (activeN > 0) params.append('N', activeN);
      if (activeMinPriority > 0.0) params.append('min_priority', activeMinPriority);

      const response = await fetch(`${API_BASE_URL}/cml/motivation/active_goals?${params.toString()}`);
      const resultData = await response.json();
      if (!response.ok) throw new Error(resultData.error || `HTTP error! status: ${response.status}`);
      setActiveGoalsResult(resultData);
    } catch (error) { setActiveGoalsError(error.message); }
    finally { setIsLoadingActiveGoals(false); }
  };

  const handleUpdateState = async (e) => {
    e.preventDefault();
    setIsUpdatingState(true); setUpdateStateResult(null); setUpdateStateError('');
    let parsedStateInfo = {};
    try {
        if (newStateInfo.trim()) parsedStateInfo = JSON.parse(newStateInfo);
        else { setUpdateStateError("New State Info cannot be empty JSON."); setIsUpdatingState(false); return; }
    } catch (jsonError) {
        setUpdateStateError("New State Info is not valid JSON."); setIsUpdatingState(false); return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/cml/motivation/update_state`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(parsedStateInfo),
        });
        const resultData = await response.json();
        if (!response.ok) throw new Error(resultData.error || `HTTP error! status: ${response.status}`);
        setUpdateStateResult(resultData);
        fetchStatus(); // Refresh status
    } catch (error) { setUpdateStateError(error.message); }
    finally { setIsUpdatingState(false); }
  };

  const commonInputStyle = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
  const commonButtonStyle = "px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50";
  const sectionStyle = "p-4 border border-gray-300 rounded-lg mb-6 bg-white shadow";
  const headingStyle = "text-xl font-semibold mb-3 text-gray-700";
  const resultBoxStyle = "mt-2 p-2 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto";
  const subHeadingStyle = "text-lg font-medium text-gray-800 mb-2";

  return (
    <div>
      <h2 className={headingStyle}>Motivational System Interface</h2>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Module Status</h3>
        <button onClick={fetchStatus} disabled={isLoadingStatus} className={`${commonButtonStyle} mb-2`}>
          {isLoadingStatus ? 'Loading...' : 'Refresh Status'}
        </button>
        {statusError && <p className="text-red-500">Error: {statusError}</p>}
        {status && <pre className={resultBoxStyle}>{JSON.stringify(status, null, 2)}</pre>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Manage Goals</h3>
        <form onSubmit={handleManageGoal}>
          <div className="mb-4">
            <label htmlFor="manageAction" className="block text-sm font-medium text-gray-700">Action:</label>
            <select id="manageAction" value={manageAction} onChange={(e) => setManageAction(e.target.value)} className={commonInputStyle}>
              <option value="add">Add Goal</option>
              <option value="update_status">Update Goal Status</option>
              <option value="remove">Remove Goal</option>
              <option value="list_all">List All Goals</option>
            </select>
          </div>

          { (manageAction === 'add' || manageAction === 'update_status' || manageAction === 'remove') &&
            <div className="mb-4">
              <label htmlFor="goalId" className="block text-sm font-medium text-gray-700">Goal ID (for update/remove):</label>
              <input type="text" id="goalId" value={goalId} onChange={(e) => setGoalId(e.target.value)} className={commonInputStyle} disabled={manageAction === 'add'}/>
            </div>
          }
          { manageAction === 'add' && (<>
            <div className="mb-4"><label className="block text-sm font-medium">Description:</label><input type="text" value={goalDescription} onChange={(e) => setGoalDescription(e.target.value)} required className={commonInputStyle}/></div>
            <div className="mb-4"><label className="block text-sm font-medium">Type:</label><input type="text" value={goalType} onChange={(e) => setGoalType(e.target.value)} required placeholder="intrinsic/extrinsic" className={commonInputStyle}/></div>
            <div className="mb-4"><label className="block text-sm font-medium">Priority (0.0-1.0):</label><input type="number" step="0.1" min="0" max="1" value={goalPriority} onChange={(e) => setGoalPriority(parseFloat(e.target.value))} required className={commonInputStyle}/></div>
            <div className="mb-4"><label className="block text-sm font-medium">Source (optional):</label><input type="text" value={goalSource} onChange={(e) => setGoalSource(e.target.value)} className={commonInputStyle}/></div>
            <div className="mb-4"><label className="block text-sm font-medium">Details (JSON, optional):</label><textarea value={goalDetails} onChange={(e) => setGoalDetails(e.target.value)} className={commonInputStyle} rows="2" placeholder='e.g., {"target_metric": "accuracy"}'/></div>
          </>) }
          { manageAction === 'update_status' && (
            <div className="mb-4"><label className="block text-sm font-medium">New Status:</label><input type="text" value={goalNewStatus} onChange={(e) => setGoalNewStatus(e.target.value)} required placeholder="e.g., active, achieved" className={commonInputStyle}/></div>
          )}
          <button type="submit" disabled={isManagingGoal} className={commonButtonStyle}>
            {isManagingGoal ? 'Executing...' : 'Execute Manage Goal'}
          </button>
        </form>
        {manageError && <p className="text-red-500 mt-2">Error: {manageError}</p>}
        {manageResult && <div className="mt-4"><h4 className="text-md font-medium">Result:</h4><pre className={resultBoxStyle}>{JSON.stringify(manageResult, null, 2)}</pre></div>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Get Active Goals</h3>
        <form onSubmit={handleGetActiveGoals}>
            <div className="mb-4"><label className="block text-sm font-medium">N (top N, 0 for all):</label><input type="number" value={activeN} onChange={(e) => setActiveN(parseInt(e.target.value))} min="0" className={commonInputStyle}/></div>
            <div className="mb-4"><label className="block text-sm font-medium">Min Priority (0.0-1.0):</label><input type="number" step="0.1" min="0" max="1" value={activeMinPriority} onChange={(e) => setActiveMinPriority(parseFloat(e.target.value))} className={commonInputStyle}/></div>
            <button type="submit" disabled={isLoadingActiveGoals} className={commonButtonStyle}>
                {isLoadingActiveGoals ? 'Loading...' : 'Get Active Goals'}
            </button>
        </form>
        {activeGoalsError && <p className="text-red-500 mt-2">Error: {activeGoalsError}</p>}
        {activeGoalsResult && <div className="mt-4"><h4 className="text-md font-medium">Active Goals:</h4><pre className={resultBoxStyle}>{JSON.stringify(activeGoalsResult, null, 2)}</pre></div>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Update Motivation State</h3>
        <form onSubmit={handleUpdateState}>
            <div className="mb-4"><label className="block text-sm font-medium">New State Info (JSON):</label><textarea value={newStateInfo} onChange={(e) => setNewStateInfo(e.target.value)} required className={commonInputStyle} rows="2" placeholder='e.g., {"overall_drive_level": 0.8}'/></div>
            <button type="submit" disabled={isUpdatingState} className={commonButtonStyle}>
                {isUpdatingState ? 'Updating...' : 'Update State'}
            </button>
        </form>
        {updateStateError && <p className="text-red-500 mt-2">Error: {updateStateError}</p>}
        {updateStateResult && <div className="mt-4"><h4 className="text-md font-medium">Update Result:</h4><pre className={resultBoxStyle}>{JSON.stringify(updateStateResult, null, 2)}</pre></div>}
      </div>
    </div>
  );
};

export default MotivationalSystemInterface;
