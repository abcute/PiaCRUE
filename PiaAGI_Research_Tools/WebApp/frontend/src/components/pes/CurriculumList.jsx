import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

function CurriculumList() {
  const [curricula, setCurricula] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchCurricula = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/pes/curricula`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setCurricula(data);
    } catch (err) {
      setError(err.message);
      setCurricula([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCurricula();
  }, [fetchCurricula]);

  const handleDelete = async (filename) => {
    // Placeholder: Implement delete functionality if required by backend
    // For now, curricula delete might not be directly implemented on backend or might have restrictions
    if (!window.confirm(`Are you sure you want to delete curriculum: ${filename}? This feature might not be fully implemented on the backend.`)) {
        return;
    }
     try {
        const response = await fetch(`${API_BASE_URL}/api/pes/curricula/${encodeURIComponent(filename)}`, { // Assuming a DELETE endpoint exists
            method: 'DELETE',
        });
        const resData = await response.json();
        if (!response.ok) {
            throw new Error(resData.error || `HTTP error! status: ${response.status}`);
        }
        alert(resData.message || 'Curriculum deleted successfully (if backend supports it).');
        fetchCurricula(); // Refresh list
    } catch (err) {
        setError(err.message);
        alert(`Failed to delete curriculum: ${err.message}`);
    }
    // console.warn(`Delete functionality for curriculum ${filename} not yet implemented or confirmed.`);
  };

  if (isLoading) return <p>Loading curricula...</p>;
  if (error) return <p className="text-red-500">Error fetching curricula: {error}</p>;

  return (
    <div className="curriculum-list mt-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Available Curricula</h2>
        <Link 
            to="/pes/curriculum/new" 
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
            Create New Curriculum
        </Link>
      </div>
      {curricula.length === 0 ? (
        <p>No curricula found. <Link to="/pes/curriculum/new" className="text-blue-400 hover:underline">Create one?</Link></p>
      ) : (
        <ul className="space-y-3">
          {curricula.map((curriculum) => (
            <li key={curriculum.filename} className="p-4 bg-slate-800 rounded-lg shadow hover:bg-slate-700 transition-colors">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-medium text-teal-400">{curriculum.name || curriculum.filename}</h3>
                  <p className="text-sm text-gray-400">Filename: {curriculum.filename}</p>
                  <p className="text-sm text-gray-400">Version: {curriculum.version || 'N/A'}</p>
                </div>
                <div className="space-x-2">
                  <Link 
                    to={`/pes/curriculum/view/${encodeURIComponent(curriculum.filename)}`}
                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                  >
                    View
                  </Link>
                  <Link 
                    to={`/pes/curriculum/edit/${encodeURIComponent(curriculum.filename)}`}
                    className="px-3 py-1 bg-yellow-500 text-white text-sm rounded hover:bg-yellow-600"
                  >
                    Edit
                  </Link>
                  <button 
                    onClick={() => handleDelete(curriculum.filename)}
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

export default CurriculumList;
