import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { ThemeProvider } from './context/ThemeContext'
import { ExecutionProvider } from './context/ExecutionContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <ThemeProvider>
        <ExecutionProvider>
          <App />
        </ExecutionProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
)
