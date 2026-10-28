import React from 'react';
import { createRoot } from 'react-dom/client';
import { POD_CONCEPTS, REVIEW_STAGES } from './podData.js';
import './style.css';

const NAV = ['Overview', 'POD Studio', 'Earnings Hunter', 'AI Agents', 'Creative Intelligence', 'Training Loop', 'Task Queue', 'Reports', 'Settings'];
const ICONS = { 'Overview': '◫', 'POD Studio': '✦', 'Earnings Hunter': '₹', 'AI Agents': '✧', 'Creative Intelligence': '✧', 'Training Loop': '↻', 'Task Queue': '☷', 'Reports': '▤', 'Settings': '⚙' };

const CREATIVE_TOOL_CARDS = [
  { name: 'ComfyUI', access: 'Local workflow graph', purpose: 'Run connected image/video/audio workflows and expose them through a local API.', url: 'https://github.com/Comfy-Org/ComfyUI', autopilot: 'Versioned workflow nodes and explicit input/output contracts.' },
  { name: 'Wan2.2', access: 'Open weights · local', purpose: 'Candidate for text-to-video and image-to-video generation.', url: 'https://github.com/Wan-Video/Wan2.2', autopilot: 'Local rendering option after GPU, checkpoint and license validation.' },
  { name: 'LTX-2.5', access: 'Community license', purpose: 'Video/audio model family with version-specific usage conditions.', url: 'https://github.com/Lightricks/LTX-2', autopilot: 'Optional candidate; commercial license clearance is a hard gate.' },
  { name: 'VBench', access: 'Evaluation tools', purpose: 'Video quality dimensions such as motion smoothness, flicker and subject/background consistency.', url: 'https://github.com/Vchitect/VBench', autopilot: 'Compare actual exports with a fixed benchmark, not sales claims.' },
  { name: 'Ideogram', access: 'Hosted service', purpose: 'Text-heavy poster and typography generation.', url: 'https://ideogram.ai/features/text-rendering/', autopilot: 'Proofread copy and keep critical text editable whenever possible.' },
  { name: 'Pika', access: 'Hosted · credits/plan', purpose: 'Photo animation and transitions between ordered keyframes.', url: 'https://creation.pika.art/apps/pikaframes?tab=video-tools', autopilot: 'Implement our own keyframe planner and measure continuity.' },
  { name: 'Krea', access: 'Hosted multi-model', purpose: 'Image/video generation, editing and enhancement in one workspace.', url: 'https://www.krea.ai/', autopilot: 'Separate generation, edit, enhancement and style/identity checks.' },
  { name: 'Canva Magic Video', access: 'Hosted freemium', purpose: 'Template-guided assembly of photos/clips, transitions and music.', url: 'https://www.canva.com/help/magic-video/', autopilot: 'Use template assembly after the custom concept passes originality checks.' },
  { name: 'Adobe Firefly Agent', access: 'Proprietary hosted', purpose: 'Brand kits, storyboards-to-video, product-photo video and first-cut editing.', url: 'https://news.adobe.com/news/2026/06/adobe-unveils-major-expansion', autopilot: 'Independent modular pipeline: brief → storyboard → shots → edit.' },
  { name: 'Runway Workflows', access: 'Proprietary · credits/API', purpose: 'Reusable multi-model workflow chains and model routing.', url: 'https://dev.runwayml.com/workflows', autopilot: 'Transparent local-first router, cost/latency evidence and no silent paid fallback.' },
  { name: 'FFmpeg', access: 'Local media pipeline', purpose: 'Deterministic cut, transcode, crop, audio mix and export.', url: 'https://www.ffmpeg.org/ffmpeg.html', autopilot: 'Validate final dimensions, frame rate, duration, codec and audio.' },
  { name: 'Pillow', access: 'Local image library', purpose: 'Exact pixel-level text and image composition.', url: 'https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html', autopilot: 'Build crisp poster text overlays using approved copy and licensed fonts.' },
  { name: 'OpenCV', access: 'Local vision library', purpose: 'Frame analysis, image processing and image/video quality signals.', url: 'https://github.com/opencv/opencv', autopilot: 'Screen for blur, crop shifts and frame differences, then human-review.' },
  { name: 'Whisper', access: 'Open source · local', purpose: 'Speech transcription and subtitle drafts.', url: 'https://github.com/openai/whisper', autopilot: 'Proofread names, prices, accents, subtitle timing and audio consent.' }
];

function deriveCreativeHypotheses(observation) {
  const text = [observation.publicBehavior, observation.inputOutputObserved].join(' ').toLowerCase();
  const rules = [
    { terms: ['keyframe', 'ordered image', 'first and last frame'], title: 'Keyframe continuity planner', proposal: 'Plan ordered reference frames and a separate motion instruction for each transition.', test: 'Compare subject/product continuity at the start, middle and end frames.' },
    { terms: ['image to video', 'photo', 'uploaded image', 'reference image', 'image-to-video'], title: 'Reference-image anchoring', proposal: 'Preserve approved product, person, framing and colour attributes through each shot prompt.', test: 'Inspect identity and product details at three points in the clip.' },
    { terms: ['workflow', 'node graph', 'multi-step', 'pipeline', 'storyboard'], title: 'Versioned workflow graph', proposal: 'Split research, concepts, shot prompts, rendering, editing and QA into versioned stages.', test: 'Replay the same brief and seed; compare reproducibility and recovery from failed stages.' },
    { terms: ['typography', 'text rendering', 'editable text', 'headline', 'poster'], title: 'Editable typography layer', proposal: 'Generate the visual separately and add approved copy/logo as editable layout layers.', test: 'Verify exact text, contrast and readability at phone size and 200% zoom.' },
    { terms: ['router', 'latency', 'cost', 'quality', 'model selection'], title: 'Transparent local-first router', proposal: 'Route by task fit, hardware, license and measured quality; never silently use a paid fallback.', test: 'Run a fixed prompt suite and log actual latency, validity and cost for each backend.' },
    { terms: ['flicker', 'consistency', 'motion smoothness', 'benchmark', 'evaluation'], title: 'Temporal and identity QA', proposal: 'Check frame-to-frame identity, flicker, blur, crop and continuity before editing.', test: 'Compare automated signals with human labels on the same output sample.' },
    { terms: ['audio', 'sound', 'music', 'voice', 'subtitle', 'caption'], title: 'Rights-aware audio and caption stage', proposal: 'Keep soundtrack, transcript, subtitle timing and audio rights as separate reviewable artifacts.', test: 'Review transcript, timing, loudness and license/consent evidence.' },
    { terms: ['upscale', 'enhance', 'resolution', 'sharpness'], title: 'Post-generation enhancement', proposal: 'Enhance only after the best identity-consistent source is chosen; retain originals and settings.', test: 'Compare source and enhanced frames for detail loss and false texture.' }
  ];
  const results = rules.filter(rule => rule.terms.some(term => text.includes(term)));
  return (results.length ? results : [{ title: 'Input/output contract', proposal: 'Document public inputs, visible outputs, constraints and unknowns before designing an independent module.', test: 'Repeat an authorized input and compare validity, consistency and failure handling.' }])
    .map(({ title, proposal, test }) => ({ title, proposal, test, basis: 'Public behaviour only; proprietary internals not inferred or copied.' }));
}

const EARNING_SOURCES = [
  { name: 'Karmyug AI', url: 'https://work.karmyug.in/jobs', kind: 'Phone-based voice/data tasks', note: 'Last checked listings showed ₹2 per approved recording. Easy to start, but below the ₹50–₹200 task target; verify available tasks and payout terms.' },
  { name: 'YPAI Data Annotator India', url: 'https://freelancer.ypai.ai/jobs/openings/data-annotator-in', kind: 'Image/video/audio/text annotation', note: 'Official India role page advertises typical INR 550–800/hour. Selection, project volume and exact invitation rate are not guaranteed.' },
  { name: 'YPAI Model Evaluator India', url: 'https://freelancer.ypai.ai/jobs/openings/model-evaluator-in', kind: 'AI answer evaluation and fact-checking', note: 'Official India role page advertises typical INR 550–800/hour. Requires rubric-based judgement and clear written reasoning; selection is required.' },
  { name: 'YPAI Data Collection Contributor India', url: 'https://freelancer.ypai.ai/jobs/openings/data-contributor-in', kind: 'Audio/video/image/text data collection', note: 'Official India role page advertises typical INR 550–800/hour. Device, consent and project-specific instructions apply.' },
  { name: 'HumanSignal AI Training Contributors', url: 'https://onboard.humansignal.com/', kind: 'AI training and data labeling', note: 'Rates appear after matching to an eligible project. Location, skills, ID checks and project availability apply.' },
  { name: 'Corpshore/Jwuma India', url: 'https://platform.corpshore.ai/india', kind: 'AI annotation, evaluation and transcription', note: 'Public pages may show USD per-task examples; the exact accepted task and rate must be confirmed before starting.' },
  { name: 'CrowdGen by Appen', url: 'https://crowdgen.com/coffee-en-in/', kind: 'AI data & evaluation projects', note: 'Project availability and payout requirements change; if the project page is unavailable, use the official main site and re-check eligibility.' },
  { name: 'Clickworker', url: 'https://www.clickworker.com/clickworker/', kind: 'Microtasks & data work', note: 'Check India availability and supported payout method before investing time.' },
  { name: 'OneForma', url: 'https://www.oneforma.com/jobs/', kind: 'Language & AI projects', note: 'Project requirements, rates and recruitment status vary. Avoid jobs whose country or professional qualifications do not fit you.' },
  { name: 'TELUS Digital AI Community', url: 'https://jobs.telusdigital.com/search/cfm5/ai-community/jobs/in/country/india', kind: 'Rating & evaluation roles', note: 'Application and qualification based; not instant task income.' },
  { name: 'Microworkers', url: 'https://www.microworkers.com/', kind: 'Small online tasks', note: 'KYC and withdrawal conditions apply. Use only genuine tasks and proof.' },
  { name: 'Toloka', url: 'https://toloka.ai/tolokers/', kind: 'Data annotation and related work', note: 'Check current country/project restrictions and payment route.' },
  { name: 'OpenTrain Python Software Engineering LLM Evaluator', url: 'https://www.opentrain.ai/jobs/python-software-engineering-llm-evaluator--cmub37q18000d0agmbhe9iifm/', kind: 'Specialist coding evaluation', note: 'A specialist listing has advertised high per-task pay, but only apply if your real Python/software evaluation skills match the requirements; verify live terms.' },
  { name: 'Gitcoin Bounties', url: 'https://gitcoin.co/mechanisms/bounties', kind: 'Open-source & skill bounties', note: 'Acceptance is competitive; check the live amount, deadline, requirements and payout terms.' }
];

const EARNING_LEADS = [
  {
    id: 'ypai-annotator', title: 'Data Annotator — India', source: 'YPAI Data Annotator India',
    url: 'https://freelancer.ypai.ai/jobs/openings/data-annotator-in',
    rate: '₹550–₹800/hour typical project rate', ratePerTaskInr: null, rateValue: '550-800', rateUnit: 'Per hour', rateCurrency: 'INR', badge: 'High-value; application required',
    detail: 'The official India page advertises typical project pay of INR 550–800/hour and biweekly payments after approved work. This is not a guaranteed offer: application review, qualification, project supply and exact invitation rate apply.'
  },
  {
    id: 'ypai-evaluator', title: 'Model Evaluator — India', source: 'YPAI Model Evaluator India',
    url: 'https://freelancer.ypai.ai/jobs/openings/model-evaluator-in',
    rate: '₹550–₹800/hour typical project rate', ratePerTaskInr: null, rateValue: '550-800', rateUnit: 'Per hour', rateCurrency: 'INR', badge: 'High-value; judgement required',
    detail: 'Rate is a typical project range shown by the provider, not guaranteed work. The role requires reading AI answers against project rubrics and explaining why an answer is correct or wrong.'
  },
  {
    id: 'ypai-contributor', title: 'Data Collection Contributor — India', source: 'YPAI Data Collection Contributor India',
    url: 'https://freelancer.ypai.ai/jobs/openings/data-contributor-in',
    rate: '₹550–₹800/hour typical project rate', ratePerTaskInr: null, rateValue: '550-800', rateUnit: 'Per hour', rateCurrency: 'INR', badge: 'Device/project requirements',
    detail: 'The provider advertises typical INR 550–800/hour with payment every two weeks after approved work. Follow project capture instructions and consent requirements; exact pay and work volume depend on the invitation.'
  },
  {
    id: 'ypai-voice', title: 'Voice Recording Contributor — India', source: 'YPAI Voice Recording Contributor India',
    url: 'https://freelancer.ypai.ai/jobs/openings/voice-recording-contributor-in',
    rate: '₹550–₹800/hour typical project rate', ratePerTaskInr: null, rateValue: '550-800', rateUnit: 'Per hour', rateCurrency: 'INR', badge: 'Native language + quiet room',
    detail: 'Official page currently says applications open in India and advertises typical INR 550–800/hour. Native or near-native language, suitable recording device and quiet space are needed. Work is project-based; payment is biweekly after approved work. Verify exact invitation terms.'
  },
  {
    id: 'ypai-text-nlp', title: 'Text and NLP Annotator — India', source: 'YPAI Text and NLP Annotator India',
    url: 'https://freelancer.ypai.ai/jobs/openings/text-annotator-in',
    rate: 'Project-specific rate; verify invitation', ratePerTaskInr: null, rateValue: '', rateUnit: 'Unknown', rateCurrency: 'INR', badge: 'Native language + assessment',
    detail: 'Official page currently says applications open in India. Requires native or near-native command of the annotation language and project assessment. Work availability depends on language demand; check exact rate before accepting.'
  },
  {
    id: 'ypai-translator', title: 'Translator — India', source: 'YPAI Translator India',
    url: 'https://freelancer.ypai.ai/jobs/openings/translator-in',
    rate: '₹950–₹1,450/hour typical project rate', ratePerTaskInr: null, rateValue: '950-1450', rateUnit: 'Per hour', rateCurrency: 'INR', badge: 'Strong writing + English required',
    detail: 'Official page currently says applications open in India and advertises typical INR 950–1,450/hour. Requires native or near-native writing in your language and strong written English. Language-pair demand and selection apply; exact rate is stated in the invitation.'
  },
  {
    id: 'humansignal', title: 'HumanSignal AI Training Contributor', source: 'HumanSignal AI Training Contributors',
    url: 'https://onboard.humansignal.com/',
    rate: 'Rate shown after eligible project matching', ratePerTaskInr: null, rateValue: '', rateUnit: 'Unknown', rateCurrency: 'INR', badge: 'Profile and matching required',
    detail: 'Create a truthful profile, verify your identity and see if eligible projects are available in your location and skill areas. No rate or work is promised before matching.'
  },
  {
    id: 'jwuma-india', title: 'AI Annotation & Evaluation Tasks — India', source: 'Corpshore/Jwuma India',
    url: 'https://platform.corpshore.ai/india',
    rate: 'Public pages have shown USD per-task examples; exact task rate varies', ratePerTaskInr: null, rateValue: '', rateUnit: 'Unknown', rateCurrency: 'USD', badge: 'Verify exact offer',
    detail: 'The provider lists annotation, evaluation and transcription work. Confirm the exact available task, payment unit, currency, qualification and payout method in your own offer before starting.'
  },
  {
    id: 'karmyug-hindi', title: 'Hindi Script Recording Project', source: 'Karmyug AI',
    url: 'https://work.karmyug.in/jobs/d6f10b46-7249-4484-b114-c8008519acbf',
    rate: '₹2 per approved recording', ratePerTaskInr: 2, rateValue: '2', rateUnit: 'Per approved task', rateCurrency: 'INR', badge: 'Below target',
    detail: 'Public listing shows ₹2 per approved recording. Current task slots, deadline, quality acceptance and payout terms must be confirmed on the official page.'
  },
  {
    id: 'karmyug-english', title: 'English Script Recording Project', source: 'Karmyug AI',
    url: 'https://work.karmyug.in/jobs/df3d4bf3-c11b-449c-abd6-97e382c5bdf9',
    rate: '₹2 per approved recording', ratePerTaskInr: 2, rateValue: '2', rateUnit: 'Per approved task', rateCurrency: 'INR', badge: 'Below target',
    detail: 'Public listing shows ₹2 per approved recording. Current task slots, deadline, quality acceptance and payout terms must be confirmed on the official page.'
  },
  {
    id: 'crowdgen-coffee', title: 'Project Coffee — India Data Labeling', source: 'CrowdGen by Appen',
    url: 'https://crowdgen.com/coffee-en-in/',
    rate: 'US$2/hour (page previously advertised about ₹175/hour)', ratePerTaskInr: null, rateValue: '2', rateUnit: 'Per hour', rateCurrency: 'USD', badge: 'Hourly, not per task',
    detail: 'The project page has sometimes been unavailable in automated scans. Published requirements included India residence, fluent English and laptop/PC. Re-check the live page and recruitment status; this is an hourly USD rate, not ₹175 per task.'
  },
  {
    id: 'opentrain-python', title: 'Python Software Engineering LLM Evaluator', source: 'OpenTrain Python Software Engineering LLM Evaluator',
    url: 'https://www.opentrain.ai/jobs/python-software-engineering-llm-evaluator--cmub37q18000d0agmbhe9iifm/',
    rate: '$100 per task advertised in the specific role listing', ratePerTaskInr: null, rateValue: '100', rateUnit: 'Per task', rateCurrency: 'USD', badge: 'Specialist only',
    detail: 'A public listing described a coding-evaluation contract and India among eligible countries. It requires genuine Python/software-engineering judgement and strong English. Verify the current live rate and only apply if your real experience matches; no skills are assumed.'
  }
];

const EARNING_STATUSES = ['Lead found', 'Applied', 'Qualification pending', 'Approved to work', 'Work submitted', 'Accepted', 'Rejected', 'Payment pending', 'Paid'];

const PDF_AGENT_ROLES = [
  { name: 'Architect', status: 'Partial', note: 'Routes known tasks; no general autonomous planner.' },
  { name: 'Coder', status: 'Not implemented', note: 'No safe, tested code-generation worker yet.' },
  { name: 'Reviewer / Editor', status: 'Partial', note: 'Evidence and annotation checks exist; not a general security auditor.' },
  { name: 'Researcher', status: 'Partial', note: 'Bounded public-source research exists; verify current terms manually.' },
  { name: 'Writer', status: 'Partial', note: 'Offline caption, calendar and Reel draft templates exist.' },
  { name: 'Analyst', status: 'Partial', note: 'Structured tracking exists; general AI analysis is not connected.' },
  { name: 'Communicator', status: 'Partial', note: 'Creates drafts only; does not send messages.' },
  { name: 'Executor', status: 'Partial', note: 'Local task routing only; no arbitrary shell or external actions.' },
  { name: 'Memory', status: 'Partial', note: 'Evaluation/learning loop exists; no semantic conversation vector store connected.' },
  { name: 'Orchestrator', status: 'Partial', note: 'Offline workflows coordinate bounded functions; CrewAI/LangGraph are not installed.' }
];
const DEFAULT_AGENT_BRIEF = {
  businessName: 'Sample Cafe',
  businessType: 'Cafe / restaurant',
  location: 'Ahmedabad',
  audience: 'local customers',
  offer: 'coffee and fresh pastries',
  platform: 'Instagram',
  brandVoice: 'warm and friendly',
  callToAction: 'Save this idea for your next outing',
  verifiedFacts: ''
};

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
  const [agentBrief, setAgentBrief] = React.useState(() => readStore('aps-agent-brief', DEFAULT_AGENT_BRIEF));
  const [agentRuns, setAgentRuns] = React.useState(() => readStore('aps-agent-runs', []));
  const [agentOutput, setAgentOutput] = React.useState(() => readStore('aps-agent-output', null));
  const [trainingRuns, setTrainingRuns] = React.useState(() => readStore('aps-training-runs', []));
  const [trainingForm, setTrainingForm] = React.useState(() => readStore('aps-training-form', {
    agent: 'Writer / Content Strategist',
    task: 'Create a clear Instagram caption',
    baselineScore: '60',
    candidateScore: '75',
    errorCategory: 'Clarity / completeness',
    regression: 'pass',
    evidence: '',
    changeSummary: ''
  }));
  const [podState, setPodState] = React.useState(() => readStore('aps-pod-state', {}));
  const [search, setSearch] = React.useState('');
  const [productFilter, setProductFilter] = React.useState('All products');
  const [stageFilter, setStageFilter] = React.useState('All stages');
  const [notice, setNotice] = React.useState('');
  const [earningsLog, setEarningsLog] = React.useState(() => readStore('aps-earnings-log', []));
  const [earningTitle, setEarningTitle] = React.useState('');
  const [earningSource, setEarningSource] = React.useState('Karmyug AI');
  const [earningRate, setEarningRate] = React.useState('');
  const [earningRateUnit, setEarningRateUnit] = React.useState('Per accepted task');
  const [earningRateCurrency, setEarningRateCurrency] = React.useState('INR');
  const [earningUrl, setEarningUrl] = React.useState('');
  const [earningStatus, setEarningStatus] = React.useState('Lead found');
  const [creativeObservation, setCreativeObservation] = React.useState(() => readStore('aps-creative-observation-form', {
    toolName: '', sourceUrl: '', observedOn: new Date().toISOString().slice(0, 10),
    publicBehavior: '', inputOutputObserved: '', unknowns: 'Underlying model, internal prompts and private implementation details are not verified.'
  }));
  const [creativeObservationRuns, setCreativeObservationRuns] = React.useState(() => readStore('aps-creative-observation-runs', []));
  const [creativeCycleForm, setCreativeCycleForm] = React.useState(() => readStore('aps-creative-cycle-form', {
    experimentName: 'Client-specific cinematic ad experiment',
    baselineScore: '60', candidateScore: '75', evidence: '',
    actualOutputsReviewed: false, assetRightsConfirmed: false, commercialLicenseCleared: false,
    noUnsupportedClaims: false, noDirectImitation: false, privacyReviewed: false
  }));
  const [creativeCycles, setCreativeCycles] = React.useState(() => readStore('aps-creative-cycles', []));

  React.useEffect(() => { localStorage.setItem('aps-notes', JSON.stringify(notes)); }, [notes]);
  React.useEffect(() => { localStorage.setItem('aps-agent-brief', JSON.stringify(agentBrief)); }, [agentBrief]);
  React.useEffect(() => { localStorage.setItem('aps-agent-runs', JSON.stringify(agentRuns.slice(0, 10))); }, [agentRuns]);
  React.useEffect(() => { if (agentOutput) localStorage.setItem('aps-agent-output', JSON.stringify(agentOutput)); }, [agentOutput]);
  React.useEffect(() => { localStorage.setItem('aps-training-runs', JSON.stringify(trainingRuns.slice(0, 30))); }, [trainingRuns]);
  React.useEffect(() => { localStorage.setItem('aps-training-form', JSON.stringify(trainingForm)); }, [trainingForm]);
  React.useEffect(() => { localStorage.setItem('aps-pod-state', JSON.stringify(podState)); }, [podState]);
  React.useEffect(() => { localStorage.setItem('aps-earnings-log', JSON.stringify(earningsLog)); }, [earningsLog]);
  React.useEffect(() => { localStorage.setItem('aps-creative-observation-form', JSON.stringify(creativeObservation)); }, [creativeObservation]);
  React.useEffect(() => { localStorage.setItem('aps-creative-observation-runs', JSON.stringify(creativeObservationRuns.slice(0, 30))); }, [creativeObservationRuns]);
  React.useEffect(() => { localStorage.setItem('aps-creative-cycle-form', JSON.stringify(creativeCycleForm)); }, [creativeCycleForm]);
  React.useEffect(() => { localStorage.setItem('aps-creative-cycles', JSON.stringify(creativeCycles.slice(0, 50))); }, [creativeCycles]);

  function add() {
    if (!task.trim()) return;
    setNotes([{ text: task.trim(), status: 'Queued locally', time: new Date().toLocaleString() }, ...notes]);
    setTask('');
  }

  async function importTrainingEvidenceFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const record = JSON.parse(await file.text());
      if (record.record_type !== 'autopilot_learning_cycle_evidence_v1' || !record.result || !record.result.baseline_review || !record.result.candidate_review) {
        throw new Error('This is not a supported Python learning-cycle evidence JSON file.');
      }
      const result = record.result;
      const baselineScore = Number(result.baseline_review.weighted_score);
      const candidateScore = Number(result.candidate_review.weighted_score);
      const regression = result.regression_passed === true ? 'pass' : 'fail';
      const run = {
        id: result.task_id || 'imported-' + Date.now(),
        createdAt: record.created_at || new Date().toISOString(),
        agent: record.agent_name || 'Unspecified specialist',
        task: result.task_id || 'Imported Python learning-cycle result',
        baselineScore, candidateScore,
        delta: Number(result.comparison?.delta ?? (candidateScore - baselineScore)),
        errorCategory: record.error_category || 'Unspecified',
        regression,
        evidence: record.evidence_notes || result.change_rationale || '',
        changeSummary: result.change_rationale || '',
        approvalStatus: result.reviewer_approved ? 'Reviewer approved for manual release review' :
          result.decision === 'awaiting_human_approval' ? 'Pending human review' : result.decision,
        status: result.decision,
        scoreMethod: 'Imported from actual Python evaluation-cycle output; rubric scores remain reviewer-supplied',
        approvedAt: null,
        importedEvidence: true,
        result
      };
      setTrainingRuns(prev => [run, ...prev.filter(x => x.id !== run.id)].slice(0, 30));
      setNotice('Python learning-cycle evidence imported. Decision: ' + result.decision + '. No code deployed and no model weights changed.');
    } catch (error) {
      setNotice('Import failed: ' + (error?.message || 'invalid JSON'));
    } finally {
      event.target.value = '';
    }
  }

  function updateTrainingForm(field, value) {
    setTrainingForm(prev => ({ ...prev, [field]: value }));
  }

  function recordTrainingCycle(event) {
    event.preventDefault();
    const baseline = Number(trainingForm.baselineScore);
    const candidate = Number(trainingForm.candidateScore);
    if (!Number.isFinite(baseline) || !Number.isFinite(candidate) || baseline < 0 || baseline > 100 || candidate < 0 || candidate > 100) {
      setNotice('Baseline and candidate scores must be between 0 and 100.');
      return;
    }
    const run = {
      id: 'cycle-' + Date.now(),
      createdAt: new Date().toISOString(),
      agent: trainingForm.agent,
      task: trainingForm.task.trim(),
      baselineScore: baseline,
      candidateScore: candidate,
      delta: candidate - baseline,
      errorCategory: trainingForm.errorCategory,
      regression: trainingForm.regression,
      evidence: trainingForm.evidence.trim(),
      changeSummary: trainingForm.changeSummary.trim(),
      approvalStatus: 'Pending human review',
      status: trainingForm.regression === 'fail' ? 'blocked_regression' : 'review_required',
      scoreMethod: 'Manually entered reviewer scores; not an independent AI evaluation',
      approvedAt: null
    };
    setTrainingRuns(prev => [run, ...prev].slice(0, 30));
    setNotice(trainingForm.regression === 'fail' ? 'Cycle recorded and blocked: regression failed. No approval or release performed.' : 'Cycle recorded for human review. Scores are manually entered and do not prove model learning.');
  }

  function decideTrainingCycle(id, decision) {
    setTrainingRuns(prev => prev.map(run => run.id === id
      ? { ...run, approvalStatus: decision === 'approve' ? 'Approved by user in dashboard' : 'Rejected by user in dashboard', status: decision === 'approve' && run.regression === 'pass' && run.delta >= 0 ? 'approved_for_manual_release' : 'rejected_or_blocked', approvedAt: new Date().toISOString() }
      : run));
    setNotice(decision === 'approve'
      ? 'Marked approved for manual release only. This does not deploy code or change model weights.'
      : 'Cycle rejected. No code or model weights were changed.');
  }

  function exportTrainingLog() {
    saveDownload('autopilot-training-loop-evidence.json', JSON.stringify({
      exportedAt: new Date().toISOString(),
      source: 'device-local training loop dashboard',
      limitations: ['Scores are manually entered, not independently generated.', 'No model weights are trained.', 'Approval records do not deploy code.', 'This local log is not a server-backed audit log.'],
      runs: trainingRuns
    }, null, 2), 'application/json;charset=utf-8;');
    setNotice('Training-loop evidence exported. See the JSON limitations before interpreting results.');
  }

  function updateAgentBrief(field, value) {
    setAgentBrief(prev => ({ ...prev, [field]: value }));
  }

  function runLocalContentWorkflow(event) {
    event.preventDefault();
    const brief = Object.fromEntries(Object.entries(agentBrief).map(([key, value]) => [key, String(value ?? '').trim()]));
    const required = ['businessName', 'businessType', 'audience', 'offer'];
    const missing = required.filter(key => !brief[key]);
    if (missing.length) {
      setNotice('Complete business name, type, audience and offer before running the draft workflow.');
      return;
    }
    const id = 'local-' + Date.now();
    const createdAt = new Date().toISOString();
    const offer = brief.offer.replace(/[.!?]+$/, '');
    const cta = brief.callToAction || 'Save this post for later';
    const location = brief.location ? ` in ${brief.location}` : '';
    const facts = brief.verifiedFacts || 'Add one verified product, service or business detail before publishing.';
    const captions = [
      `${brief.businessName}: ${offer}. A simple introduction for ${brief.audience}. ${cta}.`,
      `Looking for ${offer}${location}? This ${brief.businessType.toLowerCase()} content idea is for ${brief.audience}. Check the details and choose what fits you. ${cta}.`,
      `A little look at ${brief.businessName}. Topic: ${offer}. Keep the message clear, use real photos or footage, and share only confirmed details. ${cta}.`
    ];
    const calendar = [
      { day: 'Day 1', format: 'Intro post', idea: `Introduce ${brief.businessName} and explain ${offer} in plain language.` },
      { day: 'Day 2', format: 'Helpful tip', idea: `Share one useful tip related to ${offer}; fact-check it before posting.` },
      { day: 'Day 3', format: 'Behind the scenes', idea: 'Show a real workspace, preparation step or service process, only if footage is available.' },
      { day: 'Day 4', format: 'FAQ', idea: `Answer one real customer question about ${offer} using a confirmed answer.` },
      { day: 'Day 5', format: 'Product or service detail', idea: `Explain one feature or step of ${offer}. Use this verified detail: ${facts}` },
      { day: 'Day 6', format: 'Story poll', idea: `Ask ${brief.audience} a relevant question; avoid implying customer results that are not evidenced.` },
      { day: 'Day 7', format: 'Weekly recap', idea: `Summarize the week's useful points and invite viewers to take this action: ${cta}.` }
    ];
    const reelScript = [
      { time: '0–3 sec', visual: 'Clear shot of the actual product, place or service', onScreen: `Need to know about ${offer}?`, voiceover: `Here is a quick look at ${offer}.` },
      { time: '3–7 sec', visual: `Show ${brief.businessName} or the relevant work in progress`, onScreen: brief.businessName, voiceover: `This is ${brief.businessName}. Show only what is genuinely available.` },
      { time: '7–12 sec', visual: 'Close-up, process demonstration or one real detail', onScreen: facts, voiceover: 'Add one verified detail or useful tip. Do not invent claims.' },
      { time: '12–17 sec', visual: 'Simple end card with readable text', onScreen: cta, voiceover: cta }
    ];
    const output = {
      id, createdAt, businessName: brief.businessName,
      status: 'review_required',
      generationMode: 'browser-local deterministic templates v0.1.0',
      agentRuns: [
        { agent: 'Brief Structurer', version: '0.1.0', status: 'completed', output: `Brief checked for ${brief.businessType}; required fields present.` },
        { agent: 'Caption Variant Lab', version: '0.1.0', status: 'completed', output: 'Three caption drafts generated from the supplied brief.' },
        { agent: 'Content Calendar Architect', version: '0.1.0', status: 'completed', output: 'Seven-day draft calendar generated.' },
        { agent: 'Reel Script Engineer', version: '0.1.0', status: 'completed', output: '17-second, four-scene Reel outline generated.' },
        { agent: 'Quality Reviewer', version: '0.1.0', status: 'review_required', output: 'Human review is required; check every factual claim, brand detail, CTA and permission before publication.' }
      ],
      brief, captions, calendar, reelScript,
      qualityNotes: [
        'This is a browser-local template workflow, not a connected language model or a call to the Python backend.',
        'No public web research, client contact, DM, publication, listing change or purchase was performed.',
        'Review the wording and verify all business claims before using the material externally.',
        'Treat sample or fictional business details as spec work; do not imply a real client relationship.'
      ],
      evidence: { generatedInCurrentBrowser: true, externalSourcesFetched: false, outreachSent: false, contentPublished: false, modelApiCalled: false }
    };
    setAgentOutput(output);
    setAgentRuns(prev => [output, ...prev].slice(0, 10));
    setNotes(prev => [{ text: `Draft package generated: ${brief.businessName}`, status: 'Review required · local templates', time: new Date().toLocaleString() }, ...prev].slice(0, 30));
    setNotice('Draft package generated locally. It has not been published or sent.');
  }

  function exportAgentRun(run) {
    saveDownload(`autopilot-agent-run-${run.id}.json`, JSON.stringify(run, null, 2), 'application/json;charset=utf-8;');
    setNotice('Run evidence JSON exported. It records a local template draft, not a live or model-backed agent run.');
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
      claimedRateText: earningRate.trim(),
      claimedRateCurrency: earningRateCurrency,
      claimedRateUnit: earningRateUnit,
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
    setEarningRateUnit('Per accepted task');
    setEarningRateCurrency('INR');
    setEarningUrl('');
    setEarningStatus('Lead found');
    setNotice('Task saved on this device. No application or task submission was made.');
  }
  function updateEarning(id, field, value) {
    const current = earningsLog.find(item => item.id === id);
    if (!current) return;
    if (field === 'status' && value === 'Applied' && current.status !== 'Applied') {
      const confirmation = window.prompt('Confirm only after you submitted the application on the official site. Enter the confirmation/reference text (do not enter passwords, OTPs or ID numbers):');
      if (!confirmation || !confirmation.trim()) {
        setNotice('Status unchanged. Add Applied only after submission and a confirmation/reference.');
        return;
      }
      setEarningsLog(prev => prev.map(item => item.id === id ? { ...item, status: value, applicationEvidenceNote: confirmation.trim(), applicationConfirmedAt: new Date().toISOString(), updatedAt: new Date().toISOString() } : item));
      setNotice('Application marked Applied based on your confirmation. The app did not submit it or independently verify the platform.');
      return;
    }
    if (field === 'status' && value === 'Paid' && current.status !== 'Paid') {
      const amount = Number(current.payoutInr);
      if (!Number.isFinite(amount) || amount <= 0) {
        setNotice('Cannot mark Paid yet: enter the actual payout received (₹) first.');
        return;
      }
      const confirmation = window.prompt('Confirm the money actually arrived. Enter a short evidence note (e.g. payout date/reference; no bank details, OTPs or account numbers):');
      if (!confirmation || !confirmation.trim()) {
        setNotice('Status unchanged. A payout evidence note is required.');
        return;
      }
      setEarningsLog(prev => prev.map(item => item.id === id ? { ...item, status: value, paymentEvidenceNote: confirmation.trim(), paymentConfirmedAt: new Date().toISOString(), updatedAt: new Date().toISOString() } : item));
      setNotice('Marked Paid based on your confirmation only; receipt was not independently verified by the app.');
      return;
    }
    setEarningsLog(prev => prev.map(item => item.id === id ? { ...item, [field]: value, updatedAt: new Date().toISOString() } : item));
  }
  function exportEarnings() {
    const cols = ['id','source','title','claimed_rate_text','rate_currency','rate_unit','status','actual_earned_inr','payout_received_inr','url','created_at','updated_at'];
    const rows = [
      cols.map(csvCell).join(','),
      ...earningsLog.map(item => [item.id,item.source,item.title,item.claimedRateText ?? item.claimedRateInr,item.claimedRateCurrency || 'Unknown',item.claimedRateUnit || 'Unknown',item.status,item.earnedInr,item.payoutInr,item.url,item.createdAt,item.updatedAt].map(csvCell).join(','))
    ];
    saveDownload('autopilot-earnings-tracker.csv', '\ufeff' + rows.join('\r\n'));
    setNotice('Earnings tracker CSV exported. It contains only entries saved on this device.');
  }
  function deleteEarning(id) {
    setEarningsLog(prev => prev.filter(item => item.id !== id));
    setNotice('Tracker entry removed from this device.');
  }
  function updateCreativeObservation(field, value) {
    setCreativeObservation(prev => ({ ...prev, [field]: value }));
  }
  function analyzeCreativeObservation(event) {
    event.preventDefault();
    const observation = {
      toolName: creativeObservation.toolName.trim(),
      sourceUrl: creativeObservation.sourceUrl.trim(),
      observedOn: creativeObservation.observedOn,
      publicBehavior: creativeObservation.publicBehavior.trim(),
      inputOutputObserved: creativeObservation.inputOutputObserved.trim(),
      unknowns: creativeObservation.unknowns.trim()
    };
    if (!observation.toolName || !observation.publicBehavior || !observation.inputOutputObserved || !observation.unknowns) {
      setNotice('Fill the tool name, visible behaviour, observed input/output and unknowns first.');
      return;
    }
    if (!observation.sourceUrl.startsWith('https://')) {
      setNotice('Use a public HTTPS source URL. Private pages, code or bypassed access are out of scope.');
      return;
    }
    const run = {
      id: 'observation-' + Date.now(),
      createdAt: new Date().toISOString(),
      ...observation,
      hypotheses: deriveCreativeHypotheses({
        publicBehavior: observation.publicBehavior,
        inputOutputObserved: observation.inputOutputObserved
      }),
      executionTruth: {
        pageFetched: false,
        privateCodeCopied: false,
        accessControlsBypassed: false,
        generatedBy: 'Browser-local rule-based hypothesis mapper'
      },
      status: 'review_required'
    };
    setCreativeObservationRuns(prev => [run, ...prev].slice(0, 30));
    setNotice('Observation saved locally and original experiment ideas generated. The URL was not fetched; review the public source yourself.');
  }
  function updateCreativeCycleForm(field, value) {
    setCreativeCycleForm(prev => ({ ...prev, [field]: value }));
  }
  function recordCreativeExperimentCycle(event) {
    event.preventDefault();
    const baseline = Number(creativeCycleForm.baselineScore);
    const candidate = Number(creativeCycleForm.candidateScore);
    if (!creativeCycleForm.experimentName.trim() || !Number.isFinite(baseline) || !Number.isFinite(candidate) ||
        baseline < 0 || baseline > 100 || candidate < 0 || candidate > 100) {
      setNotice('Enter an experiment name and valid baseline/candidate scores between 0 and 100.');
      return;
    }
    const hardGates = {
      assetRightsConfirmed: creativeCycleForm.assetRightsConfirmed,
      commercialLicenseCleared: creativeCycleForm.commercialLicenseCleared,
      noUnsupportedClaims: creativeCycleForm.noUnsupportedClaims,
      noDirectImitation: creativeCycleForm.noDirectImitation,
      privacyReviewed: creativeCycleForm.privacyReviewed,
      actualOutputsExist: creativeCycleForm.actualOutputsReviewed && Boolean(creativeCycleForm.evidence.trim())
    };
    const allGatesPass = Object.values(hardGates).every(Boolean);
    let decision;
    if (!creativeCycleForm.actualOutputsReviewed || !creativeCycleForm.evidence.trim()) decision = 'NEED_REAL_OUTPUT_MEASUREMENTS';
    else if (!allGatesPass) decision = 'BLOCK_PROMOTION_FIX_HARD_GATES';
    else if (candidate > baseline) decision = 'PROMOTE_CANDIDATE_TO_HUMAN_REVIEW';
    else decision = 'KEEP_BASELINE_OR_RUN_ANOTHER_EXPERIMENT';
    const cycle = {
      id: 'creative-cycle-' + Date.now(),
      createdAt: new Date().toISOString(),
      experimentName: creativeCycleForm.experimentName.trim(),
      baselineScore: baseline,
      candidateScore: candidate,
      delta: Number((candidate - baseline).toFixed(2)),
      scoreMethod: 'Manual reviewer-entered scores; not an independent AI evaluation.',
      evidence: creativeCycleForm.evidence.trim(),
      metricsAreActual: creativeCycleForm.actualOutputsReviewed && Boolean(creativeCycleForm.evidence.trim()),
      hardGates,
      hardGatesPassed: allGatesPass,
      decision,
      productionAutoDeployed: false,
      paidProviderAutoSelected: false,
      modelWeightsChanged: false
    };
    setCreativeCycles(prev => [cycle, ...prev].slice(0, 50));
    setNotice(decision === 'PROMOTE_CANDIDATE_TO_HUMAN_REVIEW'
      ? 'Candidate is eligible for human review only. Nothing was deployed or published.'
      : decision === 'NEED_REAL_OUTPUT_MEASUREMENTS'
        ? 'Cycle recorded as unmeasured. Placeholder scores cannot promote a candidate.'
        : decision === 'BLOCK_PROMOTION_FIX_HARD_GATES'
          ? 'Promotion blocked: resolve every rights, license, factuality, originality, privacy and output gate.'
          : 'Baseline retained. Change one variable and compare actual outputs using the same brief.');
  }
  function exportCreativeIntelligence() {
    const output = {
      exportedAt: new Date().toISOString(),
      registryVersion: 'browser-local-creative-intelligence-prototype-v1',
      tools: CREATIVE_TOOL_CARDS,
      observations: creativeObservationRuns,
      cycles: creativeCycles,
      limitations: [
        'This dashboard prototype stores data in this browser; it is not synced to the Python CLI or GitHub ledger.',
        'The hypothesis mapper uses the text you enter; it does not fetch the source URL or inspect private internals.',
        'Scores are reviewer-entered and do not prove sales, virality or model learning.',
        'The page does not run an LLM, render images/videos, call ComfyUI or publish content.',
        'No private code is copied; no access controls are bypassed; no paid provider is selected automatically.'
      ]
    };
    saveDownload('autopilot-creative-intelligence-evidence.json', JSON.stringify(output, null, 2), 'application/json;charset=utf-8;');
    setNotice('Creative Intelligence evidence exported. Check the limitations in the JSON before interpreting it.');
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
      <div className="side-note"><span className="dot"/> Local workspace<br/><small>Daily public scan · no auto-submit</small></div>
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
            <a className="primary earning-link-button" href="https://github.com/kumbipakam29-dev/autopilot-studio/actions/workflows/data-labeling-hunter.yml" target="_blank" rel="noreferrer">Open data-labeling scan ↗</a>
            <button className="secondary" onClick={exportEarnings}>Export tracker ↓</button>
          </div>
        </section>

        <div className="earning-stats">
          <article><small>SOURCE PROFILES IN REGISTRY</small><b>{EARNING_SOURCES.length}</b><span>Live fetch status is in the GitHub Actions report</span></article>
          <article><small>₹50–₹200 PER TASK</small><b>{targetLeadCount}</b><span>Exact public INR rates in this lead snapshot</span></article>
          <article><small>ACTUAL EARNED</small><b>₹{earnedTotal.toFixed(2)}</b><span>Only what you record as accepted</span></article>
          <article><small>PAYOUT RECEIVED</small><b>₹{payoutTotal.toFixed(2)}</b><span>Enter only when money really arrives</span></article>
        </div>

        <div className="notice"><b>Higher-value data-labeling experiments</b><p>YPAI's official India pages advertise typical project pay of <strong>₹550–₹800/hour</strong> for data annotation, model evaluation and data collection. Application review, qualification, work availability and the exact project rate are not guaranteed. Karmyug's public listings have shown ₹2 per approved recording, which is below the target. The app uses a dated lead snapshot; verify the official listing and current terms before applying.</p></div>

        <section className="earning-section">
          <div className="earning-section-head"><div><h3>Specific leads found</h3><p>Rate and availability here reflect the last scan; verify live details before applying.</p></div><span className="status warn">No target-rate task verified</span></div>
          <div className="earning-lead-grid">{EARNING_LEADS.map(lead => <article className="earning-lead" key={lead.id}>
            <div className="earning-lead-top"><span className={'status ' + (lead.ratePerTaskInr === 2 ? 'warn' : '')}>{lead.badge}</span><small>{lead.source}</small></div>
            <h4>{lead.title}</h4><div className="earning-rate">{lead.rate}</div><p>{lead.detail}</p>
            <div className="earning-actions"><a href={lead.url} target="_blank" rel="noreferrer">Open official listing ↗</a><button className="secondary" onClick={() => { setEarningTitle(lead.title); setEarningSource(lead.source); setEarningRate(lead.rateValue ?? (lead.ratePerTaskInr === null ? '' : String(lead.ratePerTaskInr))); setEarningRateUnit(lead.rateUnit || 'Unknown'); setEarningRateCurrency(lead.rateCurrency || (lead.ratePerTaskInr !== null ? 'INR' : 'Unknown')); setEarningUrl(lead.url); setNotice('Lead added to the form below. Review it and save your tracker entry.'); document.getElementById('earning-tracker-form')?.scrollIntoView({behavior:'smooth', block:'start'}); }}>Track this lead +</button></div>
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
            <label>Posted rate (range allowed)<input type="text" value={earningRate} onChange={e => setEarningRate(e.target.value)} placeholder="e.g. 550-800" /></label>
            <label>Rate currency<select value={earningRateCurrency} onChange={e => setEarningRateCurrency(e.target.value)}>{['INR','USD','EUR','GBP','Unknown'].map(code => <option key={code}>{code}</option>)}</select></label>
            <label>Rate unit<select value={earningRateUnit} onChange={e => setEarningRateUnit(e.target.value)}>{['Per accepted task','Per task','Per hour','Per batch','Fixed project','Unknown'].map(unit => <option key={unit}>{unit}</option>)}</select></label>
            <label>Official task URL<input type="url" value={earningUrl} onChange={e => setEarningUrl(e.target.value)} placeholder="https://…" /></label>
            <label>Status<select value={earningStatus} onChange={e => setEarningStatus(e.target.value)}>{EARNING_STATUSES.map(status => <option key={status}>{status}</option>)}</select></label>
            <button className="primary" type="submit">Save tracker entry</button>
          </form>
          {notice && <div className="inline-notice" role="status">{notice}</div>}
          {earningsLog.length ? <div className="earning-log-list">{earningsLog.map(item => <article className="earning-log" key={item.id}>
            <div className="earning-log-head"><div><b>{item.title}</b><small>{item.source} · Rate: {item.claimedRateText ?? item.claimedRateInr ?? 'Unknown'} {item.claimedRateCurrency || 'Unknown'} / {item.claimedRateUnit || 'unit unknown'} · Added {new Date(item.createdAt).toLocaleDateString()}</small></div>{item.url && <a href={item.url} target="_blank" rel="noreferrer">Open task ↗</a>}</div>
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

      {tab === 'AI Agents' && <section className="agent-lab">
        <section className="panel">
          <div className="agent-hero-head">
            <div><p className="eyebrow">VISIBLE WORKBENCH · ZERO API COST</p><h2>Run a local content draft workflow</h2><p className="muted">This runs deterministic browser templates using the brief below. It is not a live LLM or the Python backend.</p></div>
            <span className="status good">Local run available</span>
          </div>
          <div className="notice"><b>Honest execution status</b><p>When you press Run, the browser creates real copy/calendar/Reel draft output and an evidence record on this device. No web research, AI-model API, DM, publication or external account action is performed. Saved browser data can be lost if app data is cleared.</p></div>
          <form className="agent-brief-form" onSubmit={runLocalContentWorkflow}>
            <label>Business / sample name<input value={agentBrief.businessName} onChange={e => updateAgentBrief('businessName', e.target.value)} required /></label>
            <label>Business type<input value={agentBrief.businessType} onChange={e => updateAgentBrief('businessType', e.target.value)} required /></label>
            <label>Location<input value={agentBrief.location} onChange={e => updateAgentBrief('location', e.target.value)} placeholder="City or area" /></label>
            <label>Target audience<input value={agentBrief.audience} onChange={e => updateAgentBrief('audience', e.target.value)} required /></label>
            <label>Offer / topic<input value={agentBrief.offer} onChange={e => updateAgentBrief('offer', e.target.value)} required /></label>
            <label>Platform<select value={agentBrief.platform} onChange={e => updateAgentBrief('platform', e.target.value)}>{['Instagram','LinkedIn','Facebook','WhatsApp Status'].map(x => <option key={x}>{x}</option>)}</select></label>
            <label>Brand voice<input value={agentBrief.brandVoice} onChange={e => updateAgentBrief('brandVoice', e.target.value)} placeholder="warm and friendly" /></label>
            <label>Call to action<input value={agentBrief.callToAction} onChange={e => updateAgentBrief('callToAction', e.target.value)} /></label>
            <label className="agent-wide">Verified facts / actual details<textarea value={agentBrief.verifiedFacts} onChange={e => updateAgentBrief('verifiedFacts', e.target.value)} placeholder="Optional: enter details you have verified. Leave blank if there are none." rows="3" /></label>
            <button className="primary agent-wide" type="submit">Run local draft workflow →</button>
          </form>
        </section>

        {agentOutput && <section className="panel agent-output" aria-live="polite">
          <div className="agent-output-head"><div><p className="eyebrow">LATEST RUN · {agentOutput.id}</p><h2>{agentOutput.businessName}</h2><p className="muted">{new Date(agentOutput.createdAt).toLocaleString()} · {agentOutput.generationMode}</p></div><span className="status warn">Review required</span></div>
          <div className="agent-run-steps">{agentOutput.agentRuns.map((item, i) => <article key={item.agent}><div className="agent-step-num">{String(i + 1).padStart(2, '0')}</div><div><b>{item.agent} v{item.version}</b><small>{item.output}</small></div><span className={'status ' + (item.status === 'completed' ? 'good' : 'warn')}>{item.status}</span></article>)}</div>
          <div className="agent-output-section"><h3>1. Caption drafts · {agentOutput.brief.platform}</h3>{agentOutput.captions.map((caption, i) => <article className="agent-output-card" key={i}><div><b>Caption {i + 1}</b><p>{caption}</p></div><button className="secondary" type="button" onClick={() => copyText(caption, 'Caption copied. Verify claims before use.')}>Copy</button></article>)}</div>
          <div className="agent-output-section"><h3>2. Seven-day content calendar</h3><div className="agent-calendar">{agentOutput.calendar.map(day => <article key={day.day}><span>{day.day}</span><b>{day.format}</b><p>{day.idea}</p></article>)}</div></div>
          <div className="agent-output-section"><h3>3. 17-second Reel outline</h3><div className="agent-reel-scenes">{agentOutput.reelScript.map(scene => <article key={scene.time}><span>{scene.time}</span><div><b>Visual</b><p>{scene.visual}</p><b>On-screen text</b><p>{scene.onScreen}</p><b>Voiceover</b><p>{scene.voiceover}</p></div></article>)}</div></div>
          <div className="notice"><b>Quality and evidence notes</b><ul>{agentOutput.qualityNotes.map(note => <li key={note}>{note}</li>)}</ul></div>
          <button className="primary" type="button" onClick={() => exportAgentRun(agentOutput)}>Export run evidence JSON ↓</button>
        </section>}

        <section className="panel">
          <div className="panel-head"><div><h3>PDF 10-agent ecosystem — honest status map</h3><p>Status describes mapped repository capability, not an always-running autonomous agent.</p></div><a href="https://github.com/kumbipakam29-dev/autopilot-studio/blob/feat/open-source-agent-learning-roadmap/docs/PDF_AGENT_ECOSYSTEM_CROSSWALK.md" target="_blank" rel="noreferrer">Implementation map ↗</a></div>
          <div className="agent-role-grid">{PDF_AGENT_ROLES.map(role => <article key={role.name}><div><b>{role.name}</b><span className={'status ' + (role.status === 'Not implemented' ? 'warn' : '')}>{role.status}</span></div><p>{role.note}</p></article>)}</div>
          <div className="notice"><b>Not yet connected</b><p>CrewAI/LangGraph, hosted model APIs, semantic vector memory and unrestricted execution are intentionally not activated. The 10 roles are not claimed to be 10 live model-backed agents.</p></div>
        </section>

        {agentRuns.length > 0 && <section className="panel"><div className="panel-head"><div><h3>Recent local draft runs</h3><p>Stored on this device only; not an authoritative cloud activity log.</p></div></div>{agentRuns.slice(0, 5).map(run => <div className="task" key={run.id}><span className="task-icon">✧</span><div><b>{run.businessName}</b><small>{new Date(run.createdAt).toLocaleString()} · {run.generationMode}</small></div><span className="status warn">Review required</span><button className="secondary" type="button" onClick={() => { setAgentOutput(run); setNotice('Loaded a saved local draft run.'); }}>View</button></div>)}</section>}
      </section>}

      {tab === 'Creative Intelligence' && <section className="training-lab">
        <section className="welcome">
          <div>
            <p className="eyebrow">PUBLIC TOOL INTELLIGENCE · ORIGINAL IMPLEMENTATION</p>
            <h2>Study the workflow. Build our own better.</h2>
            <p>Compare visible capabilities, record source evidence, design original experiments and keep quality gates in the loop.</p>
          </div>
          <div className="spark">↻</div>
        </section>
        <div className="notice"><b>Honest execution status</b><p>This dashboard version is browser-local and rule-based. It does not fetch the source URL, call an LLM, render media or connect to ComfyUI. The Python tool catalog, reverse-engineering ledger, creative planners and guarded ComfyUI runner are in the draft GitHub PR. Do not treat a hypothesis or hand-entered score as proof of quality or sales.</p></div>
        <section className="panel">
          <div className="panel-head">
            <div><h3>Creative tools worth studying</h3><p>Public product behaviour → our own implementation idea. Access, licenses, model versions and costs can change.</p></div>
            <button className="secondary" type="button" onClick={exportCreativeIntelligence}>Export local evidence ↓</button>
          </div>
          <div className="creative-tool-grid">{CREATIVE_TOOL_CARDS.map(tool => <article className="creative-tool-card" key={tool.name}>
            <div className="earning-lead-top"><h4>{tool.name}</h4></div><span className="status creative-access">{tool.access}</span>
            <p>{tool.purpose}</p>
            <p><b>AutoPilot idea:</b> {tool.autopilot}</p>
            <a href={tool.url} target="_blank" rel="noreferrer">Open public source ↗</a>
          </article>)}</div>
          <div className="notice"><b>Zero-budget routing principle</b><p>Prioritize local tools such as ComfyUI, Wan2.2, FFmpeg, Pillow, OpenCV, Whisper and VBench when the hardware and license fit. Hosted products can be comparison references, but never silently route a job to a paid endpoint.</p></div>
        </section>

        <section className="panel">
          <div className="panel-head"><div><h3>1. Public observation → original hypotheses</h3><p>Record only what you can see in public demos/docs. Unknown internals stay unknown.</p></div></div>
          <form className="training-form" onSubmit={analyzeCreativeObservation}>
            <label>Tool / product<input required value={creativeObservation.toolName} onChange={e => updateCreativeObservation('toolName', e.target.value)} placeholder="e.g. a photo-to-video ad tool" /></label>
            <label>Public source URL<input required type="url" value={creativeObservation.sourceUrl} onChange={e => updateCreativeObservation('sourceUrl', e.target.value)} placeholder="https://official-docs-or-public-demo..." /></label>
            <label>Observation date<input required type="date" value={creativeObservation.observedOn} onChange={e => updateCreativeObservation('observedOn', e.target.value)} /></label>
            <label className="training-wide">What did the public tool visibly do?<textarea rows="3" required value={creativeObservation.publicBehavior} onChange={e => updateCreativeObservation('publicBehavior', e.target.value)} placeholder="Describe visible features only: e.g. transitions between ordered keyframes, storyboard, editable text…" /></label>
            <label className="training-wide">Observed inputs → outputs<textarea rows="3" required value={creativeObservation.inputOutputObserved} onChange={e => updateCreativeObservation('inputOutputObserved', e.target.value)} placeholder="Input photo / brief / keyframes → visible result and constraints…" /></label>
            <label className="training-wide">Unknowns and limitations<textarea rows="2" required value={creativeObservation.unknowns} onChange={e => updateCreativeObservation('unknowns', e.target.value)} /></label>
            <button className="primary training-wide" type="submit">Derive original experiment ideas</button>
          </form>
          {creativeObservationRuns.length === 0 ? <div className="empty">No public observations recorded on this device yet.</div> :
            <div className="training-history">{creativeObservationRuns.map(run => <article className="training-run" key={run.id}>
              <div className="training-run-head"><div><b>{run.toolName}</b><small>{new Date(run.createdAt).toLocaleString()} · source date {run.observedOn}</small></div><span className="status warn">Review required</span></div>
              <p>{run.publicBehavior}</p>
              <a href={run.sourceUrl} target="_blank" rel="noreferrer">Open the public source ↗</a>
              <h4>Original hypotheses to test</h4>
              {run.hypotheses.map((idea, i) => <div className="agent-output-card" key={idea.title}><div><b>{i + 1}. {idea.title}</b><p><b>Our implementation:</b> {idea.proposal}</p><p><b>Test:</b> {idea.test}</p><small>{idea.basis}</small></div></div>)}
              <small>Source fetch: not performed · private code copied: false · access controls bypassed: false</small>
            </article>)}</div>}
        </section>

        <section className="panel">
          <div className="panel-head"><div><h3>2. Baseline vs candidate learning loop</h3><p>Use actual output files and the same brief; do not promote a candidate from placeholder scores.</p></div></div>
          <form className="training-form" onSubmit={recordCreativeExperimentCycle}>
            <label className="training-wide">Experiment name<input required value={creativeCycleForm.experimentName} onChange={e => updateCreativeCycleForm('experimentName', e.target.value)} /></label>
            <label>Baseline score (0–100)<input type="number" min="0" max="100" required value={creativeCycleForm.baselineScore} onChange={e => updateCreativeCycleForm('baselineScore', e.target.value)} /></label>
            <label>Candidate score (0–100)<input type="number" min="0" max="100" required value={creativeCycleForm.candidateScore} onChange={e => updateCreativeCycleForm('candidateScore', e.target.value)} /></label>
            <label className="training-wide">Actual outputs and reviewer evidence<textarea rows="3" required value={creativeCycleForm.evidence} onChange={e => updateCreativeCycleForm('evidence', e.target.value)} placeholder="Describe actual baseline/candidate files, same test brief, reviewer/evaluator and the measured quality differences. Do not enter secrets." /></label>
            <label className="creative-gate"><input type="checkbox" checked={creativeCycleForm.actualOutputsReviewed} onChange={e => updateCreativeCycleForm('actualOutputsReviewed', e.target.checked)} /> Actual baseline and candidate media files were reviewed</label>
            <label className="creative-gate"><input type="checkbox" checked={creativeCycleForm.assetRightsConfirmed} onChange={e => updateCreativeCycleForm('assetRightsConfirmed', e.target.checked)} /> Asset rights and subject consent confirmed</label>
            <label className="creative-gate"><input type="checkbox" checked={creativeCycleForm.commercialLicenseCleared} onChange={e => updateCreativeCycleForm('commercialLicenseCleared', e.target.checked)} /> Model, custom-node, font and music licenses checked for this use</label>
            <label className="creative-gate"><input type="checkbox" checked={creativeCycleForm.noUnsupportedClaims} onChange={e => updateCreativeCycleForm('noUnsupportedClaims', e.target.checked)} /> No unsupported claims, offers, testimonials or metrics</label>
            <label className="creative-gate"><input type="checkbox" checked={creativeCycleForm.noDirectImitation} onChange={e => updateCreativeCycleForm('noDirectImitation', e.target.checked)} /> Original execution; no direct copying of a protected ad, brand or character</label>
            <label className="creative-gate"><input type="checkbox" checked={creativeCycleForm.privacyReviewed} onChange={e => updateCreativeCycleForm('privacyReviewed', e.target.checked)} /> Client data and privacy reviewed</label>
            <button className="primary training-wide" type="submit">Record benchmark cycle</button>
          </form>
          {creativeCycles.length === 0 ? <div className="empty">No creative evaluation cycles recorded on this device yet.</div> :
            <div className="training-history">{creativeCycles.map(cycle => <article className="training-run" key={cycle.id}>
              <div className="training-run-head"><div><b>{cycle.experimentName}</b><small>{new Date(cycle.createdAt).toLocaleString()} · device-local evidence</small></div><span className={'status ' + (cycle.decision === 'PROMOTE_CANDIDATE_TO_HUMAN_REVIEW' ? 'good' : 'warn')}>{cycle.decision}</span></div>
              <div className="training-score-row"><div><small>Baseline</small><strong>{cycle.baselineScore}/100</strong></div><div><small>Candidate</small><strong>{cycle.candidateScore}/100</strong></div><div><small>Delta</small><strong>{cycle.delta > 0 ? '+' : ''}{cycle.delta}</strong></div><div><small>Measured outputs</small><strong>{cycle.metricsAreActual ? 'Yes' : 'No'}</strong></div></div>
              <p className="muted">{cycle.evidence}</p>
              <p className="training-blocked">No deployment, publishing, paid provider selection or model-weight update was performed.</p>
            </article>)}</div>}
          <div className="notice"><b>Promotion rule</b><p>The dashboard only marks an improved candidate as “eligible for human review” when actual media was reviewed, evidence was recorded, and every rights/license/factuality/originality/privacy gate is checked. This is a local user-entered record, not an independent model evaluation or server-backed audit ledger.</p></div>
        </section>

        <section className="panel">
          <div className="panel-head"><div><h3>3. Python agent pipeline + CI evidence</h3><p>The Python tools and CI samples are separate from the browser-local prototype above.</p></div></div>
          <div className="earning-actions">
            <a href="https://github.com/kumbipakam29-dev/autopilot-studio/pull/62" target="_blank" rel="noreferrer">Open draft implementation PR ↗</a>
            <a href="https://api.github.com/repos/kumbipakam29-dev/autopilot-studio/actions/artifacts/12788574385/zip" target="_blank" rel="noreferrer">Download creative evidence ZIP ↗</a>
          </div>
          <div className="notice"><b>What's inside the ZIP</b><p>Three client-specific campaign packs (salon, auto-parts, retail), 18-second shot plans, prompt sets, 11-agent handoff reports, source-linked tool registry, five public-tool hypothesis reports, learning ledger snapshot and hard-task test report. Packs are prompts/plans—not finished rendered Reels.</p></div>
        </section>
      </section>}

      {tab === 'Training Loop' && <section className="training-lab">
        <section className="panel">
          <p className="eyebrow">SUPERVISED EVALUATION · HUMAN GATE</p>
          <h2>Training Loop & Evidence</h2>
          <p className="muted">Record a before/after task review, the error category, regression result and approval decision. This dashboard tracks evidence; it does not train model weights or independently verify the scores.</p>
          <div className="notice"><b>Honest status</b><p>Numbers entered below are reviewer-provided. A higher candidate score is a recorded comparison, not proof that an AI model learned. Approval means “eligible for a separate manual release review” only.</p></div>
          <form className="training-form" onSubmit={recordTrainingCycle}>
            <label>Specialist<select value={trainingForm.agent} onChange={e => updateTrainingForm('agent', e.target.value)}>{['Architect / Orchestrator','Coder','Browser Agent','Researcher / Source Verifier','Writer / Content Strategist','Reviewer / Quality Evaluator','Analyst','Communicator','Executor','Memory'].map(x => <option key={x}>{x}</option>)}</select></label>
            <label>Task / benchmark<input required value={trainingForm.task} onChange={e => updateTrainingForm('task', e.target.value)} /></label>
            <label>Baseline score (0–100)<input type="number" min="0" max="100" required value={trainingForm.baselineScore} onChange={e => updateTrainingForm('baselineScore', e.target.value)} /></label>
            <label>Candidate score (0–100)<input type="number" min="0" max="100" required value={trainingForm.candidateScore} onChange={e => updateTrainingForm('candidateScore', e.target.value)} /></label>
            <label>Error category<select value={trainingForm.errorCategory} onChange={e => updateTrainingForm('errorCategory', e.target.value)}>{['None observed','Factual accuracy / evidence','Clarity / completeness','Formatting','Tool failure / timeout','Safety / permission','Regression','Other'].map(x => <option key={x}>{x}</option>)}</select></label>
            <label>Regression test<select value={trainingForm.regression} onChange={e => updateTrainingForm('regression', e.target.value)}><option value="pass">Pass</option><option value="fail">Fail — block approval</option><option value="not_run">Not run — review only</option></select></label>
            <label className="training-wide">Change summary<input value={trainingForm.changeSummary} onChange={e => updateTrainingForm('changeSummary', e.target.value)} placeholder="What changed between baseline and candidate?" /></label>
            <label className="training-wide">Evidence / reviewer notes<textarea rows="3" value={trainingForm.evidence} onChange={e => updateTrainingForm('evidence', e.target.value)} placeholder="Paste test result, example output, or reviewer notes. Do not enter secrets." /></label>
            <button className="primary training-wide" type="submit">Record evaluation cycle</button>
          </form>
        </section>
        <section className="panel">
          <div className="panel-head"><div><h3>Evaluation history</h3><p>Device-local records · newest first · maximum 30 cycles</p></div><button className="secondary" type="button" onClick={exportTrainingLog}>Export JSON ↓</button></div>
          <div className="training-import">
            <label htmlFor="training-evidence-file">Import a real Python learning-cycle JSON record</label>
            <input id="training-evidence-file" type="file" accept=".json,application/json" onChange={importTrainingEvidenceFile} />
            <small>Generate the file with <code>python -m agents.learning_cycle_cli --input cycle.json --output evidence.json</code>. The CLI runs the repository's Python evaluation logic. Scores still need independent evidence and reviewer input.</small>
          </div>
          {trainingRuns.length === 0 ? <div className="empty">No evaluation cycles recorded on this device yet. Add a real benchmark run above; example scores are not imported as real evidence.</div> :
            <div className="training-history">{trainingRuns.map(run => <article key={run.id} className="training-run">
              <div className="training-run-head"><div><b>{run.agent}</b><small>{new Date(run.createdAt).toLocaleString()} · {run.id}</small></div><span className={'status ' + (run.regression === 'fail' || run.status === 'rejected_or_blocked' ? 'warn' : 'good')}>{run.approvalStatus}</span></div>
              <p className="training-task">{run.task}</p>
              <div className="training-score-row"><div><small>Baseline</small><strong>{run.baselineScore}/100</strong></div><div><small>Candidate</small><strong>{run.candidateScore}/100</strong></div><div><small>Change</small><strong>{run.delta > 0 ? '+' : ''}{run.delta}</strong></div><div><small>Regression</small><strong>{run.regression}</strong></div></div>
              <p className="muted training-meta">Error: {run.errorCategory} · {run.scoreMethod}</p>
              {run.changeSummary && <p><b>Change:</b> {run.changeSummary}</p>}
              {run.evidence && <p><b>Evidence:</b> {run.evidence}</p>}
              {run.approvalStatus === 'Pending human review' && run.regression === 'pass' && run.delta >= 0 && <div className="training-actions"><button className="primary" type="button" onClick={() => decideTrainingCycle(run.id, 'approve')}>Approve for manual release review</button><button className="secondary" type="button" onClick={() => decideTrainingCycle(run.id, 'reject')}>Reject</button></div>}
              {run.regression === 'fail' && <p className="training-blocked">Blocked: regression failed; approval controls disabled.</p>}
              {run.regression === 'not_run' && <p className="training-blocked">Review only: run regression tests before any release decision.</p>}
              {run.approvedAt && <small>Decision recorded: {new Date(run.approvedAt).toLocaleString()}</small>}
            </article>)}</div>}
        </section>
        <section className="panel"><h3>What this dashboard does not claim</h3><ul className="training-limits"><li>No LLM fine-tuning or model-weight updates.</li><li>No autonomous code edits, deployment or production release.</li><li>No external evaluator is connected; scores are manually entered.</li><li>Records are stored in this browser/device, not synced to GitHub or a server.</li><li>For valid comparisons, use the same benchmark inputs and independently capture baseline/candidate outputs.</li></ul></section>
      </section>}
      {tab === 'Task Queue' && <section className="panel"><h3>Add a task</h3><p className="muted">Tasks are stored locally; they are not executed automatically.</p><form onSubmit={e => { e.preventDefault(); add(); }} className="task-form"><input value={task} onChange={e => setTask(e.target.value)} placeholder="Describe a task to track…" aria-label="Task description"/><button className="primary">Add task</button></form>{notes.map((n,i) => <div className="task" key={i}><span className="task-icon">☷</span><div><b>{n.text}</b><small>{n.time}</small></div><span className="status">{n.status}</span></div>)}</section>}

      {tab === 'Reports' && <section className="panel"><h3>Reports</h3><p className="muted">Reports will appear after a backend or data source is connected.</p><div className="empty">No sales or marketplace reports available yet.</div></section>}
      {tab === 'Settings' && <section className="panel"><h3>Settings</h3><p className="muted">Task notes, POD stages and the Earnings Hunter ledger are stored locally on this device. A scheduled GitHub Actions job scans public opportunity pages daily, but the app has no worker-account login, cloud database, AI image API, marketplace credentials or payment integration.</p><div className="notice"><b>Integration requirements</b><p>Use official platform APIs and secure server-side credential storage. Never place seller secrets inside the Android app or in public source code.</p></div><button className="secondary" onClick={() => exportConcepts()}>Export POD concept library</button></section>}
      <footer>AutoPilot Studio <span>Public leads only · manual work and payout verification</span></footer>
    </main>
  </div>;
}

createRoot(document.getElementById('root')).render(<App />);
