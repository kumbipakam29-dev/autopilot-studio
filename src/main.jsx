import React from 'react';
import { createRoot } from 'react-dom/client';
import { POD_CONCEPTS, REVIEW_STAGES } from './podData.js';
import './style.css';

const NAV = ['Overview', 'POD Studio', 'AI Agents', 'Task Queue', 'Reports', 'Settings'];
const ICONS = { 'Overview': '◫', 'POD Studio': '✦', 'AI Agents': '✧', 'Task Queue': '☷', 'Reports': '▤', 'Settings': '⚙' };
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

  React.useEffect(() => { localStorage.setItem('aps-notes', JSON.stringify(notes)); }, [notes]);
  React.useEffect(() => { localStorage.setItem('aps-pod-state', JSON.stringify(podState)); }, [podState]);

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

      {tab === 'AI Agents' && <section className="panel"><h3>Agent connections</h3><p className="muted">No live agents are connected yet. The POD concept library is a local planning module, not a running autonomous agent.</p>{['Trend & Demand Research Agent','Original Design Brief Agent','Listing SEO Agent','IP & Print QA Agent','Publishing Queue Agent','Sales Learning Agent'].map(a => <div className="task" key={a}><span className="task-icon">✧</span><div><b>{a}</b><small>Backend integration required</small></div><span className="status warn">Not connected</span></div>)}</section>}

      {tab === 'Task Queue' && <section className="panel"><h3>Add a task</h3><p className="muted">Tasks are stored locally; they are not executed automatically.</p><form onSubmit={e => { e.preventDefault(); add(); }} className="task-form"><input value={task} onChange={e => setTask(e.target.value)} placeholder="Describe a task to track…" aria-label="Task description"/><button className="primary">Add task</button></form>{notes.map((n,i) => <div className="task" key={i}><span className="task-icon">☷</span><div><b>{n.text}</b><small>{n.time}</small></div><span className="status">{n.status}</span></div>)}</section>}

      {tab === 'Reports' && <section className="panel"><h3>Reports</h3><p className="muted">Reports will appear after a backend or data source is connected.</p><div className="empty">No sales or marketplace reports available yet.</div></section>}
      {tab === 'Settings' && <section className="panel"><h3>Settings</h3><p className="muted">This prototype stores task notes and POD workflow stages in this browser. It has no login, cloud database, AI image API, marketplace account, or secrets manager.</p><div className="notice"><b>Integration requirements</b><p>Use official platform APIs and secure server-side credential storage. Never place seller secrets inside the Android app or in public source code.</p></div><button className="secondary" onClick={() => exportConcepts()}>Export POD concept library</button></section>}
      <footer>AutoPilot Studio <span>Local workspace · no live marketplace connection</span></footer>
    </main>
  </div>;
}

createRoot(document.getElementById('root')).render(<App />);
