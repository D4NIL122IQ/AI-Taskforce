import { useState } from 'react'
import { Link } from 'react-router-dom'
import NavBar from '../components/layout/NavBar'
import PageBackground from '../components/layout/PageBackground'
import { Plus, Bot, Pencil, Trash2, Globe, Thermometer, Hash } from 'lucide-react'

const useAgents = () => {
  const load = () => {
    try { return JSON.parse(localStorage.getItem('agents') || '[]') } catch { return [] }
  }
  const [agents, setAgents] = useState(load)

  const remove = (id) => {
    const updated = agents.filter((a) => a.id !== id)
    setAgents(updated)
    localStorage.setItem('agents', JSON.stringify(updated))
  }

  return { agents, remove }
}

const AgentCard = ({ agent, onDelete }) => (
  <div className="flex flex-col gap-4 bg-white/[0.03] border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-colors duration-200">

    {/* Header */}
    <div className="flex items-start justify-between gap-3">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center flex-shrink-0">
          <Bot size={17} className="text-violet-400" />
        </div>
        <div>
          <h3 className="text-white text-sm font-semibold leading-tight">{agent.name}</h3>
          <p className="text-white/40 text-xs mt-0.5">{agent.role || 'Personnalisé'}</p>
        </div>
      </div>
      <span className="text-xs text-white/30 bg-white/5 border border-white/10 px-2.5 py-1 rounded-full flex-shrink-0">
        {agent.model}
      </span>
    </div>

    {/* Prompt système */}
    {agent.systemPrompt && (
      <p className="text-white/40 text-xs leading-relaxed line-clamp-2 border-t border-white/5 pt-3">
        {agent.systemPrompt}
      </p>
    )}

    {/* Infos */}
    <div className="flex items-center gap-4 text-xs text-white/35">
      <span className="flex items-center gap-1.5">
        <Thermometer size={12} />
        {agent.temperature}
      </span>
      <span className="flex items-center gap-1.5">
        <Hash size={12} />
        {agent.maxTokens} tokens
      </span>
      {agent.webSearch && (
        <span className="flex items-center gap-1.5 text-violet-400/70">
          <Globe size={12} />
          Web
        </span>
      )}
    </div>

    {/* Actions */}
    <div className="flex gap-2 border-t border-white/5 pt-3">
      <Link
        to={`/agents/edit/${agent.id}`}
        className="flex items-center gap-2 flex-1 justify-center py-2 rounded-xl text-xs font-medium text-white/60 bg-white/5 border border-white/10 hover:text-white hover:border-white/20 transition-all duration-200"
      >
        <Pencil size={13} />
        Modifier
      </Link>
      <button
        type="button"
        onClick={() => onDelete(agent.id)}
        className="flex items-center gap-2 flex-1 justify-center py-2 rounded-xl text-xs font-medium text-red-400/70 bg-red-500/5 border border-red-500/10 hover:text-red-400 hover:border-red-500/30 transition-all duration-200"
      >
        <Trash2 size={13} />
        Supprimer
      </button>
    </div>
  </div>
)

const GestionAgentPage = () => {
  const { agents, remove } = useAgents()

  return (
    <div className="min-h-screen bg-[#080808] text-white font-body">
      <PageBackground />
      <NavBar />

      <main className="relative max-w-6xl mx-auto px-6 pt-[100px] pb-24">

        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-bold">Mes agents</h1>
            <p className="text-white/50 text-sm mt-1">
              {agents.length === 0
                ? 'Aucun agent créé pour le moment'
                : `${agents.length} agent${agents.length > 1 ? 's' : ''} configuré${agents.length > 1 ? 's' : ''}`}
            </p>
          </div>
          <Link
            to="/agents/create"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors duration-200"
          >
            <Plus size={16} />
            Créer un agent
          </Link>
        </div>

        {/* Grille ou état vide */}
        {agents.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-4 py-32 border border-dashed border-white/10 rounded-2xl">
            <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
              <Bot size={24} className="text-white/30" />
            </div>
            <div className="text-center">
              <p className="text-white/50 text-sm">Aucun agent pour le moment</p>
              <p className="text-white/25 text-xs mt-1">Créez votre premier agent pour commencer</p>
            </div>
            <Link
              to="/agents/create"
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 text-white/70 hover:text-white text-sm font-medium transition-all duration-200 mt-2"
            >
              <Plus size={15} />
              Créer un agent
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} onDelete={remove} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default GestionAgentPage
