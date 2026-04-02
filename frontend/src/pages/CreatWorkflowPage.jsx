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
import { useNavigate } from 'react-router-dom'
import { Bot, Crown, Trash2, Plus, Save, AlertCircle,Play  } from 'lucide-react'

/* ─────────────────────────── helpers ────────────────────────────── */

const loadAgents = () => {
  try { return JSON.parse(localStorage.getItem('agents') || '[]') } catch { return [] }
}

const SUPERVISOR_ID = 'supervisor-0'

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
    <Handle type="target" position={Position.Top} style={{ background: '#8b5cf6', border: '2px solid transparent', width: 10, height: 10 }} />
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
    <Handle type="source" position={Position.Top} style={{ background: 'rgba(0,0,0,0.4)', border: '2px solid transparent', width: 10, height: 10 }} />
    <Handle type="target" position={Position.Bottom} style={{ background: 'rgba(0,0,0,0.4)', border: '2px solid transparent', width: 10, height: 10 }} />
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
    <Handle type="target" position={Position.Top} style={{ background: '#8b5cf6', border: '2px solid #080808', width: 10, height: 10 }} />
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
    <Handle type="source" position={Position.Top} style={{ background: 'rgba(255,255,255,0.5)', border: '2px solid #080808', width: 10, height: 10 }} />
    <Handle type="target" position={Position.Bottom} style={{ background: 'rgba(255,255,255,0.5)', border: '2px solid #080808', width: 10, height: 10 }} />
  </div>
)

const lightNodeTypes = { supervisor: SupervisorNode, agent: AgentNode }
const darkNodeTypes  = { supervisor: SupervisorNodeDark, agent: AgentNodeDark }

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

function FlowCanvas({ agents, dark }) {
  const reactFlowWrapper = useRef(null)
  const { screenToFlowPosition } = useReactFlow()

  const [nodes, setNodes, onNodesChange] = useNodesState([initialSupervisorNode])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [toast, setToast] = useState(null)
  const nodeCounter = useRef(1)

  const nodeTypes = dark ? darkNodeTypes : lightNodeTypes
  const navigate = useNavigate()
  useEffect(() => {
    const sup = agents.find(a => a.role === 'Superviseur' || a.role === 'supervisor')
    if (sup) {
      setNodes(ns => ns.map(n => n.id === SUPERVISOR_ID
        ? { ...n, data: { ...n.data, label: sup.name, model: sup.model } }
        : n
      ))
    }
  }, [agents, setNodes])

  const showToast = (msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const onConnect = useCallback((params) => {
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
    setNodes(ns => [...ns, {
      id: `agent-${nodeCounter.current++}`,
      type: 'agent',
      position,
      data: { label: agent.name, role: agent.role, model: agent.model },
    }])
  }, [screenToFlowPosition, setNodes])

  const deleteSelected = useCallback(() => {
    setNodes(ns => ns.filter(n => !n.selected || n.id === SUPERVISOR_ID))
    setEdges(es => es.filter(e => !e.selected))
  }, [setNodes, setEdges])

  const saveWorkflow = () => {
    localStorage.setItem('workflow_draft', JSON.stringify({ nodes, edges, savedAt: new Date().toISOString() }))
    showToast('Workflow sauvegardé !')
  }

  const sidebarBg = dark ? 'rgba(8,8,8,0.95)' : 'rgba(255,255,255,0.95)'
  const sidebarBorder = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)'
  const canvasBg = dark ? '#080808' : '#f3f4f6'
  const bgColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'

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
            Glissez un agent sur le canvas
          </p>
        </div>

        <div className="flex-1 px-3 py-3 flex flex-col gap-2">
          {agents.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-3 py-10 text-center">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${dark ? 'bg-white/4 border border-dashed border-white/12' : 'bg-gray-100 border border-dashed border-gray-300'}`}>
                <Bot size={18} className={dark ? 'text-white/25' : 'text-gray-300'} />
              </div>
              <div>
                <p className={`text-xs ${dark ? 'text-white/35' : 'text-gray-400'}`}>Aucun agent disponible</p>
                <a href="/agents/create" className="text-xs mt-1 inline-flex items-center gap-1 text-violet-500">
                  <Plus size={11} /> Créer un agent
                </a>
              </div>
            </div>
          ) : (
            agents.map(a => <ToolboxItem key={a.id} agent={a} dark={dark} />)
          )}
        </div>

        <div className="px-4 py-4 border-t" style={{ borderColor: sidebarBorder }}>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-5 h-5 rounded flex items-center justify-center" style={{ background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)' }}>
              <Crown size={11} style={{ color: '#8b5cf6' }} />
            </div>
            <span className={`text-xs ${dark ? 'text-white/40' : 'text-gray-400'}`}>Superviseur (nœud central)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-5 h-5 rounded flex items-center justify-center ${dark ? 'bg-white/5 border border-white/15' : 'bg-gray-100 border border-gray-200'}`}>
              <Bot size={11} className={dark ? 'text-white/50' : 'text-gray-400'} />
            </div>
            <span className={`text-xs ${dark ? 'text-white/40' : 'text-gray-400'}`}>Agent spécialisé</span>
          </div>
        </div>
      </aside>

      {/* ── Main canvas ── */}
      <div className="flex-1 relative" ref={reactFlowWrapper}>

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
              localStorage.setItem('workflow_execution', JSON.stringify({ nodes, edges }))
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

/* ─────────────────────────── page wrapper ───────────────────────── */

export default function CreatWorkflowPage() {
  const agents = loadAgents()
  const { dark } = useTheme()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white font-body transition-colors duration-300">
      <NavBar />
      <div style={{ paddingTop: 68 }}>
        <ReactFlowProvider>
          <FlowCanvas agents={agents} dark={dark} />
        </ReactFlowProvider>
      </div>
    </div>
  )
}
