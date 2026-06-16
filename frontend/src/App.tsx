import { useState } from 'react'
import './App.css'
import { useAgent } from './hooks/useAgent'
import { useHistory } from './hooks/useHistory'
import type { ActionType } from './lib/api'

function App() {
  const [prompt, setPrompt] = useState('')
  const [file, setFile] = useState<File | null>(null)
  
  // UI States
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [activeModal, setActiveModal] = useState<'none' | 'ideas' | 'chat'>('none')
  
  // Modal Specific States
  const [ideaKeyword, setIdeaKeyword] = useState('')
  const [chatMessages, setChatMessages] = useState<{role: 'user'|'ai', text: string}[]>([])
  const [chatInput, setChatInput] = useState('')

  const { sendRequest, result, isLoading, error } = useAgent()
  const { history, isLoading: historyLoading, refetch: refetchHistory, clear: clearHistory } = useHistory()

  // Standard Main Form Submit
  const handleMainSubmit = async (action: ActionType) => {
    if (!prompt.trim() && !file) return
    const isSuccess = await sendRequest(action, prompt, file || undefined)
    if (isSuccess) refetchHistory()
  }

  // Ideas Modal Submit
  const handleIdeaSubmit = async () => {
    if (!ideaKeyword.trim()) return
    await sendRequest('generate_ideas', ideaKeyword)
    refetchHistory()
  }

  // Chat Modal Submit
  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return
    const userMsg = chatInput
    setChatMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setChatInput('')
    
    // Send to backend
    const isSuccess = await sendRequest('general_ai', userMsg)
    if (isSuccess) {
        refetchHistory()
    }
  }

  return (
    <div className="app-layout">
      
      {/* ── Mobile Menu Toggle & Overlay ── */}
      <button className="menu-toggle" onClick={() => setIsSidebarOpen(true)}>
        ☰
      </button>
      <div 
        className={`sidebar-overlay ${isSidebarOpen ? 'open' : ''}`}
        onClick={() => setIsSidebarOpen(false)}
      ></div>

      {/* ── Sidebar ── */}
      <aside className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div className="sidebar-title" style={{ margin: 0 }}>Past Conversations</div>
          {history.length > 0 && !historyLoading && (
            <button 
              onClick={clearHistory} 
              title="Clear all history" 
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1rem', opacity: 0.5 }}
            >
              🗑️
            </button>
          )}
        </div>

        <ul className="history-list">
          {historyLoading && <li style={{padding: '0.5rem', color: 'var(--text-muted)'}}>Loading…</li>}
          {!historyLoading && history.length === 0 && (
            <li style={{padding: '0.5rem', color: 'var(--text-muted)'}}>No history yet.</li>
          )}
          {history.map((entry, i) => {
            const isActive = entry.prompt === prompt;
            return (
              <li
                key={i}
                className={`history-item ${isActive ? 'active' : ''}`}
                onClick={() => {
                  setPrompt(entry.prompt)
                  setIsSidebarOpen(false) // Auto-close on mobile
                }}
                title={entry.prompt}
              >
                {isActive && <span>✓</span>}
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {entry.prompt}
                </span>
              </li>
            )
          })}
        </ul>
      </aside>

      {/* ── Main Panel ── */}
      <main className="main-panel">
        <header className="main-header">
          <h1>DevMadeEasy</h1>
          <p className="subtitle">Your intelligent partner for coding, debugging, project management, and creative ideation.</p>
        </header>

        <div className="input-card">
          <textarea
            className="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your task... (e.g., 'Generate a Python factorial function')"
            rows={4}
          />

          <div className="file-upload-container">
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </div>

          <div className="action-grid">
            <button className="action-btn" onClick={() => handleMainSubmit('code_generation')} disabled={isLoading}>
              <span>&lt;/&gt;</span> Generate Code
            </button>
            <button className="action-btn" onClick={() => handleMainSubmit('debugging')} disabled={isLoading}>
              <span>🐛</span> Debug Code
            </button>
            <button className="action-btn" onClick={() => handleMainSubmit('git_operation')} disabled={isLoading}>
              <span>🔀</span> Git Operation
            </button>
            <button className="action-btn" onClick={() => handleMainSubmit('analyze_file')} disabled={isLoading}>
              <span>📄</span> Analyze File
            </button>
            
            {/* Modal Triggers */}
            <button className="action-btn" onClick={() => setActiveModal('ideas')}>
              <span>💡</span> Generate Ideas
            </button>
            <button className="action-btn" onClick={() => setActiveModal('chat')}>
              <span>🤖</span> General AI
            </button>
          </div>
        </div>

        {/* Clean Error Banner */}
        {error && <div className="error-banner">{error}</div>}

        {/* Main Result Area */}
        {result && activeModal === 'none' && (
          <section className="result-card">
            <pre className="result-content">{typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</pre>
          </section>
        )}
      </main>

      {/* ── IDEAS MODAL ── */}
      {activeModal === 'ideas' && (
        <div className="modal-overlay" onClick={() => setActiveModal('none')}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">Blog Post Idea Generator</div>
            <div className="modal-body">
              <input 
                type="text" 
                className="prompt-input" 
                style={{marginBottom: '1rem'}}
                placeholder="e.g., eco park, sustainable living, AI in education"
                value={ideaKeyword}
                onChange={e => setIdeaKeyword(e.target.value)}
              />
              {isLoading && <p style={{color: 'var(--text-muted)'}}>Generating ideas...</p>}
              {result && !isLoading && (
                 <div style={{background: 'var(--input-bg)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--border-color)'}}>
                    <pre style={{whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0, color: 'var(--text-main)'}}>{result}</pre>
                 </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn-outline" onClick={() => setActiveModal('none')}>Close</button>
              <button className="action-btn" onClick={handleIdeaSubmit} disabled={isLoading} style={{background: 'var(--text-main)', color: 'var(--bg-color)', border: 'none'}}>Generate Ideas</button>
            </div>
          </div>
        </div>
      )}

      {/* ── CHAT MODAL ── */}
      {activeModal === 'chat' && (
        <div className="modal-overlay" onClick={() => setActiveModal('none')}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">General Purpose AI Chat</div>
            
            <div className="modal-body" style={{display: 'flex', flexDirection: 'column'}}>
              {chatMessages.length === 0 ? (
                <div style={{textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem'}}>Ask me anything!</div>
              ) : (
                chatMessages.map((msg, i) => (
                  <div key={i} className={`chat-bubble ${msg.role === 'user' ? 'chat-user' : 'chat-ai'}`}>
                    {msg.text}
                  </div>
                ))
              )}
              {result && !isLoading && chatMessages.length > 0 && (
                 <div className="chat-bubble chat-ai">
                   {result}
                 </div>
              )}
              {isLoading && <div className="chat-bubble chat-ai" style={{opacity: 0.5}}>Thinking...</div>}
            </div>

            <div style={{display: 'flex', gap: '0.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem'}}>
              <input 
                type="text" 
                className="prompt-input" 
                style={{marginBottom: 0, flex: 1}}
                placeholder="Message DevMadeEasy..."
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleChatSubmit()}
              />
              <button className="action-btn" onClick={handleChatSubmit} disabled={isLoading} style={{background: 'var(--text-main)', color: 'var(--bg-color)', border: 'none', padding: '0 1.5rem'}}>Send</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App