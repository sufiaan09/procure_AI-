import os

# Create pages folder
os.makedirs('src/pages', exist_ok=True)
os.makedirs('src/components', exist_ok=True)

# ── index.css ──────────────────────────────────────────────
open('src/index.css', 'w', encoding='utf-8').write('''
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0a0e1a; --bg2: #0f1629; --bg3: #151d35;
  --border: #1e2d4a; --border2: #2a3f6a;
  --text: #e2e8f0; --text2: #94a3b8; --text3: #4a6080;
  --accent: #3b82f6; --green: #10b981; --red: #ef4444;
  --amber: #f59e0b; --purple: #8b5cf6;
}
body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
button { cursor: pointer; font-family: system-ui; }
input, select, textarea { font-family: system-ui; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
''')

# ── Login Page ──────────────────────────────────────────────
open('src/pages/Login.jsx', 'w', encoding='utf-8').write('''
import { useState } from "react"

const USERS = {
  "admin": { password: "crpf2024", role: "Admin", name: "Admin Officer" },
  "evaluator": { password: "eval123", role: "Evaluator", name: "Evaluation Officer" },
  "viewer": { password: "view123", role: "Viewer", name: "View Only User" }
}

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleLogin = () => {
    const user = USERS[username.toLowerCase()]
    if (user && user.password === password) {
      onLogin({ username, ...user })
    } else {
      setError("Invalid username or password")
    }
  }

  return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"var(--bg)"}}>
      <div style={{width:420,background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:16,padding:40}}>
        <div style={{textAlign:"center",marginBottom:32}}>
          <div style={{width:56,height:56,background:"var(--accent)",borderRadius:12,display:"flex",alignItems:"center",justifyContent:"center",fontSize:24,fontWeight:700,color:"#fff",margin:"0 auto 16px"}}>C</div>
          <h1 style={{fontSize:22,fontWeight:700,marginBottom:6}}>CRPF Tender Platform</h1>
          <p style={{color:"var(--text2)",fontSize:13}}>Sign in to your account</p>
        </div>

        <div style={{marginBottom:16}}>
          <label style={{display:"block",fontSize:12,color:"var(--text2)",marginBottom:6}}>USERNAME</label>
          <input value={username} onChange={e=>setUsername(e.target.value)}
            placeholder="Enter username"
            style={{width:"100%",padding:"10px 14px",background:"var(--bg3)",border:"1px solid var(--border2)",borderRadius:8,color:"var(--text)",fontSize:14,outline:"none"}} />
        </div>

        <div style={{marginBottom:20}}>
          <label style={{display:"block",fontSize:12,color:"var(--text2)",marginBottom:6}}>PASSWORD</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)}
            onKeyDown={e=>e.key==="Enter"&&handleLogin()}
            placeholder="Enter password"
            style={{width:"100%",padding:"10px 14px",background:"var(--bg3)",border:"1px solid var(--border)",borderRadius:8,color:"var(--text)",fontSize:14,outline:"none"}} />
        </div>

        {error && <div style={{color:"var(--red)",fontSize:13,marginBottom:16,padding:"8px 12px",background:"rgba(239,68,68,0.1)",borderRadius:6}}>{error}</div>}

        <button onClick={handleLogin}
          style={{width:"100%",padding:"11px",background:"var(--accent)",color:"#fff",borderRadius:8,fontSize:14,fontWeight:600,border:"none"}}>
          Sign In
        </button>

        <div style={{marginTop:24,padding:16,background:"var(--bg3)",borderRadius:8,fontSize:12,color:"var(--text3)"}}>
          <div style={{marginBottom:6,color:"var(--text2)",fontWeight:500}}>Demo Accounts:</div>
          <div>admin / crpf2024 (full access)</div>
          <div>evaluator / eval123 (evaluate only)</div>
          <div>viewer / view123 (view reports only)</div>
        </div>
      </div>
    </div>
  )
}
''')

# ── Sidebar ──────────────────────────────────────────────
open('src/components/Sidebar.jsx', 'w', encoding='utf-8').write('''
export default function Sidebar({ page, setPage, user, onLogout }) {
  const nav = [
    { id: "dashboard", label: "Dashboard", icon: "D" },
    { id: "upload", label: "Upload Documents", icon: "U" },
    { id: "evaluate", label: "Run Evaluation", icon: "E" },
    { id: "history", label: "Report History", icon: "H" },
    { id: "admin", label: "Admin Panel", icon: "A", adminOnly: true },
  ]

  return (
    <aside style={{width:220,background:"var(--bg2)",borderRight:"1px solid var(--border)",display:"flex",flexDirection:"column",position:"fixed",top:0,left:0,bottom:0}}>
      <div style={{padding:"20px",borderBottom:"1px solid var(--border)"}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <div style={{width:32,height:32,background:"var(--accent)",borderRadius:6,display:"flex",alignItems:"center",justifyContent:"center",fontWeight:700,color:"#fff"}}>C</div>
          <div>
            <div style={{fontSize:13,fontWeight:600}}>CRPF Tender</div>
            <div style={{fontSize:11,color:"var(--text3)"}}>Evaluation Platform</div>
          </div>
        </div>
      </div>

      <nav style={{flex:1,padding:"12px 0"}}>
        {nav.filter(n => !n.adminOnly || user.role === "Admin").map(n => (
          <div key={n.id} onClick={() => setPage(n.id)}
            style={{display:"flex",alignItems:"center",gap:10,padding:"10px 20px",cursor:"pointer",
              background: page===n.id ? "rgba(59,130,246,0.1)" : "transparent",
              borderLeft: page===n.id ? "2px solid var(--accent)" : "2px solid transparent",
              color: page===n.id ? "var(--accent)" : "var(--text2)",
              fontSize:13,transition:"all 0.15s"}}>
            <span style={{width:20,height:20,background:"var(--bg3)",borderRadius:4,display:"flex",alignItems:"center",justifyContent:"center",fontSize:10,fontWeight:700}}>{n.icon}</span>
            {n.label}
          </div>
        ))}
      </nav>

      <div style={{padding:"16px 20px",borderTop:"1px solid var(--border)"}}>
        <div style={{fontSize:13,fontWeight:500,marginBottom:2}}>{user.name}</div>
        <div style={{fontSize:11,color:"var(--accent)",marginBottom:10}}>{user.role}</div>
        <button onClick={onLogout}
          style={{width:"100%",padding:"7px",background:"transparent",border:"1px solid var(--border2)",color:"var(--text2)",borderRadius:6,fontSize:12}}>
          Sign Out
        </button>
      </div>
    </aside>
  )
}
''')

# ── Dashboard Page ──────────────────────────────────────────────
open('src/pages/Dashboard.jsx', 'w', encoding='utf-8').write('''
import { useEffect, useState } from "react"

export default function Dashboard({ setPage }) {
  const [reports, setReports] = useState([])

  useEffect(() => {
    fetch("/api/reports").then(r=>r.json()).then(d=>setReports(d.reports||[])).catch(()=>{})
  }, [])

  const total = reports.length
  const qualified = reports.reduce((s,r)=>s+r.qualified_count,0)
  const bidders = reports.reduce((s,r)=>s+r.total_bidders,0)

  return (
    <div>
      <h1 style={{fontSize:22,fontWeight:700,marginBottom:6}}>Dashboard</h1>
      <p style={{color:"var(--text2)",fontSize:13,marginBottom:28}}>Overview of all tender evaluations</p>

      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:16,marginBottom:32}}>
        {[
          {label:"Total Reports",value:total,color:"var(--accent)"},
          {label:"Total Bidders",value:bidders,color:"var(--purple)"},
          {label:"Qualified Bidders",value:qualified,color:"var(--green)"},
        ].map(s=>(
          <div key={s.label} style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,padding:"20px 24px",borderTop:`3px solid ${s.color}`}}>
            <div style={{fontSize:28,fontWeight:700,color:s.color}}>{s.value}</div>
            <div style={{fontSize:12,color:"var(--text3)",marginTop:4}}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,overflow:"hidden"}}>
        <div style={{padding:"16px 20px",borderBottom:"1px solid var(--border)",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <span style={{fontWeight:500}}>Recent Reports</span>
          <button onClick={()=>setPage("upload")}
            style={{background:"var(--accent)",color:"#fff",padding:"7px 16px",borderRadius:6,fontSize:12,fontWeight:600,border:"none"}}>
            + New Evaluation
          </button>
        </div>
        {reports.length === 0 ? (
          <div style={{padding:48,textAlign:"center",color:"var(--text3)"}}>
            No reports yet. Run a demo or upload documents.
          </div>
        ) : (
          <table style={{width:"100%",borderCollapse:"collapse"}}>
            <thead>
              <tr style={{borderBottom:"1px solid var(--border)"}}>
                {["Report ID","Tender","Bidders","Qualified","Date"].map(h=>(
                  <th key={h} style={{padding:"10px 20px",textAlign:"left",fontSize:11,color:"var(--text3)",fontWeight:600,textTransform:"uppercase",letterSpacing:"0.05em"}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {reports.map(r=>(
                <tr key={r.report_id} style={{borderBottom:"1px solid var(--border)"}}>
                  <td style={{padding:"12px 20px",fontFamily:"monospace",fontSize:12,color:"var(--accent)"}}>{r.report_id}</td>
                  <td style={{padding:"12px 20px",fontWeight:500}}>{r.tender_title}</td>
                  <td style={{padding:"12px 20px",textAlign:"center"}}>{r.total_bidders}</td>
                  <td style={{padding:"12px 20px",textAlign:"center"}}>
                    <span style={{background:"rgba(16,185,129,0.1)",color:"var(--green)",padding:"2px 10px",borderRadius:99,fontSize:12}}>{r.qualified_count}</span>
                  </td>
                  <td style={{padding:"12px 20px",fontSize:12,color:"var(--text3)"}}>{new Date(r.generated_at).toLocaleDateString("en-IN")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
''')

# ── Upload Page ──────────────────────────────────────────────
open('src/pages/Upload.jsx', 'w', encoding='utf-8').write('''
import { useState } from "react"

export default function Upload({ setPage }) {
  const [tenderFile, setTenderFile] = useState(null)
  const [bidderFiles, setBidderFiles] = useState([])
  const [bidderNames, setBidderNames] = useState([])
  const [tenderId, setTenderId] = useState("")
  const [status, setStatus] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const runDemo = async () => {
    setLoading(true); setError(""); setStatus("Running demo evaluation...")
    try {
      const res = await fetch("/api/demo/evaluate", { method: "POST" })
      const data = await res.json()
      if (data.success) { setStatus("Demo complete! Go to Report History to view."); setPage("history") }
      else throw new Error("Demo failed")
    } catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const addBidder = (files) => {
    const arr = Array.from(files)
    setBidderFiles(prev => [...prev, ...arr])
    setBidderNames(prev => [...prev, ...arr.map(f => f.name.replace(".pdf",""))])
  }

  const removeBidder = (i) => {
    setBidderFiles(prev => prev.filter((_,idx)=>idx!==i))
    setBidderNames(prev => prev.filter((_,idx)=>idx!==i))
  }

  return (
    <div>
      <h1 style={{fontSize:22,fontWeight:700,marginBottom:6}}>Upload Documents</h1>
      <p style={{color:"var(--text2)",fontSize:13,marginBottom:28}}>Upload tender and bidder documents to run an evaluation</p>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:24}}>

        <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,padding:24}}>
          <h2 style={{fontSize:15,fontWeight:600,marginBottom:16}}>Tender Document</h2>
          <input value={tenderId} onChange={e=>setTenderId(e.target.value)}
            placeholder="Tender ID e.g. CRPF-2024-001"
            style={{width:"100%",padding:"9px 12px",background:"var(--bg3)",border:"1px solid var(--border2)",borderRadius:6,color:"var(--text)",fontSize:13,marginBottom:12,outline:"none"}} />
          <label style={{display:"block",border:"2px dashed var(--border2)",borderRadius:10,padding:24,textAlign:"center",cursor:"pointer"}}>
            <input type="file" accept=".pdf" style={{display:"none"}} onChange={e=>setTenderFile(e.target.files[0])} />
            <div style={{fontSize:28,marginBottom:8}}>+</div>
            <div style={{fontSize:13,fontWeight:500}}>{tenderFile ? tenderFile.name : "Drop tender PDF here"}</div>
            <div style={{fontSize:11,color:"var(--text3)",marginTop:4}}>Click to browse</div>
          </label>
        </div>

        <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,padding:24}}>
          <h2 style={{fontSize:15,fontWeight:600,marginBottom:16}}>Bidder Submissions</h2>
          <label style={{display:"block",border:"2px dashed var(--border2)",borderRadius:10,padding:16,textAlign:"center",cursor:"pointer",marginBottom:12}}>
            <input type="file" accept=".pdf" multiple style={{display:"none"}} onChange={e=>addBidder(e.target.files)} />
            <div style={{fontSize:13,fontWeight:500}}>+ Add Bidder PDFs</div>
            <div style={{fontSize:11,color:"var(--text3)",marginTop:2}}>Multiple files allowed</div>
          </label>
          {bidderFiles.map((f,i)=>(
            <div key={i} style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}>
              <input value={bidderNames[i]||""} onChange={e=>{const n=[...bidderNames];n[i]=e.target.value;setBidderNames(n)}}
                placeholder="Firm name"
                style={{flex:1,padding:"6px 10px",background:"var(--bg3)",border:"1px solid var(--border)",borderRadius:6,color:"var(--text)",fontSize:12,outline:"none"}} />
              <span style={{fontSize:11,color:"var(--text3)",maxWidth:80,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{f.name}</span>
              <button onClick={()=>removeBidder(i)} style={{background:"rgba(239,68,68,0.1)",color:"var(--red)",border:"none",borderRadius:4,padding:"4px 8px",fontSize:11}}>X</button>
            </div>
          ))}
        </div>
      </div>

      {error && <div style={{color:"var(--red)",fontSize:13,marginBottom:12,padding:"10px 14px",background:"rgba(239,68,68,0.08)",borderRadius:8}}>{error}</div>}
      {status && <div style={{color:"var(--green)",fontSize:13,marginBottom:12,padding:"10px 14px",background:"rgba(16,185,129,0.08)",borderRadius:8}}>{status}</div>}

      <div style={{display:"flex",gap:12}}>
        <button onClick={runDemo} disabled={loading}
          style={{background:loading?"var(--border)":"var(--accent)",color:"#fff",padding:"11px 28px",borderRadius:8,fontSize:13,fontWeight:600,border:"none"}}>
          {loading ? "Running..." : "Run Demo Evaluation"}
        </button>
        <button disabled style={{background:"var(--bg2)",color:"var(--text3)",padding:"11px 28px",borderRadius:8,fontSize:13,border:"1px solid var(--border)"}}>
          Upload & Evaluate (needs API key)
        </button>
      </div>
    </div>
  )
}
''')

# ── History Page ──────────────────────────────────────────────
open('src/pages/History.jsx', 'w', encoding='utf-8').write('''
import { useEffect, useState } from "react"

function BidderCard({ ev }) {
  const [open, setOpen] = useState(false)
  const ok = ev.overall_status === "QUALIFIED"
  return (
    <div style={{border:"1px solid "+(ok?"rgba(16,185,129,0.25)":"rgba(239,68,68,0.25)"),borderRadius:10,marginBottom:10,overflow:"hidden"}}>
      <div onClick={()=>setOpen(!open)} style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:"12px 16px",cursor:"pointer",background:ok?"rgba(16,185,129,0.04)":"rgba(239,68,68,0.04)"}}>
        <div>
          <span style={{fontWeight:600,marginRight:10}}>{ev.firm_name}</span>
          <span style={{fontSize:11,color:"var(--text3)",fontFamily:"monospace"}}>{ev.bidder_id}</span>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <span style={{background:ok?"var(--green)":"var(--red)",color:"#fff",padding:"3px 12px",borderRadius:99,fontSize:11,fontWeight:600}}>{ev.overall_status}</span>
          <span style={{fontSize:12,color:"var(--text3)"}}>{open?"v":">"}</span>
        </div>
      </div>
      {!ok && ev.disqualification_reasons.map((r,i)=>(
        <div key={i} style={{padding:"6px 16px",fontSize:12,color:"var(--red)",background:"rgba(239,68,68,0.04)",borderTop:"1px solid rgba(239,68,68,0.1)"}}>x {r}</div>
      ))}
      {open && ev.criteria_results.map((cr,i)=>(
        <div key={i} style={{display:"flex",gap:10,padding:"9px 16px",borderTop:"1px solid var(--border)",fontSize:12,background:i%2===0?"transparent":"rgba(255,255,255,0.01)"}}>
          <span style={{minWidth:56,fontWeight:700,color:cr.status==="PASS"?"var(--green)":cr.status==="FAIL"?"var(--red)":cr.status==="EXEMPT"?"var(--accent)":"var(--text3)"}}>{cr.status}</span>
          <span style={{flex:1}}>{cr.criterion}</span>
          <span style={{color:"var(--text3)"}}>{cr.bidder_value||"-"}</span>
          {cr.evidence && <span style={{color:"var(--purple)",fontSize:11}}>p.{cr.evidence.page_number}</span>}
        </div>
      ))}
    </div>
  )
}

export default function History() {
  const [reports, setReports] = useState([])
  const [selected, setSelected] = useState(null)
  const [search, setSearch] = useState("")

  useEffect(() => {
    fetch("/api/reports").then(r=>r.json()).then(d=>setReports(d.reports||[])).catch(()=>{})
  }, [])

  const loadReport = (id) => {
    fetch(`/api/reports/${id}`).then(r=>r.json()).then(d=>setSelected(d)).catch(()=>{})
  }

  const filtered = reports.filter(r =>
    r.tender_title.toLowerCase().includes(search.toLowerCase()) ||
    r.report_id.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={{display:"grid",gridTemplateColumns:"280px 1fr",gap:20}}>
      <div>
        <h1 style={{fontSize:18,fontWeight:700,marginBottom:16}}>Report History</h1>
        <input value={search} onChange={e=>setSearch(e.target.value)}
          placeholder="Search reports..."
          style={{width:"100%",padding:"8px 12px",background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:8,color:"var(--text)",fontSize:13,marginBottom:12,outline:"none"}} />
        {filtered.length === 0 && <div style={{color:"var(--text3)",fontSize:13,padding:16,textAlign:"center"}}>No reports found</div>}
        {filtered.map(r=>(
          <div key={r.report_id} onClick={()=>loadReport(r.report_id)}
            style={{background:selected?.report_id===r.report_id?"var(--bg3)":"var(--bg2)",border:"1px solid "+(selected?.report_id===r.report_id?"var(--accent)":"var(--border)"),borderRadius:10,padding:"12px 14px",marginBottom:8,cursor:"pointer"}}>
            <div style={{fontSize:11,color:"var(--accent)",fontFamily:"monospace",marginBottom:4}}>{r.report_id}</div>
            <div style={{fontSize:13,fontWeight:500,marginBottom:4}}>{r.tender_title}</div>
            <div style={{display:"flex",gap:8,fontSize:11}}>
              <span style={{color:"var(--text3)"}}>{r.total_bidders} bidders</span>
              <span style={{color:"var(--green)"}}>{r.qualified_count} qualified</span>
            </div>
          </div>
        ))}
      </div>

      <div>
        {!selected ? (
          <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,padding:48,textAlign:"center",color:"var(--text3)"}}>
            Select a report from the left to view details
          </div>
        ) : (
          <div>
            <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,padding:24,marginBottom:20}}>
              <div style={{fontSize:11,color:"var(--accent)",fontFamily:"monospace",marginBottom:6}}>{selected.report_id}</div>
              <h2 style={{fontSize:18,fontWeight:700,marginBottom:12}}>{selected.tender_title}</h2>
              <div style={{display:"flex",gap:16}}>
                {[
                  {label:"Total",value:selected.total_bidders,color:"var(--accent)"},
                  {label:"Qualified",value:selected.qualified_count,color:"var(--green)"},
                  {label:"Disqualified",value:selected.disqualified_count,color:"var(--red)"},
                ].map(s=>(
                  <div key={s.label} style={{background:"var(--bg3)",borderRadius:8,padding:"10px 16px",textAlign:"center"}}>
                    <div style={{fontSize:22,fontWeight:700,color:s.color}}>{s.value}</div>
                    <div style={{fontSize:11,color:"var(--text3)"}}>{s.label}</div>
                  </div>
                ))}
              </div>
            </div>
            {selected.evaluations?.map(ev=><BidderCard key={ev.bidder_id} ev={ev} />)}
          </div>
        )}
      </div>
    </div>
  )
}
''')

# ── Admin Panel ──────────────────────────────────────────────
open('src/pages/Admin.jsx', 'w', encoding='utf-8').write('''
export default function Admin({ user }) {
  if (user.role !== "Admin") return (
    <div style={{padding:48,textAlign:"center",color:"var(--text3)"}}>Access denied. Admin only.</div>
  )

  const users = [
    {username:"admin",role:"Admin",status:"Active"},
    {username:"evaluator",role:"Evaluator",status:"Active"},
    {username:"viewer",role:"Viewer",status:"Active"},
  ]

  const settings = [
    {label:"Anthropic Model",value:"claude-sonnet-4-20250514"},
    {label:"Solvency Threshold",value:"25% of estimated cost"},
    {label:"Turnover Threshold",value:"30% of estimated cost"},
    {label:"Performance Security",value:"5% of contract value"},
    {label:"EMD Exemptions",value:"MSME, NSIC, DPIIT Startups"},
  ]

  return (
    <div>
      <h1 style={{fontSize:22,fontWeight:700,marginBottom:6}}>Admin Panel</h1>
      <p style={{color:"var(--text2)",fontSize:13,marginBottom:28}}>Manage users and system settings</p>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20}}>
        <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,overflow:"hidden"}}>
          <div style={{padding:"14px 20px",borderBottom:"1px solid var(--border)",fontWeight:600,fontSize:14}}>User Management</div>
          <table style={{width:"100%",borderCollapse:"collapse"}}>
            <thead>
              <tr style={{borderBottom:"1px solid var(--border)"}}>
                {["Username","Role","Status"].map(h=>(
                  <th key={h} style={{padding:"8px 16px",textAlign:"left",fontSize:11,color:"var(--text3)",fontWeight:600,textTransform:"uppercase"}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {users.map(u=>(
                <tr key={u.username} style={{borderBottom:"1px solid var(--border)"}}>
                  <td style={{padding:"10px 16px",fontFamily:"monospace",fontSize:13}}>{u.username}</td>
                  <td style={{padding:"10px 16px"}}>
                    <span style={{background:u.role==="Admin"?"rgba(59,130,246,0.1)":"rgba(139,92,246,0.1)",color:u.role==="Admin"?"var(--accent)":"var(--purple)",padding:"2px 10px",borderRadius:99,fontSize:11,fontWeight:600}}>{u.role}</span>
                  </td>
                  <td style={{padding:"10px 16px"}}>
                    <span style={{color:"var(--green)",fontSize:12}}>Active</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,overflow:"hidden"}}>
          <div style={{padding:"14px 20px",borderBottom:"1px solid var(--border)",fontWeight:600,fontSize:14}}>System Settings</div>
          {settings.map(s=>(
            <div key={s.label} style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"12px 20px",borderBottom:"1px solid var(--border)"}}>
              <span style={{fontSize:13,color:"var(--text2)"}}>{s.label}</span>
              <span style={{fontSize:13,fontFamily:"monospace",color:"var(--text)"}}>{s.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
''')

# ── Evaluate Page ──────────────────────────────────────────────
open('src/pages/Evaluate.jsx', 'w', encoding='utf-8').write('''
import { useState } from "react"

export default function Evaluate({ setPage }) {
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState("")

  const runDemo = async () => {
    setRunning(true); setError(""); setResult(null)
    try {
      const res = await fetch("/api/demo/evaluate", { method: "POST" })
      const data = await res.json()
      if (data.success) setResult(data.report)
      else throw new Error("Evaluation failed")
    } catch(e) { setError(e.message) }
    finally { setRunning(false) }
  }

  return (
    <div>
      <h1 style={{fontSize:22,fontWeight:700,marginBottom:6}}>Run Evaluation</h1>
      <p style={{color:"var(--text2)",fontSize:13,marginBottom:28}}>Run the 4-step AI evaluation pipeline</p>

      <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:12,padding:24,marginBottom:24}}>
        <h2 style={{fontSize:15,fontWeight:600,marginBottom:16}}>Demo: 9mm Pistol Tender</h2>
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:10,marginBottom:20}}>
          {[
            {label:"Estimated Cost",value:"Rs. 4.8 Crore"},
            {label:"EMD Required",value:"Rs. 12,00,000"},
            {label:"Solvency",value:"25% of est. cost"},
            {label:"Turnover",value:"30% of est. cost"},
            {label:"Bidders",value:"3 sample bidders"},
            {label:"Tech Specs",value:"Weight, Height, Capacity"},
          ].map(s=>(
            <div key={s.label} style={{background:"var(--bg3)",borderRadius:8,padding:"10px 14px"}}>
              <div style={{fontSize:11,color:"var(--text3)",marginBottom:2}}>{s.label}</div>
              <div style={{fontSize:13,fontWeight:500}}>{s.value}</div>
            </div>
          ))}
        </div>

        {error && <div style={{color:"var(--red)",fontSize:13,marginBottom:12,padding:"10px 14px",background:"rgba(239,68,68,0.08)",borderRadius:8}}>{error}</div>}

        <button onClick={runDemo} disabled={running}
          style={{background:running?"var(--border)":"var(--accent)",color:"#fff",padding:"11px 28px",borderRadius:8,fontSize:14,fontWeight:600,border:"none",width:"100%"}}>
          {running ? "Running 4-step pipeline..." : "Run Demo Evaluation"}
        </button>
      </div>

      {result && (
        <div style={{background:"var(--bg2)",border:"1px solid var(--green)",borderRadius:12,padding:24}}>
          <div style={{color:"var(--green)",fontWeight:600,marginBottom:12}}>Evaluation Complete!</div>
          <div style={{fontSize:13,color:"var(--text2)",marginBottom:16}}>Report ID: <span style={{fontFamily:"monospace",color:"var(--accent)"}}>{result.report_id}</span></div>
          <div style={{display:"flex",gap:12,marginBottom:20}}>
            <div style={{background:"var(--bg3)",borderRadius:8,padding:"10px 16px",textAlign:"center"}}>
              <div style={{fontSize:20,fontWeight:700,color:"var(--accent)"}}>{result.total_bidders}</div>
              <div style={{fontSize:11,color:"var(--text3)"}}>Total</div>
            </div>
            <div style={{background:"var(--bg3)",borderRadius:8,padding:"10px 16px",textAlign:"center"}}>
              <div style={{fontSize:20,fontWeight:700,color:"var(--green)"}}>{result.qualified_count}</div>
              <div style={{fontSize:11,color:"var(--text3)"}}>Qualified</div>
            </div>
            <div style={{background:"var(--bg3)",borderRadius:8,padding:"10px 16px",textAlign:"center"}}>
              <div style={{fontSize:20,fontWeight:700,color:"var(--red)"}}>{result.disqualified_count}</div>
              <div style={{fontSize:11,color:"var(--text3)"}}>Disqualified</div>
            </div>
          </div>
          <button onClick={()=>setPage("history")}
            style={{background:"var(--green)",color:"#fff",padding:"10px 24px",borderRadius:8,fontSize:13,fontWeight:600,border:"none"}}>
            View Full Report in History
          </button>
        </div>
      )}
    </div>
  )
}
''')

# ── Main App ──────────────────────────────────────────────
open('src/App.jsx', 'w', encoding='utf-8').write('''
import { useState } from "react"
import Login from "./pages/Login.jsx"
import Sidebar from "./components/Sidebar.jsx"
import Dashboard from "./pages/Dashboard.jsx"
import Upload from "./pages/Upload.jsx"
import Evaluate from "./pages/Evaluate.jsx"
import History from "./pages/History.jsx"
import Admin from "./pages/Admin.jsx"

export default function App() {
  const [user, setUser] = useState(null)
  const [page, setPage] = useState("dashboard")

  if (!user) return <Login onLogin={setUser} />

  const pages = {
    dashboard: <Dashboard setPage={setPage} />,
    upload: <Upload setPage={setPage} />,
    evaluate: <Evaluate setPage={setPage} />,
    history: <History />,
    admin: <Admin user={user} />,
  }

  return (
    <div style={{display:"flex",minHeight:"100vh"}}>
      <Sidebar page={page} setPage={setPage} user={user} onLogout={()=>setUser(null)} />
      <main style={{marginLeft:220,flex:1,padding:"32px 36px",maxWidth:1100}}>
        {pages[page] || pages.dashboard}
      </main>
    </div>
  )
}
''')

print("All files created successfully!")
