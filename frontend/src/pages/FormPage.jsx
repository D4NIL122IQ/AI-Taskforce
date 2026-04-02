import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, ArrowLeft } from 'lucide-react'
import PageBackground from '../components/layout/PageBackground'

const GithubIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
  </svg>
)

const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
  </svg>
)

const InputField = ({ icon: Icon, type, placeholder, value, onChange, rightElement }) => (
  <div className="relative">
    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-white/40">
      <Icon size={17} />
    </div>
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className="w-full bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 pl-11 pr-11 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/30 text-sm focus:outline-none focus:border-violet-400 dark:focus:border-white/30 focus:bg-white dark:focus:bg-white/[0.08] transition-all duration-200"
    />
    {rightElement && (
      <div className="absolute right-4 top-1/2 -translate-y-1/2">
        {rightElement}
      </div>
    )}
  </div>
)

const OAuthButton = ({ icon: Icon, label, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className="flex items-center justify-center gap-3 w-full bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 text-gray-600 dark:text-white/70 text-sm hover:bg-gray-100 dark:hover:bg-white/10 hover:border-gray-300 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-white transition-all duration-200"
  >
    <Icon />
    <span>{label}</span>
  </button>
)

export default function FormPage() {
  const [mode, setMode] = useState('login')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const navigate = useNavigate()

  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [registerForm, setRegisterForm] = useState({ name: '', email: '', password: '', confirm: '' })

  const handleLoginSubmit = (e) => { e.preventDefault() }
  const handleRegisterSubmit = (e) => { e.preventDefault() }

  const eyeBtn = (show, setShow) => (
    <button
      type="button"
      onClick={() => setShow(!show)}
      className="text-gray-400 dark:text-white/30 hover:text-gray-600 dark:hover:text-white/60 transition-colors"
    >
      {show ? <EyeOff size={16} /> : <Eye size={16} />}
    </button>
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] flex items-center justify-center px-4 transition-colors duration-300 font-body">

      <PageBackground />

      <div className="relative w-full max-w-md">

        <button
          type="button"
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-400 dark:text-white/40 hover:text-gray-700 dark:hover:text-white/80 text-sm transition-colors duration-200 mb-6"
        >
          <ArrowLeft size={16} />
          Retour
        </button>

        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>
            AI Taskforce
          </h1>
          <p className="text-gray-400 dark:text-white/40 text-sm">
            {mode === 'login' ? 'Content de te revoir' : 'Crée ton compte'}
          </p>
        </div>

        <div className="bg-white dark:bg-white/[0.03] border border-gray-200 dark:border-white/10 rounded-2xl p-8 backdrop-blur-sm">

          <div className="flex bg-gray-100 dark:bg-white/5 rounded-xl p-1 mb-7">
            {['login', 'register'].map((m) => (
              <button
                key={m} type="button" onClick={() => setMode(m)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  mode === m
                    ? 'bg-white dark:bg-white/10 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-400 dark:text-white/40 hover:text-gray-600 dark:hover:text-white/60'
                }`}
              >
                {m === 'login' ? 'Connexion' : 'Inscription'}
              </button>
            ))}
          </div>

          {mode === 'login' && (
            <form onSubmit={handleLoginSubmit} className="flex flex-col gap-4">

              <InputField icon={Mail} type="email" placeholder="Adresse email"
                value={loginForm.email} onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })} />

              <InputField icon={Lock} type={showPassword ? 'text' : 'password'} placeholder="Mot de passe"
                value={loginForm.password} onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                rightElement={eyeBtn(showPassword, setShowPassword)} />

              <div className="text-right -mt-1">
                <button type="button" className="text-xs text-gray-400 dark:text-white/40 hover:text-gray-600 dark:hover:text-white/70 transition-colors">
                  Mot de passe oublié ?
                </button>
              </div>

              <button
                type="submit"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:opacity-90 mt-1"
                style={{ background: 'linear-gradient(90deg, #f43f5e 0%, #8b5cf6 50%, #f97316 100%)' }}
              >
                Se connecter
                <ArrowRight size={16} />
              </button>

              <div className="flex items-center gap-3 my-1">
                <div className="flex-1 h-px bg-gray-200 dark:bg-white/10" />
                <span className="text-gray-400 dark:text-white/30 text-xs">ou continuer avec</span>
                <div className="flex-1 h-px bg-gray-200 dark:bg-white/10" />
              </div>

              <div className="flex flex-col gap-3">
                <OAuthButton icon={GoogleIcon} label="Continuer avec Gmail" onClick={() => {}} />
                <OAuthButton icon={GithubIcon} label="Continuer avec GitHub" onClick={() => {}} />
              </div>

            </form>
          )}

          {mode === 'register' && (
            <form onSubmit={handleRegisterSubmit} className="flex flex-col gap-4">

              <InputField icon={User} type="text" placeholder="Nom complet"
                value={registerForm.name} onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })} />

              <InputField icon={Mail} type="email" placeholder="Adresse email"
                value={registerForm.email} onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })} />

              <InputField icon={Lock} type={showPassword ? 'text' : 'password'} placeholder="Mot de passe"
                value={registerForm.password} onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                rightElement={eyeBtn(showPassword, setShowPassword)} />

              <InputField icon={Lock} type={showConfirm ? 'text' : 'password'} placeholder="Confirmer le mot de passe"
                value={registerForm.confirm} onChange={(e) => setRegisterForm({ ...registerForm, confirm: e.target.value })}
                rightElement={eyeBtn(showConfirm, setShowConfirm)} />

              <button
                type="submit"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:opacity-90 mt-1"
                style={{ background: 'linear-gradient(90deg, #f43f5e 0%, #8b5cf6 50%, #f97316 100%)' }}
              >
                Créer mon compte
                <ArrowRight size={16} />
              </button>

              <div className="flex items-center gap-3 my-1">
                <div className="flex-1 h-px bg-gray-200 dark:bg-white/10" />
                <span className="text-gray-400 dark:text-white/30 text-xs">ou continuer avec</span>
                <div className="flex-1 h-px bg-gray-200 dark:bg-white/10" />
              </div>

              <div className="flex flex-col gap-3">
                <OAuthButton icon={GoogleIcon} label="Continuer avec Gmail" onClick={() => {}} />
                <OAuthButton icon={GithubIcon} label="Continuer avec GitHub" onClick={() => {}} />
              </div>

            </form>
          )}
        </div>

      </div>
    </div>
  )
}
