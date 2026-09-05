import { useCallback, useEffect, useMemo, useState } from 'react';
import { apiRequest } from '../api';
import type { SimulationSnapshot } from '../types';
import type { PlantGraph } from '../types/topology';
import { IncidentImpact } from './IncidentImpact';
import { AutomaticMonitoring, type Monitoring } from './AutomaticMonitoring';

type Finding = { domain: string; severity: string; confidence: number; summary: string; evidence: string[]; recommended_procedures: string[]; escalation_required: boolean };
type AcamisStatus = {
  automatic_monitoring?: Monitoring;
  incident_origin?: string | null;
  connection: string; operating_mode: string; plant_health: string; state_version: number;
  incident: null | { id: string; title: string; severity: string; summary: string; affected_equipment: string[]; verified: boolean; contained: boolean };
  specialist_findings: Finding[];
  recovery_plan: { status: string; priority_order: string[]; recommended_procedures: string[]; procedure_statuses: Record<string, string>; rationale: string };
  audit: { id: string; at: string; event: string; detail: string; severity: string }[];
  model_gateway: { configured: boolean; connected: boolean; provider: string | null; model: string | null; base_url: string | null; transport?: string; available_models?: string[]; message: string };
  model_advisory: null | { reply: string; provider: string; model: string; advisory_only: boolean; trigger: string };
  context_manifest: { ruleset: string; snapshot_contract: string; domains: string[]; approved_procedures_only: boolean };
};

const scenarios = [
  ['cooling_water_degradation', 'Cooling water'], ['furnace_instability', 'Furnace stability'],
  ['rolling_mill_slowdown', 'Rolling mill'], ['substation_capacity_constraint', 'Electrical capacity'],
  ['raw_material_disruption', 'Raw material'],
] as const;

const geminiModels = [
  { id: 'gemini-3.8-flash', label: 'Gemini 3.8 Flash — recommended orchestrator' },
  { id: 'gemini-3.7-flash', label: 'Gemini 3.7 Flash — balanced fallback' },
  { id: 'gemini-3.6-flash', label: 'Gemini 3.6 Flash — compatible fallback' },
  { id: 'gemini-3.5-flash', label: 'Gemini 3.5 Flash — routine analysis' },
  { id: 'gemini-3.5-flash-lite', label: 'Gemini 3.5 Flash-Lite — high-volume subagents' },
] as const;

const severityClass = (severity: string) => severity === 'HIGH' || severity === 'CRITICAL'
  ? 'border-red-700/70 bg-red-950/30 text-red-300' : severity === 'WARNING'
    ? 'border-amber-700/70 bg-amber-950/25 text-amber-300' : 'border-emerald-700/70 bg-emerald-950/25 text-emerald-300';

export function AcamisConsole({ simulationId, snapshot, onOpenSimulation, graph, onLocate }: { simulationId: string | null; snapshot: SimulationSnapshot | null; onOpenSimulation: () => void; graph: PlantGraph | null; onLocate: (view: 'BUILDER' | 'SIMULATION', nodeId: string) => void }) {
  const [data, setData] = useState<AcamisStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [provider, setProvider] = useState('GEMINI');
  const [modelName, setModelName] = useState('gemini-3.8-flash');
  const [baseUrl, setBaseUrl] = useState('');
  const [providerKey, setProviderKey] = useState('');
  const [chatMessage, setChatMessage] = useState('Assess the current incident and explain the safest next step.');
  const [chatReply, setChatReply] = useState<string | null>(null);
  const [modelNotice, setModelNotice] = useState<string | null>(null);
  const [dismissedApprovalPromptKey, setDismissedApprovalPromptKey] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!simulationId) return;
    try { setData(await apiRequest<AcamisStatus>(`/api/simulations/${simulationId}/acamis/status`)); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'ACAMIS is unavailable.'); }
  }, [simulationId]);
  useEffect(() => {
    const initial = window.setTimeout(() => void refresh(), 0);
    const timer = window.setInterval(() => void refresh(), 1200);
    return () => { window.clearTimeout(initial); window.clearInterval(timer); };
  }, [refresh]);

  const invoke = async (path: string, body?: unknown) => {
    if (!simulationId || busy) return;
    setBusy(true);
    try {
      const result = await apiRequest<AcamisStatus>(`/api/simulations/${simulationId}/acamis/${path}`, body === undefined ? { method: 'POST' } : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      setData(result); setError(null);
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'ACAMIS action failed.'); }
    finally { setBusy(false); }
  };
  const connectModel = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!simulationId || busy) return;
    setBusy(true);
    try {
      const result = await apiRequest<AcamisStatus['model_gateway']>(`/api/simulations/${simulationId}/acamis/model/connect`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ provider, model: modelName, api_key: providerKey, base_url: baseUrl || null }) });
      if (result.model) setModelName(result.model);
      setProviderKey('');
      setModelNotice(result.message);
      setError(null);
      await refresh();
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Model connection failed.';
      setModelNotice(message); setError(message);
    }
    finally { setBusy(false); }
  };
  const askModel = async () => {
    if (!simulationId || busy) return;
    setBusy(true);
    try {
      const result = await apiRequest<{ reply: string }>(`/api/simulations/${simulationId}/acamis/model/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: chatMessage }) });
      setChatReply(result.reply); setError(null); await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Model review failed.'); }
    finally { setBusy(false); }
  };
  const health = data?.plant_health ?? 'STANDBY';
  const incident = data?.incident;
  const procedures = data?.recovery_plan.recommended_procedures ?? [];
  const approvalProcedure = procedures.find(procedure => data?.recovery_plan.procedure_statuses?.[procedure] === 'AWAITING_HUMAN_APPROVAL') ?? null;
  const approvalPromptKey = data?.audit.find(item => item.event === 'SCENARIO_INJECTED')?.id ?? null;
  const selectableGeminiModels = useMemo(() => {
    const known = new Set(geminiModels.map(option => option.id));
    return [
      ...geminiModels,
      ...(data?.model_gateway.available_models ?? [])
        .filter(model => model.startsWith('gemini-') && !/(image|tts|live|omni)/.test(model))
        .filter(model => !known.has(model as typeof geminiModels[number]['id']))
        .map(model => ({ id: model, label: `${model} — provider available` })),
    ];
  }, [data?.model_gateway.available_models]);
  const statusText = useMemo(() => data?.connection === 'LIVE' ? 'Live SteelSim digital twin' : 'Awaiting active simulation', [data]);

  if (!simulationId) return <main className="h-full overflow-y-auto p-6 lg:p-8"><section className="mx-auto mt-16 max-w-xl rounded-xl border border-dashed border-industrial-600 bg-industrial-800/70 p-10 text-center"><div className="font-mono text-[10px] font-bold uppercase tracking-[0.24em] text-cyan-400">ACAMIS / Task 3</div><h1 className="mt-3 text-2xl font-bold text-white">Operational Intelligence is standing by</h1><p className="mt-3 text-sm leading-6 text-gray-400">Start a SteelSim simulation first. ACAMIS connects to the backend-authoritative digital twin; it never scrapes the interface.</p><button onClick={onOpenSimulation} className="mt-6 rounded border border-cyan-700 bg-cyan-950/40 px-4 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-900/60">Open Simulation Control</button></section></main>;

  return <main className="h-full overflow-y-auto p-5 lg:p-7" aria-label="ACAMIS operational intelligence">
    <div className="mx-auto max-w-7xl">
      <header className="flex flex-col gap-4 border-b border-industrial-700 pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div><div className="font-mono text-[10px] font-bold uppercase tracking-[0.24em] text-cyan-400">ACAMIS / SteelSim Digital Twin</div><h1 className="mt-1 text-2xl font-bold text-white">Autonomous Operations Center</h1><p className="mt-1 text-sm text-gray-500">{statusText} · deterministic policy-gated intelligence · simulation only</p></div>
        <div className="flex flex-wrap gap-2"><span className={`rounded border px-3 py-2 font-mono text-[10px] font-bold tracking-wider ${severityClass(health === 'INCIDENT' ? 'HIGH' : health === 'STABILIZED' ? 'WARNING' : 'INFO')}`}>{health}</span><select value={data?.operating_mode ?? 'OBSERVE'} disabled={busy} onChange={event => void invoke('autonomy', { mode: event.target.value })} className="rounded border border-industrial-600 bg-industrial-800 px-3 py-2 font-mono text-[10px] font-bold text-gray-200"><option value="OBSERVE">OBSERVE</option><option value="ADVISORY">ADVISORY</option><option value="AUTONOMOUS_SIMULATION">AUTONOMOUS SIMULATION</option></select></div>
      </header>
      <div role="status" className="mt-4 rounded border border-industrial-600 p-3 text-xs text-gray-300">Simulation: {snapshot?.status ?? 'CONNECTING'} · tick {snapshot?.tick ?? 0}. {snapshot?.status === 'RUNNING' ? 'Running — scenario effects update live below.' : 'Use Run / Resume in the top bar before injecting an anomaly.'}{busy && ' Processing request; provider review may take a few seconds.'}</div>
      <IncidentImpact snapshot={snapshot} graph={graph} onLocate={onLocate} />
      <AutomaticMonitoring monitor={data?.automatic_monitoring} busy={busy} hasIncident={!!data?.incident} onDemo={() => void invoke('monitoring/demo')} onClear={() => void invoke('scenarios/reset')} onLocate={onLocate} />
      {data?.incident_origin && <p className="mt-3 text-xs font-bold text-cyan-200">Incident source: {data.incident_origin}</p>}
      {data?.incident && data.recovery_plan.status === 'HUMAN_VERIFICATION_REQUIRED' && approvalProcedure && approvalPromptKey !== dismissedApprovalPromptKey && <div className="fixed inset-0 z-50 flex items-center justify-center bg-industrial-950/70 p-4" role="alertdialog" aria-modal="true" aria-label="Human intervention required"><section className="w-full max-w-md rounded-xl border border-red-600 bg-industrial-900 p-5 shadow-2xl shadow-red-950/50"><div className="flex items-start gap-3"><div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-red-500 bg-red-950/70 font-mono text-lg font-bold text-red-300">!</div><div><div className="font-mono text-[10px] font-bold uppercase tracking-[0.18em] text-red-300">Human intervention required</div><h2 className="mt-1 text-lg font-bold text-white">{data.incident.title}</h2></div></div><p className="mt-4 text-sm leading-6 text-gray-300">{data.incident.contained ? 'ACAMIS has applied simulated containment.' : 'This incident has not yet been contained.'} Final recovery requires an operator decision. In Observe mode, change to Advisory or Autonomous Simulation from the plan before applying a procedure.</p><div className="mt-4 rounded border border-industrial-700 bg-industrial-950/70 p-3 text-xs text-gray-300"><div><span className="text-gray-500">Affected assets:</span> {data.incident.affected_equipment.length}</div><div className="mt-1"><span className="text-gray-500">Proposed action:</span> {approvalProcedure.replaceAll('_', ' ')}</div></div><div className="mt-5 flex flex-wrap justify-end gap-2"><button type="button" onClick={() => { setDismissedApprovalPromptKey(approvalPromptKey); document.getElementById('central-recovery-plan')?.scrollIntoView({ behavior: 'smooth', block: 'center' }); }} className="rounded border border-industrial-600 px-3 py-2 text-[10px] font-bold text-gray-300">Review plan</button><button type="button" disabled={busy || data.operating_mode === 'OBSERVE'} onClick={() => void invoke(`procedures/${approvalProcedure}`, { human_verified: true })} className="rounded border border-amber-500 bg-amber-950/60 px-3 py-2 text-[10px] font-bold text-amber-100 disabled:opacity-30">Apply human intervention</button></div></section></div>}
      {error && <div role="alert" className="mt-4 rounded border border-red-700 bg-red-950/50 px-4 py-3 text-xs text-red-200">{error}</div>}
      <section className="mt-5 grid gap-3 md:grid-cols-4"><Kpi label="Plant health" value={health} accent={health === 'INCIDENT' ? 'text-red-300' : health === 'STABILIZED' ? 'text-amber-300' : 'text-emerald-300'} /><Kpi label="Connection" value={data?.connection ?? 'CONNECTING'} accent="text-cyan-300" /><Kpi label="State version" value={data?.state_version ?? '—'} /><Kpi label="Autonomy" value={(data?.operating_mode ?? 'OBSERVE').replaceAll('_', ' ')} accent="text-blue-300" /></section>
      <section className={`mt-5 rounded-lg border p-5 ${incident ? severityClass(incident.contained ? 'WARNING' : incident.severity) : 'border-industrial-700 bg-industrial-800/70'}`}><div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"><div><div className="font-mono text-[10px] font-bold uppercase tracking-[0.18em]">{incident?.contained ? 'Incident contained · approval pending' : incident ? 'Verified operating incident' : 'Situation assessment'}</div><h2 className="mt-1 text-lg font-bold text-white">{incident?.title ?? (data?.recovery_plan.status === 'RECOVERED' ? 'Simulated recovery complete' : 'Plant baseline is being monitored')}</h2><p className="mt-1 text-sm text-gray-300">{incident?.contained ? 'ACAMIS has applied a safe stabilization procedure. Final high-risk repair awaits human verification.' : incident?.summary ?? (data?.recovery_plan.status === 'RECOVERED' ? 'The incident was rectified and telemetry has returned to its normal operating envelope.' : 'No active ACAMIS scenario is present. Inject a deterministic scenario to exercise the recovery workflow.')}</p></div>{incident && <span className="font-mono text-xs font-bold">{incident.affected_equipment.length} affected assets</span>}</div></section>
      <section className="mt-5 rounded-lg border border-industrial-700 bg-industrial-800/70 p-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-sm font-bold text-white">Scenario Control</h2><p className="mt-1 text-xs text-gray-500">Deterministic incidents alter SteelSim telemetry and are fully resettable.</p></div><div className="flex flex-wrap gap-2">{scenarios.map(([id, label]) => <button key={id} aria-pressed={incident?.id === id} disabled={busy || snapshot?.status !== 'RUNNING'} onClick={() => void invoke(`scenarios/${id}`)} className="rounded border border-industrial-600 bg-industrial-900 px-3 py-2 text-[11px] font-semibold text-gray-300 hover:border-amber-500 hover:text-amber-200 disabled:opacity-40">{label}{incident?.id === id ? ' · Active' : ''}</button>)}<button disabled={busy} onClick={() => void invoke('scenarios/reset')} className="rounded border border-blue-700 bg-blue-950/40 px-3 py-2 text-[11px] font-bold text-blue-200 hover:bg-blue-900/60 disabled:opacity-40">Clear scenario</button></div></div></section>
      <section className="mt-5 rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="flex flex-col gap-2 border-b border-industrial-700 px-4 py-3 lg:flex-row lg:items-center lg:justify-between"><div><h2 className="text-sm font-bold text-white">Advisory Model Gateway</h2><p className="mt-1 text-xs text-gray-500">Optional BYOK reasoning layer. Credentials remain in backend memory only; ACAMIS policy gates retain control.</p></div><div className="text-left lg:text-right"><div className={`rounded border px-2 py-1 font-mono text-[9px] font-bold ${data?.model_gateway.connected ? severityClass('INFO') : 'border-amber-800 bg-amber-950/20 text-amber-300'}`}>API STATUS · {data?.model_gateway.connected ? `VERIFIED · ${data.model_gateway.model}` : 'NOT CONNECTED'}</div><p className="mt-1 text-[10px] text-gray-500">{data?.model_gateway.connected ? `${data.model_gateway.transport ?? 'MODEL API'} · transient session` : 'API key required · deterministic core remains active'}</p></div></div>
        <div className="grid items-start gap-4 p-4 xl:grid-cols-2"><form onSubmit={connectModel} className="grid gap-3 self-start sm:grid-cols-2"><label className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Provider<select value={provider} onChange={event => { setProvider(event.target.value); if (event.target.value === 'GEMINI') { setModelName('gemini-3.8-flash'); setBaseUrl(''); } }} className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200"><option value="GEMINI">Google Gemini</option><option value="OPENAI_COMPATIBLE">OpenAI-compatible</option></select></label><label className="text-[10px] font-bold uppercase tracking-wider text-gray-500">ACAMIS model{provider === 'GEMINI' ? <select value={modelName} onChange={event => setModelName(event.target.value)} className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200">{selectableGeminiModels.map(option => <option key={option.id} value={option.id}>{option.label}</option>)}</select> : <input value={modelName} onChange={event => setModelName(event.target.value)} placeholder="Provider model ID" className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200" />}</label>{provider === 'OPENAI_COMPATIBLE' && <label className="text-[10px] font-bold uppercase tracking-wider text-gray-500 sm:col-span-2">Base URL<input value={baseUrl} onChange={event => setBaseUrl(event.target.value)} placeholder="https://provider.example/v1" className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200" /></label>}<label className="text-[10px] font-bold uppercase tracking-wider text-gray-500 sm:col-span-2">Transient API key<input type="password" autoComplete="off" value={providerKey} onChange={event => setProviderKey(event.target.value)} placeholder="Not saved to files or returned by the API" className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200" /></label><div className="flex flex-wrap gap-2 sm:col-span-2"><button disabled={busy || !providerKey || !modelName} className="rounded border border-cyan-700 bg-cyan-950/40 px-3 py-2 text-[10px] font-bold text-cyan-200 disabled:opacity-30">Test & connect</button>{data?.model_gateway.connected && <button type="button" disabled={busy} onClick={() => void invoke('model/disconnect')} className="rounded border border-industrial-600 px-3 py-2 text-[10px] font-bold text-gray-300">Disconnect</button>}</div>{(modelNotice || data?.model_gateway.message) && <p className={`text-[10px] leading-4 sm:col-span-2 ${data?.model_gateway.connected ? 'text-emerald-300' : modelNotice ? 'text-red-300' : 'text-gray-500'}`}>{modelNotice || data?.model_gateway.message}</p>}</form>
          <div className="self-start rounded border border-industrial-700 bg-industrial-900/60 p-3"><div className="font-mono text-[10px] font-bold text-cyan-300">OPERATOR CHANNEL · ADVISORY ONLY</div>{data?.model_advisory && <details className="mt-2 rounded border border-cyan-900/70 bg-cyan-950/20 p-2 text-[10px] leading-4 text-cyan-100"><summary className="cursor-pointer font-bold">LATEST AUTONOMOUS REVIEW · EXPAND</summary><div className="mt-2 max-h-48 overflow-y-auto whitespace-pre-wrap text-gray-300">{data.model_advisory.reply}</div></details>}<textarea value={chatMessage} onChange={event => setChatMessage(event.target.value)} rows={3} className="mt-2 w-full resize-none rounded border border-industrial-600 bg-industrial-950 p-2 text-xs text-gray-200" /><button disabled={busy || !data?.model_gateway.connected || !chatMessage.trim()} onClick={() => void askModel()} className="mt-2 rounded border border-blue-700 bg-blue-950/40 px-3 py-2 text-[10px] font-bold text-blue-200 disabled:opacity-30">Request model review</button>{chatReply && <div className="mt-3 max-h-32 overflow-y-auto whitespace-pre-wrap border-l-2 border-cyan-700 pl-3 text-xs leading-5 text-gray-300">{chatReply}</div>}</div></div>
      </section>
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.4fr_0.9fr]"><section className="rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="border-b border-industrial-700 px-4 py-3"><h2 className="text-sm font-bold text-white">Specialist Intelligence</h2><p className="mt-1 text-xs text-gray-500">Six domains independently assess the same versioned operational snapshot.</p></div><div className="grid gap-px bg-industrial-700 sm:grid-cols-2 xl:grid-cols-3">{(data?.specialist_findings ?? []).map(finding => <article key={finding.domain} className="bg-industrial-800 p-4"><div className="flex items-center justify-between gap-2"><h3 className="text-xs font-bold text-white">{finding.domain}</h3><span className={`rounded border px-1.5 py-0.5 font-mono text-[9px] font-bold ${severityClass(finding.severity)}`}>{finding.severity}</span></div><p className="mt-3 min-h-12 text-xs leading-5 text-gray-400">{finding.summary}</p><div className="mt-3 font-mono text-[10px] text-cyan-300">Confidence {Math.round(finding.confidence * 100)}%</div></article>)}</div></section>
      <section id="central-recovery-plan" className="rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="border-b border-industrial-700 px-4 py-3"><h2 className="text-sm font-bold text-white">Central Recovery Plan</h2><p className="mt-1 font-mono text-[10px] text-gray-500">{data?.recovery_plan.status ?? 'MONITORING'}</p></div><div className="p-4"><p className="text-xs leading-5 text-gray-400">{data?.recovery_plan.rationale}</p><ol className="mt-4 space-y-2">{procedures.length ? procedures.map((procedure, index) => { const stepStatus = data?.recovery_plan.procedure_statuses?.[procedure] ?? 'AVAILABLE'; const needsApproval = stepStatus === 'AWAITING_HUMAN_APPROVAL'; return <li key={procedure} className="flex items-center justify-between gap-3 rounded border border-industrial-700 bg-industrial-900/70 p-3"><div><span className="text-xs text-gray-200"><b className="mr-2 font-mono text-cyan-400">{index + 1}</b>{procedure.replaceAll('_', ' ')}</span><div className={`mt-1 font-mono text-[9px] ${stepStatus === 'APPLIED' ? 'text-emerald-400' : needsApproval ? 'text-amber-300' : 'text-gray-500'}`}>{stepStatus.replaceAll('_', ' ')}</div></div><button disabled={busy || data?.operating_mode === 'OBSERVE' || stepStatus === 'APPLIED'} onClick={() => void invoke(`procedures/${procedure}`, needsApproval ? { human_verified: true } : undefined)} className={`rounded border px-2 py-1 text-[10px] font-bold disabled:opacity-30 ${needsApproval ? 'border-amber-600 bg-amber-950/40 text-amber-200' : 'border-emerald-700 bg-emerald-950/40 text-emerald-200'}`}>{stepStatus === 'APPLIED' ? 'Applied' : needsApproval ? 'Approve & apply' : 'Apply'}</button></li>; }) : <li className="rounded border border-industrial-700 bg-industrial-900/50 p-3 text-xs text-gray-500">No recovery procedure is required.</li>}</ol></div></section></div>
      <section className="mt-5 rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="border-b border-industrial-700 px-4 py-3"><h2 className="text-sm font-bold text-white">Audit Timeline</h2><p className="mt-1 text-xs text-gray-500">Traceability for scenarios, autonomy changes, and approved simulated procedures.</p></div><div className="divide-y divide-industrial-700/70">{(data?.audit ?? []).length ? data!.audit.map(item => <div key={item.id} className="flex gap-4 px-4 py-3 text-xs"><span className={`mt-1 h-2 w-2 rounded-full ${item.severity === 'HIGH' ? 'bg-red-400' : 'bg-cyan-400'}`} /><div><div className="font-mono text-[10px] text-cyan-300">{item.event}</div><div className="mt-1 text-gray-300">{item.detail}</div></div></div>) : <div className="px-4 py-8 text-center text-sm text-gray-500">ACAMIS audit events appear after a scenario or operating-mode change.</div>}</div></section>
    </div>
  </main>;
}

function Kpi({ label, value, accent = 'text-white' }: { label: string; value: string | number; accent?: string }) { return <div className="rounded-lg border border-industrial-700 bg-industrial-800/80 p-4"><div className="text-[10px] font-bold uppercase tracking-[0.18em] text-gray-500">{label}</div><div className={`mt-2 truncate font-mono text-lg font-bold ${accent}`}>{value}</div></div>; }
