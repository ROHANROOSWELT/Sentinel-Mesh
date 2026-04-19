import { useState } from 'react';
import { api } from '../api';

const PRESETS = [
  "Ignore Instructions", "DAN Jailbreak", "Reveal Token", 
  "New Instructions", "God Mode", "Email Exfiltration", "What is 12x12?", "Summarise the database"
];

export default function Compare() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [vulnResult, setVulnResult] = useState(null);
  const [protResult, setProtResult] = useState(null);

  const runCompare = async (text) => {
    if (!text.trim()) return;
    setLoading(true);
    setInput(text);
    
    try {
      const [vuln, prot] = await Promise.all([
        api.chat({ message: text, mode: 'vulnerable' }),
        api.chat({ message: text, mode: 'protected' })
      ]);
      setVulnResult(vuln);
      setProtResult(prot);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div>
      <h2 style={{ marginBottom: '24px' }}>Side-by-Side Comparison</h2>

      <div style={{ marginBottom: '24px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '13px', display: 'flex', alignItems: 'center', marginRight: '8px' }}>Try preset:</span>
        {PRESETS.map(p => (
           <button key={p} className="btn btn-secondary" style={{ padding: '4px 12px', fontSize: '12px' }} onClick={() => runCompare(p)} disabled={loading}>{p}</button>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '32px' }}>
         <input 
            value={input} 
            onChange={e => setInput(e.target.value)} 
            placeholder="Enter prompt..." 
            disabled={loading}
            onKeyDown={e => e.key === 'Enter' && runCompare(input)}
         />
         <button className="btn btn-primary" onClick={() => runCompare(input)} disabled={loading}>
           {loading ? 'Running...' : 'Compare'}
         </button>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
         <div style={{ flex: 1, border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '24px', background: 'var(--surface)' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--danger)', display: 'flex', justifyContent: 'space-between' }}>
               Vulnerable (no protection)
               {vulnResult && <span style={{ fontSize: '12px', color: 'var(--text-3)' }}>{vulnResult.total_latency_ms}ms</span>}
            </h3>
            {vulnResult ? (
              <div>
                <div style={{ background: 'var(--bg)', padding: '16px', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
                   {vulnResult.final_response}
                </div>
              </div>
            ) : (
              <div style={{ color: 'var(--text-3)', fontSize: '13px' }}>Run a test to see the vulnerable response.</div>
            )}
         </div>
         
         <div style={{ flex: 1, border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '24px', background: 'var(--surface)' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--success)', display: 'flex', justifyContent: 'space-between' }}>
               Protected (SentinelMesh active)
               {protResult && <span style={{ fontSize: '12px', color: 'var(--text-3)' }}>{protResult.total_latency_ms}ms</span>}
            </h3>
            {protResult ? (
              <div>
                <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                   <span className={`badge ${protResult.analysis.verdict.toLowerCase()}`}>{protResult.analysis.verdict}</span>
                   {protResult.analysis.verdict !== 'SAFE' && (
                      <span style={{ fontSize: '12px', color: 'var(--danger)', fontWeight: 'bold' }}>✓ ATTACK CAUGHT</span>
                   )}
                </div>
                <div style={{ background: 'var(--bg)', padding: '16px', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
                   {protResult.final_response}
                </div>
                {protResult.raw_response && (
                  <div style={{ marginTop: '16px', borderTop: '1px solid var(--border)', paddingTop: '16px', fontSize: '12px' }}>
                    <div style={{ fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '4px' }}>Intercepted LLM Attempt:</div>
                    <div style={{ color: 'var(--danger)', background: 'var(--danger-light)', padding: '8px', borderRadius: '4px', border: '1px dashed var(--danger)' }}>
                       {protResult.raw_response}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: 'var(--text-3)', fontSize: '13px' }}>Run a test to see the protected response.</div>
            )}
         </div>
      </div>
    </div>
  );
}
