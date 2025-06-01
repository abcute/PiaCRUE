import React, { useState, useEffect, useCallback } from 'react';

const WorkingMemoryInterface = () => {
  const [status, setStatus] = useState(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [statusError, setStatusError] = useState('');

  const [contents, setContents] = useState([]);
  const [isLoadingContents, setIsLoadingContents] = useState(false);
  const [contentsError, setContentsError] = useState('');

  const [addItemContent, setAddItemContent] = useState(''); // JSON string
  const [addItemSalience, setAddItemSalience] = useState(0.5);
  const [addItemContext, setAddItemContext] = useState(''); // JSON string
  const [isAddingItem, setIsAddingItem] = useState(false);
  const [addItemResult, setAddItemResult] = useState(null);
  const [addItemError, setAddItemError] = useState('');

  const [removeItemId, setRemoveItemId] = useState('');
  const [isRemovingItem, setIsRemovingItem] = useState(false);
  const [removeItemResult, setRemoveItemResult] = useState(null);
  const [removeItemError, setRemoveItemError] = useState('');

  const [focusItemId, setFocusItemId] = useState('');
  const [isSettingFocus, setIsSettingFocus] = useState(false);
  const [setFocusResult, setSetFocusResult] = useState(null);
  const [setFocusError, setSetFocusError] = useState('');

  const [currentFocus, setCurrentFocus] = useState(null);
  const [isLoadingFocus, setIsLoadingFocus] = useState(false);
  const [focusError, setFocusError] = useState('');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

  const fetchStatus = useCallback(async () => {
    setIsLoadingStatus(true); setStatusError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/wm/status`);
      if (!response.ok) throw new Error((await response.json()).error || `HTTP error! status: ${response.status}`);
      setStatus(await response.json());
    } catch (error) { setStatusError(error.message); setStatus(null); }
    finally { setIsLoadingStatus(false); }
  }, [API_BASE_URL]);

  const fetchContents = useCallback(async () => {
    setIsLoadingContents(true); setContentsError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/wm/contents`);
      if (!response.ok) throw new Error((await response.json()).error || `HTTP error! status: ${response.status}`);
      setContents(await response.json());
    } catch (error) { setContentsError(error.message); setContents([]); }
    finally { setIsLoadingContents(false); }
  }, [API_BASE_URL]);

  const fetchCurrentFocus = useCallback(async () => {
    setIsLoadingFocus(true); setFocusError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/wm/get_focus`);
      if (!response.ok) throw new Error((await response.json()).error || `HTTP error! status: ${response.status}`);
      setCurrentFocus(await response.json());
    } catch (error) { setFocusError(error.message); setCurrentFocus(null); }
    finally { setIsLoadingFocus(false); }
  }, [API_BASE_URL]);


  useEffect(() => {
    fetchStatus();
    fetchContents();
    fetchCurrentFocus();
  }, [fetchStatus, fetchContents, fetchCurrentFocus]);

  const handleAddItem = async (e) => {
    e.preventDefault();
    setIsAddingItem(true); setAddItemResult(null); setAddItemError('');
    let parsedItemContent, parsedContext = {};
    try {
      parsedItemContent = JSON.parse(addItemContent);
      if (addItemContext.trim()) parsedContext = JSON.parse(addItemContext);
    } catch (jsonError) {
      setAddItemError("Item Content or Context is not valid JSON."); setIsAddingItem(false); return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/cml/wm/add_item`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_content: parsedItemContent, salience: parseFloat(addItemSalience), context: parsedContext }),
      });
      const resultData = await response.json();
      if (!response.ok) throw new Error(resultData.error || `HTTP error! status: ${response.status}`);
      setAddItemResult(resultData);
      fetchStatus(); fetchContents(); fetchCurrentFocus(); // Refresh all
    } catch (error) { setAddItemError(error.message); }
    finally { setIsAddingItem(false); }
  };

  const handleRemoveItem = async (e) => {
    e.preventDefault();
    setIsRemovingItem(true); setRemoveItemResult(null); setRemoveItemError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/wm/remove_item`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: removeItemId }),
      });
      const resultData = await response.json();
      if (!response.ok) throw new Error(resultData.error || `HTTP error! status: ${response.status}`);
      setRemoveItemResult(resultData);
      fetchStatus(); fetchContents(); fetchCurrentFocus(); // Refresh all
    } catch (error) { setRemoveItemError(error.message); }
    finally { setIsRemovingItem(false); }
  };

  const handleSetFocus = async (e) => {
    e.preventDefault();
    setIsSettingFocus(true); setSetFocusResult(null); setSetFocusError('');
    try {
      const response = await fetch(`${API_BASE_URL}/cml/wm/set_focus`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: focusItemId }),
      });
      const resultData = await response.json();
      if (!response.ok) throw new Error(resultData.error || `HTTP error! status: ${response.status}`);
      setSetFocusResult(resultData);
      fetchStatus(); fetchCurrentFocus(); // Refresh status and current focus
    } catch (error) { setSetFocusError(error.message); }
    finally { setIsSettingFocus(false); }
  };

  const commonInputStyle = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
  const commonButtonStyle = "px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50";
  const sectionStyle = "p-4 border border-gray-300 rounded-lg mb-6 bg-white shadow";
  const headingStyle = "text-xl font-semibold mb-3 text-gray-700";
  const resultBoxStyle = "mt-2 p-2 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto";
  const subHeadingStyle = "text-lg font-medium text-gray-800 mb-2";

  return (
    <div>
      <h2 className={headingStyle}>Working Memory Interface</h2>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Module Status</h3>
        <button onClick={fetchStatus} disabled={isLoadingStatus} className={`${commonButtonStyle} mb-2`}>{isLoadingStatus ? 'Loading...' : 'Refresh Status'}</button>
        {statusError && <p className="text-red-500">Error: {statusError}</p>}
        {status && <pre className={resultBoxStyle}>{JSON.stringify(status, null, 2)}</pre>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Workspace Contents</h3>
        <button onClick={fetchContents} disabled={isLoadingContents} className={`${commonButtonStyle} mb-2`}>{isLoadingContents ? 'Loading...' : 'Refresh Contents'}</button>
        {contentsError && <p className="text-red-500">Error: {contentsError}</p>}
        {contents && <pre className={resultBoxStyle}>{JSON.stringify(contents, null, 2)}</pre>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Current Focus</h3>
        <button onClick={fetchCurrentFocus} disabled={isLoadingFocus} className={`${commonButtonStyle} mb-2`}>{isLoadingFocus ? 'Loading...' : 'Get Current Focus'}</button>
        {focusError && <p className="text-red-500">Error: {focusError}</p>}
        {currentFocus && <pre className={resultBoxStyle}>{JSON.stringify(currentFocus, null, 2)}</pre>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Add Item to Workspace</h3>
        <form onSubmit={handleAddItem}>
          <div className="mb-4"><label className="block text-sm font-medium">Item Content (JSON):</label><textarea value={addItemContent} onChange={(e) => setAddItemContent(e.target.value)} required className={commonInputStyle} rows="2" placeholder='e.g., {"type": "percept", "value": "red ball"}'/></div>
          <div className="mb-4"><label className="block text-sm font-medium">Salience (0.0-1.0):</label><input type="number" step="0.1" min="0" max="1" value={addItemSalience} onChange={(e) => setAddItemSalience(parseFloat(e.target.value))} required className={commonInputStyle}/></div>
          <div className="mb-4"><label className="block text-sm font-medium">Context (JSON, optional):</label><textarea value={addItemContext} onChange={(e) => setAddItemContext(e.target.value)} className={commonInputStyle} rows="2" placeholder='e.g., {"source": "perception"}'/></div>
          <button type="submit" disabled={isAddingItem} className={commonButtonStyle}>{isAddingItem ? 'Adding...' : 'Add Item'}</button>
        </form>
        {addItemError && <p className="text-red-500 mt-2">Error: {addItemError}</p>}
        {addItemResult && <div className="mt-2"><h4 className="text-md font-medium">Add Result:</h4><pre className={resultBoxStyle}>{JSON.stringify(addItemResult, null, 2)}</pre></div>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Remove Item from Workspace</h3>
        <form onSubmit={handleRemoveItem}>
          <div className="mb-4"><label className="block text-sm font-medium">Item ID:</label><input type="text" value={removeItemId} onChange={(e) => setRemoveItemId(e.target.value)} required className={commonInputStyle}/></div>
          <button type="submit" disabled={isRemovingItem} className={commonButtonStyle}>{isRemovingItem ? 'Removing...' : 'Remove Item'}</button>
        </form>
        {removeItemError && <p className="text-red-500 mt-2">Error: {removeItemError}</p>}
        {removeItemResult && <div className="mt-2"><h4 className="text-md font-medium">Remove Result:</h4><pre className={resultBoxStyle}>{JSON.stringify(removeItemResult, null, 2)}</pre></div>}
      </div>

      <div className={sectionStyle}>
        <h3 className={subHeadingStyle}>Set Active Focus</h3>
        <form onSubmit={handleSetFocus}>
          <div className="mb-4"><label className="block text-sm font-medium">Item ID to Focus:</label><input type="text" value={focusItemId} onChange={(e) => setFocusItemId(e.target.value)} required className={commonInputStyle}/></div>
          <button type="submit" disabled={isSettingFocus} className={commonButtonStyle}>{isSettingFocus ? 'Setting...' : 'Set Focus'}</button>
        </form>
        {setFocusError && <p className="text-red-500 mt-2">Error: {setFocusError}</p>}
        {setFocusResult && <div className="mt-2"><h4 className="text-md font-medium">Set Focus Result:</h4><pre className={resultBoxStyle}>{JSON.stringify(setFocusResult, null, 2)}</pre></div>}
      </div>
      {/* Optional: Explicit calls to manage_capacity and handle_forgetting could be added here */}
    </div>
  );
};

export default WorkingMemoryInterface;
