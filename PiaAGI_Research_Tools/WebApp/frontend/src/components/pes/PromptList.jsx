import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

function PromptList() {
  const [prompts, setPrompts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchPrompts = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/pes/prompts`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPrompts(data);
    } catch (err) {
      setError(err.message);
      setPrompts([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  const handleDelete = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete prompt: ${filename}?`)) {
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/api/pes/prompts/${encodeURIComponent(filename)}`, {
            method: 'DELETE',
        });
        const resData = await response.json();
        if (!response.ok) {
            throw new Error(resData.error || `HTTP error! status: ${response.status}`);
        }
        alert(resData.message || 'Prompt deleted successfully');
        fetchPrompts(); // Refresh list
    } catch (err) {
        setError(err.message);
        alert(`Failed to delete prompt: ${err.message}`);
    }
  };


  if (isLoading) return <p>Loading prompts...</p>;
  if (error) return <p className="text-red-500">Error fetching prompts: {error}</p>;

  return (
    <div className="prompt-list mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Available Prompts</h2>
        <Link 
          to="/pes/prompt/new" 
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          Create New Prompt
        </Link>
      </div>
      {prompts.length === 0 ? (
        <p>No prompts found. <Link to="/pes/prompt/new" className="text-blue-400 hover:underline">Create one?</Link></p>
      ) : (
        <ul className="space-y-3">
          {prompts.map((prompt) => (
            <li key={prompt.filename} className="p-4 bg-slate-800 rounded-lg shadow hover:bg-slate-700 transition-colors">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-medium text-sky-400">{prompt.name || prompt.filename}</h3>
                  <p className="text-sm text-gray-400">Filename: {prompt.filename}</p>
                  <p className="text-sm text-gray-400">Version: {prompt.version || 'N/A'}</p>
                </div>
                <div className="space-x-2">
                  <Link 
                    to={`/pes/prompt/view/${encodeURIComponent(prompt.filename)}`} 
                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                  >
                    View
                  </Link>
                  <Link 
                    to={`/pes/prompt/edit/${encodeURIComponent(prompt.filename)}`} 
                    className="px-3 py-1 bg-yellow-500 text-white text-sm rounded hover:bg-yellow-600"
                  >
                    Edit
                  </Link>
                   <button 
                    onClick={() => handleDelete(prompt.filename)}
                    className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default PromptList;
