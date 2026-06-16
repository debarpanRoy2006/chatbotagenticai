import { createRoot } from 'react-dom/client'
import { ApiProvider } from './context/ApiContext'
import App from './App'
import './App.css'

const rootElement = document.getElementById('root')
if (!rootElement) throw new Error('Root element not found')

createRoot(rootElement).render(
  <ApiProvider>
    <App />
  </ApiProvider>,
)
