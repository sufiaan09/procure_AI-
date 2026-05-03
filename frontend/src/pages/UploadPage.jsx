import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, FileText, CheckCircle, ArrowRight, ArrowLeft } from 'lucide-react';

const API = '/api';

function FileDropZone({ label, accept, multiple, onChange, files }) {
  const inputRef = useRef();
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault(); 
    setDragging(false);
    const dropped = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
    if (dropped.length) onChange(multiple ? dropped : [dropped[0]]);
  };

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      style={{
        border: `2px dashed ${dragging ? 'var(--accent-blue)' : 'var(--border-subtle)'}`,
        borderRadius: 16, padding: '40px 20px',
        textAlign: 'center', cursor: 'pointer',
        background: dragging ? 'rgba(59,130,246,0.05)' : 'var(--bg-input)',
        transition: 'all 0.2s ease',
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept || '.pdf'}
        multiple={multiple}
        style={{ display: 'none' }}
        onChange={e => onChange(Array.from(e.target.files))}
      />
      <div style={{ 
        width: 64, height: 64, borderRadius: '50%', 
        background: 'rgba(255,255,255,0.05)', 
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 16px', color: 'var(--text-muted)'
      }}>
        <UploadIcon size={28} />
      </div>
      <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Drag and drop PDFs here, or click to browse</div>

      {files && files.length > 0 && (
        <div style={{ marginTop: 24, display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
          {files.map((f, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: 'rgba(59,130,246,0.15)', color: 'var(--accent-blue)',
              padding: '6px 12px', borderRadius: 99, fontSize: 12, fontWeight: 500
            }}>
              <FileText size={14} /> {f.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Step({ num, title, active, done }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, opacity: active || done ? 1 : 0.5 }}>
      <div style={{
        width: 32, height: 32, borderRadius: '50%',
        background: done ? 'var(--accent-green)' : active ? 'var(--accent-blue)' : 'var(--bg-input)',
        color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 14, fontWeight: 600, flexShrink: 0,
        boxShadow: active ? '0 0 15px rgba(59,130,246,0.3)' : 'none',
        transition: 'all 0.3s ease',
      }}>
        {done ? <CheckCircle size={16} /> : num}
      </div>
      <span style={{ fontSize: 14, fontWeight: active ? 600 : 500, color: active || done ? 'var(--text-primary)' : 'var(--text-muted)' }}>
        {title}
      </span>
    </div>
  );
}

export default function UploadPage() {
  const navigate = useNavigate();
  const [phase, setPhase] = useState(1);
  const [tenderId, setTenderId] = useState('');
  const [tenderFile, setTenderFile] = useState([]);
  const [bidderFiles, setBidderFiles] = useState([]);
  const [bidderNames, setBidderNames] = useState(['']);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [parsedCriteria, setParsedCriteria] = useState(null);

  const parseStep = async () => {
    if (!tenderId || !tenderFile[0]) return setError('Provide a Tender ID and PDF');
    setLoading(true); setError(''); setStatus('Extracting criteria from tender PDF...');

    const form = new FormData();
    form.append('tender_id', tenderId);
    form.append('file', tenderFile[0]);

    try {
      const res = await fetch(`${API}/tender/parse`, { method: 'POST', body: form });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || 'Extraction failed');
      setParsedCriteria(data.criteria);
      setStatus('');
      setPhase(2);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const runFull = async () => {
    if (!bidderFiles.length) return setError('Upload at least one bidder submission');
    const names = bidderNames.filter(n => n.trim());
    if (names.length !== bidderFiles.length) return setError('Provide a firm name for every bidder PDF');

    setLoading(true); setError(''); setStatus('Processing bidder submissions & running evaluation...');

    const form = new FormData();
    form.append('tender_id', tenderId);
    form.append('tender_file', tenderFile[0]);
    form.append('bidder_names', JSON.stringify(names));
    bidderFiles.forEach(f => form.append('bidder_files', f));

    try {
      const res = await fetch(`${API}/pipeline/full`, { method: 'POST', body: form });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || 'Evaluation failed');
      navigate(`/reports/${data.report.report_id}`);
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: 40, textAlign: 'center' }}>
        <h1 className="text-gradient" style={{ fontSize: 36, fontWeight: 800, marginBottom: 12, letterSpacing: '-0.5px' }}>New AI Evaluation</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 16 }}>
          Run the automated evaluation pipeline to analyze eligibility against tender criteria.
        </p>
      </div>

      {/* Progress steps */}
      <div className="glass-panel" style={{
        display: 'flex', gap: 24, alignItems: 'center', marginBottom: 32,
        padding: '20px 32px', justifyContent: 'space-between'
      }}>
        <Step num={1} title="Parse Tender" active={phase === 1} done={phase > 1} />
        <div style={{ flex: 1, height: 2, background: 'var(--border-subtle)' }} />
        <Step num={2} title="Add Bidders" active={phase === 2} done={phase > 2} />
        <div style={{ flex: 1, height: 2, background: 'var(--border-subtle)' }} />
        <Step num={3} title="Run Evaluation" active={phase === 3} done={false} />
      </div>

      <div className="glass-panel delay-200 fade-in" style={{ padding: 40, position: 'relative', overflow: 'hidden' }}>
        {/* Phase 1: Tender */}
        {phase === 1 && (
          <div className="fade-in">
            <h2 style={{ fontSize: 22, fontWeight: 600, marginBottom: 28, display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 6, height: 24, background: 'var(--accent-blue)', borderRadius: 4 }}></div>
              Tender Information
            </h2>

            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, fontWeight: 500 }}>
                Tender ID Reference *
              </label>
              <input
                type="text"
                className="glass-input"
                value={tenderId}
                onChange={e => setTenderId(e.target.value)}
                placeholder="e.g. PAI-9MM-2024-001"
                style={{ width: '100%', fontSize: 15 }}
              />
            </div>

            <div style={{ marginBottom: 32 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, fontWeight: 500 }}>
                Tender Notice Document (PDF) *
              </label>
              <FileDropZone
                label="Upload Tender PDF"
                onChange={setTenderFile}
                files={tenderFile}
              />
            </div>

            {error && <div style={{ color: 'var(--accent-red)', fontSize: 14, marginBottom: 16, background: 'rgba(239, 68, 68, 0.1)', padding: 12, borderRadius: 8 }}>{error}</div>}
            {status && <div style={{ color: 'var(--accent-blue)', fontSize: 14, marginBottom: 16 }}>{status}</div>}

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={parseStep}
                disabled={loading || !tenderId || !tenderFile[0]}
                className="btn-primary"
                style={{ display: 'flex', alignItems: 'center', gap: 8, width: loading ? '100%' : 'auto', justifyContent: 'center' }}
              >
                {loading ? 'Extracting Criteria with AI...' : <>Extract Criteria <ArrowRight size={18} /></>}
              </button>
            </div>
          </div>
        )}

        {/* Phase 2: Bidders */}
        {phase === 2 && (
          <div className="fade-in">
            <h2 style={{ fontSize: 22, fontWeight: 600, marginBottom: 28, display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 6, height: 24, background: 'var(--accent-purple)', borderRadius: 4 }}></div>
              Bidder Submissions
            </h2>

            {parsedCriteria && (
              <div style={{
                background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)',
                borderRadius: 12, padding: '16px 20px', marginBottom: 32, display: 'flex', alignItems: 'flex-start', gap: 12
              }}>
                <CheckCircle size={20} color="var(--accent-green)" style={{ marginTop: 2 }} />
                <div>
                  <div style={{ color: 'var(--accent-green)', fontWeight: 600, marginBottom: 4, fontSize: 15 }}>
                    Criteria successfully extracted
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    <strong>{parsedCriteria.tender_title}</strong><br />
                    EMD: ₹{(parsedCriteria.emd_amount_inr || 0).toLocaleString('en-IN')} |
                    Found {parsedCriteria.mandatory_documents?.length} mandatory documents.
                  </div>
                </div>
              </div>
            )}

            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, fontWeight: 500 }}>
                Upload Bidder Submissions (Multi-select) *
              </label>
              <FileDropZone
                label="Bidder Submission PDFs"
                multiple
                onChange={files => {
                  setBidderFiles(files);
                  setBidderNames(files.map((_, i) => bidderNames[i] || ''));
                }}
                files={bidderFiles}
              />
            </div>

            {bidderFiles.length > 0 && (
              <div className="glass-card" style={{ marginBottom: 32, padding: 24 }}>
                <label style={{ display: 'block', fontSize: 14, color: 'var(--text-secondary)', marginBottom: 16, fontWeight: 600 }}>
                  Assign Firm Names
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {bidderFiles.map((f, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                      <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text-primary)' }}>
                        <FileText size={16} color="var(--text-muted)" />
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.name}</span>
                      </div>
                      <input
                        type="text"
                        className="glass-input"
                        value={bidderNames[i] || ''}
                        onChange={e => {
                          const n = [...bidderNames]; n[i] = e.target.value; setBidderNames(n);
                        }}
                        placeholder="Enter firm name"
                        style={{ flex: 1 }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && <div style={{ color: 'var(--accent-red)', fontSize: 14, marginBottom: 16, background: 'rgba(239, 68, 68, 0.1)', padding: 12, borderRadius: 8 }}>{error}</div>}
            {status && <div style={{ color: 'var(--accent-blue)', fontSize: 14, marginBottom: 16 }}>{status}</div>}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button onClick={() => setPhase(1)} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <ArrowLeft size={18} /> Back
              </button>
              <button
                onClick={runFull}
                disabled={loading || !bidderFiles.length}
                className="btn-primary"
                style={{ 
                  background: 'linear-gradient(135deg, var(--accent-green), #059669)',
                  display: 'flex', alignItems: 'center', gap: 8, boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)'
                }}
              >
                {loading ? 'Evaluating...' : <>Run AI Evaluation <ArrowRight size={18} /></>}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
