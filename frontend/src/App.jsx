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

const SESSION_DURATION = 4 * 60 * 60 * 1000 // 4 heures en ms

const clearIfExpired = () => {
  const stored = JSON.parse(localStorage.getItem('user') || 'null')
  if (stored?.expires_at && Date.now() > stored.expires_at) {
    localStorage.removeItem('user')
  }
}

// Protection de route
const ProtectedRoute = ({ children }) => {
  const location = useLocation()
  clearIfExpired()
  const user = JSON.parse(localStorage.getItem("user") || "null")
  if (!user) return <Navigate to="/auth" state={{ from: location.pathname }} />
  return children
}

export default function App() {
  useEffect(() => {
    // Vérification à l'ouverture
    clearIfExpired()

    // Vérification périodique toutes les minutes
    const interval = setInterval(clearIfExpired, 60_000)

    supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN' && session) {
        localStorage.setItem('user', JSON.stringify({
          user_id: session.user.id,
          email: session.user.email,
          nom: session.user.user_metadata?.nom || session.user.email,
          expires_at: Date.now() + SESSION_DURATION,
        }))
      }
      if (event === 'SIGNED_OUT') {
        localStorage.removeItem('user')
      }
    })

    return () => clearInterval(interval)
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
       <Route path="/workflow/execute" element={<ExecuteWorkflowPage />} />
       <Route path="/dashboard" element={<ProtectedRoute><DashboardPage/></ProtectedRoute>} />
       <Route path="/rag-config/:id" element={<ProtectedRoute><RagConfigPage /></ProtectedRoute>} />
     </Routes>
  )
}