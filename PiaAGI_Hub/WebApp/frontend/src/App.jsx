// import { useState, useEffect } from 'react' // No longer needed for App.jsx
// import reactLogo from './assets/react.svg' // No longer needed
// import viteLogo from '/vite.svg' // No longer needed
import './App.css'
import PromptForm from './components/PromptForm'

function App() {
  // const [count, setCount] = useState(0) // No longer needed
  // const [backendMessage, setBackendMessage] = useState('') // No longer needed

  // const fetchBackendMessage = () => { // No longer needed
  //   fetch('/api/hello')
  //     .then(response => response.json())
  //     .then(data => setBackendMessage(data.message))
  //     .catch(error => console.error('Error fetching data:', error));
  // };

  return (
    <div className="App">
      <PromptForm />
    </div>
  )
}

export default App
