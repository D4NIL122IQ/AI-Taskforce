import { useState } from 'react'
import { useParams } from 'react-router-dom'
import NavBar from '../components/layout/NavBar'
import PageBackground from '../components/layout/PageBackground'

const RagConfigPage = () => {
  const { id } = useParams()

  const [config, setConfig] = useState({
    chunkSize: 500,
    chunkOverlap: 50,
    topK: 5,
    lambdaMult: 0.5,
    usePostProcessing: true,
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setConfig((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : Number(value)
    }))
  }

  const handleSave = () => {
    localStorage.setItem(`rag_config_${id}`, JSON.stringify(config))
    alert("Configuration RAG sauvegardée")
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#080808] text-gray-900 dark:text-white">
      <PageBackground />
      <NavBar />

      <main className="max-w-3xl mx-auto px-6 pt-[100px] pb-24">

        <h1 className="text-3xl font-bold mb-6">Configuration RAG</h1>

        <div className="flex flex-col gap-6">

          {/* Chunk Size */}
          <div>
            <label className="text-sm">Chunk Size : {config.chunkSize}</label>
            <input
              type="range"
              name="chunkSize"
              min="100"
              max="2000"
              step="50"
              value={config.chunkSize}
              onChange={handleChange}
              className="w-full"
            />
          </div>

          {/* Overlap */}
          <div>
            <label className="text-sm">Chunk Overlap : {config.chunkOverlap}</label>
            <input
              type="range"
              name="chunkOverlap"
              min="0"
              max="500"
              step="10"
              value={config.chunkOverlap}
              onChange={handleChange}
              className="w-full"
            />
          </div>

          {/* Top K */}
          <div>
            <label className="text-sm">Top K : {config.topK}</label>
            <input
              type="range"
              name="topK"
              min="1"
              max="20"
              value={config.topK}
              onChange={handleChange}
              className="w-full"
            />
          </div>

          {/* Lambda */}
          <div>
            <label className="text-sm">Lambda (MMR) : {config.lambdaMult}</label>
            <input
              type="range"
              name="lambdaMult"
              min="0"
              max="1"
              step="0.1"
              value={config.lambdaMult}
              onChange={handleChange}
              className="w-full"
            />
          </div>

          {/* Post processing */}
          <div className="flex items-center justify-between">
            <span className="text-sm">Post-traitement (Rerank + Extraction)</span>
            <input
              type="checkbox"
              name="usePostProcessing"
              checked={config.usePostProcessing}
              onChange={handleChange}
            />
          </div>

          {/* Save */}
          <button
            onClick={handleSave}
            className="mt-4 px-6 py-3 bg-violet-600 hover:bg-violet-500 rounded-xl text-white"
          >
            Sauvegarder
          </button>

        </div>
      </main>
    </div>
  )
}

export default RagConfigPage