import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, ChevronRight, FileText } from 'lucide-react';

const API = '/api';

export default function HistoryStore() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API}/reports`)
      .then(r => r.json())
      .then(d => { setReports(d.reports || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const filteredReports = reports.filter(r => 
    r.tender_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.report_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fade-in" style={{ maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 32 }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: 32, fontWeight: 800, marginBottom: 8, letterSpacing: '-0.5px' }}>Evaluation History</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 16 }}>View and audit past tender evaluations.</p>
        </div>
        
        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
            <input 
              type="text" 
              className="glass-input" 
              placeholder="Search evaluations..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: 280, paddingLeft: 36, paddingRight: 12, height: 40 }}
            />
          </div>
          <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 8, height: 40 }}>
            <Filter size={16} /> Filter
          </button>
        </div>
      </div>

      <div className="glass-panel delay-100 fade-in" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-subtle)' }}>
              <th style={{ padding: '16px 24px', color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Report ID</th>
              <th style={{ padding: '16px 24px', color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Tender Information</th>
              <th style={{ padding: '16px 24px', color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Bidders</th>
              <th style={{ padding: '16px 24px', color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</th>
              <th style={{ padding: '16px 24px', color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Date Generated</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="6" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</td></tr>
            ) : filteredReports.length === 0 ? (
              <tr><td colSpan="6" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>No evaluations found.</td></tr>
            ) : (
              filteredReports.map((r) => {
                const passRate = r.total_bidders > 0 ? Math.round((r.qualified_count / r.total_bidders) * 100) : 0;
                return (
                  <tr 
                    key={r.report_id} 
                    style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.2s', cursor: 'pointer' }}
                    onClick={() => navigate(`/reports/${r.report_id}`)}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-panel-hover)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '16px 24px', fontFamily: 'monospace', color: 'var(--accent-blue)', fontSize: 13 }}>
                      {r.report_id.substring(0, 8)}...
                    </td>
                    <td style={{ padding: '16px 24px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{ background: 'rgba(255,255,255,0.05)', padding: 8, borderRadius: 8 }}>
                          <FileText size={16} color="var(--text-muted)" />
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14 }}>{r.tender_title}</div>
                          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>ID: {r.tender_id}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '16px 24px' }}>
                      <div style={{ fontWeight: 600 }}>{r.total_bidders}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Total Submissions</div>
                    </td>
                    <td style={{ padding: '16px 24px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ width: 40, height: 4, background: 'rgba(255,255,255,0.1)', borderRadius: 2, overflow: 'hidden' }}>
                          <div style={{ width: `${passRate}%`, height: '100%', background: 'var(--accent-green)' }}></div>
                        </div>
                        <span style={{ fontSize: 13, fontWeight: 500 }}>{r.qualified_count} Passed</span>
                      </div>
                    </td>
                    <td style={{ padding: '16px 24px', fontSize: 13, color: 'var(--text-secondary)' }}>
                      {new Date(r.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </td>
                    <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                      <ChevronRight size={20} color="var(--text-muted)" />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
