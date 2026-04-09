import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff, ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react'
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
      <div className="absolute right-4 top-1/2 -translate-y-1/2">{rightElement}</div>
    )}
  </div>
)

const OtpInput = ({ value, onChange }) => {
  const inputs = useRef([])
  const digits = value.split('')

  const handleChange = (i, e) => {
    const val = e.target.value.replace(/\D/g, '')
    if (!val) return
    const next = [...digits]
    next[i] = val[val.length - 1]
    onChange(next.join(''))
    if (i < 5) inputs.current[i + 1]?.focus()
  }

  const handleKeyDown = (i, e) => {
    if (e.key === 'Backspace') {
      const next = [...digits]
      if (next[i]) {
        next[i] = ''
        onChange(next.join(''))
      } else if (i > 0) {
        inputs.current[i - 1]?.focus()
      }
    }
  }

  const handlePaste = (e) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    onChange(pasted.padEnd(6, '').slice(0, 6))
    inputs.current[Math.min(pasted.length, 5)]?.focus()
    e.preventDefault()
  }

  return (
    <div className="flex gap-3 justify-center">
      {Array.from({ length: 6 }).map((_, i) => (
        <input
          key={i}
          ref={(el) => (inputs.current[i] = el)}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={digits[i] || ''}
          onChange={(e) => handleChange(i, e)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          onPaste={handlePaste}
          className="w-11 h-13 text-center text-lg font-semibold bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl py-3 text-gray-900 dark:text-white focus:outline-none focus:border-violet-400 dark:focus:border-violet-400 transition-all duration-200"
        />
      ))}
    </div>
  )
}

export default function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const eyeBtn = (show, setShow) => (
    <button
      type="button"
      onClick={() => setShow(!show)}
      className="text-gray-400 dark:text-white/30 hover:text-gray-600 dark:hover:text-white/60 transition-colors"
    >
      {show ? <EyeOff size={16} /> : <Eye size={16} />}
    </button>
  )

  // Étape 1 — envoi du code OTP
  const handleSendOtp = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { error } = await supabase.auth.signInWithOtp({ email })
      if (error) throw new Error(error.message)
      setStep(2)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Étape 2 — vérification du code OTP
  const handleVerifyOtp = async (e) => {
    e.preventDefault()
    setError('')
    if (otp.length < 6) {
      setError('Saisis les 6 chiffres du code.')
      return
    }
    setLoading(true)
    try {
      const { error } = await supabase.auth.verifyOtp({
        email,
        token: otp,
        type: 'email',
      })
      if (error) throw new Error(error.message)
      setStep(3)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Étape 3 — nouveau mot de passe
  const handleUpdatePassword = async (e) => {
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
      setStep(4)
      setTimeout(() => navigate('/auth'), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const stepTitles = {
    1: 'Mot de passe oublié',
    2: 'Vérifie ton email',
    3: 'Nouveau mot de passe',
    4: 'Mot de passe mis à jour !',
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] flex items-center justify-center px-4 transition-colors duration-300 font-body">
      <PageBackground />

      <div className="relative w-full max-w-md">
        {step < 4 && (
          <button
            type="button"
            onClick={() => (step === 1 ? navigate('/auth') : setStep(step - 1))}
            className="flex items-center gap-2 text-gray-400 dark:text-white/40 hover:text-gray-700 dark:hover:text-white/80 text-sm transition-colors duration-200 mb-6"
          >
            <ArrowLeft size={16} />
            {step === 1 ? 'Retour à la connexion' : 'Étape précédente'}
          </button>
        )}

        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>
            AI Taskforce
          </h1>
          <p className="text-gray-400 dark:text-white/40 text-sm">{stepTitles[step]}</p>

          {step < 4 && (
            <div className="flex gap-2 justify-center mt-4">
              {[1, 2, 3].map((s) => (
                <div
                  key={s}
                  className={`h-1 rounded-full transition-all duration-300 ${
                    s <= step ? 'w-8 bg-violet-400' : 'w-4 bg-gray-200 dark:bg-white/10'
                  }`}
                />
              ))}
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-white/[0.03] border border-gray-200 dark:border-white/10 rounded-2xl p-8 backdrop-blur-sm">

          {/* Étape 1 — Email */}
          {step === 1 && (
            <form onSubmit={handleSendOtp} className="flex flex-col gap-4">
              <p className="text-gray-500 dark:text-white/50 text-sm mb-2">
                Saisis ton adresse email. On t'envoie un code à 6 chiffres pour réinitialiser ton mot de passe.
              </p>
              <InputField
                icon={Mail}
                type="email"
                placeholder="Adresse email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              {error && <p className="text-red-400 text-xs">{error}</p>}
              <button
                type="submit"
                disabled={loading || !email}
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:opacity-90 mt-1 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: 'linear-gradient(90deg, #f43f5e 0%, #8b5cf6 50%, #f97316 100%)' }}
              >
                {loading ? 'Envoi en cours...' : 'Envoyer le code'}
                {!loading && <ArrowRight size={16} />}
              </button>
            </form>
          )}

          {/* Étape 2 — Code OTP */}
          {step === 2 && (
            <form onSubmit={handleVerifyOtp} className="flex flex-col gap-6">
              <p className="text-gray-500 dark:text-white/50 text-sm text-center">
                Un code à 6 chiffres a été envoyé à <span className="text-gray-700 dark:text-white/80 font-medium">{email}</span>.
              </p>
              <OtpInput value={otp} onChange={setOtp} />
              {error && <p className="text-red-400 text-xs text-center">{error}</p>}
              <button
                type="submit"
                disabled={loading || otp.length < 6}
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: 'linear-gradient(90deg, #f43f5e 0%, #8b5cf6 50%, #f97316 100%)' }}
              >
                {loading ? 'Vérification...' : 'Vérifier le code'}
                {!loading && <ArrowRight size={16} />}
              </button>
              <button
                type="button"
                onClick={handleSendOtp}
                className="text-xs text-gray-400 dark:text-white/40 hover:text-gray-600 dark:hover:text-white/60 transition-colors text-center"
              >
                Renvoyer le code
              </button>
            </form>
          )}

          {/* Étape 3 — Nouveau mot de passe */}
          {step === 3 && (
            <form onSubmit={handleUpdatePassword} className="flex flex-col gap-4">
              <p className="text-gray-500 dark:text-white/50 text-sm mb-2">
                Choisis un nouveau mot de passe.
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
              {error && <p className="text-red-400 text-xs">{error}</p>}
              <button
                type="submit"
                disabled={loading || !password || !confirm}
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:opacity-90 mt-1 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: 'linear-gradient(90deg, #f43f5e 0%, #8b5cf6 50%, #f97316 100%)' }}
              >
                {loading ? 'Mise à jour...' : 'Mettre à jour'}
                {!loading && <ArrowRight size={16} />}
              </button>
            </form>
          )}

          {/* Étape 4 — Succès */}
          {step === 4 && (
            <div className="flex flex-col items-center gap-4 text-center py-4">
              <CheckCircle size={48} className="text-violet-400" />
              <h2 className="text-gray-900 dark:text-white font-semibold text-lg">Mot de passe mis à jour !</h2>
              <p className="text-gray-500 dark:text-white/50 text-sm">
                Redirection vers la connexion...
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
