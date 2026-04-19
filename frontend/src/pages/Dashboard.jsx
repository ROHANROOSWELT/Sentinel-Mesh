import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isConfirming, setIsConfirming] = useState(false);

  const fetchData = async () => {
    try {
      const s = await api.stats();
      setStats(s);
      const l = await api.log('', 10);
      setLogs(l);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) return <div>Loading...</div>;

  const handleReset = async () => {
    try {
      await api.reset();
      setIsConfirming(false);
      await fetchData();
    } catch (e) {
      console.error("Reset failed:", e);
      alert("Failed to reset data. Please try again.");
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2>Dashboard</h2>
        {!isConfirming ? (
          <button className="btn btn-secondary" onClick={() => setIsConfirming(true)} style={{ color: 'var(--danger)', borderColor: 'var(--danger-light)' }}>
            Clear All Data
          </button>
        ) : (
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-secondary" onClick={() => setIsConfirming(false)} style={{ fontSize: '12px' }}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleReset} style={{ background: 'var(--danger)', borderColor: 'var(--danger)', color: 'white', fontSize: '12px' }}>
              Confirm Wipe
            </button>
          </div>
        )}
      </div>
      
      <div className="metric-grid">
        <div className="metric-card">
          <span className="metric-title">Total Requests</span>
          <span className="metric-value">{stats.total_requests}</span>
        </div>
        <div className="metric-card">
          <span className="metric-title">Attacks Detected</span>
          <span className="metric-value">{stats.attacks}</span>
        </div>
        <div className="metric-card">
          <span className="metric-title">Blocked</span>
          <span className="metric-value">{stats.blocked}</span>
        </div>
        <div className="metric-card">
          <span className="metric-title">Detection Rate</span>
          <span className="metric-value">{stats.detection_rate}%</span>
        </div>
      </div>

      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ marginBottom: '16px', fontSize: '14px', color: 'var(--text-2)' }}>OWASP Breakdown</h3>
        <div style={{ display: 'flex', gap: '2px', height: '24px', borderRadius: '4px', overflow: 'hidden' }}>
          {Object.entries(stats.owasp_breakdown).length === 0 ? (
            <div style={{ background: 'var(--surface)', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', color: 'var(--text-3)' }}>No data</div>
          ) : (
            Object.entries(stats.owasp_breakdown).map(([code, count], idx) => {
              const colors = ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#9333ea', '#db2777', '#ea580c'];
              const color = colors[idx % colors.length];
              const total = Object.values(stats.owasp_breakdown).reduce((a, b) => a + b, 0);
              const pct = (count / total) * 100;
              return (
                <div key={code} style={{ width: `${pct}%`, background: color }} title={`${code}: ${count}`} />
              )
            })
          )}
        </div>
        <div style={{ display: 'flex', gap: '16px', marginTop: '8px', flexWrap: 'wrap' }}>
          {Object.entries(stats.owasp_breakdown).map(([code, count], idx) => {
             const colors = ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#9333ea', '#db2777', '#ea580c'];
             const color = colors[idx % colors.length];
             return (
               <div key={code} style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                 <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: color }} />
                 {code} ({count})
               </div>
             )
          })}
        </div>
      </div>

      <h3 style={{ marginBottom: '16px', fontSize: '14px', color: 'var(--text-2)' }}>Recent Activity</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Session ID</th>
              <th>Verdict</th>
              <th>OWASP</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.entry_id}>
                <td className="mono" style={{ fontSize: '12px' }}>{new Date(log.event.ts).toLocaleString()}</td>
                <td className="mono">{log.event.session_id.substring(0, 8)}...</td>
                <td><span className={`badge ${log.event.verdict.toLowerCase()}`}>{log.event.verdict}</span></td>
                <td className="mono" style={{ fontSize: '12px' }}>{log.event.owasp_refs.join(', ') || '-'}</td>
                <td>{log.event.latency_ms.toFixed(1)}ms</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-3)' }}>No activity yet</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
