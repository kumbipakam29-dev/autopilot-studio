import React from 'react';
import { createRoot } from 'react-dom/client';
import { POD_CONCEPTS, REVIEW_STAGES } from './podData.js';
import './style.css';

const NAV = ['Overview', 'POD Studio', 'Earnings Hunter', 'AI Agents', 'Task Queue', 'Reports', 'Settings'];
const ICONS = { 'Overview': '◫', 'POD Studio': '✦', 'Earnings Hunter': '₹', 'AI Agents': '✧', 'Task Queue': '☷', 'Reports': '▤', 'Settings': '⚙' };

const EARNING_SOURCES = [
  { name: 'Karmyug AI', url: 'https://work.karmyug.in/jobs', kind: 'Language & AI data tasks', note: 'Public India listings show ₹2 per approved recording on the last scan. ID verification and quality acceptance apply.' },
  { name: 'CrowdGen by Appen', url: 'https://crowdgen.com/', kind: 'AI data & evaluation projects', note: 'Project-specific qualification, rates and availability. Never pay to join.' },
  { name: 'Clickworker', url: 'https://www.clickworker.com/clickworker/', kind: 'Microtasks & data work', note: 'Check India availability and supported payout method before investing time.' },
  { name: 'OneForma', url: 'https://www.oneforma.com/jobs/', kind: 'Language & AI projects', note: 'Project requirements, rates and recruitment status vary. Confirm that a listing fits your location and skills.' },
  { name: 'TELUS Digital AI Community', url: 'https://jobs.telusdigital.com/search/cfm5/ai-community/jobs/in/country/india', kind: 'Rating & evaluation roles', note: 'Often application/qualification based, not instant microtask cash.' },
  { name: 'Microworkers', url: 'https://www.microworkers.com/', kind: 'Small online tasks', note: 'KYC and withdrawal conditions apply. Use only genuine tasks and proof.' },
  { name: 'Toloka', url: 'https://toloka.ai/tolokers/', kind: 'Data annotation', note: 'Check current country and project restrictions, which can change.' },
  { name: 'Gitcoin Bounties', url: 'https://gitcoin.co/mechanisms/bounties', kind: 'Open-source & skill bounties', note: 'Acceptance is competitive; check the live amount, deadline, requirements and payout terms.' }
];

const EARNING_LEADS = [
  {
    id: 'karmyug-hindi', title: 'Hindi Script Recording Project', source: 'Karmyug AI',
    url: 'https://work.karmyug.in/jobs/d6f10b46-7249-4484-b114-c8008519acbf',
    rate: '₹2 per approved recording', ratePerTaskInr: 2, badge: 'Below target',
    detail: 'On the 24 Oct 2026 scan: 186 tasks available; apply-by date shown as 31 Oct 2026. Work must be your own Hindi recording and pass quality review. Check live slots and payout terms on the official page.'
  },
  {
    id: 'karmyug-english', title: 'English Script Recording Project', source: 'Karmyug AI',
    url: 'https://work.karmyug.in/jobs/df3d4bf3-c11b-449c-abd6-97e382c5bdf9',
    rate: '₹2 per approved recording', ratePerTaskInr: 2, badge: 'Below target',
    detail: 'On the 24 Oct 2026 scan: 129 tasks available; apply-by date shown as 31 Oct 2026. Requires your original English recording and acceptance by quality checks. Verify current availability first.'
  },
  {
    id: 'karmyug-bengali', title: 'Bengali Script Recording Project', source: 'Karmyug AI',
    url: 'https://work.karmyug.in/jobs/ed08603e-04a2-4e5e-a053-65c45980bc47',
    rate: '₹2 per approved recording', ratePerTaskInr: 2, badge: '0 tasks last checked',
    detail: 'The same scan showed zero tasks available. Included for completeness, not as a recommended immediate task. Re-check the official page before applying.'
  },
  {
    id: 'crowdgen-coffee', title: 'Project Coffee — India Data Labeling', source: 'CrowdGen by Appen',
    url: 'https://crowdgen.com/coffee-en-in/',
    rate: 'US$2/hour (site advertises about ₹175/hour)', ratePerTaskInr: null, badge: 'Hourly, not per task',
    detail: 'Potentially better hourly value, but recruitment status must be confirmed. Published requirements include India residence, fluent English, laptop/PC, up to 20 hours/week and passing qualification/identity checks. Do not treat this as ₹175 per task.'
  }
];

const EARNING_STATUSES = ['Lead found', 'Applied', 'Qualification pending', 'Approved to work', 'Work submitted', 'Accepted', 'Rejected', 'Payment pending', 'Paid'];
const readStore = (key, fallback) => {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch { return fallback; }
};
const saveDownload = (filename, content, type = 'text/csv;charset=utf-8;') => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
};
const csvCell = value => '"' + String(value ?? '').replace(/"/g, '""') + '"';

function App() {
  const [tab, setTab] = React.useState('Overview');
  const [notes, setNotes] = React.useState(() => readStore('aps-notes', []));
  const [task, setTask] = React.useState('');
  const [podState, setPodState] = React.useState(() => readStore('aps-pod-state', {}));
  const [search, setSearch] = React.useState('');
  const [productFilter, setProductFilter] = React.useState('All products');
  const [stageFilter, setStageFilter] = React.useState('All stages');
  const [notice, setNotice] = React.useState('');
  const [earningsLog, setEarningsLog] = React.useState(() => readStore('aps-earnings-log', []));
  const [earningTitle, setEarningTitle] = React.useState('');
  const [earningSource, setEarningSource] = React.useState('Karmyug AI');
  const [earningRate, setEarningRate] = React.useState('');
  const [earningUrl, setEarningUrl] = React.useState('');
  const [earningStatus, setEarningStatus] = React.useState('Lead found');

  React.useEffect(() => { localStorage.setItem('aps-notes', JSON.stringify(notes)); }, [notes]);
  React.useEffect(() => { localStorage.setItem('aps-pod-state', JSON.stringify(podState)); }, [podState]);
  React.useEffect(() => { localStorage.setItem('aps-earnings-log', JSON.stringify(earningsLog)); }, [earningsLog]);

  function add() {
    if (!task.trim()) return;
    setNotes([{ text: task.trim(), status: 'Queued locally', time: new Date().toLocaleString() }, ...notes]);
    setTask('');
  }
  function stageOf(id) { return podState[id]?.stage || 'Idea'; }
  function setStage(id, stage) {
    setPodState(prev => ({ ...prev, [id]: { ...(prev[id] || {}), stage, updatedAt: new Date().toISOString() } }));
  }
  async function copyText(text, message) {
    try {
      await navigator.clipboard.writeText(text);
      setNotice(message || 'Copied to clipboard.');
    } catch {
      setNotice('Clipboard access unavailable here. Use Export CSV to move the prompts to another tool.');
    }
  }
  function exportConcepts(items = POD_CONCEPTS) {
    const cols = ['id','niche','market','product','audience','title','keywords','concept','prompt','workflow_stage'];
    const rows = [cols.map(csvCell).join(','), ...items.map(item => [...cols.slice(0,9).map(k => item[k]), stageOf(item.id)].map(csvCell).join(','))];
    saveDownload('autopilot-pod-concepts.csv', '\ufeff' + rows.join('\r\n'));
    setNotice('CSV exported. Research ideas are hypotheses, not verified search-volume data.');
  }
  function addEarning() {
    if (!earningTitle.trim()) {
      setNotice('Enter a task title first.');
      return;
    }
    const entry = {
      id: String(Date.now()),
      title: earningTitle.trim(),
      source: earningSource,
      claimedRateInr: earningRate.trim(),
      url: earningUrl.trim(),
      status: earningStatus,
      earnedInr: '',
      payoutInr: '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    setEarningsLog(prev => [entry, ...prev]);
    setEarningTitle('');
    setEarningRate('');
    setEarningUrl('');
    setEarningStatus('Lead found');
    setNotice('Task saved on this device. No application or task submission was made.');
  }
  function updateEarning(id, field, value) {
    setEarningsLog(prev => prev.map(item => item.id === id ? { ...item, [field]: value, updatedAt: new Date().toISOString() } : item));
  }
  function exportEarnings() {
    const cols = ['id','source','title','claimed_rate_inr','status','actual_earned_inr','payout_received_inr','url','created_at','updated_at'];
    const rows = [
      cols.map(csvCell).join(','),
      ...earningsLog.map(item => [item.id,item.source,item.title,item.claimedRateInr,item.status,item.earnedInr,item.payoutInr,item.url,item.createdAt,item.updatedAt].map(csvCell).join(','))
    ];
    saveDownload('autopilot-earnings-tracker.csv', '\ufeff' + rows.join('\r\n'));
    setNotice('Earnings tracker CSV exported. It contains only entries saved on this device.');
  }
  function deleteEarning(id) {
    setEarningsLog(prev => prev.filter(item => item.id !== id));
    setNotice('Tracker entry removed from this device.');
  }
  const earnedTotal = earningsLog.reduce((sum, item) => sum + (Number(item.earnedInr) || 0), 0);
  const payoutTotal = earningsLog.reduce((sum, item) => sum + (Number(item.payoutInr) || 0), 0);
  const targetLeadCount = EARNING_LEADS.filter(item => item.ratePerTaskInr !== null && item.ratePerTaskInr >= 50 && item.ratePerTaskInr <= 200).length;
  const productTypes = ['All products', ...new Set(POD_CONCEPTS.flatMap(x => x.product.split(' / ')))];
  const filtered = POD_CONCEPTS.filter(item => {
    const query = search.trim().toLowerCase();
    const matchesQuery = !query || [item.id,item.niche,item.market,item.product,item.audience,item.title,item.keywords,item.concept].some(v => v.toLowerCase().includes(query));
    const matchesProduct = productFilter === 'All products' || item.product.split(' / ').includes(productFilter);
    const matchesStage = stageFilter === 'All stages' || stageOf(item.id) === stageFilter;
    return matchesQuery && matchesProduct && matchesStage;
  });
  const stageCounts = REVIEW_STAGES.map(stage => ({ stage, count: POD_CONCEPTS.filter(x => stageOf(x.id) === stage).length }));

  return <div className="app">
    <aside>
      <div className="brand"><span className="logo">✦</span><div><b>AutoPilot</b><small>STUDIO</small></div></div>
      <nav>{NAV.map(x => <button className={tab === x ? 'active' : ''} onClick={() => { setTab(x); setNotice(''); }} key={x}>{ICONS[x]}　{x}</button>)}</nav>
      <div className="side-note"><span className="dot"/> Local workspace<br/><small>Backend not connected</small></div>
    </aside>
    <main>
      <header><div><small>WORKSPACE / AUTOPILOT</small><h1>{tab}</h1></div><div className="avatar">AS</div></header>

      {tab === 'Overview' && <>
        <section className="welcome"><div><p className="eyebrow">YOUR CONTROL CENTER</p><h2>Build. Automate. Grow.</h2><p>One place to plan and monitor your automation work.</p></div><div className="spark">✦</div></section>
        <div className="cards">
          <article><small>AGENT CONNECTION</small><h2>Not connected</h2><p>Connect a real automation backend to show live status.</p></article>
          <article><small>POD CONCEPT LIBRARY</small><h2>{POD_CONCEPTS.length} concepts</h2><p>Local prompts and listing briefs ready for review.</p></article>
          <article><small>LIVE REVENUE</small><h2>—</h2><p>No financial data source connected.</p></article>
        </div>
        <section className="panel"><div className="panel-head"><div><h3>POD Studio is ready for review</h3><p>25 original design directions; demand is not yet independently validated.</p></div><button className="secondary" onClick={() => setTab('POD Studio')}>Open POD Studio →</button></div>
          <div className="stage-summary">{stageCounts.map(s => <div key={s.stage}><b>{s.count}</b><span>{s.stage}</span></div>)}</div>
        </section>
        <section className="panel"><div className="panel-head"><div><h3>Recent task queue</h3><p>Tasks saved on this device</p></div><button className="secondary" onClick={() => setTab('Task Queue')}>View queue →</button></div>
          {notes.length ? notes.slice(0,4).map((n,i) => <div className="task" key={i}><span className="task-icon">↗</span><div><b>{n.text}</b><small>{n.time}</small></div><span className="status">{n.status}</span></div>) : <div className="empty">No tasks yet. Add a task in Task Queue to get started.</div>}
        </section>
        <div className="notice"><b>Honest status</b><p>This app currently stores data on this device. It does not generate images via an AI API, fetch live marketplace trends, or publish listings. Those need service access, integration and seller-account authorization.</p></div>
      </>}

      {tab === 'POD Studio' && <section className="pod-workspace">
        <section className="pod-hero"><div><p className="eyebrow">PRINT-ON-DEMAND WORKSPACE</p><h2>25 original concept briefs</h2><p>India + international · T-shirts, mugs, totes and more</p></div><button className="primary" onClick={() => exportConcepts()}>Export all to CSV ↓</button></section>
        <div className="notice"><b>Research status: starter hypotheses</b><p>These are original design directions and keyword seeds, not proof of current demand or search volume. Validate each niche in marketplace search and trend tools before spending money or publishing. AI-generated artwork must be checked for errors and intellectual-property risk.</p></div>
        <section className="platform-readiness">
          <h3>Zero-budget launch path — India + international</h3>
          <div className="platform-options">
            <article><span className="status good">First to check</span><h4>Amazon Merch on Demand</h4><p>No upfront inventory/production payment according to Amazon. Application and India-based seller eligibility must be confirmed; acceptance is not guaranteed.</p><a href="https://merch.amazon.com/" target="_blank" rel="noreferrer">Check eligibility ↗</a></article>
            <article><span className="status warn">Not ₹0 upfront</span><h4>Etsy</h4><p>Etsy says new Indian shops can sell internationally, but onboarding currently includes a US$10 setup fee, GSTIN verification and Payoneer. Listing fees are additional.</p><a href="https://help.etsy.com/hc/en-in/articles/6742925359255-How-to-Accept-Payments-as-a-Seller-in-India" target="_blank" rel="noreferrer">India seller requirements ↗</a></article>
            <article><span className="status">Free plan, fulfilment costs</span><h4>Printify</h4><p>The platform has a free plan, but products and shipping must still be funded when orders are fulfilled. Connect a sales channel and calculate cash flow first.</p><a href="https://printify.com/pricing/" target="_blank" rel="noreferrer">Check current pricing ↗</a></article>
          </div>
        </section>
        {notice && <div className="inline-notice" role="status">{notice}</div>}
        <div className="pod-metrics"><div><b>{POD_CONCEPTS.length}</b><span>Briefs loaded</span></div><div><b>{POD_CONCEPTS.filter(x => stageOf(x.id) === 'Research reviewed').length}</b><span>Research reviewed</span></div><div><b>{POD_CONCEPTS.filter(x => stageOf(x.id) === 'Brief ready').length}</b><span>Brief ready</span></div><div><b>{POD_CONCEPTS.filter(x => stageOf(x.id) === 'Approved for upload').length}</b><span>Approved by you</span></div></div>
        <div className="pod-filters">
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search niche, title, keyword…" aria-label="Search POD concepts" />
          <select value={productFilter} onChange={e => setProductFilter(e.target.value)} aria-label="Filter by product">{productTypes.map(v => <option key={v}>{v}</option>)}</select>
          <select value={stageFilter} onChange={e => setStageFilter(e.target.value)} aria-label="Filter by stage">{['All stages', ...REVIEW_STAGES].map(v => <option key={v}>{v}</option>)}</select>
        </div>
        <div className="pod-grid">{filtered.map(item => <article className="pod-card" key={item.id}>
          <div className="pod-card-top"><span className="pod-id">{item.id}</span><span className={'status ' + (stageOf(item.id) === 'Approved for upload' ? 'good' : '')}>{stageOf(item.id)}</span></div>
          <p className="pod-niche">{item.niche} · {item.market}</p><h3>{item.title}</h3><p className="pod-audience">For: {item.audience}</p>
          <div className="pod-field"><b>Products</b><span>{item.product}</span></div>
          <div className="pod-field"><b>Design direction</b><span>{item.concept}</span></div>
          <details><summary>Artwork prompt + keyword seeds</summary><div className="pod-field"><b>Keywords to validate</b><span>{item.keywords}</span></div><div className="prompt-box">{item.prompt}</div><button className="secondary" onClick={() => copyText(item.prompt, item.id + ' prompt copied.')}>Copy artwork prompt</button><button className="secondary" onClick={() => copyText(item.title + '\n' + item.keywords, item.id + ' title and keywords copied.')}>Copy listing seed</button></details>
          <label className="stage-label">Workflow stage</label><select value={stageOf(item.id)} onChange={e => setStage(item.id, e.target.value)} aria-label={'Workflow stage for ' + item.id}>{REVIEW_STAGES.map(v => <option key={v}>{v}</option>)}</select>
        </article>)}</div>
        {!filtered.length && <div className="empty">No concepts match these filters.</div>}
        <div className="notice"><b>Before publishing</b><p>Search the exact phrase and close variants in relevant trademark registers; inspect every pixel for malformed text; confirm print dimensions, transparent background, colour contrast, product margin, platform-specific rules and any AI/production-partner disclosures. Never use famous characters, logos, team names or copied artwork.</p></div>
      </section>}

      {tab === 'Earnings Hunter' && <section className="earning-workspace">
        <section className="earning-hero">
          <div><p className="eyebrow">CROSS-PLATFORM MICROTASKS</p><h2>Hunt real work. Track every rupee.</h2><p>Daily public-page scans, rate evidence, scam-risk checks and a private task-to-payout ledger. This is separate from POD.</p></div>
          <div className="earning-hero-actions">
            <a className="primary earning-link-button" href="https://github.com/kumbipakam29-dev/autopilot-studio/actions/workflows/earnings-hunter.yml" target="_blank" rel="noreferrer">Open latest hunt ↗</a>
            <button className="secondary" onClick={exportEarnings}>Export tracker ↓</button>
          </div>
        </section>

        <div className="earning-stats">
          <article><small>PUBLIC SOURCES SCANNED</small><b>8</b><span>Last verified scan: 24 Oct 2026</span></article>
          <article><small>₹50–₹200 PER TASK</small><b>{targetLeadCount}</b><span>Exact public INR rates in this lead snapshot</span></article>
          <article><small>ACTUAL EARNED</small><b>₹{earnedTotal.toFixed(2)}</b><span>Only what you record as accepted</span></article>
          <article><small>PAYOUT RECEIVED</small><b>₹{payoutTotal.toFixed(2)}</b><span>Enter only when money really arrives</span></article>
        </div>

        <div className="notice"><b>Honest hunt result — 24 October 2026</b><p>The latest scan emitted 30 leads but found <strong>zero verified public rates in the ₹50–₹200 per-task target band</strong>. Three current Karmyug recording pages showed ₹2 per approved recording; CrowdGen Project Coffee advertises about ₹175/hour, not ₹175 per task, and requires a laptop/PC and qualification. Listings can change, so open the source and confirm the current terms before doing any work.</p></div>

        <section className="earning-section">
          <div className="earning-section-head"><div><h3>Specific leads found</h3><p>Rate and availability here reflect the last scan; verify live details before applying.</p></div><span className="status warn">No target-rate task verified</span></div>
          <div className="earning-lead-grid">{EARNING_LEADS.map(lead => <article className="earning-lead" key={lead.id}>
            <div className="earning-lead-top"><span className={'status ' + (lead.ratePerTaskInr === 2 ? 'warn' : '')}>{lead.badge}</span><small>{lead.source}</small></div>
            <h4>{lead.title}</h4><div className="earning-rate">{lead.rate}</div><p>{lead.detail}</p>
            <div className="earning-actions"><a href={lead.url} target="_blank" rel="noreferrer">Open official listing ↗</a><button className="secondary" onClick={() => { setEarningTitle(lead.title); setEarningSource(lead.source); setEarningRate(lead.ratePerTaskInr === null ? '' : String(lead.ratePerTaskInr)); setEarningUrl(lead.url); setNotice('Lead added to the form below. Review it and save your tracker entry.'); document.getElementById('earning-tracker-form')?.scrollIntoView({behavior:'smooth', block:'start'}); }}>Track this lead +</button></div>
          </article>)}</div>
        </section>

        <section className="earning-section">
          <div className="earning-section-head"><div><h3>Where the hunter looks</h3><p>Official starting points only. It does not log in, claim tasks or submit proof.</p></div></div>
          <div className="earning-source-grid">{EARNING_SOURCES.map(source => <article className="earning-source" key={source.name}>
            <h4>{source.name}</h4><span>{source.kind}</span><p>{source.note}</p><a href={source.url} target="_blank" rel="noreferrer">Open source ↗</a>
          </article>)}</div>
        </section>

        <section className="earning-section" id="earning-tracker-form">
          <div className="earning-section-head"><div><h3>Task → acceptance → payout tracker</h3><p>Saved only on this device. Keep passwords, OTPs, government-ID numbers and payment details out of it.</p></div></div>
          <form className="earning-form" onSubmit={e => { e.preventDefault(); addEarning(); }}>
            <label>Task title<input value={earningTitle} onChange={e => setEarningTitle(e.target.value)} placeholder="e.g. Hindi data labeling task" required /></label>
            <label>Source<select value={earningSource} onChange={e => setEarningSource(e.target.value)}>{[...EARNING_SOURCES.map(s => s.name), 'Other / new source'].map(name => <option key={name}>{name}</option>)}</select></label>
            <label>Claimed rate (₹/task, if stated)<input type="number" min="0" step="0.01" value={earningRate} onChange={e => setEarningRate(e.target.value)} placeholder="Leave blank if unknown" /></label>
            <label>Official task URL<input type="url" value={earningUrl} onChange={e => setEarningUrl(e.target.value)} placeholder="https://…" /></label>
            <label>Status<select value={earningStatus} onChange={e => setEarningStatus(e.target.value)}>{EARNING_STATUSES.map(status => <option key={status}>{status}</option>)}</select></label>
            <button className="primary" type="submit">Save tracker entry</button>
          </form>
          {notice && <div className="inline-notice" role="status">{notice}</div>}
          {earningsLog.length ? <div className="earning-log-list">{earningsLog.map(item => <article className="earning-log" key={item.id}>
            <div className="earning-log-head"><div><b>{item.title}</b><small>{item.source} · Added {new Date(item.createdAt).toLocaleDateString()}</small></div>{item.url && <a href={item.url} target="_blank" rel="noreferrer">Open task ↗</a>}</div>
            <div className="earning-log-fields">
              <label>Status<select value={item.status} onChange={e => updateEarning(item.id, 'status', e.target.value)}>{EARNING_STATUSES.map(status => <option key={status}>{status}</option>)}</select></label>
              <label>Actual earned (₹)<input type="number" min="0" step="0.01" value={item.earnedInr} onChange={e => updateEarning(item.id, 'earnedInr', e.target.value)} placeholder="0.00" /></label>
              <label>Received in payout (₹)<input type="number" min="0" step="0.01" value={item.payoutInr} onChange={e => updateEarning(item.id, 'payoutInr', e.target.value)} placeholder="0.00" /></label>
              <button className="secondary" type="button" onClick={() => deleteEarning(item.id)}>Remove</button>
            </div>
          </article>)}</div> : <div className="empty">No tasks tracked yet. Add a verified lead above; the app does not auto-apply or mark anything as paid.</div>}
        </section>

        <div className="notice"><b>First-payment playbook</b><p>Use only official pages, confirm the payout method and minimum withdrawal before starting, do not pay a joining/deposit/unlock fee, do the real task yourself, follow its AI-assistance rules, and record “Accepted” or “Paid” only when the platform confirms it. Fake reviews, fake proof, duplicate accounts, location spoofing and CAPTCHA bypass are out.</p></div>
      </section>}

      {tab === 'AI Agents' && <section className="panel"><h3>Agent connections</h3><p className="muted">No live agents are connected yet. The POD concept library is a local planning module, not a running autonomous agent.</p>{['Trend & Demand Research Agent','Original Design Brief Agent','Listing SEO Agent','IP & Print QA Agent','Publishing Queue Agent','Sales Learning Agent'].map(a => <div className="task" key={a}><span className="task-icon">✧</span><div><b>{a}</b><small>Backend integration required</small></div><span className="status warn">Not connected</span></div>)}</section>}

      {tab === 'Task Queue' && <section className="panel"><h3>Add a task</h3><p className="muted">Tasks are stored locally; they are not executed automatically.</p><form onSubmit={e => { e.preventDefault(); add(); }} className="task-form"><input value={task} onChange={e => setTask(e.target.value)} placeholder="Describe a task to track…" aria-label="Task description"/><button className="primary">Add task</button></form>{notes.map((n,i) => <div className="task" key={i}><span className="task-icon">☷</span><div><b>{n.text}</b><small>{n.time}</small></div><span className="status">{n.status}</span></div>)}</section>}

      {tab === 'Reports' && <section className="panel"><h3>Reports</h3><p className="muted">Reports will appear after a backend or data source is connected.</p><div className="empty">No sales or marketplace reports available yet.</div></section>}
      {tab === 'Settings' && <section className="panel"><h3>Settings</h3><p className="muted">This prototype stores task notes and POD workflow stages in this browser. It has no login, cloud database, AI image API, marketplace account, or secrets manager.</p><div className="notice"><b>Integration requirements</b><p>Use official platform APIs and secure server-side credential storage. Never place seller secrets inside the Android app or in public source code.</p></div><button className="secondary" onClick={() => exportConcepts()}>Export POD concept library</button></section>}
      <footer>AutoPilot Studio <span>Local workspace · no live marketplace connection</span></footer>
    </main>
  </div>;
}

createRoot(document.getElementById('root')).render(<App />);
