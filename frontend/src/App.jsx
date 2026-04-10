import { Routes, Route,Navigate, useLocation } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GestionAgentPage from './pages/GestionAgentPage'
import CreatAgentPage from './pages/CreatAgentPage'
import FormPage from './pages/FormPage'
import CreatWorkflowPage from './pages/CreatWorkflowPage'
import GestionWorkflowPage from './pages/GestionWorkflowPage'
import ExecuteWorkflowPage from './pages/ExecuteWorkflowPage'
import DashboardPage from './pages/DashbordPage'
import RagConfigPage from './pages/RagConfigPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import { useEffect } from 'react'
import { supabase } from './supabase'


// Protection de route
const ProtectedRoute = ({ children }) => {
  const location = useLocation()
  const user = JSON.parse(localStorage.getItem("user") || "null")
  if (!user) return <Navigate to="/auth" state={{ from: location.pathname }} />
  return children
}

export default function App() {
    useEffect(() => {
    supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN' && session) {
        localStorage.setItem('user', JSON.stringify({
          user_id: session.user.id,
          email: session.user.email,
          nom: session.user.user_metadata?.nom || session.user.email
        }))
      }
      if (event === 'SIGNED_OUT') {
        localStorage.removeItem('user')
      }
    })
  }, [])
  return (
     <Routes>
       <Route path="/" element={<HomePage />} />
       <Route path="/agents" element={<GestionAgentPage />} />
       <Route path="/agents/create" element={<CreatAgentPage />} />
       <Route path="/agents/edit/:id" element={<CreatAgentPage />} />
       <Route path="/auth" element={<FormPage />} />
       <Route path="/forgot-password" element={<ForgotPasswordPage />} />
       <Route path="/reset-password" element={<ResetPasswordPage />} />
       <Route path="/workflow" element={<GestionWorkflowPage />} />
       <Route path="/workflow/create" element={<CreatWorkflowPage />} />
       <Route path="/workflow/edit/:id" element={<CreatWorkflowPage />} />
       <Route path="/workflow/execute" element={<ProtectedRoute><ExecuteWorkflowPage /></ProtectedRoute>} />
       <Route path="/dashboard" element={<ProtectedRoute><DashboardPage/></ProtectedRoute>} />
       <Route path="/ragconfig" element={<ProtectedRoute><RagConfigPage /></ProtectedRoute>} />
       <Route path="/rag-config" element={<ProtectedRoute><RagConfigPage /></ProtectedRoute>} />
     </Routes>
  )
}