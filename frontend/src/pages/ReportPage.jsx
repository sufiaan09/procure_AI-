import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, CheckCircle, XCircle, AlertCircle, ChevronDown, ChevronUp, FileText } from 'lucide-react';

const API = '/api';

const STATUS_COLORS = {
  PASS: { bg: 'rgba(16,185,129,0.15)', color: 'var(--accent-green)', label: 'PASS', icon: CheckCircle },
  FAIL: { bg: 'rgba(239,68,68,0.15)', color: 'var(--accent-red)', label: 'FAIL', icon: XCircle },
  EXEMPT: { bg: 'rgba(59,130,246,0.15)', color: 'var(--accent-blue)', label: 'EXEMPT', icon: AlertCircle },
  NOT_APPLICABLE: { bg: 'rgba(100,116,139,0.15)', color: 'var(--text-muted)', label: 'N/A', icon: AlertCircle },
};

function Badge({ status }) {
  const s = STATUS_COLORS[status] || STATUS_COLORS.NOT_APPLICABLE;
  return (
    <span style={{
      background: s.bg, color: s.color,
      padding: '4px 12px', borderRadius: 99,
      fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap',
      display: 'inline-flex', alignItems: 'center', gap: 4
    }}>
      {s.label}
    </span>
  );
}

function EvidenceTag({ evidence }) {
  if (!evidence) return <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>No evidence</span>;
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.2)',
      borderRadius: 8, padding: '4px 12px', fontSize: 12, color: 'var(--accent-purple)',
      cursor: 'help',
    }}
      title={evidence.text_snippet}
    >
      <FileText size={12} /> Page {evidence.page_number}
      {evidence.confidence && (
        <span style={{ opacity: 0.7 }}>· {Math.round(evidence.confidence * 100)}% conf</span>
      )}
    </div>
  );
}

function BidderCard({ evaluation }) {
  const [open, setOpen] = useState(false);
  const qualified = evaluation.overall_status === 'QUALIFIED';
  const passCount = evaluation.criteria_results.filter(r => r.status === 'PASS' || r.status === 'EXEMPT').length;
  const total = evaluation.criteria_results.length;

  return (
    <div className="glass-panel fade-in delay-200" style={{
      border: `1px solid ${qualified ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
      overflow: 'hidden', marginBottom: 16,
      boxShadow: qualified ? '0 4px 20px rgba(16,185,129,0.05)' : '0 4px 20px rgba(239,68,68,0.05)'
    }}>
      {/* Header */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '20px 24px', cursor: 'pointer',
          background: qualified ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)',
          transition: 'background 0.2s'
        }}
        onMouseEnter={e => e.currentTarget.style.background = qualified ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)'}
        onMouseLeave={e => e.currentTarget.style.background = qualified ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)'}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: qualified ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)',
            color: qualified ? 'var(--accent-green)' : 'var(--accent-red)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: qualified ? '0 0 15px rgba(16,185,129,0.2)' : '0 0 15px rgba(239,68,68,0.2)'
          }}>
            {qualified ? <CheckCircle size={24} /> : <XCircle size={24} />}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>{evaluation.firm_name}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'monospace' }}>
              ID: {evaluation.bidder_id}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: qualified ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              {passCount} <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>/ {total}</span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>criteria met</div>
          </div>
          <div style={{
            padding: '6px 16px', borderRadius: 99, fontWeight: 700, fontSize: 12, letterSpacing: '0.05em',
            background: qualified ? 'var(--accent-green)' : 'var(--accent-red)', color: '#fff',
            boxShadow: qualified ? '0 4px 10px rgba(16,185,129,0.3)' : '0 4px 10px rgba(239,68,68,0.3)'
          }}>
            {evaluation.overall_status}
          </div>
          <div style={{ color: 'var(--text-muted)' }}>
            {open ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>
        </div>
      </div>

      {/* Disqualification reasons */}
      {!qualified && evaluation.disqualification_reasons.length > 0 && (
        <div style={{
          padding: '16px 24px', background: 'rgba(239,68,68,0.08)',
          borderTop: '1px solid rgba(239,68,68,0.2)',
        }}>
          <div style={{ fontSize: 12, color: 'var(--accent-red)', fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <AlertCircle size={14} /> DISQUALIFICATION REASONS
          </div>
          {evaluation.disqualification_reasons.map((r, i) => (
            <div key={i} style={{ fontSize: 13, color: 'var(--text-primary)', marginBottom: 4, display: 'flex', gap: 8 }}>
              <span style={{ color: 'var(--accent-red)' }}>•</span> {r}
            </div>
          ))}
        </div>
      )}

      {/* Expanded criteria detail */}
      {open && (
        <div style={{ borderTop: '1px solid var(--border-subtle)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
                {['Criterion', 'Status', 'Required', 'Bidder Value', 'Evidence'].map(h => (
                  <th key={h} style={{
                    padding: '12px 24px', fontSize: 11,
                    color: 'var(--text-muted)', fontWeight: 600,
                    textTransform: 'uppercase', letterSpacing: '0.05em',
                    borderBottom: '1px solid var(--border-subtle)'
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {evaluation.criteria_results.map((cr, i) => (
                <tr key={i} style={{
                  borderBottom: '1px solid var(--border-subtle)',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-panel-hover)'}
                onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)'}
                >
                  <td style={{ padding: '16px 24px', fontSize: 13, fontWeight: 500 }}>{cr.criterion}</td>
                  <td style={{ padding: '16px 24px' }}><Badge status={cr.status} /></td>
                  <td style={{ padding: '16px 24px', fontSize: 13, color: 'var(--text-secondary)' }}>{cr.required_value || '—'}</td>
                  <td style={{ padding: '16px 24px', fontSize: 13, fontWeight: cr.status === 'FAIL' ? 600 : 400, color: cr.status === 'FAIL' ? 'var(--accent-red)' : 'var(--text-primary)' }}>
                    {cr.bidder_value || '—'}
                  </td>
                  <td style={{ padding: '16px 24px' }}>
                    <EvidenceTag evidence={cr.evidence} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function ReportPage() {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetch(`${API}/reports/${reportId}`)
      .then(r => r.json())
      .then(d => { setReport(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [reportId]);

  if (loading) return <div style={{ padding: 40, color: 'var(--text-muted)', textAlign: 'center' }}>Loading report data...</div>;
  if (!report) return <div style={{ padding: 40, color: 'var(--accent-red)', textAlign: 'center' }}>Report not found.</div>;

  const c = report.tender_criteria;
  const filtered = report.evaluations.filter(e => {
    if (activeTab === 'qualified') return e.overall_status === 'QUALIFIED';
    if (activeTab === 'disqualified') return e.overall_status === 'DISQUALIFIED';
    return true;
  });

  const downloadMarkdown = async () => {
    const res = await fetch(`${API}/reports/${reportId}/markdown`);
    const text = await res.text();
    const blob = new Blob([text], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${reportId}.md`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fade-in" style={{ maxWidth: 1200, margin: '0 auto' }}>
      {/* Header Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <button
          onClick={() => navigate('/history')}
          className="btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 8, border: 'none', padding: '8px 0' }}
        >
          <ArrowLeft size={18} /> Back to History
        </button>
        <button
          onClick={downloadMarkdown}
          className="btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
        >
          <Download size={16} /> Export Audit Report (.md)
        </button>
      </div>

      {/* Main Report Header */}
      <div className="glass-panel" style={{ padding: 32, marginBottom: 32, position: 'relative', overflow: 'hidden' }}>
        {/* Glow effect */}
        <div style={{ position: 'absolute', top: -50, right: -50, width: 200, height: 200, background: 'var(--accent-blue)', filter: 'blur(80px)', opacity: 0.1, borderRadius: '50%' }}></div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 24, position: 'relative', zIndex: 1 }}>
          <div>
            <div style={{ fontSize: 13, color: 'var(--accent-blue-glow)', fontWeight: 700, marginBottom: 8, letterSpacing: '0.05em', fontFamily: 'monospace' }}>
              REPORT ID: {report.report_id}
            </div>
            <h1 className="text-gradient" style={{ fontSize: 32, fontWeight: 800, marginBottom: 12, letterSpacing: '-0.5px' }}>{report.tender_title}</h1>
            <div style={{ display: 'flex', gap: 16, color: 'var(--text-secondary)', fontSize: 14 }}>
              <span><FileText size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }}/> {report.tender_id}</span>
              <span>•</span>
              <span>Generated {new Date(report.generated_at).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })}</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <StatBox label="Total Submissions" value={report.total_bidders} color="var(--accent-blue)" />
            <StatBox label="Qualified" value={report.qualified_count} color="var(--accent-green)" />
            <StatBox label="Disqualified" value={report.disqualified_count} color="var(--accent-red)" />
          </div>
        </div>
      </div>

      {/* Tender Criteria Summary */}
      <div className="glass-panel delay-100 fade-in" style={{ padding: '24px 32px', marginBottom: 32 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Extracted Tender Criteria
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          {c.emd_amount_inr && <Chip label="EMD Required" value={`₹${c.emd_amount_inr.toLocaleString('en-IN')}`} color="#f59e0b" />}
          {c.solvency_percent && <Chip label="Solvency" value={`≥ ${c.solvency_percent}% of cost`} color="var(--accent-blue)" />}
          {c.turnover_percent && <Chip label="Turnover" value={`≥ ${c.turnover_percent}% of cost`} color="var(--accent-blue)" />}
          {c.estimated_cost_inr && <Chip label="Est. Cost" value={`₹${(c.estimated_cost_inr / 100000).toFixed(2)}L`} color="var(--accent-purple)" />}
          {c.experience && <Chip label="Experience" value="Required" color="var(--accent-green)" />}
          {c.technical_specs?.map(s => (
            <Chip key={s.parameter} label={s.parameter} value={`${s.condition} ${s.value}${s.unit}`} color="var(--text-primary)" />
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24, borderBottom: '1px solid var(--border-subtle)', paddingBottom: 16 }}>
        {[
          { key: 'all', label: `All Bidders (${report.total_bidders})` },
          { key: 'qualified', label: `Qualified (${report.qualified_count})` },
          { key: 'disqualified', label: `Disqualified (${report.disqualified_count})` },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            style={{
              padding: '8px 20px', borderRadius: 99, fontSize: 14, fontWeight: 500,
              background: activeTab === t.key ? 'var(--accent-blue)' : 'transparent',
              color: activeTab === t.key ? '#fff' : 'var(--text-secondary)',
              border: activeTab === t.key ? 'none' : '1px solid var(--border-subtle)',
              cursor: 'pointer', transition: 'all 0.2s',
              boxShadow: activeTab === t.key ? '0 4px 12px rgba(59,130,246,0.3)' : 'none'
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Results List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>No bidders found for this filter.</div>
        ) : (
          filtered.map(ev => <BidderCard key={ev.bidder_id} evaluation={ev} />)
        )}
      </div>
    </div>
  );
}

function StatBox({ label, value, color }) {
  return (
    <div className="glass-card" style={{
      padding: '16px 24px', textAlign: 'center', minWidth: 120
    }}>
      <div style={{ fontSize: 36, fontWeight: 800, color, marginBottom: 4, fontFamily: 'Outfit' }}>{value}</div>
      <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }}>{label}</div>
    </div>
  );
}

function Chip({ label, value, color }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-subtle)',
      borderRadius: 8, padding: '8px 14px', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8
    }}>
      <span style={{ color: 'var(--text-secondary)' }}>{label}:</span>
      <span style={{ color, fontWeight: 600 }}>{value}</span>
    </div>
  );
}
