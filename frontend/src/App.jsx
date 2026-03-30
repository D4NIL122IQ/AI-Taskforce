import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      {/* Les autres pages (Login, Register, etc.) seront ajoutées ici */}
    </Routes>
  )
}