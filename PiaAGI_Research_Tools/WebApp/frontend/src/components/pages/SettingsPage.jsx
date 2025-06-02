import React from 'react';

function SettingsPage() {
  const sectionClass = "p-4 bg-slate-800 rounded-lg mb-6 shadow";
  const headingClass = "text-xl font-semibold mb-3 text-sky-400";
  const codeBlockClass = "p-3 bg-slate-900 text-sm text-gray-300 rounded-md overflow-x-auto whitespace-pre-wrap"; // Added whitespace-pre-wrap

  const llmConfigExample = `
[DEFAULT]
# Default LLM provider and settings
# Options for LLM_PROVIDER: OpenAI, Anthropic, HuggingFace_Hub, Custom_API, etc.
LLM_PROVIDER = OpenAI
DEFAULT_MODEL_NAME = gpt-3.5-turbo

[OpenAI]
API_KEY = YOUR_OPENAI_API_KEY_HERE
# Optional: Specify a default model for OpenAI, overrides DEFAULT_MODEL_NAME if LLM_PROVIDER is OpenAI
# MODEL_NAME = gpt-4o
# ORGANISATION_ID = YOUR_OPENAI_ORG_ID_IF_APPLICABLE

# --- Other provider sections (Anthropic, HuggingFace_Hub, Custom_API) would follow ---
# [Anthropic]
# API_KEY = YOUR_ANTHROPIC_API_KEY_HERE
# ...
  `.trim();

  return (
    <div className="settings-page p-4">
      <h1 className="text-2xl font-bold mb-6 text-sky-300">Application Settings & LLM Configuration</h1>

      <div className={sectionClass}>
        <h2 className={headingClass}>LLM API Key Configuration</h2>
        <p className="text-gray-400 mb-3">
          The PiaAGI WebApp backend needs to be configured with your Large Language Model (LLM) API keys 
          and preferred models to function correctly (e.g., for the CML module's general purpose LLM calls, or future integrations).
        </p>
        <p className="text-gray-400 mb-3">
          Configuration is handled via a file named <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code> located in the backend directory: 
          <code className="text-orange-400 bg-slate-700 p-1 rounded">PiaAGI_Research_Tools/WebApp/backend/</code>.
        </p>

        <h3 className="text-lg font-semibold text-gray-300 mt-4 mb-2">Steps to Configure:</h3>
        <ol className="list-decimal list-inside text-gray-400 space-y-2 mb-4">
          <li>
            Locate the template file: <br />
            <code className="text-orange-400 bg-slate-700 p-1 rounded">PiaAGI_Research_Tools/WebApp/backend/llm_config.ini</code>.
            <br />
            (This file should have been automatically created by copying it from 
            <code className="text-orange-400 bg-slate-700 p-1 rounded">PiaAGI_Research_Tools/PiaPES/web_app/llm_config.ini.template</code> 
            during a previous backend setup step. If it's missing, you can manually copy the template.)
          </li>
          <li>
            If you haven't already, rename or copy this template to <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code> in the 
            same <code className="text-orange-400 bg-slate-700 p-1 rounded">PiaAGI_Research_Tools/WebApp/backend/</code> directory.
          </li>
          <li>
            Open <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code> with a text editor.
          </li>
          <li>
            Fill in your API key for the desired provider (e.g., OpenAI). Replace <code className="text-orange-400">YOUR_OPENAI_API_KEY_HERE</code> with your actual key.
          </li>
          <li>
            You can also set a default model name or provider. The <code className="text-orange-400 bg-slate-700 p-1 rounded">DEFAULT_MODEL_NAME</code> under the 
            <code className="text-orange-400 bg-slate-700 p-1 rounded">[DEFAULT]</code> section will be used if a more specific model isn't found for the chosen <code className="text-orange-400 bg-slate-700 p-1 rounded">LLM_PROVIDER</code>.
          </li>
        </ol>

        <h3 className="text-lg font-semibold text-gray-300 mt-4 mb-2">Example `llm_config.ini` structure:</h3>
        <pre className={codeBlockClass}>
          {llmConfigExample}
        </pre>
        
        <h3 className="text-lg font-semibold text-gray-300 mt-4 mb-2">Important:</h3>
        <ul className="list-disc list-inside text-gray-400 space-y-1">
          <li>
            The backend currently prioritizes API keys sent directly from the frontend (e.g., from a specific tool's UI if it allows temporary key input) over the <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code> file.
            However, for general backend-initiated LLM calls or if no key is provided by the frontend, the <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code> is essential.
          </li>
          <li>
            After saving changes to <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code>, you **must restart the backend Flask application** for the changes to take effect.
          </li>
          <li>
            Keep your API keys secure. The <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code> file should not be committed to public version control if it contains sensitive keys. The <code className="text-orange-400 bg-slate-700 p-1 rounded">.gitignore</code> file in the backend directory should already be configured to ignore `llm_config.ini`.
          </li>
        </ul>
      </div>

      {/* 
        Future "Test LLM Connection" button could be added here.
        <div className={sectionClass}>
          <h2 className={headingClass}>Test LLM Connection (Conceptual)</h2>
          <p className="text-gray-400 mb-3">
            Click the button below to send a test prompt to the backend. 
            The backend will use its configured API key from <code className="text-orange-400 bg-slate-700 p-1 rounded">llm_config.ini</code>.
          </p>
          <button 
            // onClick={handleTestConnection} 
            // disabled={isTesting}
            className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:opacity-50"
          >
            {isTesting ? 'Testing...' : 'Test Backend LLM Connection'}
          </button>
          {testResult && <pre className={`${codeBlockClass} mt-3`}>{JSON.stringify(testResult, null, 2)}</pre>}
          {testError && <p className="text-red-400 bg-red-900 p-3 rounded mt-3">{testError}</p>}
        </div> 
      */}

    </div>
  );
}

export default SettingsPage;
