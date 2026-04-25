import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import NavBar from '../components/layout/NavBar'
import PageBackground from '../components/layout/PageBackground'
import { useTheme } from '../context/ThemeContext'
import { useExecution } from '../context/ExecutionContext'
import { Bot, Crown, Send, CheckCircle, GitBranch, FileText, Globe, LogIn, LogOut, AlertTriangle, Square, Mail } from 'lucide-react'

const GithubGlyph = ({ size = 12, color = 'currentColor' }) => (
  <svg viewBox="0 0 24 24" fill={color} width={size} height={size}>
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
  </svg>
)

/* ─────────────────────────── helpers localStorage ──────────────────── */

const loadWorkflow = () => {
  try { return JSON.parse(localStorage.getItem('workflow_execution') || localStorage.getItem('workflow_draft') || 'null') } catch { return null }
}

const loadUserId = () => {
  try { return JSON.parse(localStorage.getItem('user') || 'null')?.user_id || null } catch { return null }
}

/* ─────────────────────────── nœuds lecture seule ───────────────────── */

const SupervisorNodeExec = ({ data }) => (
  <div className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border transition-all duration-200"
    style={{
      background: data.active ? 'rgba(139,92,246,0.3)' : 'rgba(139,92,246,0.12)',
      borderColor: data.active ? '#8b5cf6' : 'rgba(139,92,246,0.45)',
      boxShadow: data.active ? '0 0 0 2px #8b5cf6, 0 0 24px rgba(139,92,246,0.5)' : '0 0 16px rgba(139,92,246,0.15)',
      minWidth: 160,
    }}>
    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(139,92,246,0.25)', border: '1px solid rgba(139,92,246,0.5)' }}>
      <Crown size={20} style={{ color: '#a78bfa' }} />
    </div>
    <p className="text-sm font-semibold text-gray-900 dark:text-white">{data.label}</p>
    <p className="text-xs" style={{ color: 'rgba(139,92,246,0.9)' }}>Superviseur</p>
    {data.model && <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(139,92,246,0.15)', color: 'rgba(167,139,250,0.8)', border: '1px solid rgba(139,92,246,0.2)' }}>{data.model}</span>}
    <Handle type="source" position={Position.Bottom} style={{ background: '#8b5cf6', border: '2px solid #080808', width: 10, height: 10 }} />
  </div>
)

const AgentNodeExec = ({ data }) => {
  const d = data.dark
  return (
    <div style={{
      display:'flex', flexDirection:'column', alignItems:'center', gap:6,
      padding:'12px 16px', borderRadius:16,
      border: `1px solid ${data.active ? '#8b5cf6' : d ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)'}`,
      background: data.active ? 'rgba(139,92,246,0.15)' : d ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
      boxShadow: data.active ? '0 0 0 2px #8b5cf6' : 'none',
      minWidth: 150, transition:'all 0.3s',
    }}>
      <div style={{
        width:36, height:36, borderRadius:10,
        background: d ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)',
        border: `1px solid ${d ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
        display:'flex', alignItems:'center', justifyContent:'center',
      }}>
        <Bot size={18} style={{ color: d ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.45)' }} />
      </div>
      <p style={{ fontSize:13, fontWeight:600, color: d ? 'white' : '#111827', margin:0 }}>{data.label}</p>
      <p style={{ fontSize:11, color: d ? 'rgba(255,255,255,0.35)' : 'rgba(0,0,0,0.4)', margin:0 }}>{data.role || 'Agent'}</p>
      {data.model && <span style={{
        fontSize:10, padding:'2px 8px', borderRadius:99,
        background: d ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
        color: d ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.4)',
        border: `1px solid ${d ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
      }}>{data.model}</span>}
      {data.status && (
        <span style={{
          fontSize:10, padding:'2px 8px', borderRadius:99, marginTop:2,
          background: data.status === 'TERMINE' ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)',
          color: data.status === 'TERMINE' ? '#34d399' : '#fbbf24',
          border: `1px solid ${data.status === 'TERMINE' ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'}`,
        }}>
          {data.status === 'TERMINE' ? '✓ Terminé' : '⟳ En cours'}
        </span>
      )}
      <Handle type="target" position={Position.Top} style={{ background: '#8b5cf6', width: 10, height: 10 }} />
      <Handle type="source" id="mcp" position={Position.Right} style={{ background: 'transparent', border: 'none', width: 1, height: 1, top: '50%' }} />
    </div>
  )
}

const ConditionNodeExec = ({ data }) => (
  <div className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border" style={{ background: 'rgba(245,158,11,0.08)', borderColor: 'rgba(245,158,11,0.3)', minWidth: 140 }}>
    <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.4)' }}><GitBranch size={18} style={{ color: '#f59e0b' }} /></div>
    <p className="text-sm font-semibold text-gray-900 dark:text-white">{data.label || 'Condition'}</p>
    <Handle type="target" position={Position.Top} style={{ background: '#f59e0b', width: 10, height: 10 }} />
    <Handle type="source" position={Position.Bottom} style={{ background: '#f59e0b', width: 10, height: 10 }} />
  </div>
)

const DocumentNodeExec = ({ data }) => (
  <div className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border" style={{ background: 'rgba(16,185,129,0.08)', borderColor: 'rgba(16,185,129,0.3)', minWidth: 140 }}>
    <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.4)' }}><FileText size={18} style={{ color: '#10b981' }} /></div>
    <p className="text-sm font-semibold text-gray-900 dark:text-white">{data.label || 'Document'}</p>
    <Handle type="target" position={Position.Top} style={{ background: '#10b981', width: 10, height: 10 }} />
    <Handle type="source" position={Position.Bottom} style={{ background: '#10b981', width: 10, height: 10 }} />
  </div>
)

const WebSearchNodeExec = ({ data }) => (
  <div className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border" style={{ background: 'rgba(236,72,153,0.08)', borderColor: 'rgba(236,72,153,0.3)', minWidth: 140 }}>
    <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(236,72,153,0.15)', border: '1px solid rgba(236,72,153,0.4)' }}><Globe size={18} style={{ color: '#ec4899' }} /></div>
    <p className="text-sm font-semibold text-gray-900 dark:text-white">{data.label || 'Recherche web'}</p>
    <Handle type="target" position={Position.Top} style={{ background: '#ec4899', width: 10, height: 10 }} />
    <Handle type="source" position={Position.Bottom} style={{ background: '#ec4899', width: 10, height: 10 }} />
  </div>
)

const EntryNodeExec = ({ data }) => (
  <div className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border" style={{ background: 'rgba(99,102,241,0.08)', borderColor: 'rgba(99,102,241,0.3)', minWidth: 140 }}>
    <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.4)' }}><LogIn size={18} style={{ color: '#6366f1' }} /></div>
    <p className="text-sm font-semibold text-gray-900 dark:text-white">{data.label || 'Entrée'}</p>
    <Handle type="source" position={Position.Bottom} style={{ background: '#6366f1', width: 10, height: 10 }} />
  </div>
)

const ExitNodeExec = ({ data }) => (
  <div className="flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border" style={{ background: 'rgba(239,68,68,0.08)', borderColor: 'rgba(239,68,68,0.3)', minWidth: 140 }}>
    <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)' }}><LogOut size={18} style={{ color: '#ef4444' }} /></div>
    <p className="text-sm font-semibold text-gray-900 dark:text-white">{data.label || 'Sortie'}</p>
    <Handle type="target" position={Position.Top} style={{ background: '#ef4444', width: 10, height: 10 }} />
  </div>
)

const MCP_META_EXEC = {
  github: { label: 'GitHub', accent: '#f0f6fc', accentLight: '#24292f' },
  gmail:  { label: 'Gmail',  accent: '#f28b82', accentLight: '#ea4335' },
}

const McpNodeExec = ({ data }) => {
  const key = data.mcp_type in MCP_META_EXEC ? data.mcp_type : 'github'
  const meta = MCP_META_EXEC[key]
  const d = data.dark
  const glyphColor = d ? meta.accent : meta.accentLight
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 6,
      padding: '6px 10px', borderRadius: 10,
      border: `1px solid ${d ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)'}`,
      background: d ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
      minWidth: 90,
    }}>
      {key === 'gmail'
        ? <Mail size={12} style={{ color: glyphColor }} />
        : <GithubGlyph size={12} color={glyphColor} />}
      <span style={{ fontSize: 11, fontWeight: 500, color: d ? 'rgba(255,255,255,0.75)' : 'rgba(0,0,0,0.7)' }}>{meta.label}</span>
      <Handle type="target" position={Position.Left} style={{ background: glyphColor, width: 8, height: 8 }} />
    </div>
  )
}

const nodeTypes = {
  supervisor: SupervisorNodeExec,
  agent:      AgentNodeExec,
  condition:  ConditionNodeExec,
  document:   DocumentNodeExec,
  webSearch:  WebSearchNodeExec,
  entry:      EntryNodeExec,
  exit:       ExitNodeExec,
  mcp:        McpNodeExec,
}

/* ─────────────────────────── canvas animé ──────────────────────────── */

function ExecutionCanvas({ workflow, activeNodeId, nodeStatuses, dark }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(workflow?.nodes || [])
  const [edges, setEdges, onEdgesChange] = useEdgesState(workflow?.edges || [])

  useEffect(() => {
    if (!workflow) return
    setNodes(workflow.nodes.map(n => ({
      ...n,
      data: {
        ...n.data,
        active: n.id === activeNodeId,
        status: nodeStatuses[n.id] || null,
        dark: dark,
      },
    })))
    setEdges(workflow.edges.map(e => ({
      ...e,
      animated: e.source === activeNodeId || e.target === activeNodeId,
      style: {
        stroke: e.source === activeNodeId || e.target === activeNodeId ? '#8b5cf6' : (dark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.15)'),
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: e.source === activeNodeId || e.target === activeNodeId ? '#8b5cf6' : (dark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.15)'),
      },
    })))
  }, [activeNodeId, nodeStatuses, workflow])

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      fitView
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
      style={{ background: dark ? '#080808' : '#f3f4f6' }}
    >
      <Background color={dark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.04)"} gap={24} size={1} />
    </ReactFlow>
  )
}

/* ─────────────────────────── rendu markdown ────────────────────────── */

const mdComponents = {
  h1: ({ children }) => <h1 className="text-xl font-bold mt-4 mb-2 text-gray-900 dark:text-white">{children}</h1>,
  h2: ({ children }) => <h2 className="text-lg font-semibold mt-3 mb-1.5 text-gray-900 dark:text-white">{children}</h2>,
  h3: ({ children }) => <h3 className="text-base font-semibold mt-2 mb-1 text-gray-800 dark:text-white/90">{children}</h3>,
  p:  ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-0.5">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-0.5">{children}</ol>,
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold text-gray-900 dark:text-white">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  code: ({ inline, children }) => inline
    ? <code className="px-1.5 py-0.5 rounded text-xs font-mono bg-black/10 dark:bg-white/10 text-violet-700 dark:text-violet-300">{children}</code>
    : <pre className="my-2 p-3 rounded-xl overflow-x-auto text-xs font-mono bg-black/10 dark:bg-white/10 text-gray-800 dark:text-white/80"><code>{children}</code></pre>,
  blockquote: ({ children }) => <blockquote className="pl-3 border-l-2 border-violet-400/50 italic text-gray-600 dark:text-white/60 my-2">{children}</blockquote>,
  hr: () => <hr className="my-3 border-gray-200 dark:border-white/10" />,
}

const MarkdownContent = ({ content }) => (
  <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
    {content}
  </ReactMarkdown>
)

/* ─────────────────────────── message chat ──────────────────────────── */

const ChatMessage = ({ msg }) => {
  if (msg.role === 'user') return (
    <div className="flex justify-end">
      <div className="max-w-[85%] px-4 py-3 rounded-2xl rounded-br-sm text-base text-white"
        style={{ background: 'rgba(139,92,246,0.5)', border: '1px solid rgba(139,92,246,0.4)' }}>
        {msg.content}
      </div>
    </div>
  )

  if (msg.role === 'result') return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-2 px-1">
        <CheckCircle size={13} style={{ color: '#34d399' }} />
        <span className="text-sm font-medium" style={{ color: '#34d399' }}>Résultat final</span>
      </div>
      <div className="px-5 py-4 rounded-2xl rounded-tl-sm text-base text-gray-800 dark:text-white/90 leading-relaxed"
        style={{ background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)' }}>
        <MarkdownContent content={msg.content} />
      </div>
    </div>
  )

  if (msg.role === 'supervisor') return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-2 px-1">
        <Crown size={12} style={{ color: '#a78bfa' }} />
        <span className="text-sm font-medium" style={{ color: '#a78bfa' }}>{msg.name}</span>
      </div>
      <div className="px-5 py-3 rounded-2xl rounded-tl-sm text-base leading-relaxed text-gray-700 dark:text-white/75"
        style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)' }}>
        <MarkdownContent content={msg.content} />
      </div>
    </div>
  )

  if (msg.role === 'agent') return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-2 px-1">
        <Bot size={12} className="text-gray-500 dark:text-white/40" />
        <span className="text-sm font-medium text-gray-500 dark:text-white/40">{msg.agent}</span>
      </div>
      <div className="px-5 py-3 rounded-2xl rounded-tl-sm text-base leading-relaxed text-gray-700 dark:text-white/75 bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10">
        <MarkdownContent content={msg.content} />
      </div>
    </div>
  )

  if (msg.role === 'document') return (
  <div className="flex flex-col gap-1.5">
    <div className="flex items-center gap-2 px-1">
      <FileText size={12} style={{ color: '#10b981' }} />
      <span className="text-sm font-medium" style={{ color: '#10b981' }}>
        Document généré par {msg.agent}
      </span>
    </div>

    <a
      href={`http://localhost:8000/executions/documents/download/${msg.filename}`}
      download
      className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all hover:scale-[1.02]"
      style={{
        background: 'rgba(16,185,129,0.12)',
        border: '1px solid rgba(16,185,129,0.3)'
      }}
    >
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center"
        style={{
          background: 'rgba(16,185,129,0.2)',
          border: '1px solid rgba(16,185,129,0.4)'
        }}
      >
        <FileText size={18} style={{ color: '#10b981' }} />
      </div>

      <div className="flex-1">
        <p className="text-sm font-medium text-gray-800 dark:text-white">
          {msg.filename}
        </p>
        <p className="text-xs text-gray-500 dark:text-white/40">
          📥 Cliquer pour télécharger
        </p>
      </div>
    </a>
  </div>
)   
  if (msg.role === 'warning') return (
    <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl"
      style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)' }}>
      <AlertTriangle size={14} className="shrink-0 mt-0.5" style={{ color: '#f59e0b' }} />
      <span className="text-sm leading-snug" style={{ color: '#fbbf24' }}>{msg.content}</span>
    </div>
  )

  return (
    <div className="px-4 py-1 text-sm text-center text-gray-400 dark:text-white/25">
      {msg.content}
    </div>
  )
}

/* ─────────────────────────── page principale ───────────────────────── */

const ExecuteWorkflowPage = () => {
  const navigate = useNavigate()
  const { dark } = useTheme()
  const workflow = loadWorkflow()
  const utilisateurId = loadUserId()

  // État de l'exécution partagé via contexte global
  const {
    executionId, setExecutionId,
    isRunning, setIsRunning,
    messages, setMessages, addMsg,
    activeNodeId, setActiveNodeId,
    nodeStatuses, setNodeStatuses,
    controllerRef,
  } = useExecution()

  const [prompt, setPrompt]           = useState('')
  const [chatWidth, setChatWidth]     = useState(520)
  const [niveauRecherche, setNiveauRecherche] = useState(1)
  const chatBottomRef  = useRef(null)
  const isDragging     = useRef(false)
  const dragStartX     = useRef(0)
  const dragStartWidth = useRef(520)

  const CHAT_MIN = 340
  const CHAT_MAX = 900

  const onDragStart = (e) => {
    isDragging.current     = true
    dragStartX.current     = e.clientX
    dragStartWidth.current = chatWidth
    document.body.style.cursor    = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  useEffect(() => {
    const onMove = (e) => {
      if (!isDragging.current) return
      const delta = dragStartX.current - e.clientX
      setChatWidth(Math.min(CHAT_MAX, Math.max(CHAT_MIN, dragStartWidth.current + delta)))
    }
    const onUp = () => {
      if (!isDragging.current) return
      isDragging.current = false
      document.body.style.cursor    = ''
      document.body.style.userSelect = ''
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp) }
  }, [])

  const agentNodes     = workflow?.nodes.filter(n => n.type === 'agent') || []
  const supervisorNode = workflow?.nodes.find(n => n.type === 'supervisor')

  // Charge le détail d'une exécution passée depuis le Dashboard
  useEffect(() => {
    const raw = localStorage.getItem('execution_detail')
    if (!raw) return
    try {
      const detail = JSON.parse(raw)
      localStorage.removeItem('execution_detail')
      const msgs = []
      if (detail.prompt) msgs.push({ role: 'user', content: detail.prompt })
      if (detail.echanges) {
        Object.entries(detail.echanges).forEach(([agent, reponse]) => {
          msgs.push({ role: 'agent', agent, content: reponse })
        })
      }
      if (detail.reponse_finale) {
        msgs.push({ role: 'result', content: detail.reponse_finale })
      }
      setMessages(msgs)
    } catch (e) {
      console.error('Erreur chargement détail:', e)
    }
  }, [])

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // ── Lit le stream SSE et alimente les messages ───────────────────────────────
  const listenToStream = async (execId, controller) => {
    const res = await fetch(`http://localhost:8000/executions/stream/${execId}`, {
      signal: controller.signal,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Erreur stream')
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const lines = decoder.decode(value).split('\n').filter(l => l.trim())
      for (const line of lines) {
        try {
          const data = JSON.parse(line)
          if (data.type === 'warning') {
            addMsg({ role: 'warning', content: data.message })
          }
          if (data.type === 'supervisor') {
            setActiveNodeId(supervisorNode?.id)
            addMsg({ role: 'supervisor', name: 'Superviseur', content: data.content })
          }
          if (data.type === 'echange') {
            const agentNode = agentNodes.find(n => n.data.label === data.agent)
            if (agentNode) {
              setActiveNodeId(agentNode.id)
              setNodeStatuses(s => ({ ...s, [agentNode.id]: 'TERMINE' }))
            }
            addMsg({ role: 'agent', agent: data.agent, content: data.content })
          }
          if (data.type === 'final') {
            setActiveNodeId(null)
            setMessages(prev => {
              const hasDocument = prev.some(m => m.role === 'document')
              if (hasDocument) return prev
              return [...prev, { role: 'result', content: data.response }]
            })
          }
          if (data.type === 'document') {
            addMsg({ role: 'document', agent: data.agent, filename: data.filename })
          }
          if (data.type === 'error') {
            throw new Error(data.message)
          }
        } catch (e) {
          console.error('Parse error:', e)
        }
      }
    }
  }

  const handleSend = async () => {
    if (!prompt.trim() || isRunning || !workflow) return
    const userPrompt = prompt
    setPrompt('')
    setIsRunning(true)
    setMessages([])
    setNodeStatuses({})

    addMsg({ role: 'user', content: userPrompt })
    addMsg({ role: 'system', content: "Workflow en cours d'exécution..." })
    setActiveNodeId(supervisorNode?.id)

    try {
      // 1. Lancer l'exécution → le thread démarre en arrière-plan, retourne l'execution_id
      const res = await fetch('http://localhost:8000/executions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: workflow.id_workflow,
          prompt: userPrompt,
          nodes: workflow.nodes,
          niveau_recherche: niveauRecherche,
          utilisateur_id: utilisateurId,
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || 'Erreur serveur')
      }
      const { execution_id: execId } = await res.json()
      setExecutionId(execId)

      // 2. Se connecter au stream (le contexte garde isRunning=true → bouton NavBar visible)
      const controller = new AbortController()
      controllerRef.current = controller
      await listenToStream(execId, controller)

    } catch (err) {
      if (err.name === 'AbortError') {
        addMsg({ role: 'system', content: "Exécution interrompue." })
        setIsRunning(false)
        return
      }
      setActiveNodeId(null)
      addMsg({ role: 'result', content: `Erreur : ${err.message}` })
    }

    setIsRunning(false)
  }

  /* Arrêt du workflow */
  const stopExecution = async () => {
    if (controllerRef.current) {
      controllerRef.current.abort()
    }
    if (executionId) {
      await fetch(`http://localhost:8000/executions/stop/${executionId}`, { method: 'POST' })
    }
    setIsRunning(false)
    setActiveNodeId(null)
  }

  /* Pas de workflow */
  if (!workflow) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white font-body transition-colors duration-300">
        <PageBackground />
        <NavBar />
        <main className="max-w-xl mx-auto px-6 pt-[120px] pb-24 flex flex-col items-center gap-6 text-center">
          <p className="text-white/50 text-sm">Aucun workflow sauvegardé.</p>
          <button onClick={() => navigate('/workflow')}
            className="px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors">
            Créer un workflow
          </button>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white font-body transition-colors duration-300">
      <PageBackground />
      <NavBar />

      <div style={{ paddingTop: 68, height: '100vh', display: 'flex', flexDirection: 'column' }}>



        {/* Corps */}
        <div className="flex flex-1 overflow-hidden">

          {/* Canvas */}
          <div className="flex-1 border-r border-gray-200 dark:border-white/[0.06]">
            <ReactFlowProvider>
              <ExecutionCanvas
                workflow={workflow}
                activeNodeId={activeNodeId}
                nodeStatuses={nodeStatuses}
                dark={dark}
              />
            </ReactFlowProvider>
          </div>

          {/* Drag handle */}
          <div
            onMouseDown={onDragStart}
            style={{
              width: 6,
              flexShrink: 0,
              cursor: 'col-resize',
              background: 'transparent',
              position: 'relative',
              zIndex: 10,
              transition: 'background 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(139,92,246,0.35)'}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            title="Glisser pour redimensionner"
          />

          {/* Chat */}
          <div
            className="flex-shrink-0 flex flex-col"
            style={{ width: chatWidth, background: dark ? 'rgba(8,8,8,0.95)' : 'rgba(255,255,255,0.95)' }}
          >

            <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
                  <div className="w-12 h-12 rounded-2xl flex items-center justify-center"
                    style={{ background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)' }}>
                    <Send size={18} style={{ color: '#a78bfa' }} />
                  </div>
                  <p className="text-gray-400 dark:text-white/35 text-sm">Entrez votre demande<br />pour démarrer le workflow</p>
                </div>
              )}
              {messages.map((msg, i) => <ChatMessage key={i} msg={msg} />)}
              <div ref={chatBottomRef} />
            </div>

            {/* Input */}
            <div className="px-4 py-4 border-t border-gray-200 dark:border-white/[0.06] flex flex-col gap-2">
              {/* Niveau de recherche */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 dark:text-white/35 shrink-0">Niveau :</span>
                <div className="flex gap-1">
                  {[
                    { value: 1, label: 'Rapide',    desc: '1 appel LLM par tâche' },
                    { value: 2, label: 'Moyen',     desc: '2 appels LLM par tâche' },
                    { value: 3, label: 'Réflexion', desc: '3 appels LLM par tâche' },
                  ].map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setNiveauRecherche(opt.value)}
                      title={opt.desc}
                      className="px-3 py-1 rounded-lg text-xs font-medium transition-all"
                      style={{
                        background: niveauRecherche === opt.value ? 'rgba(139,92,246,0.25)' : 'transparent',
                        border: `1px solid ${niveauRecherche === opt.value ? 'rgba(139,92,246,0.6)' : 'rgba(139,92,246,0.15)'}`,
                        color: niveauRecherche === opt.value ? '#a78bfa' : (dark ? 'rgba(255,255,255,0.35)' : 'rgba(0,0,0,0.4)'),
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex gap-2 items-end">
                <textarea
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
                  rows={5}
                  placeholder="Entrez votre demande..."
                  disabled={isRunning}
                  className="flex-1 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 text-base text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/30 focus:outline-none focus:border-violet-400 transition-colors"
                  style={{ resize: 'vertical', minHeight: 96, maxHeight: 320 }}
                />
                {isRunning ? (
                  <button
                    onClick={stopExecution}
                    className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl bg-red-600 hover:bg-red-500 transition-colors"
                  >
                    <Square size={15} />
                  </button>
                ) : (
                  <button
                    onClick={handleSend}
                    disabled={!prompt.trim()}
                    className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send size={15} />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExecuteWorkflowPage
