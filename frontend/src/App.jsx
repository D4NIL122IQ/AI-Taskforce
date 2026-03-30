import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GestionAgentPage from './pages/GestionAgentPage'
import CreatAgentPage from './pages/CreatAgentPage'
import FormPage from './pages/FormPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/agents" element={<GestionAgentPage />} />
      <Route path="/agents/create" element={<CreatAgentPage />} />
      <Route path="/auth" element={<FormPage />} />
    </Routes>
  )
}