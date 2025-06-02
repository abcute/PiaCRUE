import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

function ViewPrompt() {
  const { filename } = useParams();
  const navigate = useNavigate();
  const [markdownContent, setMarkdownContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchRenderedPrompt = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/pes/prompts/${encodeURIComponent(filename)}/render`);
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
      fetchRenderedPrompt();
    }
  }, [filename, fetchRenderedPrompt]);

  const handleDelete = async () => {
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
        navigate('/pes/prompts'); // Navigate back to prompt list
    } catch (err) {
        setError(err.message); // Display error on current page
        alert(`Failed to delete prompt: ${err.message}`);
    }
  };

  if (isLoading) return <p>Loading rendered prompt...</p>;
  if (error) return <p className="text-red-500">Error loading prompt: {error}</p>;

  return (
    <div className="view-prompt p-4 bg-slate-800 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-sky-400">Viewing Prompt: {filename}</h1>
        <div>
          <Link 
            to={`/pes/prompt/edit/${encodeURIComponent(filename)}`} 
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
            to="/pes/prompts" 
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

export default ViewPrompt;
