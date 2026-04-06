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
import { Link } from 'react-router-dom'


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
} from "lucide-react"

const Dashboard = () => {

  // STATES
  const [agents, setAgents] = useState([])
  const [workflows, setWorkflows] = useState([])
  const [documents, setDocuments] = useState([])
  const [erreurs, seterreurs] = useState([])
  const [executions, setExecutions] = useState([])
  const [loading, setLoading] = useState(true)
  const [openMenuId, setOpenMenuId] = useState(null)

  // ACTIVITES
  const activities = [
    {
      id: 1,
      type: "success",
      message: 'Workflow "Analyse CV" exécuté',
      time: "il y a 2 min",
    },
    {
      id: 2,
      type: "agent",
      message: 'Agent "Classifier GPT" a répondu',
      time: "il y a 5 min",
    },
    {
      id: 3,
      type: "update",
      message: 'Agent "Data Cleaner" modifié',
      time: "il y a 12 min",
    },
    {
      id: 4,
      type: "error",
      message: 'Erreur sur workflow "Scraping Web"',
      time: "il y a 18 min",
    },
    {
      id: 5,
      type: "info",
      message: "8 exécutions terminées aujourd'hui",
      time: "Aujourd'hui",
    },
  ]

  // DOCUMENTS (renommé de "document" en "docs")
  const docs = [
    {
      id: 1,
      name: "rapport_analyse.pdf",
      type: "pdf",
      date: "il y a 2h"
    },
    {
      id: 2,
      name: "image_dataset.png",
      type: "image",
      date: "il y a 1 jour"
    },
    {
      id: 3,
      name: "notes.txt",
      type: "text",
      date: "il y a 3 jours"
    }
  ]

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
        const userId = user?.user_id || 1

        const [
          agentsRes,
          workflowsRes,
          erreursRes,
          executionsRes
        ] = await Promise.all([
          fetch(`http://localhost:8000/agents/${userId}`),
          fetch(`http://localhost:8000/workflows/${userId}`),
          fetch(`http://localhost:8000/executions/ERREUR`),
          fetch(`http://localhost:8000/executions`),
        ])

        const agentsData = await agentsRes.json()
        const workflowsData = await workflowsRes.json()
        const erreursData = await erreursRes.json()
        const executionsData = await executionsRes.json()

        setAgents(Array.isArray(agentsData) ? agentsData : [])
        setWorkflows(Array.isArray(workflowsData) ? workflowsData : [])
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
            <button className="bg-yellow-600 hover:bg-purple-700 px-4 py-2 rounded-lg">
              + Service
            </button>
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
                        key={agent.id_agent}
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

                          <div className="relative">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                setOpenMenuId(openMenuId === agent.id_agent ? null : agent.id_agent)
                              }}
                              className="p-2 hover:bg-gray-800 rounded"
                            >
                              <MoreVertical size={16} />
                            </button>

                            {openMenuId === agent.id_agent && (
                              <div className="absolute right-0 mt-2 w-40 bg-[#1a1a1a] border border-gray-700 rounded-lg shadow-lg z-50">

                                <button
                                  onClick={() => console.log("Voir", agent.id_agent)}
                                  className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-gray-700"
                                >
                                  <Eye size={14} /> Voir détails
                                </button>

                                <button
                                  onClick={() => navigate(`/agents/edit/${agent.id_agent}`)}
                                  className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-gray-700"
                                >
                                  <Link to={`/agents/edit/${agent.id_agent}`} className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-gray-700">
                                    <Edit size={14} /> Modifier
                                  </Link>
                                </button>

                                <button
                                  onClick={() => console.log("Supprimer", agent.id_agent)}
                                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-400 hover:bg-gray-700"
                                >
                                  <Trash size={14} /> Supprimer
                                </button>

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
                  {activities.map((act) => {
                    const { icon, color } = getStyle(act.type)
                    const Icon = icon

                    return (
                      <div
                        key={act.id}
                        className="flex items-center justify-between bg-[#0d0d0d] px-3 py-2 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <Icon className={color} size={16} />
                          <span>{act.message}</span>
                        </div>

                        <span className="text-xs text-gray-500">
                          {act.time}
                        </span>
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

              {/* DOCUMENTS */}
              <div className="bg-[#111] border border-gray-800 rounded-xl p-5 flex flex-col h-[300px]">
                <h2 className="text-lg font-semibold mb-4">Documents</h2>

                <div className="space-y-3 overflow-y-auto pr-2">
                  {docs.length === 0 ? (
                    <p className="text-gray-400 text-sm">Aucun document</p>
                  ) : (
                    docs.map((doc) => {
                      const Icon = getDocIcon(doc.type)

                      return (
                        <div
                          key={doc.id}
                          className="flex items-center justify-between bg-[#0d0d0d] px-3 py-2 rounded-lg hover:bg-[#1a1a1a] transition"
                        >
                          <div className="flex items-center gap-3">
                            <Icon className="text-blue-400" size={18} />
                            <span className="truncate max-w-[180px]">{doc.name}</span>
                          </div>

                          <span className="text-xs text-gray-500">
                            {doc.date}
                          </span>
                        </div>
                      )
                    })
                  )}
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