import React, { useState, useEffect } from 'react';
import './PromptForm.css'; // Import the CSS file

function PromptForm() {
  // State for PiaCRUE prompt fields
  const [systemRules, setSystemRules] = useState('');
  const [requirements, setRequirements] = useState('');
  const [users, setUsers] = useState('');
  const [rules, setRules] = useState('');
  const [workflow, setWorkflow] = useState('');
  const [initiate, setInitiate] = useState('');

  // Role specific fields
  const [roleName, setRoleName] = useState('');
  const [profile, setProfile] = useState('');
  const [skills, setSkills] = useState('');
  const [knowledge, setKnowledge] = useState('');
  const [roleRules, setRoleRules] = useState('');
  const [roleWorkflow, setRoleWorkflow] = useState('');

  // Optional fields
  const [roleDevelopment, setRoleDevelopment] = useState('');
  const [cbtAutoTraining, setCbtAutoTraining] = useState('');

  // State for the assembled prompt
  const [assembledPrompt, setAssembledPrompt] = useState('');

  // New state variables for API interaction
  const [apiKey, setApiKey] = useState('');
  const [testQuestion, setTestQuestion] = useState('');
  const [llmModel, setLlmModel] = useState('gpt-3.5-turbo');
  const [llmResponse, setLlmResponse] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(null); // null, 'good', or 'bad'

  // Function to assemble the prompt (existing logic)
  const assemblePrompt = () => {
    let prompt = `# System Rules:\n${systemRules}\n\n`;
    prompt += `# Requirements:\n${requirements}\n\n`;
    prompt += `# Users:\n${users}\n\n`;

    if (roleName || profile || skills || knowledge || roleRules || roleWorkflow) {
      prompt += `# Role: ${roleName || '[Role Name]'}\n`;
      if (profile) prompt += `## Profile:\n${profile}\n\n`;
      if (skills) prompt += `## Skills:\n${skills}\n\n`;
      if (knowledge) prompt += `## Knowledge:\n${knowledge}\n\n`;
      if (roleRules) prompt += `## RoleRules:\n${roleRules}\n\n`;
      if (roleWorkflow) prompt += `## RoleWorkflow:\n${roleWorkflow}\n\n`;
    }
    
    prompt += `# Rules:\n${rules}\n\n`;
    prompt += `# Workflow:\n${workflow}\n\n`;

    if (roleDevelopment) prompt += `# RoleDevelopment:\n${roleDevelopment}\n\n`;
    if (cbtAutoTraining) prompt += `# CBT-AutoTraining:\n${cbtAutoTraining}\n\n`;
    
    prompt += `# Initiate:\n${initiate}`;
    
    setAssembledPrompt(prompt.trim());
  };

  useEffect(() => {
    assemblePrompt();
  }, [systemRules, requirements, users, rules, workflow, initiate, roleName, profile, skills, knowledge, roleRules, roleWorkflow, roleDevelopment, cbtAutoTraining]);

  // Function to handle sending prompt to backend
  const handleProcessPrompt = async () => {
    if (!apiKey.trim()) {
      setErrorMessage('OpenAI API Key is required.');
      return;
    }
    if (!assembledPrompt.trim()) {
      setErrorMessage('Assembled prompt is empty. Please fill in some PiaCRUE fields.');
      return;
    }
    if (!testQuestion.trim()) {
      setErrorMessage('Test Question / User Input is required.');
      return;
    }

    setIsLoading(true);
    setLlmResponse('');
    setErrorMessage('');
    setFeedbackRating(null);

    try {
      const response = await fetch('/api/process_prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          apiKey: apiKey,
          prompt: assembledPrompt,
          testQuestion: testQuestion,
          llmModel: llmModel,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.error || `Error: ${response.status} ${response.statusText}`);
      } else {
        setLlmResponse(data.response);
      }
    } catch (error) {
      console.error('Network or other error:', error);
      setErrorMessage(`Network error or unexpected issue: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleFeedback = (rating) => {
    setFeedbackRating(rating);
    console.log(`Feedback received: ${rating}`);
    // In a real app, this would send feedback to a backend.
  };

  return (
    <> {/* Use a Fragment to wrap the instruction section and the main form container */}
      <div className="instruction-section">
        <h2>PiaCRUE Prompt Engineering Assistant</h2>
        <p>
          This tool helps you construct PiaCRUE prompts, test them with a Large Language Model (LLM) 
          via an API, and view the responses. Fill in the sections below to build your PiaCRUE prompt. 
          Then, provide your OpenAI API Key, select an LLM model, enter a test question, 
          and click 'Send to LLM & Get Response'.
        </p>
        <p className="api-key-note">
          <strong>Important:</strong> Your OpenAI API Key is required to interact with the LLM. 
          It is sent securely to our backend with each request to the OpenAI API and is 
          <strong>NOT</strong> stored persistently on the server. Please ensure you are using this tool 
          in a secure environment.
        </p>
      </div>

      <div className="prompt-form-container">
        {/* Left Column: Prompt Construction Fields */}
        <div className="form-column">
          <div className="form-section">
            <h2>PiaCRUE Prompt Fields</h2>
            <div className="form-row">
              <label htmlFor="systemRules">System Rules:</label>
              <textarea id="systemRules" value={systemRules} onChange={(e) => setSystemRules(e.target.value)} placeholder="Define overall system behaviors and constraints..."/>
            </div>
            <div className="form-row">
              <label htmlFor="requirements">Requirements:</label>
              <textarea id="requirements" value={requirements} onChange={(e) => setRequirements(e.target.value)} placeholder="Describe specific user or system requirements..."/>
            </div>
            <div className="form-row">
              <label htmlFor="users">Users:</label>
              <textarea id="users" value={users} onChange={(e) => setUsers(e.target.value)} placeholder="Describe the target users or interacting systems..."/>
            </div>
          </div>

          <div className="form-section">
              <h3>Role Definition</h3>
              <div className="form-row">
                <label htmlFor="roleName">Role Name:</label>
                <input type="text" id="roleName" value={roleName} onChange={(e) => setRoleName(e.target.value)} placeholder="e.g., Expert AI Assistant" />
              </div>
              <div className="form-row">
                <label htmlFor="profile">Profile:</label>
                <textarea id="profile" value={profile} onChange={(e) => setProfile(e.target.value)} placeholder="e.g., A world-class software architect specializing in AI..." />
              </div>
              <div className="form-row">
                <label htmlFor="skills">Skills (one per line suggested):</label>
                <textarea id="skills" value={skills} onChange={(e) => setSkills(e.target.value)} placeholder="e.g., - Expertise in Python\n- API Design\n- Clear communication" />
              </div>
              <div className="form-row">
                <label htmlFor="knowledge">Knowledge:</label>
                <textarea id="knowledge" value={knowledge} onChange={(e) => setKnowledge(e.target.value)} placeholder="e.g., - Familiar with microservices patterns\n- Understands cloud-native principles" />
              </div>
              <div className="form-row">
                <label htmlFor="roleRules">RoleRules (specific to role):</label>
                <textarea id="roleRules" value={roleRules} onChange={(e) => setRoleRules(e.target.value)} placeholder="e.g., - Always respond in JSON format\n- Be concise" />
              </div>
              <div className="form-row">
                <label htmlFor="roleWorkflow">RoleWorkflow (sub-workflow for role):</label>
                <textarea id="roleWorkflow" value={roleWorkflow} onChange={(e) => setRoleWorkflow(e.target.value)} placeholder="e.g., 1. Understand user query.\n2. Ask clarifying questions if needed.\n3. Provide detailed solution." />
              </div>
          </div>
          
          <div className="form-section">
            <h3>General Interactions</h3>
            <div className="form-row">
              <label htmlFor="rules">Rules (general):</label>
              <textarea id="rules" value={rules} onChange={(e) => setRules(e.target.value)} placeholder="Define general interaction rules..." />
            </div>
            <div className="form-row">
              <label htmlFor="workflow">Workflow (general):</label>
              <textarea id="workflow" value={workflow} onChange={(e) => setWorkflow(e.target.value)} placeholder="Describe the general operational workflow..." />
            </div>
          </div>

          <div className="form-section">
              <h3>Optional Sections</h3>
              <div className="form-row">
              <label htmlFor="roleDevelopment">RoleDevelopment:</label>
              <textarea id="roleDevelopment" value={roleDevelopment} onChange={(e) => setRoleDevelopment(e.target.value)} placeholder="Describe how the role should evolve or learn..." />
              </div>
              <div className="form-row">
              <label htmlFor="cbtAutoTraining">CBT-AutoTraining:</label>
              <textarea id="cbtAutoTraining" value={cbtAutoTraining} onChange={(e) => setCbtAutoTraining(e.target.value)} placeholder="Define cognitive behavioral therapy auto-training parameters..." />
              </div>
          </div>

          <div className="form-section">
            <h3>Initiation</h3>
            <div className="form-row">
              <label htmlFor="initiate">Initiate:</label>
              <textarea id="initiate" value={initiate} onChange={(e) => setInitiate(e.target.value)} placeholder="Initial message or prompt to start the interaction..." />
            </div>
          </div>
        </div>

        {/* Right Column: Assembled Prompt, API Interaction, and Response */}
        <div className="form-column">
          <div className="form-section">
              <h3>Assembled PiaCRUE Prompt</h3>
              <pre className="pre-display assembled-prompt-display">
                {assembledPrompt}
              </pre>
          </div>
          
          <div className="form-section">
              <h3>Test with LLM</h3>
              <div className="form-row">
                  <label htmlFor="apiKey">OpenAI API Key:</label>
                  <input type="password" id="apiKey" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="Enter your OpenAI API Key here" />
                  <small className="small-text">(e.g., sk-xxxxxxxx...) Obtain from your OpenAI account.</small>
              </div>
              <div className="form-row">
                  <label htmlFor="llmModel">LLM Model:</label>
                  <input type="text" id="llmModel" value={llmModel} onChange={(e) => setLlmModel(e.target.value)} />
                  <small className="small-text">(e.g., gpt-3.5-turbo, gpt-4). Ensure the model is compatible with the OpenAI Chat Completions API.</small>
              </div>
              <div className="form-row">
                  <label htmlFor="testQuestion">Test Question / User Input:</label>
                  <textarea id="testQuestion" value={testQuestion} onChange={(e) => setTestQuestion(e.target.value)} placeholder="Enter your test question or user input here..."/>
              </div>
              <button onClick={handleProcessPrompt} disabled={isLoading} className="button-base button-primary">
              {isLoading ? 'Processing...' : 'Send to LLM & Get Response'}
              </button>
          </div>

          {isLoading && <p className="loading-message">Loading response from LLM...</p>}
          
          {errorMessage && (
            <div className="error-message">
              <strong>Error:</strong> {errorMessage}
            </div>
          )}


          {llmResponse && (
            <div className="form-section response-section">
              <h3>LLM Response:</h3>
              <pre className="pre-display llm-response-display">{llmResponse}</pre>
              <div className="feedback-section">
                  <p>Rate this response:</p>
                  <button onClick={() => handleFeedback('good')} className="button-base button-feedback" disabled={feedbackRating === 'good'}>👍 Good</button>
                  <button onClick={() => handleFeedback('bad')} className="button-base button-feedback" disabled={feedbackRating === 'bad'}>👎 Bad</button>
                  {feedbackRating && <p className="feedback-thanks">Thanks for your feedback!</p>}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default PromptForm;
