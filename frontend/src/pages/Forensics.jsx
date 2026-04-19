import React, { useEffect, useState } from 'react';
import { api } from '../api';

export default function Forensics() {
  const [logs, setLogs] = useState([]);
  const [verifyResult, setVerifyResult] = useState(null);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const resp = await api.log('', 100);
      setLogs(resp);
    } catch (e) {
      console.error(e);
    }
  };

  const handleVerify = async () => {
    try {
      const res = await api.verifyChain();
      setVerifyResult(res);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2>Signed Audit Log</h2>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          {verifyResult && (
             <span className={`badge ${verifyResult.valid ? 'safe' : 'blocked'}`} style={{ fontSize: '13px', padding: '6px 12px' }}>
                {verifyResult.valid ? 'Chain Intact ✅' : `Tampering detected at index ${verifyResult.first_tampered_index} ❌`}
             </span>
          )}
          <button className="btn btn-secondary" onClick={handleVerify}>Verify Chain HMAC</button>
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Seq</th>
              <th>Timestamp</th>
              <th>Session ID</th>
              <th>Agent</th>
              <th>Verdict</th>
              <th>Signature (truncated)</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <React.Fragment key={log.entry_id}>
                <tr onClick={() => setExpanded(expanded === log.entry_id ? null : log.entry_id)} style={{ cursor: 'pointer' }}>
                  <td className="mono">{log.sequence}</td>
                  <td className="mono" style={{ fontSize: '12px' }}>{new Date(log.event.ts).toLocaleString()}</td>
                  <td className="mono">{log.event.session_id.substring(0, 8)}...</td>
                  <td style={{ fontWeight: 'bold', fontSize: '12px' }}>{log.event.agent_id}</td>
                  <td><span className={`badge ${log.event.verdict.toLowerCase()}`}>{log.event.verdict}</span></td>
                  <td className="mono" style={{ fontSize: '12px', color: 'var(--text-3)' }}>{log.signature.substring(0, 16)}...</td>
                </tr>
                {expanded === log.entry_id && (
                  <tr>
                    <td colSpan="6" style={{ background: 'var(--bg)', padding: '16px' }}>
                       <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                          <div>
                            <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '8px' }}>Event Data</div>
                            <pre style={{ background: 'var(--surface-2)', padding: '12px', borderRadius: 'var(--radius)', fontSize: '11px', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                              {JSON.stringify(log.event, null, 2)}
                            </pre>
                          </div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                             <div>
                               <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '4px' }}>Full Hash Signature</div>
                               <div className="mono" style={{ fontSize: '11px', background: 'var(--surface-2)', padding: '8px', borderRadius: '4px', wordBreak: 'break-all' }}>{log.signature}</div>
                             </div>
                             <div>
                               <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '4px' }}>Previous Signature (Chain Link)</div>
                               <div className="mono" style={{ fontSize: '11px', background: 'var(--surface-2)', padding: '8px', borderRadius: '4px', wordBreak: 'break-all' }}>{log.prev_signature || 'GENESIS'}</div>
                             </div>
                          </div>
                       </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
            {logs.length === 0 && (
              <tr><td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-3)' }}>No logs available.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
