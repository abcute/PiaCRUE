import './App.css'
// import PromptForm from './components/PromptForm' // Temporarily remove for CML focus
import CMLDashboard from './components/cml/CMLDashboard';

function App() {
  return (
    <div className="App">
      {/* <PromptForm /> */} {/* Temporarily commented out */}
      <CMLDashboard />
    </div>
  )
}

export default App
