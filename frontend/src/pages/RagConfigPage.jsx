import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import NavBar from '../components/layout/NavBar'
import PageBackground from '../components/layout/PageBackground'
import { useTheme } from '../context/ThemeContext'
import { Save, Info, FileSearch, Layers, Sparkles } from 'lucide-react'

const API = 'http://localhost:8000'

// ── Tooltip d'aide ────────────────────────────────────────────────────────────
const Tooltip = ({ text }) => (
  <div className="group relative inline-flex items-center ml-1.5">
    <Info size={13} className="text-gray-400 dark:text-white/30 cursor-help" />
    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 px-3 py-2 rounded-xl text-xs leading-relaxed
      bg-gray-900 dark:bg-white/10 text-white border border-white/10
      opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 z-50 shadow-xl">
      {text}
    </div>
  </div>
)

// ── Slider stylisé ────────────────────────────────────────────────────────────
const Slider = ({ label, name, value, min, max, step, onChange, tooltip, formatFn }) => {
  const pct = ((value - min) / (max - min)) * 100
  const display = formatFn ? formatFn(value) : value

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center text-sm font-medium text-gray-700 dark:text-white/80">
          {label}
          {tooltip && <Tooltip text={tooltip} />}
        </div>
        <span className="text-sm font-semibold px-2.5 py-0.5 rounded-lg"
          style={{ background: 'rgba(139,92,246,0.15)', color: '#a78bfa', border: '1px solid rgba(139,92,246,0.3)' }}>
          {display}
        </span>
      </div>
      <div className="relative h-5 flex items-center">
        <div className="absolute w-full h-1.5 rounded-full bg-gray-200 dark:bg-white/10" />
        <div className="absolute h-1.5 rounded-full"
          style={{ width: `${pct}%`, background: 'rgba(139,92,246,0.6)' }} />
        <input
          type="range"
          name={name}
          min={min} max={max} step={step}
          value={value}
          onChange={onChange}
          className="absolute w-full h-1.5 opacity-0 cursor-pointer"
        />
        <div className="absolute w-4 h-4 rounded-full bg-violet-500 border-2 border-white dark:border-[#080808] shadow pointer-events-none"
          style={{ left: `calc(${pct}% - 8px)` }} />
      </div>
      <div className="flex justify-between text-xs text-gray-400 dark:text-white/25">
        <span>{formatFn ? formatFn(min) : min}</span>
        <span>{formatFn ? formatFn(max) : max}</span>
      </div>
    </div>
  )
}

// ── Carte de section ──────────────────────────────────────────────────────────
const Section = ({ icon: Icon, title, children }) => (
  <div className="rounded-2xl border p-6 flex flex-col gap-5"
    style={{ background: 'rgba(139,92,246,0.03)', border: '1px solid rgba(139,92,246,0.12)' }}>
    <div className="flex items-center gap-2.5">
      <div className="w-8 h-8 rounded-xl flex items-center justify-center"
        style={{ background: 'rgba(139,92,246,0.12)', border: '1px solid rgba(139,92,246,0.2)' }}>
        <Icon size={16} style={{ color: '#a78bfa' }} />
      </div>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h2>
    </div>
    {children}
  </div>
)

// ── Indicateur pertinence / diversité ─────────────────────────────────────────
const LambdaIndicator = ({ topK, lambdaMult }) => {
  const relevance = Math.round(lambdaMult * 100)
  const diversity = 100 - relevance
  return (
    <div className="rounded-xl p-4 flex flex-col gap-3"
      style={{ background: 'rgba(139,92,246,0.06)', border: '1px solid rgba(139,92,246,0.15)' }}>
      <p className="text-xs font-medium text-gray-500 dark:text-white/40 uppercase tracking-wide">
        Aperçu de la recherche
      </p>
      <div className="flex gap-4">
        <div className="flex-1 flex flex-col gap-1.5">
          <div className="flex justify-between text-xs text-gray-500 dark:text-white/40">
            <span>Pertinence</span>
            <span style={{ color: '#a78bfa' }}>{relevance}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-gray-200 dark:bg-white/10">
            <div className="h-full rounded-full transition-all duration-300"
              style={{ width: `${relevance}%`, background: 'linear-gradient(90deg,#7c3aed,#a78bfa)' }} />
          </div>
        </div>
        <div className="flex-1 flex flex-col gap-1.5">
          <div className="flex justify-between text-xs text-gray-500 dark:text-white/40">
            <span>Diversité</span>
            <span style={{ color: '#34d399' }}>{diversity}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-gray-200 dark:bg-white/10">
            <div className="h-full rounded-full transition-all duration-300"
              style={{ width: `${diversity}%`, background: 'linear-gradient(90deg,#059669,#34d399)' }} />
          </div>
        </div>
      </div>
      <p className="text-xs text-gray-400 dark:text-white/30 leading-relaxed">
        {topK} extrait{topK > 1 ? 's' : ''} envoyés au LLM ·{' '}
        {lambdaMult >= 0.7
          ? 'Focus pertinence — idéal pour des questions précises sur un sujet spécifique.'
          : lambdaMult <= 0.3
          ? 'Focus diversité — idéal pour des sujets larges nécessitant plusieurs angles.'
          : 'Équilibre pertinence / diversité — bon réglage général.'}
      </p>
    </div>
  )
}

// ── Page principale ───────────────────────────────────────────────────────────
const RagConfigPage = () => {
  const { id } = useParams()
  const { dark } = useTheme()

  const [config, setConfig] = useState({
    chunk_size: 500,
    chunk_overlap: 50,
    top_k: 5,
    lambda_mult: 0.5,
    use_post_processing: true,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving]   = useState(false)
  const [saved, setSaved]     = useState(false)
  const [error, setError]     = useState(null)

  useEffect(() => {
    fetch(`${API}/agents/${id}/rag-config`)
      .then(r => r.json())
      .then(data => { setConfig(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [id])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setConfig(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : Number(value) }))
    setSaved(false)
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      const res = await fetch(`${API}/agents/${id}/rag-config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      if (!res.ok) throw new Error()
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      setError('Impossible de sauvegarder. Vérifiez que le backend est démarré.')
    }
    setSaving(false)
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808]">
      <PageBackground /><NavBar />
      <div className="flex items-center justify-center h-screen">
        <div className="w-6 h-6 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white font-body">
      <PageBackground />
      <NavBar />

      <main className="max-w-2xl mx-auto px-6 pt-[100px] pb-24 flex flex-col gap-6">

        {/* En-tête */}
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold">Configuration RAG</h1>
          <p className="text-sm text-gray-500 dark:text-white/40">
            Paramètres de recherche documentaire — Agent {id}
          </p>
        </div>

        {/* Section 1 — Découpage */}
        <Section icon={Layers} title="Découpage des documents">

          <Slider
            label="Taille des chunks"
            name="chunk_size"
            value={config.chunk_size}
            min={100} max={2000} step={50}
            onChange={handleChange}
            tooltip="Taille de chaque morceau de texte indexé. Petit (200-400) = plus de précision. Grand (800-1500) = plus de contexte. Pour des documents techniques denses, privilégiez des petits chunks."
            formatFn={v => `${v} mots`}
          />

          <Slider
            label="Chevauchement entre chunks"
            name="chunk_overlap"
            value={config.chunk_overlap}
            min={0} max={500} step={10}
            onChange={handleChange}
            tooltip="Nombre de mots partagés entre deux chunks consécutifs. Évite de couper une idée en plein milieu. Recommandé : environ 10% de la taille du chunk."
            formatFn={v => `${v} mots`}
          />

          {/* Conseil adaptatif */}
          <div className="rounded-xl px-4 py-3 text-xs leading-relaxed"
            style={{
              background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)',
              border: `1px solid ${dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
              color: dark ? 'rgba(255,255,255,0.35)' : 'rgba(0,0,0,0.45)'
            }}>
            {config.chunk_size <= 300
              ? '💡 Petits chunks — idéal pour des documents techniques précis (code, tableaux, définitions courtes).'
              : config.chunk_size >= 1000
              ? '💡 Grands chunks — idéal pour des textes narratifs où le contexte est important (rapports, articles).'
              : '💡 Taille intermédiaire — bon équilibre pour la majorité des documents.'}
            {' '}Overlap recommandé : {Math.round(config.chunk_size * 0.1)} mots.
          </div>
        </Section>

        {/* Section 2 — Recherche */}
        <Section icon={FileSearch} title="Recherche & Récupération">

          <Slider
            label="Nombre d'extraits récupérés (Top K)"
            name="top_k"
            value={config.top_k}
            min={1} max={20} step={1}
            onChange={handleChange}
            tooltip="Combien d'extraits sont envoyés au LLM. Augmentez si les réponses semblent incomplètes (document dense). Diminuez si le LLM reçoit trop d'informations non pertinentes. Recommandé : 3 à 8."
            formatFn={v => `${v} extrait${v > 1 ? 's' : ''}`}
          />

          <Slider
            label="Lambda — Pertinence vs Diversité"
            name="lambda_mult"
            value={config.lambda_mult}
            min={0} max={1} step={0.05}
            onChange={handleChange}
            tooltip="Contrôle l'algorithme MMR. Valeur haute (0.7-1) = les extraits les plus similaires à la question. Valeur basse (0-0.3) = extraits variés couvrant plusieurs angles. Recommandé : 0.5."
            formatFn={v => {
              if (v <= 0.1) return 'Diversité max'
              if (v >= 0.9) return 'Pertinence max'
              return v.toFixed(2)
            }}
          />

          <LambdaIndicator topK={config.top_k} lambdaMult={config.lambda_mult} />
        </Section>

        {/* Section 3 — Post-traitement */}
        <Section icon={Sparkles} title="Post-traitement">
          <div className="flex items-start justify-between gap-6">
            <div className="flex flex-col gap-1 flex-1">
              <div className="flex items-center text-sm font-medium text-gray-700 dark:text-white/80">
                Reclassement intelligent (Reranking)
                <Tooltip text="Après la récupération vectorielle, un LLM reclasse les extraits du plus au moins pertinent pour la question. Améliore la qualité des réponses mais ajoute ~1-2 secondes de latence. Désactivez si la vitesse est prioritaire." />
              </div>
              <p className="text-xs text-gray-400 dark:text-white/30 leading-relaxed">
                Un LLM trie les extraits récupérés par ordre de pertinence avant de les envoyer à l'agent.
                {config.use_post_processing
                  ? ' Actuellement actif — meilleure qualité.'
                  : ' Actuellement désactivé — réponse plus rapide.'}
              </p>
            </div>
            {/* Toggle switch */}
            <button
              type="button"
              onClick={() => { setConfig(p => ({ ...p, use_post_processing: !p.use_post_processing })); setSaved(false) }}
              className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none"
              style={{ background: config.use_post_processing ? '#7c3aed' : (dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.12)') }}
              role="switch"
              aria-checked={config.use_post_processing}
            >
              <span
                className="inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ease-in-out"
                style={{ transform: config.use_post_processing ? 'translateX(20px)' : 'translateX(0)' }}
              />
            </button>
          </div>
        </Section>

        {/* Erreur */}
        {error && (
          <p className="text-sm text-red-400 text-center">{error}</p>
        )}

        {/* Bouton sauvegarder */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center justify-center gap-2 w-full py-3.5 rounded-2xl text-sm font-semibold transition-all duration-200 disabled:opacity-50"
          style={{
            background: saved ? 'rgba(16,185,129,0.15)' : 'rgba(139,92,246,0.2)',
            border: `1px solid ${saved ? 'rgba(16,185,129,0.4)' : 'rgba(139,92,246,0.4)'}`,
            color: saved ? '#34d399' : '#a78bfa',
          }}
        >
          {saving
            ? <div className="w-4 h-4 rounded-full border-2 border-current border-t-transparent animate-spin" />
            : <Save size={16} />
          }
          {saving ? 'Sauvegarde...' : saved ? '✓ Configuration sauvegardée' : 'Sauvegarder la configuration'}
        </button>

      </main>
    </div>
  )
}

export default RagConfigPage
