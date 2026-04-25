import { NavLink, Link, useNavigate } from 'react-router-dom'
import { Sun, Moon, Loader2, Play } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import { useExecution } from '../../context/ExecutionContext'
import { useState } from 'react'


const BASE_LINKS = [
  { label: 'Accueil',        to: '/' },
  { label: 'Gestion Agents', to: '/agents' },
  { label: 'Workflow',       to: '/workflow' },
]

const NavItem = ({ label, to }) => (
  <NavLink to={to} end={to === '/'} className="focus-visible:outline-none">
    {({ isActive }) =>
      isActive ? (
        <span
          className="inline-flex px-5 py-[7px] rounded-full text-gray-900 dark:text-white text-sm font-semibold whitespace-nowrap bg-gray-100 dark:bg-white/5"
          style={{ boxShadow: '0 0 0 1.5px #8b5cf6' }}
          aria-current="page"
        >
          {label}
        </span>
      ) : (
        <span className="inline-flex px-5 py-[7px] text-gray-500 dark:text-white/55 hover:text-gray-900 dark:hover:text-white text-sm font-medium transition-colors duration-200 whitespace-nowrap">
          {label}
        </span>
      )
    }
  </NavLink>
)

const UserIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="28" height="28"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-label="Profil utilisateur"
    role="img"
  >
    <circle cx="12" cy="8" r="4" />
    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
  </svg>
)

const NavBar = () => {
  const navigate = useNavigate()
  const { dark, toggle } = useTheme()
  const { isRunning } = useExecution()
  const [showMenu, setShowMenu] = useState(false)
  const user = JSON.parse(localStorage.getItem("user") || "null")

  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/')
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      <div className="bg-white/90 dark:bg-[#080808]/80 backdrop-blur-md border-b border-gray-200 dark:border-white/[0.06] transition-colors duration-300">
        <nav
          className="max-w-7xl mx-auto px-6 h-[68px] flex items-center justify-between"
          aria-label="Navigation principale"
        >
          {/* Logo */}
          <Link
            to="/"
            className="text-gray-900 dark:text-white font-display font-bold text-lg tracking-tight hover:opacity-85 transition-opacity duration-200 flex-shrink-0"
          >
            AI Taskforce
          </Link>

          {/* Liens centrés */}
          <ul className="md:flex items-center gap-1" role="list">
            {BASE_LINKS.map(({ label, to }) => (
              <li key={to}>
                <NavItem label={label} to={to} />
              </li>
            ))}
          </ul>

          {/* Actions */}
          <div className="flex items-center gap-3 flex-shrink-0">

            {/* Bouton exécution en cours — visible uniquement si un workflow tourne */}
            {isRunning && (
              <button
                type="button"
                onClick={() => navigate('/workflow/execute')}
                className="flex items-center gap-2 px-4 py-[7px] rounded-full text-sm font-semibold transition-all duration-200 focus-visible:outline-none"
                style={{
                  background: 'rgba(139,92,246,0.15)',
                  border: '1px solid rgba(139,92,246,0.5)',
                  color: '#a78bfa',
                  boxShadow: '0 0 12px rgba(139,92,246,0.25)',
                }}
                aria-label="Revenir à l'exécution en cours"
              >
                <Loader2 size={14} className="animate-spin" />
                <span>Exécution en cours</span>
              </button>
            )}

            {/* Toggle dark/light */}
            <button
              type="button"
              onClick={toggle}
              className="w-9 h-9 flex items-center justify-center rounded-xl border transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50
                bg-gray-100 border-gray-200 text-gray-500 hover:text-gray-900 hover:border-gray-300
                dark:bg-white/5 dark:border-white/10 dark:text-white/50 dark:hover:text-white dark:hover:border-white/20"
              aria-label={dark ? 'Passer en mode clair' : 'Passer en mode sombre'}
            >
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            {/* Profil */}
          <div className="relative">
            <button
              type="button"
              onClick={() => user ? setShowMenu(!showMenu) : navigate('/auth')}
              className="text-gray-500 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/30 rounded-full p-0.5"
              aria-label="Accéder au profil"
            >
              <UserIcon />
            </button>

            {showMenu && user && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-50 p-2">
                <p className="text-sm text-gray-500 dark:text-white/50 px-3 py-1">{user.email}</p>
                <hr className="border-gray-200 dark:border-gray-700 my-1" />
                <button
                  onClick={() => { setShowMenu(false); navigate('/dashboard') }}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-white/80 hover:bg-gray-100 dark:hover:bg-white/10 rounded-lg"
                >
                  Dashboard
                </button>
                <hr className="border-gray-200 dark:border-gray-700 my-1" />
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-3 py-2 text-sm text-red-500 hover:bg-gray-100 dark:hover:bg-white/10 rounded-lg"
                >
                  Déconnexion
                </button>
              </div>
            )}
          </div>
          </div>
        </nav>
      </div>
    </header>
  )
}

export default NavBar
