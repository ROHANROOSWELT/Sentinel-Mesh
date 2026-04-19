import { useState } from 'react';
import { api } from '../api';

export default function Benchmark() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);

  const runBenchmark = async () => {
    setRunning(true);
    setResults(null);
    try {
      const resp = await api.benchmark();
      setResults(resp);
    } catch (e) {
      console.error(e);
    }
    setRunning(false);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2>Deterministic Benchmark Engine</h2>
        <button className="btn btn-primary" onClick={runBenchmark} disabled={running}>
          {running ? 'Running 50 Cases...' : 'Run Benchmark'}
        </button>
      </div>

      {running && <div style={{ fontSize: '14px', color: 'var(--text-2)' }}>Executing 50 test cases against the detection engine...</div>}

      {results && (
        <>
          <div className="metric-grid" style={{ marginBottom: '32px' }}>
            <div className="metric-card">
              <span className="metric-title">Total Tested</span>
              <span className="metric-value">{results.summary.tested}</span>
            </div>
            <div className="metric-card">
              <span className="metric-title">Detected</span>
              <span className="metric-value" style={{ color: 'var(--success)' }}>{results.summary.detected}</span>
            </div>
            <div className="metric-card">
              <span className="metric-title">Missed</span>
              <span className="metric-value" style={{ color: results.summary.missed > 0 ? 'var(--danger)' : 'var(--text)' }}>
                {results.summary.missed}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-title">Detection Rate</span>
              <span className="metric-value">{results.summary.detection_rate}%</span>
            </div>
          </div>

          <h3 style={{ marginBottom: '16px', fontSize: '14px', color: 'var(--text-2)' }}>Per-Case Results</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Input (Truncated)</th>
                  <th>Risk Score</th>
                  <th>Expected</th>
                  <th>Actual</th>
                </tr>
              </thead>
              <tbody>
                {results.results.map((r, i) => (
                  <tr key={i} style={{ backgroundColor: r.detected ? 'var(--success-light)' : 'var(--danger-light)' }}>
                    <td style={{ fontSize: '12px', fontWeight: '500' }}>{r.category}</td>
                    <td className="mono" style={{ fontSize: '12px' }}>{r.input}</td>
                    <td style={{ fontWeight: 'bold' }}>{r.risk_score}</td>
                    <td>{r.expected}</td>
                    <td><span className={`badge ${r.actual.toLowerCase()}`}>{r.actual}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
