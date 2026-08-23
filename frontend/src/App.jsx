import { useEffect, useState } from 'react'
import { Activity, BadgeIndianRupee, Bot, Check, ChevronRight, FlaskConical, LayoutDashboard, Settings2, ShieldAlert, Sparkles, Store, WalletCards } from 'lucide-react'
import { api, API } from './lib/api'
import Metric from './components/Metric'
import Proof from './components/Proof'
import AuditTimeline from './components/AuditTimeline'

const money = n => `₹${Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

export default function App() {
  const [tab, setTab] = useState('arena')
  const [message, setMessage] = useState('I need 50 corporate gift boxes under ₹35,000, vegetarian, delivery by Friday. Premium packaging preferred.')
  const [deal, setDeal] = useState(null)
  const [events, setEvents] = useState([])
  const [counter, setCounter] = useState('30000')
  const [unsafeDiscount, setUnsafeDiscount] = useState('30')
  const [recovery, setRecovery] = useState(null)
  const [policy, setPolicy] = useState(null)
  const [catalog, setCatalog] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  const [config, setConfig] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { bootstrap() }, [])

  async function bootstrap() {
    try {
      const [p, c, a, cfg] = await Promise.all([api('/merchant/policy'), api('/catalog'), api('/analytics'), api('/config/public')])
      setPolicy(p); setCatalog(c); setAnalytics(a); setConfig(cfg)
    } catch (e) { setError(e.message) }
  }

  async function refreshDeal(id = deal?.id) {
    if (!id) return
    const [d, audit] = await Promise.all([api(`/deals/${id}`), api(`/deals/${id}/audit`)])
    setDeal(d); setEvents(audit.events)
  }

  async function startDeal() {
    setBusy(true); setError(''); setRecovery(null)
    try {
      const result = await api('/deals/start', { method:'POST', body: JSON.stringify({ message }) })
      setDeal(result.deal)
      await refreshDeal(result.deal.id)
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  async function counterOffer() {
    if (!deal) return
    setBusy(true); setError('')
    try {
      const result = await api(`/deals/${deal.id}/counter`, { method:'POST', body: JSON.stringify({ amount: Number(counter) }) })
      setDeal(result.deal); await refreshDeal(deal.id)
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  async function demonstrateFailure() {
    if (!deal) return
    setBusy(true); setError('')
    try {
      const result = await api(`/deals/${deal.id}/demo-unsafe-discount`, { method:'POST', body: JSON.stringify({ requested_discount_pct: Number(unsafeDiscount) }) })
      setRecovery(result); await refreshDeal(deal.id)
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  async function approve(decision) {
    if (!deal) return
    const result = await api(`/approvals/${deal.id}`, { method:'POST', body: JSON.stringify({ decision }) })
    setDeal(result.deal); await refreshDeal(deal.id)
  }

  async function pay() {
    if (!deal) return
    try {
      const result = await api(`/payments/order/${deal.id}`, { method:'POST' })
      if (!window.Razorpay) throw new Error('Razorpay Checkout failed to load.')
      const rz = new window.Razorpay({
        key: config?.razorpay_key_id,
        amount: result.order.amount,
        currency: result.order.currency,
        name: 'DealGuard AI',
        description: `Verified deal ${deal.id}`,
        order_id: result.order.id,
        handler: async response => {
          await api('/payments/verify', { method:'POST', body: JSON.stringify(response) })
          await refreshDeal(deal.id); alert('Payment verified. Deal marked PAID.')
        },
      })
      rz.on('payment.failed', async () => { await refreshDeal(deal.id) })
      rz.open()
    } catch (e) { setError(e.message) }
  }

  async function savePolicy() {
    try {
      const p = await api('/merchant/policy', { method:'PUT', body: JSON.stringify(policy) })
      setPolicy(p)
    } catch (e) { setError(e.message) }
  }

  async function runEval() {
    setBusy(true); setError('')
    try { setEvaluation(await api('/analytics/evaluate', { method:'POST', body: JSON.stringify({ scenarios: 500, seed: 42 }) })) }
    catch(e) { setError(e.message) } finally { setBusy(false) }
  }

  const canPay = deal && deal.status === 'APPROVED' && ['APPROVED','AUTO_APPROVED'].includes(deal.approval_status)

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><ShieldAlert size={22}/></div><div><strong>DealGuard</strong><span>Agentic Commerce</span></div></div>
      <nav>
        <button className={tab==='arena'?'active':''} onClick={()=>setTab('arena')}><Sparkles/> Deal Arena</button>
        <button className={tab==='merchant'?'active':''} onClick={()=>setTab('merchant')}><Store/> Merchant</button>
        <button className={tab==='audit'?'active':''} onClick={()=>setTab('audit')}><Activity/> Audit Trail</button>
        <button className={tab==='analytics'?'active':''} onClick={()=>setTab('analytics')}><LayoutDashboard/> Evals</button>
      </nav>
      <div className="side-footer"><span className={`status-dot ${config?.ai_enabled?'online':'fallback'}`}/>{config?.ai_enabled ? 'GPT-OSS-120B live' : 'Deterministic fallback'}<small>{config?.groq_model}</small></div>
    </aside>

    <main>
      <header><div><h1>{tab==='arena'?'Verified Deal Arena':tab==='merchant'?'Merchant Control Center':tab==='audit'?'Money Action Audit':'Revenue Evaluation'}</h1><p>{tab==='arena'?'AI negotiates. Code verifies. Razorpay executes.':tab==='merchant'?'Set the non-negotiable economic boundaries.':tab==='audit'?'Every financial decision is inspectable.':'Measure value instead of claiming it.'}</p></div><div className="protocol-pill">Protocol-aware · Razorpay Test Mode</div></header>
      {error && <div className="error-banner">{error}<button onClick={()=>setError('')}>×</button></div>}

      {tab==='arena' && <div className="arena-grid">
        <section className="panel buyer-panel">
          <div className="panel-title"><Bot size={18}/> Buyer Agent</div>
          <label>Natural-language mandate</label>
          <textarea value={message} onChange={e=>setMessage(e.target.value)} />
          <button className="primary" onClick={startDeal} disabled={busy}>{busy?'Working…':'Start agentic deal'} <ChevronRight size={16}/></button>
          {deal && <>
            <div className="divider"/>
            <label>Buyer counteroffer</label>
            <div className="inline"><input type="number" value={counter} onChange={e=>setCounter(e.target.value)}/><button onClick={counterOffer}>Counter</button></div>
            <label className="top-space">Failure demo: demand unsafe discount</label>
            <div className="inline"><input type="number" value={unsafeDiscount} onChange={e=>setUnsafeDiscount(e.target.value)}/><button className="danger-outline" onClick={demonstrateFailure}>Try unsafe action</button></div>
          </>}
        </section>

        <section className="panel offer-panel">
          <div className="panel-title"><BadgeIndianRupee size={18}/> Merchant Offer</div>
          {!deal ? <div className="empty hero-empty"><Sparkles size={28}/><p>Start a deal to see the optimizer construct a merchant-safe offer.</p></div> : <>
            <div className="deal-top"><div><span className="eyebrow">{deal.id}</span><h2>{deal.quantity} × {deal.product_sku}</h2></div><span className={`badge ${deal.status.toLowerCase()}`}>{deal.status}</span></div>
            <p className="agent-message">“{deal.ai_explanation || 'Verified offer generated.'}”</p>
            <div className="metric-row">
              <Metric label="Final price" value={money(deal.final_price)} hint={`Budget ${money(deal.buyer_budget)}`}/>
              <Metric label="Merchant profit" value={money(deal.profit)} hint={`${deal.margin_pct}% margin`}/>
              <Metric label="Expected value" value={money(deal.expected_merchant_value)} hint={`${Math.round(deal.acceptance_probability*100)}% est. acceptance`}/>
            </div>
            {deal.addons?.length > 0 && <div className="addons"><strong>Cross-sell bundle</strong>{deal.addons.map(a=><span key={a.sku}>{a.quantity} × {a.name} · {money(a.unit_price*a.quantity)}</span>)}</div>}
            <div className="price-line"><span>List / bundle value</span><strong>{money(deal.gross_price)}</strong></div>
            <div className="price-line"><span>Discount</span><strong>{deal.discount_pct}%</strong></div>
            <div className="price-line total"><span>Verified amount</span><strong>{money(deal.final_price)}</strong></div>
            {deal.requires_approval && deal.approval_status==='PENDING' && <div className="approval-box"><strong>Human approval gate</strong><p>This deal exceeds the automatic transaction threshold.</p><div><button className="ghost" onClick={()=>approve('REJECTED')}>Reject</button><button className="primary" onClick={()=>approve('APPROVED')}><Check size={16}/> Approve deal</button></div></div>}
            {deal.approval_status==='APPROVED' && <div className="success-box">Merchant approved this financial action.</div>}
            <button className="pay" disabled={!canPay} onClick={pay}><WalletCards size={18}/> Pay with Razorpay</button>
            {!canPay && <div className="muted tiny center">Payment is impossible until all deterministic checks pass and required approval is granted.</div>}
          </>}
        </section>

        <Proof proof={deal?.proof}/>
        <section className="panel recovery-panel">
          <div className="panel-title"><ShieldAlert size={18}/> Graceful Failure</div>
          {!recovery ? <div className="empty">Use “Try unsafe action” to intentionally request a discount above merchant policy.</div> : recovery.blocked ? <>
            <div className="blocked-callout"><strong>Unsafe money action blocked</strong><span>{recovery.blocked_action.requested_discount_pct}% requested · {recovery.blocked_action.maximum_discount_pct}% max</span></div>
            <div className="repair-callout"><strong>Safe alternative generated</strong><span>{money(recovery.repaired_offer.final_price)} · {recovery.repaired_offer.discount_pct}% discount · {recovery.repaired_offer.margin_pct}% margin</span></div>
          </> : <div className="success-box">The requested discount was already within policy.</div>}
        </section>
      </div>}

      {tab==='merchant' && <div className="merchant-grid">
        <section className="panel">
          <div className="panel-title"><Settings2 size={18}/> Economic Guardrails</div>
          {policy && <div className="form-grid">
            <label>Minimum margin %<input type="number" value={policy.minimum_margin_pct} onChange={e=>setPolicy({...policy,minimum_margin_pct:Number(e.target.value)})}/></label>
            <label>Maximum discount %<input type="number" value={policy.maximum_discount_pct} onChange={e=>setPolicy({...policy,maximum_discount_pct:Number(e.target.value)})}/></label>
            <label>Auto approval limit ₹<input type="number" value={policy.auto_approval_limit} onChange={e=>setPolicy({...policy,auto_approval_limit:Number(e.target.value)})}/></label>
            <label>Maximum order value ₹<input type="number" value={policy.max_order_value} onChange={e=>setPolicy({...policy,max_order_value:Number(e.target.value)})}/></label>
            <button className="primary" onClick={savePolicy}>Save merchant policy</button>
          </div>}
        </section>
        <section className="panel"><div className="panel-title"><Store size={18}/> Agent-readable Catalog</div><div className="catalog-list">{catalog.map(p=><div className="catalog-item" key={p.sku}><div><strong>{p.name}</strong><span>{p.sku}</span></div><div><strong>{money(p.price)}</strong><span>{p.inventory} in stock</span></div></div>)}</div></section>
      </div>}

      {tab==='audit' && <section className="panel audit-panel"><div className="panel-title"><Activity size={18}/> {deal ? `Audit for ${deal.id}` : 'Audit Trail'}</div>{deal ? <AuditTimeline events={events}/> : <div className="empty">Create a deal first. The full lifecycle will appear here.</div>}</section>}

      {tab==='analytics' && <div className="eval-grid">
        <section className="panel"><div className="panel-title"><FlaskConical size={18}/> Controlled Evaluation</div><p className="muted">Runs 500 seeded synthetic buyer scenarios against static commerce and DealGuard. No favorable numbers are hard-coded.</p><button className="primary" onClick={runEval} disabled={busy}>{busy?'Running…':'Run 500-scenario eval'}</button></section>
        {evaluation && <section className="panel eval-results"><div className="metric-row"><Metric label="Revenue uplift" value={`${evaluation.revenue_uplift_pct}%`}/><Metric label="Conversion uplift" value={`${evaluation.conversion_uplift_points} pts`}/><Metric label="Recovered deals" value={evaluation.dealguard.recovered_deals}/><Metric label="Policy violations" value={evaluation.dealguard.policy_violations_executed}/></div><div className="compare"><div><span>Static commerce</span><strong>{evaluation.baseline.conversion_rate_pct}% conversion</strong><small>{money(evaluation.baseline.revenue)} revenue</small></div><div><span>DealGuard</span><strong>{evaluation.dealguard.conversion_rate_pct}% conversion</strong><small>{money(evaluation.dealguard.revenue)} revenue</small></div></div><p className="muted tiny">{evaluation.methodology_note}</p></section>}
      </div>}
    </main>
  </div>
}
