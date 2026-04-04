import NavBar from "../components/layout/NavBar"
import { useState, useEffect } from "react"
import { Bot, Workflow, Activity, AlertCircle, Play, Settings } from "lucide-react"

const Dashboard = () => {
  const [agents, setAgents] = useState([])
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)

  // Charger agents depuis backend
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"))

    if (!user) return

    fetch(`http://localhost:8000/agent/${user.id}`)
      .then(res => res.json())
      .then(data => setAgents(data))
      .catch(err => console.error(err))
  }, [])

  // Charger workflows depuis backend
  useEffect(() => {
    fetch("http://localhost:8000/workflows/")
      .then(res => res.json())
      .then(data => setWorkflows(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  const stats = [
    { label: "Agents actifs", value: agents.length, icon: Bot },
    { label: "Workflows", value: workflows.length, icon: Workflow },
    { label: "Exécutions", value: 0, icon: Activity }, // 🔥 à connecter plus tard
    { label: "Erreurs", value: 0, icon: AlertCircle },
  ]

  return (
    <div className="min-h-screen bg-[#080808] text-white">
      <NavBar />

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

        {/* HEADER */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <div className="flex gap-3">
            <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg">
              + Agent
            </button>
            <button className="border border-gray-600 px-4 py-2 rounded-lg hover:bg-gray-800">
              + Workflow
            </button>
          </div>
        </div>

        {/* LOADING */}
        {loading ? (
          <p className="text-gray-400">Chargement...</p>
        ) : (
          <>
            {/* STATS */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {stats.map(({ label, value, icon: Icon }) => (
                <div
                  key={label}
                  className="bg-[#111] border border-gray-800 rounded-xl p-4 flex items-center justify-between hover:border-purple-500 transition"
                >
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
                      <div
                        key={agent.id}
                        className="flex items-center justify-between bg-[#0d0d0d] p-3 rounded-lg"
                      >
                        <div>
                          <p className="font-medium">{agent.nom}</p>
                          <p className="text-sm text-gray-400">{agent.modele}</p>
                        </div>

                        <div className="flex items-center gap-3">
                          <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">
                            actif
                          </span>

                          <button className="p-2 hover:bg-gray-800 rounded">
                            <Play size={16} />
                          </button>

                          <button className="p-2 hover:bg-gray-800 rounded">
                            <Settings size={16} />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* ACTIVITY */}
              <div className="bg-[#111] border border-gray-800 rounded-xl p-5">
                <h2 className="text-lg font-semibold mb-4">Activité</h2>

                <div className="space-y-2 text-sm text-gray-300">
                  <p>Aucune activité pour le moment</p>
                </div>
              </div>

              {/* WORKFLOWS */}
              <div className="lg:col-span-2 bg-[#111] border border-gray-800 rounded-xl p-5">
                <h2 className="text-lg font-semibold mb-4">Workflows</h2>

                <div className="space-y-3">
                  {workflows.length === 0 ? (
                    <p className="text-gray-400 text-sm">Aucun workflow</p>
                  ) : (
                    workflows.map((wf) => (
                      <div
                        key={wf.id}
                        className="flex items-center justify-between bg-[#0d0d0d] p-3 rounded-lg"
                      >
                        <div>
                          <p className="font-medium">{wf.nom}</p>
                          <p className="text-sm text-gray-400">
                            {wf.nb_agents} agents
                          </p>
                        </div>

                        <div className="flex items-center gap-3">
                          <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">
                            actif
                          </span>

                          <button className="p-2 hover:bg-gray-800 rounded">
                            <Play size={16} />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* ERRORS */}
              <div className="bg-[#111] border border-gray-800 rounded-xl p-5">
                <h2 className="text-lg font-semibold mb-4">Erreurs</h2>

                <div className="text-sm text-gray-400">
                  Aucune erreur
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Dashboard