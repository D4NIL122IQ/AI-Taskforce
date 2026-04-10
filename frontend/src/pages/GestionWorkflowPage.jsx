import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import NavBar from '../components/layout/NavBar'
import PageBackground from '../components/layout/PageBackground'
import { Plus, Workflow, Pencil, Trash2, Play, Bot, Crown } from 'lucide-react'

const useWorkflows = () => {
  const [workflows, setWorkflows] = useState([])

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    const userId = user?.user_id
    if (!userId) return
    fetch(`http://localhost:8000/workflows/user/${userId}`)
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setWorkflows(data)
      })
      .catch(() => setWorkflows([]))
  }, [])

  const remove = async (id) => {
    await fetch(`http://localhost:8000/workflows/${id}`, { method: 'DELETE' })
    setWorkflows(prev => prev.filter(w => w.id_workflow !== id))
  }

  return { workflows, remove }
}

const WorkflowCard = ({ workflow, onDelete, onExecute }) => {
  const graphe = workflow.donnees_graphe_json || {}
  const nodes = graphe.nodes || []
  const agentCount = nodes.filter(n => n.type === 'agent').length
  const date = workflow.date_creation
    ? new Date(workflow.date_creation).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
    : null

  return (
    <div className="flex flex-col gap-4 bg-white dark:bg-white/[0.03] border border-gray-200 dark:border-white/10 rounded-2xl p-5 hover:border-gray-300 dark:hover:border-white/20 transition-colors duration-200">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-violet-50 dark:bg-violet-600/20 border border-violet-200 dark:border-violet-500/30 flex items-center justify-center flex-shrink-0">
            <Workflow size={17} className="text-violet-600 dark:text-violet-400" />
          </div>
          <div>
            <h3 className="text-gray-900 dark:text-white text-sm font-semibold leading-tight">{workflow.nom}</h3>
            {date && <p className="text-gray-400 dark:text-white/40 text-xs mt-0.5">{date}</p>}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs text-gray-400 dark:text-white/35">
        <span className="flex items-center gap-1.5">
          <Crown size={12} className="text-violet-400" />
          1 superviseur
        </span>
        <span className="flex items-center gap-1.5">
          <Bot size={12} />
          {agentCount} agent{agentCount !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="flex gap-2 border-t border-gray-100 dark:border-white/5 pt-3">
        <Link
          to={`/workflow/edit/${workflow.id_workflow}`}
          className="flex items-center gap-2 flex-1 justify-center py-2 rounded-xl text-xs font-medium text-gray-500 dark:text-white/60 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-white/20 transition-all duration-200"
        >
          <Pencil size={13} />
          Modifier
        </Link>
        <button
          type="button"
          onClick={() => onExecute(workflow)}
          className="flex items-center gap-2 flex-1 justify-center py-2 rounded-xl text-xs font-medium text-green-600 dark:text-green-400/80 bg-green-50 dark:bg-green-500/5 border border-green-200 dark:border-green-500/15 hover:text-green-700 dark:hover:text-green-400 hover:border-green-300 dark:hover:border-green-500/30 transition-all duration-200"
        >
          <Play size={13} />
          Exécuter
        </button>
        <button
          type="button"
          onClick={() => onDelete(workflow.id_workflow)}
          className="flex items-center gap-2 px-3 justify-center py-2 rounded-xl text-xs font-medium text-red-500 dark:text-red-400/70 bg-red-50 dark:bg-red-500/5 border border-red-200 dark:border-red-500/10 hover:text-red-600 dark:hover:text-red-400 hover:border-red-300 dark:hover:border-red-500/30 transition-all duration-200"
        >
          <Trash2 size={13} />
        </button>
      </div>
    </div>
  )
}

const GestionWorkflowPage = () => {
  const { workflows, remove } = useWorkflows()
  const navigate = useNavigate()

  const handleExecute = (workflow) => {
    const graphe = workflow.donnees_graphe_json || {}
    localStorage.setItem('workflow_execution', JSON.stringify({
      id_workflow: workflow.id_workflow,
      nodes: graphe.nodes || [],
      edges: graphe.edges || [],
    }))
    navigate('/workflow/execute')
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white font-body transition-colors duration-300">
      <PageBackground />
      <NavBar />

      <main className="relative max-w-6xl mx-auto px-6 pt-[100px] pb-24">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mes workflows</h1>
            <p className="text-gray-500 dark:text-white/50 text-sm mt-1">
              {workflows.length === 0
                ? 'Aucun workflow créé pour le moment'
                : `${workflows.length} workflow${workflows.length > 1 ? 's' : ''} configuré${workflows.length > 1 ? 's' : ''}`}
            </p>
          </div>
          <Link
            to="/workflow/create"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors duration-200"
          >
            <Plus size={16} />
            Créer un workflow
          </Link>
        </div>

        {workflows.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-4 py-32 border border-dashed border-gray-200 dark:border-white/10 rounded-2xl">
            <div className="w-14 h-14 rounded-2xl bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 flex items-center justify-center">
              <Workflow size={24} className="text-gray-300 dark:text-white/30" />
            </div>
            <div className="text-center">
              <p className="text-gray-400 dark:text-white/50 text-sm">Aucun workflow pour le moment</p>
              <p className="text-gray-300 dark:text-white/25 text-xs mt-1">Créez votre premier workflow pour commencer</p>
            </div>
            <Link
              to="/workflow/create"
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 text-gray-600 dark:text-white/70 hover:text-gray-900 dark:hover:text-white text-sm font-medium transition-all duration-200 mt-2"
            >
              <Plus size={15} />
              Créer un workflow
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {workflows.map((wf) => (
              <WorkflowCard
                key={wf.id_workflow}
                workflow={wf}
                onDelete={remove}
                onExecute={handleExecute}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default GestionWorkflowPage
