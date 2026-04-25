import { useState, useCallback, useRef, useEffect } from 'react'
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  Handle,
  Position,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import NavBar from '../components/layout/NavBar'
import { useTheme } from '../context/ThemeContext'
import { useNavigate, useParams } from 'react-router-dom'
import { Bot, Crown, Trash2, Plus, Save, AlertCircle, Play, Workflow, ArrowLeft, Mail } from 'lucide-react'

const GithubGlyph = ({ size = 12, color = 'currentColor' }) => (
  <svg viewBox="0 0 24 24" fill={color} width={size} height={size}>
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
  </svg>
)

/* ─────────────────────────── helpers ────────────────────────────── */


const SUPERVISOR_ID = 'supervisor-0'

const isSupervisorRole = (role) => {
  if (typeof role !== 'string') return false
  const r = role.toLowerCase().trim()
  return r === 'superviseur' || r === 'supervisor'
}

/* ─────────────────────────── custom nodes ───────────────────────── */

const SupervisorNode = ({ data, selected }) => (
  <div
    className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border transition-all duration-200"
    style={{
      background: 'rgba(139,92,246,0.12)',
      borderColor: selected ? '#8b5cf6' : 'rgba(139,92,246,0.45)',
      boxShadow: selected ? '0 0 0 2px #8b5cf6, 0 0 24px rgba(139,92,246,0.3)' : '0 0 16px rgba(139,92,246,0.15)',
      minWidth: 160,
    }}
  >
    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(139,92,246,0.25)', border: '1px solid rgba(139,92,246,0.5)' }}>
      <Crown size={20} style={{ color: '#a78bfa' }} />
    </div>
    <div className="text-center">
      <p className="text-sm font-semibold leading-tight" style={{ color: '#1f2937' /* overridden by node bg */ }}>
        <span className="text-gray-900 dark:text-white">{data.label}</span>
      </p>
      <p className="text-xs mt-0.5" style={{ color: 'rgba(167,139,250,0.9)' }}>Superviseur</p>
    </div>
    {data.model && (
      <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(139,92,246,0.15)', color: 'rgba(139,92,246,0.9)', border: '1px solid rgba(139,92,246,0.2)' }}>
        {data.model}
      </span>
    )}
    <Handle type="source" position={Position.Bottom} style={{ background: '#8b5cf6', border: '2px solid transparent', width: 10, height: 10 }} />
  </div>
)

const AgentNode = ({ data, selected }) => (
  <div
    className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border transition-all duration-200"
    style={{
      background: 'rgba(0,0,0,0.04)',
      borderColor: selected ? 'rgba(0,0,0,0.35)' : 'rgba(0,0,0,0.12)',
      boxShadow: selected ? '0 0 0 2px rgba(0,0,0,0.25)' : 'none',
      minWidth: 150,
    }}
  >
    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.06)', border: '1px solid rgba(0,0,0,0.1)' }}>
      <Bot size={20} style={{ color: 'rgba(0,0,0,0.45)' }} />
    </div>
    <div className="text-center">
      <p className="text-sm font-semibold leading-tight" style={{ color: 'rgba(0,0,0,0.8)' }}>{data.label}</p>
      <p className="text-xs mt-0.5" style={{ color: 'rgba(0,0,0,0.4)' }}>{data.role || 'Agent'}</p>
    </div>
    {data.model && (
      <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(0,0,0,0.05)', color: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,0,0,0.08)' }}>
        {data.model}
      </span>
    )}
    <Handle type="target" position={Position.Top} style={{ background: 'rgba(0,0,0,0.4)', border: '2px solid transparent', width: 10, height: 10 }} />
    <Handle type="source" id="mcp" position={Position.Right} style={{ background: 'transparent', border: 'none', width: 1, height: 1, top: '50%' }} />
  </div>
)

/* Dark-specific node variants */
const SupervisorNodeDark = ({ data, selected }) => (
  <div
    className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border transition-all duration-200"
    style={{
      background: 'rgba(139,92,246,0.12)',
      borderColor: selected ? '#8b5cf6' : 'rgba(139,92,246,0.45)',
      boxShadow: selected ? '0 0 0 2px #8b5cf6, 0 0 24px rgba(139,92,246,0.3)' : '0 0 16px rgba(139,92,246,0.15)',
      minWidth: 160,
    }}
  >
    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(139,92,246,0.25)', border: '1px solid rgba(139,92,246,0.5)' }}>
      <Crown size={20} style={{ color: '#a78bfa' }} />
    </div>
    <div className="text-center">
      <p className="text-sm font-semibold leading-tight" style={{ color: 'white' }}>{data.label}</p>
      <p className="text-xs mt-0.5" style={{ color: 'rgba(167,139,250,0.7)' }}>Superviseur</p>
    </div>
    {data.model && (
      <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(139,92,246,0.15)', color: 'rgba(167,139,250,0.8)', border: '1px solid rgba(139,92,246,0.2)' }}>
        {data.model}
      </span>
    )}
    <Handle type="source" position={Position.Bottom} style={{ background: '#8b5cf6', border: '2px solid #080808', width: 10, height: 10 }} />
  </div>
)

const AgentNodeDark = ({ data, selected }) => (
  <div
    className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border transition-all duration-200"
    style={{
      background: 'rgba(255,255,255,0.03)',
      borderColor: selected ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.12)',
      boxShadow: selected ? '0 0 0 2px rgba(255,255,255,0.3)' : 'none',
      minWidth: 150,
    }}
  >
    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}>
      <Bot size={20} style={{ color: 'rgba(255,255,255,0.6)' }} />
    </div>
    <div className="text-center">
      <p className="text-sm font-semibold leading-tight" style={{ color: 'white' }}>{data.label}</p>
      <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.35)' }}>{data.role || 'Agent'}</p>
    </div>
    {data.model && (
      <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.3)', border: '1px solid rgba(255,255,255,0.08)' }}>
        {data.model}
      </span>
    )}
    <Handle type="target" position={Position.Top} style={{ background: 'rgba(255,255,255,0.5)', border: '2px solid #080808', width: 10, height: 10 }} />
    <Handle type="source" id="mcp" position={Position.Right} style={{ background: 'transparent', border: 'none', width: 1, height: 1, top: '50%' }} />
  </div>
)

const renderMcpGlyph = (mcpType, color, size = 12) => {
  if (mcpType === 'gmail') return <Mail size={size} style={{ color }} />
  return <GithubGlyph size={size} color={color} />
}

const MCP_META = {
  github: { label: 'GitHub', accent: '#24292f', accentDark: '#f0f6fc' },
  gmail:  { label: 'Gmail',  accent: '#ea4335', accentDark: '#f28b82' },
}

const McpNode = ({ data, selected }) => {
  const key = data.mcp_type in MCP_META ? data.mcp_type : 'github'
  const meta = MCP_META[key]
  return (
    <div
      className="flex items-center gap-1.5 py-1.5 px-2.5 rounded-lg border transition-all duration-200"
      style={{
        background: 'rgba(0,0,0,0.03)',
        borderColor: selected ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.12)',
        minWidth: 90,
      }}
    >
      <div className="w-5 h-5 rounded-md flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.05)' }}>
        {renderMcpGlyph(key, meta.accent)}
      </div>
      <span className="text-xs font-medium" style={{ color: 'rgba(0,0,0,0.7)' }}>{meta.label}</span>
      <Handle type="target" position={Position.Left} style={{ background: meta.accent, border: '2px solid transparent', width: 8, height: 8 }} />
    </div>
  )
}

const McpNodeDark = ({ data, selected }) => {
  const key = data.mcp_type in MCP_META ? data.mcp_type : 'github'
  const meta = MCP_META[key]
  return (
    <div
      className="flex items-center gap-1.5 py-1.5 px-2.5 rounded-lg border transition-all duration-200"
      style={{
        background: 'rgba(255,255,255,0.04)',
        borderColor: selected ? 'rgba(255,255,255,0.35)' : 'rgba(255,255,255,0.12)',
        minWidth: 90,
      }}
    >
      <div className="w-5 h-5 rounded-md flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.06)' }}>
        {renderMcpGlyph(key, meta.accentDark)}
      </div>
      <span className="text-xs font-medium" style={{ color: 'rgba(255,255,255,0.8)' }}>{meta.label}</span>
      <Handle type="target" position={Position.Left} style={{ background: meta.accentDark, border: '2px solid #080808', width: 8, height: 8 }} />
    </div>
  )
}

const lightNodeTypes = { supervisor: SupervisorNode, agent: AgentNode, mcp: McpNode }
const darkNodeTypes  = { supervisor: SupervisorNodeDark, agent: AgentNodeDark, mcp: McpNodeDark }

/* ─────────────────────────── toolbox item ───────────────────────── */

const ToolboxItem = ({ agent, dark }) => {
  const onDragStart = (e) => {
    e.dataTransfer.setData('application/reactflow-agent', JSON.stringify(agent))
    e.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div
      draggable
      onDragStart={onDragStart}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl border cursor-grab active:cursor-grabbing transition-all duration-150
        ${dark
          ? 'bg-white/[0.02] border-white/8 hover:border-white/20 hover:bg-white/5'
          : 'bg-gray-50 border-gray-200 hover:border-gray-300 hover:bg-gray-100'}`}
    >
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
        ${dark ? 'bg-violet-600/15 border border-violet-500/25' : 'bg-violet-50 border border-violet-200'}`}>
        <Bot size={15} className={dark ? 'text-violet-400' : 'text-violet-600'} />
      </div>
      <div className="min-w-0">
        <p className={`text-xs font-medium truncate ${dark ? 'text-white' : 'text-gray-800'}`}>{agent.name}</p>
        <p className={`text-xs truncate ${dark ? 'text-white/35' : 'text-gray-400'}`}>{agent.role || 'Personnalisé'}</p>
      </div>
    </div>
  )
}

/* ─────────────────────────── canvas inner ───────────────────────── */

const initialSupervisorNode = {
  id: SUPERVISOR_ID,
  type: 'supervisor',
  position: { x: 300, y: 220 },
  data: { label: 'Superviseur', model: '' },
  deletable: false,
}

function FlowCanvas({ agents, dark, workflowName, workflowId = null, initialNodes: initNodes = null, initialEdges: initEdges = null }) {
  const reactFlowWrapper = useRef(null)
  const { screenToFlowPosition } = useReactFlow()
  const isEditMode = initNodes !== null

  const [nodes, setNodes, onNodesChange] = useNodesState(initNodes ?? [initialSupervisorNode])
  const [edges, setEdges, onEdgesChange] = useEdgesState(initEdges ?? [])
  const [toast, setToast] = useState(null)

  // Initialise le compteur depuis le max des IDs existants pour éviter les conflits
  const _initCounter = () => {
    if (!initNodes) return 1
    const ids = initNodes.map(n => { const m = n.id?.match(/^agent-(\d+)$/); return m ? parseInt(m[1]) : 0 })
    return Math.max(0, ...ids) + 1
  }
  const nodeCounter = useRef(_initCounter())

  const nodeTypes = dark ? darkNodeTypes : lightNodeTypes
  const navigate = useNavigate()

  // Synchronise les badges MCP avec les agents présents (hydratation + nettoyage des orphelins)
  useEffect(() => {
    const agentIds = new Set(nodes.filter(n => n.type === 'agent').map(n => n.id))
    const missing = nodes.filter(n =>
      n.type === 'agent' &&
      (n.data?.mcp_type || n.data?.mcpType) &&
      !nodes.some(m => m.id === `mcp-${n.id}`)
    )
    const orphans = nodes.filter(n => n.type === 'mcp' && !agentIds.has(n.id.replace(/^mcp-/, '')))
    if (missing.length === 0 && orphans.length === 0) return

    const newMcpNodes = missing.map(n => ({
      id: `mcp-${n.id}`,
      type: 'mcp',
      position: { x: (n.position?.x || 0) + 180, y: (n.position?.y || 0) + 10 },
      data: { mcp_type: n.data.mcp_type || n.data.mcpType },
      selectable: false,
      deletable: false,
    }))
    const newMcpEdges = missing.map(n => ({
      id: `e-${n.id}-mcp`,
      source: n.id,
      sourceHandle: 'mcp',
      target: `mcp-${n.id}`,
      animated: false,
      style: { stroke: 'rgba(120,120,120,0.45)', strokeWidth: 1.5, strokeDasharray: '4 4' },
      selectable: false,
      deletable: false,
    }))
    const orphanIds = new Set(orphans.map(n => n.id))
    setNodes(ns => [...ns.filter(n => !orphanIds.has(n.id)), ...newMcpNodes])
    setEdges(es => [
      ...es.filter(e => !orphanIds.has(e.source) && !orphanIds.has(e.target)),
      ...newMcpEdges,
    ])
  }, [nodes, setNodes, setEdges])

  // En mode création seulement : auto-remplir le superviseur tant qu'il n'a pas été personnalisé
  useEffect(() => {
    if (isEditMode) return
    const sup = agents.find(a => isSupervisorRole(a.role))
    if (!sup) return
    setNodes(ns => ns.map(n => {
      if (n.id !== SUPERVISOR_ID) return n
      if (n.data.label && n.data.label !== 'Superviseur') return n
      return { ...n, data: { ...n.data, label: sup.name, model: sup.model, role: 'Superviseur', system_prompt: sup.systemPrompt || '' } }
    }))
  }, [agents, isEditMode, setNodes])

  const showToast = (msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const onConnect = useCallback((params) => {
    const touchesMcp = params.source?.startsWith('mcp-') || params.target?.startsWith('mcp-')
    if (touchesMcp) {
      showToast('Le nœud MCP est attaché automatiquement à son agent.')
      return
    }
    const involvesSupervisor = params.source === SUPERVISOR_ID || params.target === SUPERVISOR_ID
    if (!involvesSupervisor) {
      showToast('Les agents ne peuvent se connecter qu\'au superviseur.')
      return
    }
    setEdges(eds => addEdge({
      ...params,
      animated: true,
      style: { stroke: '#8b5cf6', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' },
    }, eds))
  }, [setEdges])

  const onDragOver = useCallback((e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    const raw = e.dataTransfer.getData('application/reactflow-agent')
    if (!raw) return
    const agent = JSON.parse(raw)
    const position = screenToFlowPosition({ x: e.clientX, y: e.clientY })
    const isSupervisor = isSupervisorRole(agent.role)

    // Drop d'un agent "Superviseur" → remplace le superviseur central (pas un nouvel agent)
    if (isSupervisor) {
      setNodes(ns => ns.map(n => n.id === SUPERVISOR_ID
        ? { ...n, data: { ...n.data, label: agent.name, model: agent.model, role: 'Superviseur', system_prompt: agent.systemPrompt || '' } }
        : n
      ))
      showToast(`Superviseur mis à jour : ${agent.name}`)
      return
    }

    const mcpType = agent.mcpType || agent.mcp_type || ''
    const agentId = `agent-${nodeCounter.current++}`
    const agentNode = {
      id: agentId,
      type: 'agent',
      position,
      data: { label: agent.name, role: agent.role, model: agent.model, system_prompt: agent.systemPrompt || '', web_search: agent.webSearch || false, generate_document: agent.generateDocument || agent.generate_document || false,utilise_mcp: !!mcpType, mcp_type: mcpType },
    }
    if (!mcpType) {
      setNodes(ns => [...ns, agentNode])
      return
    }
    const mcpId = `mcp-${agentId}`
    const mcpNode = {
      id: mcpId,
      type: 'mcp',
      position: { x: position.x + 180, y: position.y + 10 },
      data: { mcp_type: mcpType },
      selectable: false,
      deletable: false,
    }
    const mcpEdge = {
      id: `e-${agentId}-mcp`,
      source: agentId,
      sourceHandle: 'mcp',
      target: mcpId,
      animated: false,
      style: { stroke: 'rgba(120,120,120,0.45)', strokeWidth: 1.5, strokeDasharray: '4 4' },
      selectable: false,
      deletable: false,
    }
    setNodes(ns => [...ns, agentNode, mcpNode])
    setEdges(es => [...es, mcpEdge])
  }, [screenToFlowPosition, setNodes, setEdges])

  const deleteSelected = useCallback(() => {
    const removed = new Set(
      nodes.filter(n => n.selected && n.id !== SUPERVISOR_ID).map(n => n.id)
    )
    const mcpDrops = new Set()
    removed.forEach(id => { if (id.startsWith('agent-')) mcpDrops.add(`mcp-${id}`) })
    const allRemoved = new Set([...removed, ...mcpDrops])

    setNodes(ns => ns.filter(n => !allRemoved.has(n.id)))
    setEdges(es => es.filter(e =>
      !e.selected && !allRemoved.has(e.source) && !allRemoved.has(e.target)
    ))
  }, [nodes, setNodes, setEdges])

  const saveWorkflow = async () => {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    try {
      if (!user) {
        // ── Mode localStorage ─────────────────────────────────────────
        const local = JSON.parse(localStorage.getItem('local_workflows') || '[]')
        const savedId = workflowId || `local-${Date.now()}`
        const saved = {
          id_workflow: savedId,
          nom: workflowName,
          donnees_graphe_json: { nodes, edges },
          date_creation: new Date().toISOString(),
        }
        if (workflowId) {
          localStorage.setItem('local_workflows', JSON.stringify(local.map(w => w.id_workflow === workflowId ? saved : w)))
        } else {
          localStorage.setItem('local_workflows', JSON.stringify([...local, saved]))
        }
        localStorage.setItem('workflow_draft', JSON.stringify({ id_workflow: savedId, name: workflowName, nodes, edges }))
        showToast('Workflow sauvegardé !')
        return
      }

      // ── Mode API (connecté) ───────────────────────────────────────
      const isEdit = !!workflowId
      const url = isEdit
        ? `http://localhost:8000/workflows/${workflowId}`
        : 'http://localhost:8000/workflows'
      const res = await fetch(url, {
        method: isEdit ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nom: workflowName,
          donnees_graphe_json: { nodes, edges },
          utilisateur_id: user.user_id || null,
        }),
      })
      if (!res.ok) throw new Error('Erreur sauvegarde')
      const data = await res.json()
      const savedId = data.id_workflow ?? workflowId
      localStorage.setItem('workflow_draft', JSON.stringify({ id_workflow: savedId, name: workflowName, nodes, edges }))
      showToast('Workflow sauvegardé !')
    } catch (err) {
      showToast('Erreur : ' + err.message)
    }
  }

  const sidebarBg = dark ? 'rgba(8,8,8,0.95)' : 'rgba(255,255,255,0.95)'
  const sidebarBorder = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)'
  const canvasBg = dark ? '#080808' : '#f3f4f6'
  const bgColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'

  const specialistAgents = agents.filter(a => !isSupervisorRole(a.role))
  const currentSupervisorLabel = nodes.find(n => n.id === SUPERVISOR_ID)?.data?.label || ''
  const currentSupervisorAgent = agents.find(a => a.name === currentSupervisorLabel)

  const handleSupervisorChange = (agentName) => {
    const agent = agents.find(a => a.name === agentName)
    if (!agent) return
    setNodes(ns => ns.map(n => n.id === SUPERVISOR_ID
      ? { ...n, data: { ...n.data, label: agent.name, model: agent.model, role: 'Superviseur', system_prompt: agent.systemPrompt || '' } }
      : n
    ))
  }

  return (
    <div className="flex h-full" style={{ height: 'calc(100vh - 68px)' }}>

      {/* ── Toolbox sidebar ── */}
      <aside
        className="w-64 flex-shrink-0 flex flex-col border-r overflow-y-auto"
        style={{ background: sidebarBg, borderColor: sidebarBorder }}
      >
        <div className="px-4 py-4 border-b" style={{ borderColor: sidebarBorder }}>
          <h2 className={`text-sm font-semibold ${dark ? 'text-white' : 'text-gray-900'}`}>Boîte à outils</h2>
          <p className={`text-xs mt-0.5 ${dark ? 'text-white/35' : 'text-gray-400'}`}>
            Glissez un spécialiste sur le canvas
          </p>
        </div>

        {/* ── Sélecteur de superviseur ── */}
        <div className="px-4 py-3 border-b" style={{ borderColor: sidebarBorder }}>
          <div className="flex items-center gap-2 mb-2">
            <Crown size={12} style={{ color: '#8b5cf6' }} />
            <span className={`text-xs font-medium ${dark ? 'text-white/70' : 'text-gray-700'}`}>Superviseur</span>
          </div>
          {agents.length === 0 ? (
            <p className={`text-xs ${dark ? 'text-white/35' : 'text-gray-400'}`}>
              Aucun agent disponible. <a href="/agents/create" className="text-violet-500">Créer un agent</a>.
            </p>
          ) : (
            <select
              value={currentSupervisorAgent?.name || ''}
              onChange={(e) => handleSupervisorChange(e.target.value)}
              className="w-full text-xs rounded-lg px-2 py-2 cursor-pointer"
              style={{
                background: dark ? 'rgba(255,255,255,0.04)' : '#f9fafb',
                border: `1px solid ${dark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.1)'}`,
                color: dark ? 'white' : '#111827',
                outline: 'none',
              }}
            >
              <option value="" disabled>Choisir un superviseur…</option>
              {agents.map((a) => (
                <option key={a.id || a.name} value={a.name}>
                  {isSupervisorRole(a.role) ? '👑 ' : ''}{a.name}{a.model ? ` · ${a.model}` : ''}
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="flex-1 px-3 py-3 flex flex-col gap-2">
          {specialistAgents.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-3 py-10 text-center">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${dark ? 'bg-white/4 border border-dashed border-white/12' : 'bg-gray-100 border border-dashed border-gray-300'}`}>
                <Bot size={18} className={dark ? 'text-white/25' : 'text-gray-300'} />
              </div>
              <div>
                <p className={`text-xs ${dark ? 'text-white/35' : 'text-gray-400'}`}>Aucun spécialiste disponible</p>
                <a href="/agents/create" className="text-xs mt-1 inline-flex items-center gap-1 text-violet-500">
                  <Plus size={11} /> Créer un agent
                </a>
              </div>
            </div>
          ) : (
            specialistAgents.map((a, i) => <ToolboxItem key={i} agent={a} dark={dark} />)
          )}
        </div>

        <div className="px-4 py-4 border-t" style={{ borderColor: sidebarBorder }}>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-5 h-5 rounded flex items-center justify-center" style={{ background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)' }}>
              <Crown size={11} style={{ color: '#8b5cf6' }} />
            </div>
            <span className={`text-xs ${dark ? 'text-white/40' : 'text-gray-400'}`}>Superviseur (nœud central)</span>
          </div>
          <div className="flex items-center gap-2 mb-2">
            <div className={`w-5 h-5 rounded flex items-center justify-center ${dark ? 'bg-white/5 border border-white/15' : 'bg-gray-100 border border-gray-200'}`}>
              <Bot size={11} className={dark ? 'text-white/50' : 'text-gray-400'} />
            </div>
            <span className={`text-xs ${dark ? 'text-white/40' : 'text-gray-400'}`}>Agent spécialisé</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-5 h-5 rounded flex items-center justify-center ${dark ? 'bg-white/5 border border-white/15' : 'bg-gray-100 border border-gray-200'}`}>
              <GithubGlyph size={10} color={dark ? 'rgba(255,255,255,0.5)' : 'rgba(107,114,128,1)'} />
            </div>
            <span className={`text-xs ${dark ? 'text-white/40' : 'text-gray-400'}`}>Connexion MCP (auto)</span>
          </div>
        </div>
      </aside>

      {/* ── Main canvas ── */}
      <div className="flex-1 relative" ref={reactFlowWrapper}>

        {/* nom workflow + back button */}
        <div className="absolute top-4 left-4 z-10 flex items-center gap-3">
          <button
            onClick={() => navigate('/workflow')}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '6px 12px', borderRadius: 10, cursor: 'pointer',
              background: dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)',
              border: dark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
              color: dark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)',
              fontSize: 12, fontWeight: 500,
            }}
          >
            <ArrowLeft size={13} />
            Mes workflows
          </button>
          {workflowName && (
            <div style={{
              background: dark ? 'rgba(139,92,246,0.12)' : 'rgba(139,92,246,0.08)',
              border: '1px solid rgba(139,92,246,0.3)',
              borderRadius: 10,
              padding: '6px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              <Workflow size={13} style={{ color: '#8b5cf6' }} />
              <span style={{ color: dark ? 'rgba(167,139,250,0.9)' : '#7c3aed', fontSize: 13, fontWeight: 600 }}>
                {workflowName}
              </span>
            </div>
          )}
        </div>

        {/* toolbar */}
        <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
          <button
            onClick={deleteSelected}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium border transition-all duration-200
              ${dark
                ? 'bg-red-500/8 border-red-500/20 text-red-400/70 hover:text-red-400'
                : 'bg-red-50 border-red-200 text-red-500 hover:text-red-600 hover:border-red-300'}`}
          >
            <Trash2 size={13} />
            Supprimer
          </button>
          <button
            onClick={saveWorkflow}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-violet-600 hover:bg-violet-500 transition-all duration-200"
          >
            <Save size={13} />
            Sauvegarder
          </button>

          <button
            onClick={() => {
              const agentNodes = nodes.filter(n => n.type === 'agent')
              if (agentNodes.length < 2) {
                showToast('Ajoutez au moins 2 agents spécialisés avant d\'exécuter.')
                return
              }
              
              const draft = JSON.parse(localStorage.getItem('workflow_draft') || 'null')
              const id_workflow = draft?.id_workflow || null

              localStorage.setItem('workflow_execution', JSON.stringify({
                id_workflow,
                nodes,
                edges
              }))

              navigate('/workflow/execute')
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-green-600 hover:bg-green-500 transition-all duration-200"
          >
            <Play size={13} />
            Exécuter
          </button>

        </div>

        {/* toast */}
        {toast && (
          <div
            className="absolute top-16 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium shadow-lg"
            style={{
              background: dark ? 'rgba(20,20,20,0.95)' : 'rgba(255,255,255,0.97)',
              border: dark ? '1px solid rgba(255,255,255,0.12)' : '1px solid rgba(0,0,0,0.1)',
              color: dark ? 'rgba(255,255,255,0.85)' : 'rgba(0,0,0,0.75)',
              backdropFilter: 'blur(12px)',
            }}
          >
            <AlertCircle size={14} style={{ color: '#8b5cf6' }} />
            {toast}
          </div>
        )}

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={nodeTypes}
          fitView
          style={{ background: canvasBg }}
          defaultEdgeOptions={{
            animated: true,
            style: { stroke: '#8b5cf6', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' },
          }}
        >
          <Background color={bgColor} gap={24} size={1} />
          <Controls
            style={{
              background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.9)',
              border: dark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.1)',
            }}
          />
          <MiniMap
            style={{
              background: dark ? 'rgba(8,8,8,0.9)' : 'rgba(255,255,255,0.9)',
              border: dark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.1)',
            }}
            nodeColor={(n) => n.type === 'supervisor' ? '#8b5cf6' : (dark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)')}
          />
        </ReactFlow>
      </div>
    </div>
  )
}
function WorkflowNameModal({ dark, onConfirm, onCancel }) {
  const [name, setName] = useState('')
  const [error, setError] = useState(false)

  const handleConfirm = () => {
    if (!name.trim()) {
      setError(true)
      return
    }
    onConfirm(name.trim())
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 50,
      background: 'rgba(0,0,0,0.7)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      backdropFilter: 'blur(4px)',
    }}>
      <div style={{
        background: dark ? '#111' : '#fff',
        border: `1px solid ${dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
        borderRadius: 16,
        padding: '32px',
        width: '100%',
        maxWidth: 420,
      }}>
        <h2 style={{ color: dark ? 'white' : '#111', fontSize: 18, fontWeight: 700, marginBottom: 6 }}>
          Nommer le workflow
        </h2>
        <p style={{ color: dark ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.45)', fontSize: 13, marginBottom: 20 }}>
          Donnez un nom avant de commencer.
        </p>
        <input
          autoFocus
          type="text"
          placeholder="Ex: Workflow analyse de données"
          value={name}
          onChange={e => { setName(e.target.value); setError(false) }}
          onKeyDown={e => e.key === 'Enter' && handleConfirm()}
          style={{
            width: '100%', padding: '10px 14px', borderRadius: 10,
            background: dark ? 'rgba(255,255,255,0.05)' : '#f9f9f9',
            border: error ? '1px solid #ef4444' : `1px solid ${dark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.15)'}`,
            color: dark ? 'white' : '#111',
            fontSize: 14, outline: 'none', boxSizing: 'border-box',
            marginBottom: error ? 6 : 20,
          }}
        />
        {error && (
          <p style={{ color: '#ef4444', fontSize: 12, marginBottom: 16 }}>
            Veuillez entrer un nom.
          </p>
        )}
        <button
          onClick={onCancel}
          style={{
            width: '100%', padding: '11px', borderRadius: 10,
            background: 'transparent',
            color: dark ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.4)',
            fontWeight: 500, fontSize: 14,
            border: `1px solid ${dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
            cursor: 'pointer', marginBottom: 8,
          }}
        >
          Annuler
        </button>

        <button
          onClick={handleConfirm}
          style={{
            width: '100%', padding: '11px', borderRadius: 10,
            background: '#7c3aed', color: 'white', fontWeight: 600,
            fontSize: 14, border: 'none', cursor: 'pointer',
          }}
        >
          Créer le workflow
        </button>
      </div>
    </div>
  )
}

/* ─────────────────────────── page wrapper ───────────────────────── */

export default function CreatWorkflowPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [agents, setAgents] = useState([])
  const { dark } = useTheme()
  const [workflowName, setWorkflowName] = useState(null)
  const [workflowId, setWorkflowId] = useState(null)
  const [initialNodes, setInitialNodes] = useState(null)
  const [initialEdges, setInitialEdges] = useState(null)

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (user) {
      fetch(`http://localhost:8000/agents/${user.user_id}`)
        .then(r => r.json())
        .then(data => {
          if (Array.isArray(data)) {
            setAgents(data.map(a => ({
              id: String(a.id_agent ?? a.id ?? ''),
              name: a.nom,
              role: a.role || '',
              model: a.modele,
              systemPrompt: a.system_prompt || '',
              temperature: a.temperature,
              maxTokens: a.max_tokens,
              webSearch: a.web_search || false,
              generateDocument: a.generate_document || false,
              mcp_type: a.mcp_type || '',
            })))
          }
        })
        .catch(() => setAgents([]))
    } else {
      setAgents(JSON.parse(localStorage.getItem('local_agents') || '[]'))
    }
  }, [])

  useEffect(() => {
    if (!id) return
    const user = JSON.parse(localStorage.getItem('user') || 'null')

    if (!user || String(id).startsWith('local-')) {
      // ── Mode localStorage ─────────────────────────────────────────
      const local = JSON.parse(localStorage.getItem('local_workflows') || '[]')
      const wf = local.find(w => String(w.id_workflow) === String(id))
      if (!wf) { navigate('/workflow'); return }
      setWorkflowName(wf.nom)
      setWorkflowId(wf.id_workflow)
      const graphe = wf.donnees_graphe_json || {}
      setInitialNodes(graphe.nodes?.length ? graphe.nodes : [initialSupervisorNode])
      setInitialEdges(graphe.edges || [])
      return
    }

    // ── Mode API (connecté) ───────────────────────────────────────
    fetch(`http://localhost:8000/workflows/${id}`)
      .then(r => r.json())
      .then(data => {
        setWorkflowName(data.nom)
        setWorkflowId(data.id_workflow)
        const graphe = typeof data.donnees_graphe_json === 'string'
          ? JSON.parse(data.donnees_graphe_json)
          : (data.donnees_graphe_json || {})
        setInitialNodes(graphe.nodes?.length ? graphe.nodes : [initialSupervisorNode])
        setInitialEdges(graphe.edges || [])
      })
      .catch(() => navigate('/workflow'))
  }, [id])

  const isReady = workflowName !== null

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white font-body transition-colors duration-300">
      <NavBar />
      {!workflowName && !id && (
        <WorkflowNameModal
          dark={dark}
          onConfirm={(name) => setWorkflowName(name)}
          onCancel={() => navigate('/workflow')}
        />
      )}

      {isReady && (
      <div style={{ paddingTop: 68 }}>
        <ReactFlowProvider>
          <FlowCanvas
            agents={agents}
            dark={dark}
            workflowName={workflowName || ''}
            workflowId={workflowId}
            initialNodes={initialNodes ?? [initialSupervisorNode]}
            initialEdges={initialEdges ?? []}
          />
        </ReactFlowProvider>
      </div>
      )}
    </div>
  )
}
