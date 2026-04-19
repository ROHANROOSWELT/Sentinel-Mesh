import { useState, useRef, useEffect } from 'react';
import { api } from '../api';

const ATTACK_PRESETS = [
  "Ignore Instructions", "DAN Jailbreak", "Reveal Token", 
  "New Instructions", "God Mode", "Email Exfiltration"
];
const SAFE_PRESETS = [
  "Hello", "Summarise emails", "Query database", "What is 12 × 12?"
];

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState('protected');
  const [session, setSession] = useState(null);
  const [latestAnalysis, setLatestAnalysis] = useState(null);
  const [latestEvents, setLatestEvents] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    
    const userMsg = { role: 'user', content: text, id: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    
    try {
      const resp = await api.chat({
        message: text,
        mode,
        session_id: session
      });
      
      setSession(resp.session_id);
      
      if (resp.analysis) setLatestAnalysis(resp.analysis);
      if (resp.pipeline_events) setLatestEvents(resp.pipeline_events);
      
      const aiMsg = { 
        role: 'ai', 
        content: resp.final_response,
        raw_response: resp.raw_response,
        analysis: resp.analysis,
        canary: resp.canary,
        id: Date.now() + 1
      };
      setMessages(prev => [...prev, aiMsg]);
      
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { role: 'ai', content: 'Error communicating with backend.', isError: true, id: Date.now() + 1 }]);
    }
  };

  return (
    <div className="chat-layout">
      <div className="chat-main">
        <div style={{ padding: '16px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '16px' }}>Chat</h2>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
             <span style={{ fontSize: '12px' }}>Mode:</span>
             <button 
               className={`btn ${mode === 'protected' ? 'btn-primary' : 'btn-secondary'}`} 
               onClick={() => setMode('protected')}
               style={{ padding: '4px 12px' }}
             >Protected</button>
             <button 
               className={`btn ${mode === 'vulnerable' ? 'btn-primary' : 'btn-secondary'}`} 
               onClick={() => setMode('vulnerable')}
               style={{ padding: '4px 12px' }}
             >Vulnerable</button>
          </div>
        </div>
        
        <div className="messages-list">
          {messages.map(msg => (
            <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div className={`message ${msg.role} ${msg.isError ? 'error-text' : ''}`}>
                 <div>{msg.content}</div>
                 {msg.analysis && (
                   <div className="ai-meta">
                     <span className={`badge ${msg.analysis.verdict.toLowerCase()}`}>{msg.analysis.verdict}</span>
                     {msg.canary && <span className="canary-code">{msg.canary}</span>}
                     {msg.analysis.was_hardened && <span style={{ color: 'var(--success)', fontWeight: 'bold' }}>Input Hardened</span>}
                   </div>
                 )}
              </div>
              {msg.raw_response && (
                <div style={{ alignSelf: 'flex-start', background: 'var(--danger-light)', border: '1px solid var(--danger)', padding: '12px 16px', borderRadius: 'var(--radius-lg)', fontSize: '13px', width: '85%' }}>
                   <div style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--danger)', marginBottom: '4px' }}>RAW VULNERABLE RESPONSE (Intercepted)</div>
                   {msg.raw_response}
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="chat-input-area">
          <div className="preset-row">
            <span style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--danger)' }}>Attack Presets:</span>
            {ATTACK_PRESETS.map(p => (
              <button key={p} className="preset-btn" onClick={() => sendMessage(p)}>{p}</button>
            ))}
          </div>
          <div className="preset-row">
            <span style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--success)' }}>Safe Presets:</span>
            {SAFE_PRESETS.map(p => (
              <button key={p} className="preset-btn" onClick={() => sendMessage(p)}>{p}</button>
            ))}
          </div>
          <div className="input-group">
            <input 
              value={input} 
              onChange={e => setInput(e.target.value)} 
              onKeyDown={e => e.key === 'Enter' && sendMessage(input)}
              placeholder="Test the system..."
            />
            <button className="btn btn-primary" onClick={() => sendMessage(input)}>Send</button>
          </div>
        </div>
      </div>
      
      <div className="chat-security-panel">
        <h3 style={{ fontSize: '16px', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>Security Analysis</h3>
        
        {!latestAnalysis && <div style={{ color: 'var(--text-3)', fontSize: '13px' }}>No analysis available.</div>}
        
        {latestAnalysis && (
          <>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-2)' }}>Risk Score</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{latestAnalysis.risk_score}</div>
              <div style={{ 
                height: '4px', background: `linear-gradient(to right, var(--success) 0%, var(--warning) 50%, var(--danger) 100%)`,
                borderRadius: '2px', marginTop: '4px', position: 'relative'
              }}>
                 <div style={{ position: 'absolute', top: '-2px', left: `${latestAnalysis.risk_score}%`, width: '8px', height: '8px', background: '#333', borderRadius: '50%', transform: 'translateX(-50%)' }} />
              </div>
            </div>
            
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-2)', marginBottom: '4px' }}>Classification</div>
              <span className={`badge ${latestAnalysis.verdict.toLowerCase()}`} style={{ fontSize: '14px', padding: '4px 12px' }}>{latestAnalysis.verdict}</span>
              <div style={{ fontSize: '12px', marginTop: '8px', color: 'var(--text-2)' }}>{latestAnalysis.explanation}</div>
            </div>
            
            <div>
               <div style={{ fontSize: '12px', color: 'var(--text-2)', marginBottom: '4px' }}>Canary Token</div>
               {latestAnalysis.canary_leaked ? (
                  <div style={{ color: 'var(--danger)', fontWeight: 'bold', fontSize: '12px' }}>LEAKED</div>
               ) : (
                  <div style={{ color: 'var(--success)', fontWeight: 'bold', fontSize: '12px' }}>PROTECTED</div>
               )}
            </div>
            
            {latestAnalysis.owasp_refs.length > 0 && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-2)', marginBottom: '8px' }}>OWASP Mapping</div>
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {latestAnalysis.owasp_refs.map(ref => (
                    <span key={ref} style={{ padding: '2px 6px', background: 'var(--surface-2)', border: '1px solid var(--border-strong)', fontSize: '11px', borderRadius: '4px' }}>
                      {ref}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {latestEvents.length > 0 && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-2)', marginBottom: '8px' }}>Pipeline Trace</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {latestEvents.map(ev => (
                    <div key={ev.event_id} style={{ background: 'var(--bg)', border: '1px solid var(--border)', padding: '8px', borderRadius: '6px' }}>
                       <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                          <span style={{ fontSize: '11px', fontWeight: 'bold' }}>{ev.agent_id}</span>
                          <span className={`badge ${ev.verdict.toLowerCase()}`} style={{ fontSize: '9px' }}>{ev.verdict}</span>
                       </div>
                       <div style={{ fontSize: '11px', color: 'var(--text-2)' }}>Latency: {ev.latency_ms.toFixed(1)}ms</div>
                       <div style={{ fontSize: '11px', marginTop: '4px', lineHeight: '1.4' }}>{ev.reasoning}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
