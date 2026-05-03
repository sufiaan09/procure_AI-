import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, FileText, CheckCircle, XCircle } from 'lucide-react';

const API = '/api';

export default function DemoPage() {
  const [demoResult, setDemoResult] = useState(null);
  const [running, setRunning] = useState(false);
  const navigate = useNavigate();

  const runDemo = async () => {
    setRunning(true);
    try {
      const res = await fetch(`${API}/demo/evaluate`, { method: "POST" });
      const data = await res.json();
      setDemoResult(data.report);
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', animation: 'fadeIn 0.5s ease', textAlign: 'center', padding: '40px 0' }}>
      
      <div style={{
        width: 80, height: 80, borderRadius: 24, margin: '0 auto 32px',
        background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: 'var(--shadow-glow)'
      }}>
        <Play size={40} color="white" fill="white" />
      </div>

      <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 16 }}>Run System Demonstration</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: 16, marginBottom: 40, maxWidth: 600, margin: '0 auto 40px' }}>
        Don't have any tender PDFs handy? Run our built-in demonstration. This simulates the exact 
        AI-evaluation pipeline using pre-loaded sample data from a 9MM ammunition tender.
      </p>

      {!demoResult ? (
        <button 
          onClick={runDemo} 
          disabled={running} 
          className="btn-primary" 
          style={{ fontSize: 16, padding: '16px 32px', borderRadius: 12 }}
        >
          {running ? 'Simulating Evaluation Pipeline...' : 'Start Demo Evaluation'}
        </button>
      ) : (
        <div style={{ animation: 'fadeIn 0.5s ease' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'rgba(16,185,129,0.1)', color: 'var(--accent-green)',
            padding: '12px 24px', borderRadius: 99, fontWeight: 600, fontSize: 16,
            marginBottom: 32
          }}>
            <CheckCircle size={20} /> Demo Evaluation Completed Successfully
          </div>
          
          <div className="glass-panel" style={{ padding: 32, textAlign: 'left' }}>
            <div style={{ fontSize: 12, color: 'var(--accent-blue)', fontFamily: 'monospace', marginBottom: 8 }}>
              REPORT ID: {demoResult.report_id}
            </div>
            <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 24 }}>{demoResult.tender_title}</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
              <Stat label="Total Processed" value={demoResult.total_bidders} color="var(--accent-blue)" />
              <Stat label="Qualified" value={demoResult.qualified_count} color="var(--accent-green)" />
              <Stat label="Disqualified" value={demoResult.disqualified_count} color="var(--accent-red)" />
            </div>

            <button 
              onClick={() => navigate(`/reports/${demoResult.report_id}`)}
              className="btn-primary" 
              style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: 8, alignItems: 'center' }}
            >
              <FileText size={18} /> View Full Detailed Report
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({label, value, color}) {
  return (
    <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)', borderRadius: 12, padding: '20px', textAlign: 'center' }}>
      <div style={{ fontSize: 32, fontWeight: 700, color, marginBottom: 8 }}>{value}</div>
      <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 500 }}>{label}</div>
    </div>
  );
}
