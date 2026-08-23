import { CheckCircle2, XCircle, ShieldCheck } from 'lucide-react'

export default function Proof({ proof }) {
  if (!proof) return null
  return <section className="panel proof-panel">
    <div className="panel-title"><ShieldCheck size={18}/> Deal Proof</div>
    <div className={`proof-status ${proof.status?.toLowerCase()}`}>{proof.status}</div>
    <p className="muted">{proof.verdict}</p>
    <div className="check-grid">
      {(proof.checks || []).map(c => <div className="check-row" key={c.rule}>
        {c.passed ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
        <div>
          <strong>{c.rule.replaceAll('_', ' ')}</strong>
          <div className="muted tiny">Actual {typeof c.actual === 'number' ? c.actual.toLocaleString('en-IN') : c.actual} · Limit {typeof c.limit === 'number' ? c.limit.toLocaleString('en-IN') : c.limit}</div>
        </div>
      </div>)}
    </div>
  </section>
}
