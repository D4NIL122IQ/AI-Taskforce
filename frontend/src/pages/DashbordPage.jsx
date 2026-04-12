  /**
   * Dashboard Component
   * -------------------
   * Ce composant affiche :
   * - Les statistiques (agents, workflows, exécutions, erreurs)
   * - La liste des agents
   * - Les workflows
   * - Les documents
   * - Le log d'activité
   *
   * Il récupère les données depuis l'API backend et gère :
   * - Le chargement (loading)
   * - L'ouverture des menus contextuels
   */

  import NavBar from "../components/layout/NavBar"
  import { useState, useEffect } from "react"
  import PageBackground  from "../components/layout/PageBackground"
  import { useNavigate } from 'react-router-dom'

  import {
    Bot,
    Workflow,
    Activity,
    AlertCircle,
    Play,
    Settings,
    Rocket,
    BarChart3,
    FileText,
    Image,
    File,
    FileSpreadsheet,
    MoreVertical,
    Trash,
    Edit,
    Eye,
    GitBranch,
    Mail,
    Plus,
  } from "lucide-react"

  const Dashboard = () => {

    // STATES
    const [activeTab, setActiveTab] = useState('overview')
    const [agents, setAgents] = useState([])
    const [workflows, setWorkflows] = useState([])
    const [documents, setDocuments] = useState([])
    const [erreurs, seterreurs] = useState([])
    const [executions, setExecutions] = useState([])
    const [loading, setLoading] = useState(true)
    const [openMenuId, setOpenMenuId] = useState(null)

    // MCP STATES
    const [mcpConnections, setMcpConnections] = useState([])
    const [mcpLoading, setMcpLoading] = useState(false)
    const [mcpToast, setMcpToast] = useState(null)     // { type: 'success'|'error', message: string }
    const [mcpForm, setMcpForm] = useState(null)       // null | 'github' | 'gmail'
    const [mcpTokenInput, setMcpTokenInput] = useState('')

    const navigate = useNavigate()

  // MCP — chargement initial
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user?.user_id) return
    fetch(`http://localhost:8000/executions/mcp-tokens/${user.user_id}`)
      .then(r => r.ok ? r.json() : [])
      .then(data => setMcpConnections(Array.isArray(data) ? data : []))
      .catch(() => {})
  }, [])

  // MCP — soumettre un PAT
  const handlePatConnect = async (mcp_type) => {
    if (!mcpTokenInput.trim()) return
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user?.user_id) return
    setMcpLoading(true)
    try {
      const resp = await fetch(
        `http://localhost:8000/executions/mcp-tokens/${user.user_id}/pat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mcp_type, token: mcpTokenInput.trim() }),
        }
      )
      if (!resp.ok) {
        const err = await resp.json()
        setMcpToast({ type: 'error', message: err.detail || 'Token invalide' })
      } else {
        const token = await resp.json()
        setMcpConnections(prev => {
          const filtered = prev.filter(c => c.mcp_type !== mcp_type)
          return [...filtered, token]
        })
        setMcpToast({ type: 'success', message: `${mcp_type === 'github' ? 'GitHub' : 'Gmail'} connecté avec succès` })
        setMcpForm(null)
        setMcpTokenInput('')
      }
    } catch {
      setMcpToast({ type: 'error', message: 'Erreur réseau' })
    } finally {
      setMcpLoading(false)
      setTimeout(() => setMcpToast(null), 4000)
    }
  }

  // MCP — déconnecter
  const handleMcpDelete = async (mcp_type) => {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user?.user_id) return
    setMcpLoading(true)
    await fetch(
      `http://localhost:8000/executions/mcp-tokens/${user.user_id}/${mcp_type}`,
      { method: 'DELETE' }
    ).finally(() => setMcpLoading(false))
    setMcpConnections(prev => prev.filter(c => c.mcp_type !== mcp_type))
  }

    // ACTIVITES
    const activities = executions.slice(0, 5).map(e => ({
      id: e.id,
      type: e.status === 'TERMINE' ? 'success' : e.status === 'ERREUR' ? 'error' : 'info',
      message: `${e.workflow_nom || 'Workflow'} #${e.workflow_id} — ${e.status}`,
      time: e.date_execution ? new Date(e.date_execution).toLocaleString() : '',
    }))

    // DOCUMENTS (renommé de "document" en "docs")
    const docs = documents.map(d => ({
    id: d.id_document,
    name: d.nom_fichier,
    type: d.nom_fichier?.endsWith('.pdf') ? 'pdf' : 'text',
    date: d.date_upload ? new Date(d.date_upload).toLocaleString() : '',
  }))

    // STYLE DYNAMIQUE
    const getStyle = (type) => {
      switch (type) {
        case "success":
          return { icon: Rocket, color: "text-green-400" }
        case "error":
          return { icon: AlertCircle, color: "text-red-400" }
        case "agent":
          return { icon: Bot, color: "text-purple-400" }
        case "update":
          return { icon: Settings, color: "text-yellow-400" }
        default:
          return { icon: BarChart3, color: "text-gray-400" }
      }
    }

    // ICONES DOCUMENTS
    const getDocIcon = (type) => {
      switch (type) {
        case "pdf":
          return FileText
        case "image":
          return Image
        case "excel":
          return FileSpreadsheet
        default:
          return File
      }
    }

    // FERMER LES MENUS AU CLIC EXTERIEUR
    useEffect(() => {
      const handleClick = () => setOpenMenuId(null)
      document.addEventListener("click", handleClick)
      return () => document.removeEventListener("click", handleClick)
    }, [])

    // FETCH DATA
    useEffect(() => {
      const fetchData = async () => {
        try {
          const user = JSON.parse(localStorage.getItem("user") || "null")
          const userId = user?.user_id

          const [
            agentsRes,
            workflowsRes,
            documentsRes,
            erreursRes,
            executionsRes
          ] = await Promise.all([

            fetch(`http://localhost:8000/agents/${userId}`),
            fetch(`http://localhost:8000/workflows/user/${userId}`),
            fetch(`http://localhost:8000/agents/user/${userId}/documents`),
            fetch(`http://localhost:8000/executions/ERREUR`),
            fetch(`http://localhost:8000/executions/`),
          ])

          const agentsData = await agentsRes.json()
          const workflowsData = await workflowsRes.json()
          const documentsData = await documentsRes.json()
          const erreursData = await erreursRes.json()
          const executionsData = await executionsRes.json()

          setAgents(Array.isArray(agentsData) ? agentsData : [])
          setWorkflows(Array.isArray(workflowsData) ? workflowsData : [])
          setDocuments(Array.isArray(documentsData) ? documentsData : [])
          seterreurs(Array.isArray(erreursData) ? erreursData : [])
          setExecutions(Array.isArray(executionsData) ? executionsData : [])

        } catch (error) {
          console.error("ERREUR FETCH:", error)
        } finally {
          setLoading(false)
        }
      }

      fetchData()
    }, [])

    // STATS
    const stats = [
      { label: "Agents actifs", value: agents.length, icon: Bot },
      { label: "Workflows", value: workflows.length, icon: Workflow },
      { label: "Exécutions", value: executions.length, icon: Activity },
      { label: "Erreurs", value: erreurs.length, icon: AlertCircle },
    ]

    // UI
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white font-body transition-colors duration-300">
        <PageBackground/>
        <NavBar />

        <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

          {/* HEADER */}
          <div className="flex items-center justify-between sticky top-16 z-40 bg-[#080808] py-3 border-b border-gray-800">
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/agents/create')}
                className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm">
                + Agent
              </button>
              <button
                onClick={() => navigate('/workflow')}
                className="border border-gray-600 px-4 py-2 rounded-lg hover:bg-gray-800 text-sm">
                + Workflow
              </button>
            </div>
          </div>

          {/* TABS */}
          <div className="flex gap-1 bg-[#111] border border-gray-800 rounded-xl p-1 w-fit">
            {[
              { key: 'overview', label: 'Vue d\'ensemble' },
              { key: 'mcp',      label: 'Connexions MCP' },
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={[
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-150',
                  activeTab === tab.key
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-400 hover:text-white',
                ].join(' ')}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* LOADING */}
          {loading && activeTab === 'overview' ? (
            <p className="text-gray-400">Chargement...</p>
          ) : activeTab === 'overview' ? (
            <>
              {/* STATS */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map(({ label, value, icon: Icon }) => (
                  <div key={label} className="bg-[#111] border border-gray-800 rounded-xl p-4 flex items-center justify-between hover:border-purple-500 transition">
                    <div>
                      <p className="text-sm text-gray-400">{label}</p>
                      <h2 className="text-2xl font-bold">{value}</h2>
                    </div>
                    <Icon className="text-purple-500" />
                  </div>
                ))}
              </div>

              {/* GRID */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* AGENTS */}
                <div className="lg:col-span-2 bg-[#111] border border-gray-800 rounded-xl p-5">
                  <h2 className="text-lg font-semibold mb-4">Agents</h2>
                  <div className="space-y-3">
                    {agents.length === 0 ? (
                      <p className="text-gray-400 text-sm">Aucun agent créé</p>
                    ) : (
                      agents.map((agent) => (
                        <div key={agent.id} className="flex items-center justify-between bg-[#0d0d0d] p-3 rounded-lg">
                          <div>
                            <p className="font-medium">{agent.nom}</p>
                            <p className="text-sm text-gray-400">{agent.modele}</p>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">actif</span>
                            <button className="p-2 hover:bg-gray-800 rounded"><Play size={16} /></button>
                            <div className="relative">
                              <button onClick={(e) => { e.stopPropagation(); setOpenMenuId(openMenuId === agent.id ? null : agent.id) }} className="p-2 hover:bg-gray-800 rounded">
                                <MoreVertical size={16} />
                              </button>
                              {openMenuId === agent.id && (
                                <div className="absolute right-0 mt-2 w-40 bg-[#1a1a1a] border border-gray-700 rounded-lg shadow-lg z-50">
                                  <button onClick={() => navigate(`/agents/edit/${agent.id}`)} className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-gray-700"><Edit size={14} /> Modifier</button>
                                  <button onClick={async () => { await fetch(`http://localhost:8000/agents/${agent.id}`, { method: 'DELETE' }); setAgents(prev => prev.filter(a => a.id !== agent.id)); setOpenMenuId(null) }} className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-400 hover:bg-gray-700"><Trash size={14} /> Supprimer</button>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* ACTIVITY */}
                <div className="bg-[#111] border border-gray-800 rounded-xl p-5 h-[300px] flex flex-col">
                  <h2 className="text-lg font-semibold mb-4">Log d'Activité</h2>
                  <div className="space-y-3 overflow-y-auto pr-2">
                    {activities.length === 0 ? (
                      <p className="text-gray-400 text-sm">Aucune activité</p>
                    ) : activities.map((act) => {
                      const { icon, color } = getStyle(act.type)
                      const Icon = icon
                      return (
                        <div key={act.id} className="flex items-center justify-between bg-[#0d0d0d] px-3 py-2 rounded-lg">
                          <div className="flex items-center gap-3"><Icon className={color} size={16} /><span className="text-sm">{act.message}</span></div>
                          <span className="text-xs text-gray-500">{act.time}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* WORKFLOWS */}
                <div className="lg:col-span-2 bg-[#111] border border-gray-800 rounded-xl p-5">
                  <h2 className="text-lg font-semibold mb-4">Workflows</h2>
                  <div className="space-y-3">
                    {workflows.length === 0 ? (
                      <p className="text-gray-400 text-sm">Aucun workflow créé</p>
                    ) : workflows.map((wf) => (
                      <div key={wf.id_workflow} className="flex items-center justify-between bg-[#0d0d0d] p-3 rounded-lg">
                        <div>
                          <p className="font-medium">{wf.nom}</p>
                          <p className="text-sm text-gray-400">{wf.nb_agents} agents</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">actif</span>
                          <button onClick={() => { localStorage.setItem('workflow_draft', JSON.stringify(wf)); navigate('/workflow/execute') }} className="p-2 hover:bg-gray-800 rounded"><Play size={16} /></button>
                          <div className="relative">
                            <button onClick={(e) => { e.stopPropagation(); setOpenMenuId(openMenuId === wf.id_workflow ? null : wf.id_workflow) }} className="p-2 hover:bg-gray-800 rounded"><MoreVertical size={16} /></button>
                            {openMenuId === wf.id_workflow && (
                              <div className="absolute right-0 mt-2 w-40 bg-[#1a1a1a] border border-gray-700 rounded-lg shadow-lg z-50">
                                <button onClick={() => { navigate(`/workflow/edit/${wf.id_workflow}`) }} className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-gray-700"><Eye size={14} /> Voir</button>
                                <button onClick={async () => { if (!window.confirm('Supprimer ce workflow ?')) return; await fetch(`http://localhost:8000/workflows/${wf.id_workflow}`, { method: 'DELETE' }); setWorkflows(prev => prev.filter(w => w.id_workflow !== wf.id_workflow)); setOpenMenuId(null) }} className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-400 hover:bg-gray-700"><Trash size={14} /> Supprimer</button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* DOCUMENTS */}
                <div className="bg-[#111] border border-gray-800 rounded-xl p-5 flex flex-col h-[300px]">
                  <h2 className="text-lg font-semibold mb-4">Documents</h2>
                  <div className="space-y-3 overflow-y-auto pr-2">
                    {docs.length === 0 ? (
                      <p className="text-gray-400 text-sm">Aucun document</p>
                    ) : docs.map((doc) => {
                      const Icon = getDocIcon(doc.type)
                      return (
                        <div key={doc.id} className="flex items-center justify-between bg-[#0d0d0d] px-3 py-2 rounded-lg hover:bg-[#1a1a1a] transition">
                          <div className="flex items-center gap-3"><Icon className="text-blue-400" size={18} /><span className="truncate max-w-[180px] text-sm">{doc.name}</span></div>
                          <span className="text-xs text-gray-500">{doc.date}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>

              </div>
            </>
          ) : (
            /* ── ONGLET MCP ───────────────────────────────────────────────── */
            <div className="max-w-2xl space-y-4">

              {/* TOAST */}
              {mcpToast && (
                <div className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium border ${
                  mcpToast.type === 'success'
                    ? 'bg-green-500/10 border-green-500/30 text-green-400'
                    : 'bg-red-500/10 border-red-500/30 text-red-400'
                }`}>
                  {mcpToast.type === 'success' ? `✓ ${mcpToast.message}` : `✕ ${mcpToast.message}`}
                </div>
              )}

              <div>
                <h2 className="text-lg font-semibold">Connexions MCP</h2>
                <p className="text-sm text-gray-400 mt-1">
                  Connectez vos services externes une seule fois. Vos agents pourront les utiliser dans tous vos workflows.
                </p>
              </div>

              {/* CARTES SERVICES */}
              {[
                {
                  key: 'github',
                  label: 'GitHub',
                  description: 'Accès aux repos, issues, pull requests et code.',
                  Icon: GitBranch,
                  iconBg: 'bg-gray-700',
                  iconColor: 'text-white',
                  tokenLabel: 'Personal Access Token (PAT)',
                  tokenHint: 'Générer un token →',
                  tokenHref: 'https://github.com/settings/tokens/new?scopes=repo,user&description=AI-Taskforce',
                  tokenPlaceholder: 'ghp_xxxxxxxxxxxxxxxxxxxx',
                },
                {
                  key: 'gmail',
                  label: 'Gmail',
                  description: 'Lecture, envoi et gestion des emails.',
                  Icon: Mail,
                  iconBg: 'bg-red-500/20',
                  iconColor: 'text-red-400',
                  tokenLabel: 'OAuth Access Token',
                  tokenHint: 'Obtenir un token via OAuth Playground →',
                  tokenHref: 'https://developers.google.com/oauthplayground/',
                  tokenPlaceholder: 'ya29.xxxxxxxxxxxxxxxxxxxx',
                },
              ].map(({ key, label, description, Icon, iconBg, iconColor, tokenLabel, tokenHint, tokenHref, tokenPlaceholder }) => {
                const connected = mcpConnections.find(c => c.mcp_type === key)
                const formOpen = mcpForm === key

                return (
                  <div
                    key={key}
                    className={`bg-[#111] border rounded-xl px-5 py-4 space-y-3 transition-colors duration-200 ${
                      connected ? 'border-green-500/30' : 'border-gray-800'
                    }`}
                  >
                    {/* Ligne principale */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`p-2.5 rounded-xl ${iconBg}`}>
                          <Icon size={20} className={iconColor} />
                        </div>
                        <div>
                          <p className="font-medium">{label}</p>
                          <p className="text-xs text-gray-400 mt-0.5">{description}</p>
                          {connected && (
                            <p className="text-xs text-gray-500 mt-1">
                              Compte : <span className="text-gray-300">{connected.token_public}</span>
                              {' · '}mis à jour le {new Date(connected.updated_at).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {connected && (
                          <span className="text-xs px-2.5 py-1 rounded-full bg-green-500/15 text-green-400 border border-green-500/20">
                            Connecté
                          </span>
                        )}
                        <button
                          onClick={() => { setMcpForm(formOpen ? null : key); setMcpTokenInput('') }}
                          className="text-xs px-3 py-1.5 rounded-lg border border-gray-700 hover:border-gray-500 text-gray-400 hover:text-white transition-colors"
                        >
                          {connected ? 'Reconnecter' : (
                            <span className="flex items-center gap-1"><Plus size={12} /> Connecter</span>
                          )}
                        </button>
                        {connected && (
                          <button
                            disabled={mcpLoading}
                            onClick={() => handleMcpDelete(key)}
                            className="text-xs px-3 py-1.5 rounded-lg border border-red-500/30 hover:border-red-500/60 text-red-400 hover:text-red-300 disabled:opacity-50 transition-colors"
                          >
                            Déconnecter
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Formulaire PAT inline */}
                    {formOpen && (
                      <div className="border-t border-gray-800 pt-3 space-y-2">
                        <label className="text-xs text-gray-400">{tokenLabel}</label>
                        <input
                          type="password"
                          value={mcpTokenInput}
                          onChange={e => setMcpTokenInput(e.target.value)}
                          placeholder={tokenPlaceholder}
                          className="w-full bg-[#0d0d0d] border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500"
                        />
                        <div className="flex items-center justify-between">
                          <a
                            href={tokenHref}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs text-purple-400 hover:text-purple-300 underline underline-offset-2"
                          >
                            {tokenHint}
                          </a>
                          <button
                            disabled={mcpLoading || !mcpTokenInput.trim()}
                            onClick={() => handlePatConnect(key)}
                            className="text-xs px-4 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-50 transition-colors"
                          >
                            {mcpLoading ? 'Vérification...' : 'Valider'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}

            </div>
          )}
        </div>
      </div>
    )
  }

  export default Dashboard