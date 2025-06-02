import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

const createDefaultCurriculum = () => ({
  __type__: "DevelopmentalCurriculum",
  name: "",
  description: "",
  target_developmental_stage: "",
  version: "0.1.0",
  author: "DefaultUser",
  steps: [] // Steps will be { __type__: "CurriculumStep", name, order, prompt_reference, conditions, notes }
});

function CurriculumForm({ mode = "create" }) {
  const { filename: routeFilename } = useParams();
  const navigate = useNavigate();
  const [curriculumData, setCurriculumData] = useState(createDefaultCurriculum());
  const [filename, setFilename] = useState(routeFilename || ''); // Used for create, pre-filled for edit
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const isEditMode = mode === "edit";

  const fetchCurriculumData = useCallback(async (fname) => {
    if (!fname) return;
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/pes/curricula/${encodeURIComponent(fname)}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setCurriculumData({ ...createDefaultCurriculum(), ...data.curriculum_data });
      setFilename(data.filename); // Use filename from response
    } catch (err) {
      setError(`Failed to load curriculum: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isEditMode && routeFilename) {
      fetchCurriculumData(routeFilename);
    } else {
      setCurriculumData(createDefaultCurriculum());
      setFilename(''); 
    }
  }, [isEditMode, routeFilename, fetchCurriculumData]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurriculumData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleFilenameChange = (e) => {
    setFilename(e.target.value);
  };

  const handleStepChange = (index, field, value) => {
    const updatedSteps = curriculumData.steps.map((step, i) => 
      i === index ? { ...step, [field]: field === 'order' ? parseInt(value,10) || 0 : value } : step
    );
    setCurriculumData(prev => ({ ...prev, steps: updatedSteps }));
  };

  const addStep = () => {
    setCurriculumData(prev => ({
      ...prev,
      steps: [...prev.steps, { __type__: "CurriculumStep", name: "", order: prev.steps.length + 1, prompt_reference: "", conditions: "", notes: "" }]
    }));
  };

  const removeStep = (index) => {
    setCurriculumData(prev => ({
      ...prev,
      steps: prev.steps.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    let url = isEditMode 
      ? `${API_BASE_URL}/api/pes/curricula/${encodeURIComponent(routeFilename)}`
      : `${API_BASE_URL}/api/pes/curricula`;
    const method = isEditMode ? 'PUT' : 'POST';

    let bodyData = { ...curriculumData };

    if (!isEditMode) { // For create mode
        // Filename for curriculum is taken from the 'filename' state field.
        // User must provide it, ending with .curriculum.json
        if (!filename || !filename.endsWith('.curriculum.json')) {
            setError("Filename is required for new curricula and must end with '.curriculum.json'. Ex: my_curriculum.curriculum.json");
            setIsLoading(false);
            return;
        }
        bodyData.filename = filename; // Add filename to the body for POST
    }
    
    // Ensure steps have __type__ if not already set (should be by addStep)
    bodyData.steps = bodyData.steps.map(step => ({...step, __type__: "CurriculumStep"}));


    try {
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || `HTTP error! status: ${response.status}`);
      }
      setSuccessMessage(result.message || `Curriculum ${isEditMode ? 'updated' : 'created'} successfully!`);
      
      if (result.filename) { // Backend should return filename
        navigate(`/pes/curriculum/view/${encodeURIComponent(result.filename)}`);
      } else if (isEditMode) {
         navigate(`/pes/curriculum/view/${encodeURIComponent(routeFilename)}`);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  const commonInputClass = "mt-1 block w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-gray-200";
  const commonTextareaClass = `${commonInputClass} min-h-[60px]`;
  const commonLabelClass = "block text-sm font-medium text-gray-300";
  const sectionClass = "p-4 bg-slate-800 rounded-lg mb-6 shadow";
  const headingClass = "text-xl font-semibold mb-3 text-teal-400";

  if (isLoading && isEditMode && !curriculumData.name) return <p>Loading curriculum data...</p>;

  return (
    <form onSubmit={handleSubmit} className="space-y-6 p-4 bg-slate-850 rounded-lg shadow-xl">
      <h1 className="text-2xl font-bold mb-6 text-teal-300">{isEditMode ? `Edit Curriculum: ${routeFilename}` : 'Create New Curriculum'}</h1>
      
      {error && <p className="text-red-400 bg-red-900 p-3 rounded">{error}</p>}
      {successMessage && <p className="text-green-400 bg-green-900 p-3 rounded">{successMessage}</p>}

      {!isEditMode && (
         <div className={sectionClass}>
            <h2 className={headingClass}>Filename</h2>
            <label htmlFor="filename" className={commonLabelClass}>Filename (must end with .curriculum.json):</label>
            <input type="text" name="filename" id="filename" value={filename} onChange={handleFilenameChange} required className={commonInputClass} placeholder="e.g., my_learning_path.curriculum.json"/>
         </div>
      )}

      <div className={sectionClass}>
        <h2 className={headingClass}>Metadata</h2>
        <div><label htmlFor="name" className={commonLabelClass}>Name:</label><input type="text" name="name" id="name" value={curriculumData.name} onChange={handleInputChange} required className={commonInputClass} /></div>
        <div><label htmlFor="description" className={commonLabelClass}>Description:</label><textarea name="description" id="description" value={curriculumData.description} onChange={handleInputChange} className={commonTextareaClass} /></div>
        <div><label htmlFor="target_developmental_stage" className={commonLabelClass}>Target Dev. Stage:</label><input type="text" name="target_developmental_stage" id="target_developmental_stage" value={curriculumData.target_developmental_stage} onChange={handleInputChange} className={commonInputClass} /></div>
        <div><label htmlFor="author" className={commonLabelClass}>Author:</label><input type="text" name="author" id="author" value={curriculumData.author} onChange={handleInputChange} className={commonInputClass} /></div>
        <div><label htmlFor="version" className={commonLabelClass}>Version:</label><input type="text" name="version" id="version" value={curriculumData.version} onChange={handleInputChange} className={commonInputClass} /></div>
      </div>

      {/* Steps - only for create mode for now, or if edit mode explicitly supports full step editing */}
      {(isEditMode && curriculumData.steps.length > 0) || !isEditMode ? ( // Show steps if editing and steps exist, or if creating
        <div className={sectionClass}>
            <h2 className={headingClass}>Steps</h2>
            {curriculumData.steps.map((step, index) => (
            <div key={index} className="p-3 border border-slate-700 rounded-md mb-3 space-y-2">
                <h3 className="text-md font-semibold text-gray-300">Step {index + 1}</h3>
                <div><label className={commonLabelClass}>Name:</label><input type="text" value={step.name} onChange={(e) => handleStepChange(index, 'name', e.target.value)} className={commonInputClass} /></div>
                <div><label className={commonLabelClass}>Order:</label><input type="number" value={step.order} onChange={(e) => handleStepChange(index, 'order', e.target.value)} className={commonInputClass} /></div>
                <div><label className={commonLabelClass}>Prompt Reference (filename):</label><input type="text" value={step.prompt_reference} onChange={(e) => handleStepChange(index, 'prompt_reference', e.target.value)} className={commonInputClass} placeholder="e.g., my_prompt.json"/></div>
                <div><label className={commonLabelClass}>Conditions (optional):</label><textarea value={step.conditions} onChange={(e) => handleStepChange(index, 'conditions', e.target.value)} className={commonTextareaClass} /></div>
                <div><label className={commonLabelClass}>Notes (optional):</label><textarea value={step.notes} onChange={(e) => handleStepChange(index, 'notes', e.target.value)} className={commonTextareaClass} /></div>
                {!isEditMode && <button type="button" onClick={() => removeStep(index)} className="px-3 py-1 bg-red-700 text-white text-xs rounded hover:bg-red-800">Remove Step</button>}
            </div>
            ))}
            {!isEditMode && <button type="button" onClick={addStep} className="mt-2 px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700">Add Step</button>}
            {isEditMode && <p className="text-sm text-gray-400">Full step editing for existing curricula might be limited. This form primarily handles metadata edits.</p>}
        </div>
      ) : null}


      <div className="flex justify-end space-x-3 mt-8">
        <button type="button" onClick={() => navigate(isEditMode ? `/pes/curriculum/view/${routeFilename}` : '/pes')} className="px-6 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700">
          Cancel
        </button>
        <button type="submit" disabled={isLoading} className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50">
          {isLoading ? (isEditMode ? 'Updating...' : 'Creating...') : (isEditMode ? 'Save Changes' : 'Create Curriculum')}
        </button>
      </div>
    </form>
  );
}

export default CurriculumForm;
