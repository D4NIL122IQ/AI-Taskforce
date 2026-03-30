import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import AgentPage from './pages/CreatAgentPage'


export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/agents" element={<AgentPage />} />
    </Routes>
  )
}