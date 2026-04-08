import { Routes, Route,Navigate, useLocation } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GestionAgentPage from './pages/GestionAgentPage'
import CreatAgentPage from './pages/CreatAgentPage'
import FormPage from './pages/FormPage'
import CreatWorkflowPage from './pages/CreatWorkflowPage'
import ExecuteWorkflowPage from './pages/ExecuteWorkflowPage'
import DashboardPage from './pages/DashbordPage'


// Protection de route
const ProtectedRoute = ({ children }) => {
  const location = useLocation()
  const user = JSON.parse(localStorage.getItem("user") || "null")
  if (!user) return <Navigate to="/auth" state={{ from: location.pathname }} />
  return children
}

export default function App() {
  return (
     <Routes>
       <Route path="/" element={<HomePage />} />
       <Route path="/agents" element={<ProtectedRoute><GestionAgentPage /></ProtectedRoute>} />
       <Route path="/agents/create" element={<ProtectedRoute><CreatAgentPage /></ProtectedRoute>} />
        <Route path="/agents/edit/:id" element={<ProtectedRoute><CreatAgentPage /></ProtectedRoute>} />
       <Route path="/auth" element={<FormPage />} />
       <Route path="/workflow" element={<ProtectedRoute><CreatWorkflowPage /></ProtectedRoute>} />
       <Route path="/workflow/execute" element={<ProtectedRoute><ExecuteWorkflowPage /></ProtectedRoute>} />
       <Route path="/dashboard" element={<ProtectedRoute><DashboardPage/></ProtectedRoute>} />

     </Routes>
  )
}