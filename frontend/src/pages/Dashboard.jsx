import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { FileText, CheckCircle, XCircle, TrendingUp, Users, Activity } from 'lucide-react';

const API = '/api';

export default function Dashboard() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API}/reports`)
      .then(r => r.json())
      .then(d => { setReports(d.reports || []); setLoading(false) })
      .catch(() => setLoading(false));
  }, []);

  const totalBidders = reports.reduce((s, r) => s + r.total_bidders, 0);
  const totalQualified = reports.reduce((s, r) => s + r.qualified_count, 0);
  const totalDisqualified = totalBidders - totalQualified;

  const chartData = [
    { name: 'Qualified', value: totalQualified, color: 'var(--accent-green)' },
    { name: 'Disqualified', value: totalDisqualified, color: 'var(--accent-red)' }
  ];

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }} className="fade-in">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 40 }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: 36, fontWeight: 800, marginBottom: 8, letterSpacing: '-0.5px' }}>
            System Overview
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 16 }}>Welcome back, Admin. Here's what's happening today.</p>
        </div>
        <button onClick={() => navigate('/upload')} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <FileText size={18} /> New Evaluation
        </button>
      </header>

      {/* Top Stats */}
      <div className="fade-in delay-100" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24, marginBottom: 40 }}>
        <StatCard title="Total Evaluations" value={reports.length} icon={Activity} color="var(--accent-blue)" />
        <StatCard title="Total Bidders" value={totalBidders} icon={Users} color="var(--accent-purple)" />
        <StatCard title="Qualified" value={totalQualified} icon={CheckCircle} color="var(--accent-green)" />
        <StatCard title="Disqualified" value={totalDisqualified} icon={XCircle} color="var(--accent-red)" />
      </div>

      <div className="fade-in delay-200" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
        {/* Main Chart Area */}
        <div className="glass-panel" style={{ padding: 28, display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 28, display: 'flex', alignItems: 'center', gap: 10 }}>
            <TrendingUp size={20} color="var(--accent-blue)" /> Evaluation Results
          </h2>
          <div style={{ flex: 1, minHeight: 300 }}>
            {totalBidders > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="var(--text-muted)" tick={{ fill: 'var(--text-secondary)' }} />
                  <YAxis stroke="var(--text-muted)" tick={{ fill: 'var(--text-secondary)' }} />
                  <Tooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }} 
                    contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 8, color: '#fff' }} 
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={60}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                No evaluation data available yet.
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity List */}
        <div className="glass-panel" style={{ padding: 28 }}>
          <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 28 }}>Recent Activity</h2>
          {loading ? (
            <div style={{ color: 'var(--text-muted)' }}>Loading...</div>
          ) : reports.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {reports.slice(0, 5).map(r => (
                <div key={r.report_id} style={{ display: 'flex', alignItems: 'flex-start', gap: 14, paddingBottom: 16, borderBottom: '1px solid var(--border-subtle)', transition: 'all 0.2s' }}>
                  <div style={{ 
                    width: 36, height: 36, borderRadius: 10, 
                    background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-blue)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 
                  }}>
                    <FileText size={18} />
                  </div>
                  <div>
                    <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4, cursor: 'pointer', transition: 'color 0.2s' }}
                         onClick={() => navigate(`/reports/${r.report_id}`)}
                         onMouseEnter={e => e.target.style.color = 'var(--accent-blue-glow)'}
                         onMouseLeave={e => e.target.style.color = 'var(--text-primary)'}>
                      {r.tender_title}
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                      Processed {r.total_bidders} bidders
                    </div>
                  </div>
                </div>
              ))}
              <button onClick={() => navigate('/history')} className="btn-secondary" style={{ width: '100%', marginTop: 8 }}>
                View All History
              </button>
            </div>
          ) : (
             <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px 0' }}>
               No recent activity.
             </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <div className="glass-card" style={{ padding: 24, position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500, marginBottom: 12 }}>{title}</div>
          <div style={{ fontSize: 36, fontWeight: 700, color: '#fff', fontFamily: 'Outfit' }}>{value}</div>
        </div>
        <div style={{ 
          background: `color-mix(in srgb, ${color} 15%, transparent)`, 
          padding: 12, borderRadius: 12 
        }}>
          <Icon size={24} color={color} />
        </div>
      </div>
      {/* Decorative background glow */}
      <div style={{
        position: 'absolute', bottom: -20, right: -20, width: 80, height: 80,
        background: color, filter: 'blur(40px)', opacity: 0.15, borderRadius: '50%'
      }}></div>
    </div>
  );
}
