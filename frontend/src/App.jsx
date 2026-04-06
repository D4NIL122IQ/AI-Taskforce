import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GestionAgentPage from './pages/GestionAgentPage'
import CreatAgentPage from './pages/CreatAgentPage'
import FormPage from './pages/FormPage'
import CreatWorkflowPage from './pages/CreatWorkflowPage'
import ExecuteWorkflowPage from './pages/ExecuteWorkflowPage'
import DashboardPage from './pages/DashbordPage'

export default function App() {
  return (
     <Routes>
       <Route path="/" element={<HomePage />} />
       <Route path="/agents" element={<GestionAgentPage />} />
       <Route path="/agents/create" element={<CreatAgentPage />} />
        <Route path="/agents/edit/:id" element={<CreatAgentPage />} />
       <Route path="/auth" element={<FormPage />} />
       <Route path="/workflow" element={<CreatWorkflowPage />} />
       <Route path="/workflow/execute" element={<ExecuteWorkflowPage />} />
       <Route path="/dashboard" element={<DashboardPage/>} />
     </Routes>
  )
}