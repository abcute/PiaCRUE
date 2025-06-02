import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate }
from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

// Helper to create a default structure for a new prompt
const createDefaultPrompt = () => ({
  __type__: "PiaAGIPrompt",
  target_agi: "PiaAGI_GenericInstance_v1",
  developmental_stage_target: "PiaAdult",
  author: "DefaultUser",
  version: "0.1.0",
  date: new Date().toISOString().split('T')[0],
  objective: "",
  system_rules: {
    __type__: "SystemRules",
    syntax: "Markdown for general interaction, YAML/JSON for specific config blocks if used",
    language: "English",
    output_format: "Natural language",
    logging_level: "Brief",
    piaagi_interpretation_mode: "Execute_Immediate"
  },
  requirements: {
    __type__: "Requirements",
    goal: "",
    background_context: "",
    constraints_and_boundaries: [],
    success_metrics: []
  },
  users_interactors: { __type__: "UsersInteractors", type: "Human Developer", profile: "Generic user profile" },
  executors: {
    __type__: "Executors",
    role: {
      __type__: "Role",
      name: "DefaultRole",
      profile: "Default role profile",
      skills_focus: [],
      knowledge_domains_active: [],
      cognitive_module_configuration: {
        __type__: "CognitiveModuleConfiguration",
        personality_config: { __type__: "PersonalityConfig", ocean_openness: 0.5, ocean_conscientiousness: 0.5, ocean_extraversion: 0.5, ocean_agreeableness: 0.5, ocean_neuroticism: 0.5 },
        motivational_bias_config: { __type__: "MotivationalBias", biases: {} },
        emotional_profile_config: { __type__: "EmotionalProfile", baseline_valence: "Neutral" },
        learning_module_config: { __type__: "LearningModuleConfig", primary_learning_mode: "Observational" }
      },
      role_specific_rules: []
    }
  },
  workflow_or_curriculum_phase: { __type__: "Workflow", steps: [] },
  developmental_scaffolding_context: { __type__: "DevelopmentalScaffolding" },
  cbt_autotraining_protocol: { __type__: "CBTAutoTraining" },
  initiate_interaction: ""
});


function PromptForm({ mode = "create" }) {
  const { filename: routeFilename } = useParams();
  const navigate = useNavigate();
  const [promptData, setPromptData] = useState(createDefaultPrompt());
  const [filename, setFilename] = useState(routeFilename || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const isEditMode = mode === "edit";

  const fetchPromptData = useCallback(async (fname) => {
    if (!fname) return;
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/pes/prompts/${encodeURIComponent(fname)}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Ensure nested structures have __type__ or provide defaults if missing from loaded data
      // This is a simplified version; a more robust solution would deeply check and provide defaults.
      setPromptData({ ...createDefaultPrompt(), ...data.prompt_data });
      setFilename(data.filename); // Ensure filename from response is used
    } catch (err) {
      setError(`Failed to load prompt: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isEditMode && routeFilename) {
      fetchPromptData(routeFilename);
    } else {
      // For create mode, ensure filename state is clear or based on objective
      setPromptData(createDefaultPrompt()); // Reset to default for create mode
      setFilename(''); // Clear filename for new prompts
    }
  }, [isEditMode, routeFilename, fetchPromptData]);
  
  // Helper for handling nested changes
  const handleNestedChange = (path, value) => {
    setPromptData(prev => {
      let current = { ...prev };
      let obj = current;
      const keys = path.split('.');
      keys.forEach((key, index) => {
        if (index === keys.length - 1) {
          obj[key] = value;
        } else {
          obj[key] = { ...obj[key] }; // Ensure immutability for nested objects
          obj = obj[key];
        }
      });
      return current;
    });
  };
  
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name.includes('.')) { // Simple dot notation for one level nesting
        handleNestedChange(name, type === 'checkbox' ? checked : value);
    } else {
        setPromptData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    }
  };

  const handleFilenameChange = (e) => {
    setFilename(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    const url = isEditMode 
      ? `${API_BASE_URL}/api/pes/prompts/${encodeURIComponent(routeFilename)}` 
      : `${API_BASE_URL}/api/pes/prompts`;
    const method = isEditMode ? 'PUT' : 'POST';

    // For POST, include filename in the body if user provided one
    const bodyData = { ...promptData };
    if (!isEditMode && filename) {
        bodyData.filename = filename; // Server will sanitize this
    }
    
    // Ensure __type__ fields are present for all relevant objects before sending
    // This is crucial for the backend's object_hook
    // Example: (already handled by createDefaultPrompt and fetch load)
    // if (!bodyData.system_rules.__type__) bodyData.system_rules.__type__ = "SystemRules"; 
    // ... and so on for all nested objects.

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
      setSuccessMessage(result.message || `Prompt ${isEditMode ? 'updated' : 'created'} successfully!`);
      if (!isEditMode && result.filename) {
        navigate(`/pes/prompt/view/${encodeURIComponent(result.filename)}`); // Navigate to view the new prompt
      } else if (isEditMode) {
        navigate(`/pes/prompt/view/${encodeURIComponent(routeFilename)}`);
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
  const headingClass = "text-xl font-semibold mb-3 text-sky-400";


  if (isLoading && isEditMode && !promptData.objective) return <p>Loading prompt data...</p>; // Show loading only if data not yet populated

  return (
    <form onSubmit={handleSubmit} className="space-y-6 p-4 bg-slate-850 rounded-lg shadow-xl">
      <h1 className="text-2xl font-bold mb-6 text-sky-300">{isEditMode ? `Edit Prompt: ${routeFilename}` : 'Create New Prompt'}</h1>
      
      {error && <p className="text-red-400 bg-red-900 p-3 rounded">{error}</p>}
      {successMessage && <p className="text-green-400 bg-green-900 p-3 rounded">{successMessage}</p>}

      {!isEditMode && (
        <div className={sectionClass}>
          <h2 className={headingClass}>Filename (Optional)</h2>
          <label htmlFor="filename" className={commonLabelClass}>Filename (leave blank to auto-generate from objective):</label>
          <input type="text" name="filename" id="filename" value={filename} onChange={handleFilenameChange} className={commonInputClass} placeholder="e.g., my_awesome_prompt.json"/>
          <p className="text-xs text-gray-500 mt-1">If provided, will be sanitized. Must end with .json if you want that exact name.</p>
        </div>
      )}

      <div className={sectionClass}>
        <h2 className={headingClass}>Metadata</h2>
        <div><label htmlFor="objective" className={commonLabelClass}>Objective:</label><input type="text" name="objective" id="objective" value={promptData.objective} onChange={handleInputChange} required className={commonInputClass} /></div>
        <div><label htmlFor="author" className={commonLabelClass}>Author:</label><input type="text" name="author" id="author" value={promptData.author} onChange={handleInputChange} className={commonInputClass} /></div>
        <div><label htmlFor="version" className={commonLabelClass}>Version:</label><input type="text" name="version" id="version" value={promptData.version} onChange={handleInputChange} className={commonInputClass} /></div>
        <div><label htmlFor="date" className={commonLabelClass}>Date:</label><input type="date" name="date" id="date" value={promptData.date} onChange={handleInputChange} className={commonInputClass} /></div>
        <div><label htmlFor="target_agi" className={commonLabelClass}>Target AGI:</label><input type="text" name="target_agi" id="target_agi" value={promptData.target_agi} onChange={handleInputChange} className={commonInputClass} /></div>
        <div><label htmlFor="developmental_stage_target" className={commonLabelClass}>Dev. Stage Target:</label><input type="text" name="developmental_stage_target" id="developmental_stage_target" value={promptData.developmental_stage_target} onChange={handleInputChange} className={commonInputClass} /></div>
      </div>

      <div className={sectionClass}>
        <h2 className={headingClass}>System Rules</h2>
        <div><label htmlFor="system_rules.language" className={commonLabelClass}>Language:</label><input type="text" name="system_rules.language" id="system_rules.language" value={promptData.system_rules?.language || ''} onChange={handleInputChange} className={commonInputClass} /></div>
        <div><label htmlFor="system_rules.output_format" className={commonLabelClass}>Output Format:</label><input type="text" name="system_rules.output_format" id="system_rules.output_format" value={promptData.system_rules?.output_format || ''} onChange={handleInputChange} className={commonInputClass} /></div>
        {/* Add more SystemRules fields as needed */}
      </div>

      <div className={sectionClass}>
        <h2 className={headingClass}>Requirements</h2>
        <div><label htmlFor="requirements.goal" className={commonLabelClass}>Goal:</label><textarea name="requirements.goal" id="requirements.goal" value={promptData.requirements?.goal || ''} onChange={handleInputChange} className={commonTextareaClass} /></div>
        <div><label htmlFor="requirements.background_context" className={commonLabelClass}>Background Context:</label><textarea name="requirements.background_context" id="requirements.background_context" value={promptData.requirements?.background_context || ''} onChange={handleInputChange} className={commonTextareaClass} /></div>
        {/* Constraints and Success Metrics (simple comma separated for now) */}
        <div><label htmlFor="constraints_str" className={commonLabelClass}>Constraints (comma-separated):</label><input type="text" id="constraints_str" defaultValue={promptData.requirements?.constraints_and_boundaries?.join(', ') || ''} onChange={(e) => handleNestedChange('requirements.constraints_and_boundaries', e.target.value.split(',').map(s => s.trim()).filter(Boolean))} className={commonInputClass} /></div>
        <div><label htmlFor="success_metrics_str" className={commonLabelClass}>Success Metrics (comma-separated):</label><input type="text" id="success_metrics_str" defaultValue={promptData.requirements?.success_metrics?.join(', ') || ''} onChange={(e) => handleNestedChange('requirements.success_metrics', e.target.value.split(',').map(s => s.trim()).filter(Boolean))} className={commonInputClass} /></div>
      </div>
      
      {/* Placeholder for other sections like Executors, Cognitive Config, etc. */}
      {/* These would involve more complex sub-forms or JSON textareas for now */}
      <div className={sectionClass}>
         <h2 className={headingClass}>Initiate Interaction</h2>
         <div><label htmlFor="initiate_interaction" className={commonLabelClass}>Initial message/prompt from user/system to AGI:</label><textarea name="initiate_interaction" id="initiate_interaction" value={promptData.initiate_interaction} onChange={handleInputChange} className={commonTextareaClass} /></div>
      </div>

      <div className="flex justify-end space-x-3 mt-8">
        <button type="button" onClick={() => navigate(isEditMode ? `/pes/prompt/view/${routeFilename}` : '/pes')} className="px-6 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700">
          Cancel
        </button>,
        <button type="submit" disabled={isLoading} className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50">
          {isLoading ? (isEditMode ? 'Updating...' : 'Creating...') : (isEditMode ? 'Save Changes' : 'Create Prompt')}
        </button>
      </div>
    </form>
  );
}

export default PromptForm;
