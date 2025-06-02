import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';

import Navigation from './components/layout/Navigation';
import HomePage from './components/pages/HomePage';
import CMLInterface from './components/cml/CMLInterface';
// PESPage will be replaced by PESInterface for the /pes route
// For now, we import the new PES components that will be used in nested routes
import PESInterface from './components/pes/PESInterface';
import PromptList from './components/pes/PromptList';
import CurriculumList from './components/pes/CurriculumList';
import PromptForm from './components/pes/PromptForm';
import CurriculumForm from './components/pes/CurriculumForm';
import ViewPrompt from './components/pes/ViewPrompt';
import ViewCurriculum from './components/pes/ViewCurriculum';

import SEPage from './components/pages/SEPage';
import AVTPage from './components/pages/AVTPage';
import SettingsPage from './components/pages/SettingsPage';

function App() {
  return (
    <div className="app-container">
      <Navigation />
      <main className="app-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/cml" element={<CMLInterface />} />
          
          {/* PES Routes */}
          <Route path="/pes" element={<PESInterface />}>
            {/* Default child route for /pes, e.g. list prompts and curricula */}
            <Route index element={<><PromptList /><CurriculumList /></>} /> 
            <Route path="prompts" element={<PromptList />} />
            <Route path="prompt/new" element={<PromptForm mode="create" />} />
            <Route path="prompt/edit/:filename" element={<PromptForm mode="edit" />} />
            <Route path="prompt/view/:filename" element={<ViewPrompt />} />
            
            <Route path="curricula" element={<CurriculumList />} />
            <Route path="curriculum/new" element={<CurriculumForm mode="create" />} />
            <Route path="curriculum/edit/:filename" element={<CurriculumForm mode="edit" />} />
            <Route path="curriculum/view/:filename" element={<ViewCurriculum />} />
          </Route>
          
          <Route path="/se" element={<SEPage />} />
          <Route path="/avt" element={<AVTPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          {/* Default route for any unmatched path can be added here if needed */}
          {/* <Route path="*" element={<NotFoundPage />} /> */}
        </Routes>
      </main>
    </div>
  );
}

export default App;
