import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

function ViewCurriculum() {
  const { filename } = useParams();
  const navigate = useNavigate();
  const [markdownContent, setMarkdownContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchRenderedCurriculum = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/pes/curricula/${encodeURIComponent(filename)}/render`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMarkdownContent(data.markdown);
    } catch (err) {
      setError(err.message);
      setMarkdownContent('');
    } finally {
      setIsLoading(false);
    }
  }, [filename]);

  useEffect(() => {
    if (filename) {
      fetchRenderedCurriculum();
    }
  }, [filename, fetchRenderedCurriculum]);

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete curriculum: ${filename}?`)) {
        return;
    }
    try {
        // Assuming a DELETE endpoint exists, e.g., /api/pes/curricula/:filename
        const response = await fetch(`${API_BASE_URL}/api/pes/curricula/${encodeURIComponent(filename)}`, {
            method: 'DELETE',
        });
        const resData = await response.json();
        if (!response.ok) {
            throw new Error(resData.error || `HTTP error! status: ${response.status}`);
        }
        alert(resData.message || 'Curriculum deleted successfully');
        navigate('/pes/curricula'); // Navigate back to curriculum list
    } catch (err) {
        setError(err.message);
        alert(`Failed to delete curriculum: ${err.message}`);
    }
  };

  if (isLoading) return <p>Loading rendered curriculum...</p>;
  if (error) return <p className="text-red-500">Error loading curriculum: {error}</p>;

  return (
    <div className="view-curriculum p-4 bg-slate-800 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-teal-400">Viewing Curriculum: {filename}</h1>
        <div>
          <Link 
            to={`/pes/curriculum/edit/${encodeURIComponent(filename)}`}
            className="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 mr-2"
          >
            Edit
          </Link>
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Delete
          </button>
          <Link 
            to="/pes/curricula" 
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 ml-2"
          >
            Back to List
          </Link>
        </div>
      </div>
      <div 
        className="prose prose-invert max-w-none p-3 bg-slate-900 rounded"
        dangerouslySetInnerHTML={{ __html: markdownContent.replace(/\n/g, '<br />') }} // Basic rendering
      />
      {/* For more advanced markdown, consider a library like react-markdown */}
    </div>
  );
}

export default ViewCurriculum;
