import { createContext, useContext, useState, useRef, useCallback } from 'react'

const ExecutionContext = createContext(null)

export const ExecutionProvider = ({ children }) => {
  // État global de l'exécution en cours
  const [executionId, setExecutionId]   = useState(null)   // id de l'exécution active
  const [isRunning, setIsRunning]       = useState(false)   // true si en cours
  const [messages, setMessages]         = useState([])      // tous les messages accumulés
  const [activeNodeId, setActiveNodeId] = useState(null)
  const [nodeStatuses, setNodeStatuses] = useState({})
  const controllerRef                   = useRef(null)      // AbortController pour le stream

  const addMsg = useCallback((msg) => {
    setMessages(prev => [...prev, msg])
  }, [])

  const clearExecution = useCallback(() => {
    setExecutionId(null)
    setIsRunning(false)
    setMessages([])
    setActiveNodeId(null)
    setNodeStatuses({})
    controllerRef.current = null
  }, [])

  const stopExecution = useCallback(async (execId) => {
    if (controllerRef.current) {
      controllerRef.current.abort()
    }
    const id = execId || executionId
    if (id) {
      await fetch(`http://localhost:8000/executions/stop/${id}`, { method: 'POST' })
    }
    setIsRunning(false)
    setActiveNodeId(null)
  }, [executionId])

  return (
    <ExecutionContext.Provider value={{
      executionId, setExecutionId,
      isRunning, setIsRunning,
      messages, setMessages, addMsg,
      activeNodeId, setActiveNodeId,
      nodeStatuses, setNodeStatuses,
      controllerRef,
      clearExecution,
      stopExecution,
    }}>
      {children}
    </ExecutionContext.Provider>
  )
}

export const useExecution = () => {
  const ctx = useContext(ExecutionContext)
  if (!ctx) throw new Error('useExecution doit être utilisé dans ExecutionProvider')
  return ctx
}
