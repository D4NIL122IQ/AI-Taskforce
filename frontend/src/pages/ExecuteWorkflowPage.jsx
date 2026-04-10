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
import NavBar from '../components/layout/NavBar'
import PageBackground from '../components/layout/PageBackground'
import { useTheme } from '../context/ThemeContext'
import { Bot, Crown, Send, CheckCircle, GitBranch, FileText, Globe, LogIn, LogOut } from 'lucide-react'

/* ─────────────────────────── helpers localStorage ──────────────────── */

const loadWorkflow = () => {
  try { return JSON.parse(localStorage.getItem('workflow_execution') || localStorage.getItem('workflow_draft') || 'null') } catch { return null }
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
    <Handle type="target" position={Position.Top} style={{ background: '#8b5cf6', border: '2px solid #080808', width: 10, height: 10 }} />
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
      <Handle type="source" position={Position.Top} style={{ background: '#8b5cf6', width: 10, height: 10 }} />
      <Handle type="target" position={Position.Bottom} style={{ background: '#8b5cf6', width: 10, height: 10 }} />
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

const nodeTypes = {
  supervisor: SupervisorNodeExec,
  agent:      AgentNodeExec,
  condition:  ConditionNodeExec,
  document:   DocumentNodeExec,
  webSearch:  WebSearchNodeExec,
  entry:      EntryNodeExec,
  exit:       ExitNodeExec,
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

/* ─────────────────────────── message chat ──────────────────────────── */

const ChatMessage = ({ msg }) => {
  if (msg.role === 'user') return (
    <div className="flex justify-end">
      <div className="max-w-[80%] px-4 py-2.5 rounded-2xl rounded-br-sm text-sm text-white"
        style={{ background: 'rgba(139,92,246,0.5)', border: '1px solid rgba(139,92,246,0.4)' }}>
        {msg.content}
      </div>
    </div>
  )

  if (msg.role === 'result') return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2 px-1">
        <CheckCircle size={12} style={{ color: '#34d399' }} />
        <span className="text-xs" style={{ color: '#34d399' }}>Résultat final</span>
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm text-sm text-gray-800 dark:text-white leading-relaxed whitespace-pre-wrap"
        style={{ background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)' }}>
        {msg.content}
      </div>
    </div>
  )

  if (msg.role === 'supervisor') return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2 px-1">
        <Crown size={11} style={{ color: '#a78bfa' }} />
        <span className="text-xs font-medium" style={{ color: '#a78bfa' }}>{msg.name}</span>
      </div>
      <div className="px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm leading-relaxed text-gray-700 dark:text-white/75"
        style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)' }}>
        {msg.content}
      </div>
    </div>
  )

  if (msg.role === 'agent') return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2 px-1">
        <Bot size={11} className="text-gray-500 dark:text-white/40" />
        <span className="text-xs font-medium text-gray-500 dark:text-white/40">{msg.agent}</span>
      </div>
      <div className="px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm leading-relaxed text-gray-700 dark:text-white/75 bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10">
        {msg.content}
      </div>
    </div>
  )

  return (
    <div className="px-4 py-1 text-xs text-center text-gray-400 dark:text-white/25">
      {msg.content}
    </div>
  )
}

/* ─────────────────────────── page principale ───────────────────────── */

const ExecuteWorkflowPage = () => {
  const navigate = useNavigate()
  const { dark } = useTheme()
  const workflow = loadWorkflow()

  const [prompt, setPrompt]               = useState('')
  const [messages, setMessages]           = useState([])
  const [running, setRunning]             = useState(false)
  const [activeNodeId, setActiveNodeId]   = useState(null)
  const [nodeStatuses, setNodeStatuses]   = useState({})
  const chatBottomRef = useRef(null)

  const agentNodes   = workflow?.nodes.filter(n => n.type === 'agent') || []
  const supervisorNode = workflow?.nodes.find(n => n.type === 'supervisor')

  const addMsg = (msg) => setMessages(prev => [...prev, msg])

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

const handleSend = async () => {
    if (!prompt.trim() || running || !workflow) return
    const userPrompt = prompt
    setPrompt('')
    setRunning(true)
    setMessages([])
    setNodeStatuses({})

    addMsg({ role: 'user', content: userPrompt })
    addMsg({ role: 'system', content: "Workflow en cours d'exécution..." })
    setActiveNodeId(supervisorNode?.id)

    try {
      const res = await fetch('http://localhost:8000/executions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: typeof workflow.id_workflow === 'number' ? workflow.id_workflow : null,
          prompt: userPrompt,
          nodes: workflow.nodes,
          niveau_recherche: 1,
        }),
      })
      console.log(workflow.id_workflow)

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || 'Erreur serveur')
      }

      // Lecture ligne par ligne du stream
      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const lines = decoder.decode(value).split('\n').filter(l => l.trim())
        for (const line of lines) {
          try {
            const data = JSON.parse(line)

            if (data.type === 'echange') {
              const agentNode = agentNodes.find(n => n.data.label === data.agent)
              if (agentNode) {
                setNodeStatuses(s => ({ ...s, [agentNode.id]: 'TERMINE' }))
              }
              addMsg({ role: 'agent', agent: data.agent, content: data.content })
            }

            if (data.type === 'supervisor') {
                addMsg({ role: 'supervisor', name: 'Superviseur', content: data.content })
            }

            if (data.type === 'final') {
              setActiveNodeId(null)
              addMsg({ role: 'result', content: data.response })
            }

            if (data.type === 'error') {
              throw new Error(data.message)
            }

          } catch (e) {
            console.error('Parse error:', e)
          }
        }
      }

    } catch (err) {
      setActiveNodeId(null)
      addMsg({ role: 'result', content: `Erreur : ${err.message}` })
    }

    setRunning(false)
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

          {/* Chat */}
          <div className="w-[380px] flex-shrink-0 flex flex-col" style={{ background: dark ? 'rgba(8,8,8,0.95)' : 'rgba(255,255,255,0.95)' }}>

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
            <div className="px-4 py-4 border-t border-gray-200 dark:border-white/[0.06] flex gap-2 items-end">
              <textarea
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
                rows={2}
                placeholder="Entrez votre demande..."
                disabled={running}
                className="flex-1 resize-none bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl px-3 py-2.5 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/30 focus:outline-none focus:border-violet-400 transition-colors"
              />
              <button
                onClick={handleSend}
                disabled={!prompt.trim() || running}
                className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <Send size={15} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExecuteWorkflowPage
