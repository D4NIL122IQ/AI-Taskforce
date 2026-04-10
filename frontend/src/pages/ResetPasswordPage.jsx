import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, Eye, EyeOff, ArrowRight, CheckCircle } from 'lucide-react'
import PageBackground from '../components/layout/PageBackground'
import { supabase } from '../supabase'

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

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')
  const [validSession, setValidSession] = useState(false)

  useEffect(() => {
    // Supabase envoie l'access token dans le hash de l'URL (#access_token=...)
    // onAuthStateChange intercepte l'événement PASSWORD_RECOVERY automatiquement
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') {
        setValidSession(true)
      }
    })
    return () => subscription.unsubscribe()
  }, [])

  const eyeBtn = (show, setShow) => (
    <button
      type="button"
      onClick={() => setShow(!show)}
      className="text-gray-400 dark:text-white/30 hover:text-gray-600 dark:hover:text-white/60 transition-colors"
    >
      {show ? <EyeOff size={16} /> : <Eye size={16} />}
    </button>
  )

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (password !== confirm) {
      setError('Les mots de passe ne correspondent pas.')
      return
    }
    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères.')
      return
    }

    setLoading(true)
    try {
      const { error } = await supabase.auth.updateUser({ password })
      if (error) throw new Error(error.message)
      setDone(true)
      setTimeout(() => navigate('/auth'), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] flex items-center justify-center px-4 transition-colors duration-300 font-body">
      <PageBackground />

      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>
            AI Taskforce
          </h1>
          <p className="text-gray-400 dark:text-white/40 text-sm">
            Nouveau mot de passe
          </p>
        </div>

        <div className="bg-white dark:bg-white/[0.03] border border-gray-200 dark:border-white/10 rounded-2xl p-8 backdrop-blur-sm">
          {done ? (
            <div className="flex flex-col items-center gap-4 text-center py-4">
              <CheckCircle size={48} className="text-violet-400" />
              <h2 className="text-gray-900 dark:text-white font-semibold text-lg">Mot de passe mis à jour !</h2>
              <p className="text-gray-500 dark:text-white/50 text-sm">
                Redirection vers la connexion...
              </p>
            </div>
          ) : !validSession ? (
            <div className="text-center py-4">
              <p className="text-gray-500 dark:text-white/50 text-sm">
                Lien invalide ou expiré. Demande un nouveau lien de réinitialisation.
              </p>
              <button
                type="button"
                onClick={() => navigate('/forgot-password')}
                className="mt-4 text-sm text-violet-400 hover:text-violet-300 transition-colors"
              >
                Réessayer
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <p className="text-gray-500 dark:text-white/50 text-sm mb-2">
                Choisis un nouveau mot de passe pour ton compte.
              </p>

              <InputField
                icon={Lock}
                type={showPassword ? 'text' : 'password'}
                placeholder="Nouveau mot de passe"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                rightElement={eyeBtn(showPassword, setShowPassword)}
              />

              <InputField
                icon={Lock}
                type={showConfirm ? 'text' : 'password'}
                placeholder="Confirmer le mot de passe"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                rightElement={eyeBtn(showConfirm, setShowConfirm)}
              />

              {error && (
                <p className="text-red-400 text-xs">{error}</p>
              )}

              <button
                type="submit"
                disabled={loading || !password || !confirm}
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:opacity-90 mt-1 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: 'linear-gradient(90deg, #f43f5e 0%, #8b5cf6 50%, #f97316 100%)' }}
              >
                {loading ? 'Mise à jour...' : 'Mettre à jour le mot de passe'}
                {!loading && <ArrowRight size={16} />}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
