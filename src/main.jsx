import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const initialAgents = [
  { name: 'Orchestrator', role: 'Coordinates workflows', state: 'Connected', icon: '◈' },
  { name: 'Content Growth Agent', role: 'Content planning and publishing queue', state: 'Demo mode', icon: '✦' },
  { name: 'Client Delivery Agent', role: 'Client task tracking', state: 'Demo mode', icon: '▣' },
  { name: 'Lead Research', role: 'Lead pipeline support', state: 'Not connected', icon: '⌕' },
];
function App() {
  const [tab, setTab] = useState('Overview');
  const [tasks, setTasks] = useState([]);
  const [task, setTask] = useState('');
  const [agents, setAgents] = useState(initialAgents);
  const [notice, setNotice] = useState('');
  const [reports, setReports] = useState(['Workspace initialized. Live integrations are not connected yet.']);
  const done = tasks.filter(t => t.status === 'Completed').length;
  const nav = ['Overview', 'Agents', 'Tasks', 'Reports', 'Settings'];
  const addTask = () => {
    if (!task.trim()) return;
    setTasks(old => [{ id: Date.now(), title: task.trim(), status: 'Queued' }, ...old]);
    setReports(old => [`Demo task queued: ${task.trim()}`, ...old]);
    setTask(''); setNotice('Task added to this device’s demo queue.');
  };
  const toggleDemo = (name) => {
    setAgents(old => old.map(a => a.name === name ? {...a, state: a.state === 'Demo running' ? 'Demo mode' : 'Demo running'} : a));
    setNotice('Demo status changed locally only. No external agent was started or stopped.');
  };
  const title = useMemo(() => ({Overview:'Control center',Agents:'Agent workspace',Tasks:'Task queue',Reports:'Activity reports',Settings:'Workspace settings'}[tab]), [tab]);
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">A</div><div><b>AutoPilot</b><small>STUDIO</small></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav>{nav.map((n,i)=><button key={n} className={tab===n?'nav-item active':'nav-item'} onClick={()=>{setTab(n);setNotice('')}}><span>{['⌂','◈','▤','◷','⚙'][i]}</span>{n}</button>)}</nav>
      <div className="side-bottom"><span className="pulse"></span><div><b>Local workspace</b><small>Backend not connected</small></div></div>
    </aside>
    <main className="main">
      <header><div><div className="eyebrow">AUTOPILOT STUDIO / {tab.toUpperCase()}</div><h1>{title}</h1></div><div className="profile"><div className="avatar">AS</div><div><b>Studio Admin</b><small>Free workspace</small></div></div></header>
      <div className="notice"><b>Prototype mode</b><span>Tasks and demo agent switches are stored in this screen only. Real automation requires a connected backend.</span></div>
      {notice && <div className="toast">{notice}</div>}
      {tab==='Overview' && <>
        <section className="hero"><div><div className="eyebrow light">YOUR AUTOMATION HQ</div><h2>Make room for<br/>work that matters.</h2><p>Track your workflow ideas, tasks, and agent connections in one place.</p><button className="primary" onClick={()=>setTab('Tasks')}>＋ Create a task <span>→</span></button></div><div className="hero-art"><div className="orbit orbit1"></div><div className="orbit orbit2"></div><div className="core">✦</div><div className="float f1">AI</div><div className="float f2">↗</div><div className="float f3">✓</div></div></section>
        <div className="section-head"><div><h2>Workspace overview</h2><p>A quick snapshot of this device’s demo data</p></div></div>
        <div className="stats"><Stat label="Agent templates" value={agents.length} sub="Available in this demo" icon="◈"/><Stat label="Tasks queued" value={tasks.length} sub="Local task list" icon="▤"/><Stat label="Completed tasks" value={done} sub="Demo completions only" icon="✓"/><Stat label="Live connections" value="0" sub="Backend not configured" icon="⌁"/></div>
        <div className="columns"><section className="panel"><div className="panel-head"><div><h3>Agent status</h3><p>Templates and connection state</p></div><button className="text-button" onClick={()=>setTab('Agents')}>View all →</button></div>{agents.slice(0,3).map(a=><AgentRow key={a.name} agent={a}/>)}</section><section className="panel"><div className="panel-head"><div><h3>Recent tasks</h3><p>Latest items in your local queue</p></div><button className="text-button" onClick={()=>setTab('Tasks')}>View all →</button></div>{tasks.length===0?<div className="empty"><div>▤</div><b>No tasks yet</b><span>Create a task to start organizing your workflow.</span><button className="secondary" onClick={()=>setTab('Tasks')}>Create first task</button></div>:tasks.slice(0,4).map(t=><TaskRow key={t.id} task={t} onStatus={()=>setTasks(old=>old.map(x=>x.id===t.id?{...x,status:x.status==='Completed'?'Queued':'Completed'}:x))}/>)}</section></div>
      </>}
      {tab==='Agents' && <section className="panel page-panel"><div className="panel-head"><div><h3>Agent templates</h3><p>Local demo controls — not connected to external services</p></div></div>{agents.map(a=><div className="agent-full" key={a.name}><AgentRow agent={a}/><button className="secondary" onClick={()=>toggleDemo(a.name)}>{a.state==='Demo running'?'Stop demo':'Run demo'}</button></div>)}</section>}
      {tab==='Tasks' && <section className="panel page-panel"><div className="panel-head"><div><h3>Task queue</h3><p>Create and track demo tasks</p></div></div><form className="task-form" onSubmit={e=>{e.preventDefault();addTask()}}><input value={task} onChange={e=>setTask(e.target.value)} placeholder="e.g. Draft this week's content plan" aria-label="Task name"/><button className="primary" type="submit">Add task</button></form>{tasks.length===0?<div className="empty"><div>▤</div><b>Your queue is clear</b><span>Add a task above. Tasks are saved only for this current session.</span></div>:tasks.map(t=><TaskRow key={t.id} task={t} onStatus={()=>setTasks(old=>old.map(x=>x.id===t.id?{...x,status:x.status==='Completed'?'Queued':'Completed'}:x))}/>)}</section>}
      {tab==='Reports' && <section className="panel page-panel"><div className="panel-head"><div><h3>Activity log</h3><p>Events from this demo session</p></div><button className="secondary" onClick={()=>setReports([])}>Clear log</button></div>{reports.length?reports.map((r,i)=><div className="report" key={i}><span className="report-dot"></span><div><b>{r}</b><small>Local session event</small></div></div>):<div className="empty"><b>No report events</b></div>}</section>}
      {tab==='Settings' && <section className="panel page-panel"><h3>Workspace settings</h3><p className="muted">This prototype runs in your browser. It does not store secrets or connect to external services.</p><div className="setting"><div><b>Automation backend</b><p>Not configured</p></div><span className="pill warn">Disconnected</span></div><div className="setting"><div><b>Persistent storage</b><p>Tasks are currently held in UI state only.</p></div><span className="pill">Prototype</span></div><div className="setting"><div><b>API credentials</b><p>Never paste API keys into this frontend. A secure server-side backend is required.</p></div><span className="pill warn">Not set</span></div></section>}
      <footer>AutoPilot Studio <span>•</span> Prototype build <span>•</span> No paid services required to preview</footer>
    </main>
  </div>;
}
function Stat({label,value,sub,icon}){return <div className="stat"><div className="stat-top"><span>{label}</span><i>{icon}</i></div><strong>{value}</strong><small>{sub}</small></div>}
function AgentRow({agent}){return <div className="agent-row"><div className="agent-icon">{agent.icon}</div><div className="agent-info"><b>{agent.name}</b><small>{agent.role}</small></div><span className={'pill '+(agent.state==='Connected'?'good':agent.state==='Demo running'?'blue':'')}>{agent.state}</span></div>}
function TaskRow({task,onStatus}){return <div className="task-row"><button className={'check '+(task.status==='Completed'?'checked':'')} onClick={onStatus}>{task.status==='Completed'?'✓':''}</button><div className="task-info"><b>{task.title}</b><small>Local demo task</small></div><span className={'pill '+(task.status==='Completed'?'good':'')}>{task.status}</span></div>}
createRoot(document.getElementById('root')).render(<App/>);