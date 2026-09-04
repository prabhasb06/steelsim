import { useCallback, useEffect, useMemo, useState } from 'react';
import { apiRequest } from '../api';
import type { SimulationSnapshot } from '../types';

type Finding = { domain: string; severity: string; confidence: number; summary: string; evidence: string[]; recommended_procedures: string[]; escalation_required: boolean };
type AcamisStatus = {
  connection: string; operating_mode: string; plant_health: string; state_version: number;
  incident: null | { id: string; title: string; severity: string; summary: string; affected_equipment: string[]; verified: boolean };
  specialist_findings: Finding[];
  recovery_plan: { status: string; priority_order: string[]; recommended_procedures: string[]; rationale: string };
  audit: { id: string; at: string; event: string; detail: string; severity: string }[];
  model_gateway: { configured: boolean; connected: boolean; provider: string | null; model: string | null; base_url: string | null; message: string };
  context_manifest: { ruleset: string; snapshot_contract: string; domains: string[]; approved_procedures_only: boolean };
};

const scenarios = [
  ['cooling_water_degradation', 'Cooling water'], ['furnace_instability', 'Furnace stability'],
  ['rolling_mill_slowdown', 'Rolling mill'], ['substation_capacity_constraint', 'Electrical capacity'],
  ['raw_material_disruption', 'Raw material'],
] as const;

const severityClass = (severity: string) => severity === 'HIGH' || severity === 'CRITICAL'
  ? 'border-red-700/70 bg-red-950/30 text-red-300' : severity === 'WARNING'
    ? 'border-amber-700/70 bg-amber-950/25 text-amber-300' : 'border-emerald-700/70 bg-emerald-950/25 text-emerald-300';

export function AcamisConsole({ simulationId, snapshot, onOpenSimulation }: { simulationId: string | null; snapshot: SimulationSnapshot | null; onOpenSimulation: () => void }) {
  const [data, setData] = useState<AcamisStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [provider, setProvider] = useState('GEMINI');
  const [modelName, setModelName] = useState('gemini-2.5-flash');
  const [baseUrl, setBaseUrl] = useState('');
  const [providerKey, setProviderKey] = useState('');
  const [chatMessage, setChatMessage] = useState('Assess the current incident and explain the safest next step.');
  const [chatReply, setChatReply] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!simulationId) return;
    try { setData(await apiRequest<AcamisStatus>(`/api/simulations/${simulationId}/acamis/status`)); setError(null); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'ACAMIS is unavailable.'); }
  }, [simulationId]);
  useEffect(() => {
    const initial = window.setTimeout(() => void refresh(), 0);
    const timer = window.setInterval(() => void refresh(), 1200);
    return () => { window.clearTimeout(initial); window.clearInterval(timer); };
  }, [refresh, snapshot?.state_version]);

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
      await apiRequest(`/api/simulations/${simulationId}/acamis/model/connect`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ provider, model: modelName, api_key: providerKey, base_url: baseUrl || null }) });
      setProviderKey('');
      await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Model connection failed.'); }
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
  const statusText = useMemo(() => data?.connection === 'LIVE' ? 'Live SteelSim digital twin' : 'Awaiting active simulation', [data]);

  if (!simulationId) return <main className="h-full overflow-y-auto p-6 lg:p-8"><section className="mx-auto mt-16 max-w-xl rounded-xl border border-dashed border-industrial-600 bg-industrial-800/70 p-10 text-center"><div className="font-mono text-[10px] font-bold uppercase tracking-[0.24em] text-cyan-400">ACAMIS / Task 3</div><h1 className="mt-3 text-2xl font-bold text-white">Operational Intelligence is standing by</h1><p className="mt-3 text-sm leading-6 text-gray-400">Start a SteelSim simulation first. ACAMIS connects to the backend-authoritative digital twin; it never scrapes the interface.</p><button onClick={onOpenSimulation} className="mt-6 rounded border border-cyan-700 bg-cyan-950/40 px-4 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-900/60">Open Simulation Control</button></section></main>;

  return <main className="h-full overflow-y-auto p-5 lg:p-7" aria-label="ACAMIS operational intelligence">
    <div className="mx-auto max-w-7xl">
      <header className="flex flex-col gap-4 border-b border-industrial-700 pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div><div className="font-mono text-[10px] font-bold uppercase tracking-[0.24em] text-cyan-400">ACAMIS / SteelSim Digital Twin</div><h1 className="mt-1 text-2xl font-bold text-white">Autonomous Operations Center</h1><p className="mt-1 text-sm text-gray-500">{statusText} · deterministic policy-gated intelligence · simulation only</p></div>
        <div className="flex flex-wrap gap-2"><span className={`rounded border px-3 py-2 font-mono text-[10px] font-bold tracking-wider ${severityClass(health === 'INCIDENT' ? 'HIGH' : 'INFO')}`}>{health}</span><select value={data?.operating_mode ?? 'OBSERVE'} disabled={busy} onChange={event => void invoke('autonomy', { mode: event.target.value })} className="rounded border border-industrial-600 bg-industrial-800 px-3 py-2 font-mono text-[10px] font-bold text-gray-200"><option value="OBSERVE">OBSERVE</option><option value="ADVISORY">ADVISORY</option><option value="AUTONOMOUS_SIMULATION">AUTONOMOUS SIMULATION</option></select></div>
      </header>
      {error && <div role="alert" className="mt-4 rounded border border-red-700 bg-red-950/50 px-4 py-3 text-xs text-red-200">{error}</div>}
      <section className="mt-5 grid gap-3 md:grid-cols-4"><Kpi label="Plant health" value={health} accent={health === 'INCIDENT' ? 'text-red-300' : 'text-emerald-300'} /><Kpi label="Connection" value={data?.connection ?? 'CONNECTING'} accent="text-cyan-300" /><Kpi label="State version" value={data?.state_version ?? '—'} /><Kpi label="Autonomy" value={(data?.operating_mode ?? 'OBSERVE').replaceAll('_', ' ')} accent="text-blue-300" /></section>
      <section className={`mt-5 rounded-lg border p-5 ${incident ? severityClass(incident.severity) : 'border-industrial-700 bg-industrial-800/70'}`}><div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"><div><div className="font-mono text-[10px] font-bold uppercase tracking-[0.18em]">{incident ? 'Verified operating incident' : 'Situation assessment'}</div><h2 className="mt-1 text-lg font-bold text-white">{incident?.title ?? 'Plant baseline is being monitored'}</h2><p className="mt-1 text-sm text-gray-300">{incident?.summary ?? 'No active ACAMIS scenario is present. Inject a deterministic scenario to exercise the recovery workflow.'}</p></div>{incident && <span className="font-mono text-xs font-bold">{incident.affected_equipment.length} affected assets</span>}</div></section>
      <section className="mt-5 rounded-lg border border-industrial-700 bg-industrial-800/70 p-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-sm font-bold text-white">Scenario Control</h2><p className="mt-1 text-xs text-gray-500">Deterministic incidents alter SteelSim telemetry and are fully resettable.</p></div><div className="flex flex-wrap gap-2">{scenarios.map(([id, label]) => <button key={id} disabled={busy} onClick={() => void invoke(`scenarios/${id}`)} className="rounded border border-industrial-600 bg-industrial-900 px-3 py-2 text-[11px] font-semibold text-gray-300 hover:border-amber-500 hover:text-amber-200 disabled:opacity-40">{label}</button>)}<button disabled={busy} onClick={() => void invoke('scenarios/reset')} className="rounded border border-blue-700 bg-blue-950/40 px-3 py-2 text-[11px] font-bold text-blue-200 hover:bg-blue-900/60 disabled:opacity-40">Clear scenario</button></div></div></section>
      <section className="mt-5 rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="flex flex-col gap-2 border-b border-industrial-700 px-4 py-3 lg:flex-row lg:items-center lg:justify-between"><div><h2 className="text-sm font-bold text-white">Advisory Model Gateway</h2><p className="mt-1 text-xs text-gray-500">Optional BYOK reasoning layer. Credentials remain in backend memory only; ACAMIS policy gates retain control.</p></div><span className={`rounded border px-2 py-1 font-mono text-[9px] font-bold ${data?.model_gateway.connected ? severityClass('INFO') : 'border-industrial-600 text-gray-500'}`}>{data?.model_gateway.connected ? `VERIFIED · ${data.model_gateway.model}` : 'DETERMINISTIC CORE ACTIVE'}</span></div>
        <div className="grid gap-4 p-4 xl:grid-cols-2"><form onSubmit={connectModel} className="grid gap-3 sm:grid-cols-2"><label className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Provider<select value={provider} onChange={event => { setProvider(event.target.value); if (event.target.value === 'GEMINI') { setModelName('gemini-2.5-flash'); setBaseUrl(''); } }} className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200"><option value="GEMINI">Google Gemini</option><option value="OPENAI_COMPATIBLE">OpenAI-compatible</option></select></label><label className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Model<input value={modelName} onChange={event => setModelName(event.target.value)} className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200" /></label>{provider === 'OPENAI_COMPATIBLE' && <label className="text-[10px] font-bold uppercase tracking-wider text-gray-500 sm:col-span-2">Base URL<input value={baseUrl} onChange={event => setBaseUrl(event.target.value)} placeholder="https://provider.example/v1" className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200" /></label>}<label className="text-[10px] font-bold uppercase tracking-wider text-gray-500 sm:col-span-2">Transient API key<input type="password" autoComplete="off" value={providerKey} onChange={event => setProviderKey(event.target.value)} placeholder="Not saved to files or returned by the API" className="mt-1 w-full rounded border border-industrial-600 bg-industrial-900 p-2 text-xs normal-case text-gray-200" /></label><div className="flex gap-2 sm:col-span-2"><button disabled={busy || !providerKey || !modelName} className="rounded border border-cyan-700 bg-cyan-950/40 px-3 py-2 text-[10px] font-bold text-cyan-200 disabled:opacity-30">Test & connect</button>{data?.model_gateway.connected && <button type="button" disabled={busy} onClick={() => void invoke('model/disconnect')} className="rounded border border-industrial-600 px-3 py-2 text-[10px] font-bold text-gray-300">Disconnect</button>}</div></form>
          <div className="rounded border border-industrial-700 bg-industrial-900/60 p-3"><div className="font-mono text-[10px] font-bold text-cyan-300">OPERATOR CHANNEL · ADVISORY ONLY</div><textarea value={chatMessage} onChange={event => setChatMessage(event.target.value)} rows={3} className="mt-2 w-full resize-none rounded border border-industrial-600 bg-industrial-950 p-2 text-xs text-gray-200" /><button disabled={busy || !data?.model_gateway.connected || !chatMessage.trim()} onClick={() => void askModel()} className="mt-2 rounded border border-blue-700 bg-blue-950/40 px-3 py-2 text-[10px] font-bold text-blue-200 disabled:opacity-30">Request model review</button>{chatReply && <div className="mt-3 max-h-36 overflow-y-auto whitespace-pre-wrap border-l-2 border-cyan-700 pl-3 text-xs leading-5 text-gray-300">{chatReply}</div>}</div></div>
      </section>
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.4fr_0.9fr]"><section className="rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="border-b border-industrial-700 px-4 py-3"><h2 className="text-sm font-bold text-white">Specialist Intelligence</h2><p className="mt-1 text-xs text-gray-500">Six domains independently assess the same versioned operational snapshot.</p></div><div className="grid gap-px bg-industrial-700 sm:grid-cols-2 xl:grid-cols-3">{(data?.specialist_findings ?? []).map(finding => <article key={finding.domain} className="bg-industrial-800 p-4"><div className="flex items-center justify-between gap-2"><h3 className="text-xs font-bold text-white">{finding.domain}</h3><span className={`rounded border px-1.5 py-0.5 font-mono text-[9px] font-bold ${severityClass(finding.severity)}`}>{finding.severity}</span></div><p className="mt-3 min-h-12 text-xs leading-5 text-gray-400">{finding.summary}</p><div className="mt-3 font-mono text-[10px] text-cyan-300">Confidence {Math.round(finding.confidence * 100)}%</div></article>)}</div></section>
      <section className="rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="border-b border-industrial-700 px-4 py-3"><h2 className="text-sm font-bold text-white">Central Recovery Plan</h2><p className="mt-1 font-mono text-[10px] text-gray-500">{data?.recovery_plan.status ?? 'MONITORING'}</p></div><div className="p-4"><p className="text-xs leading-5 text-gray-400">{data?.recovery_plan.rationale}</p><ol className="mt-4 space-y-2">{procedures.length ? procedures.map((procedure, index) => <li key={procedure} className="flex items-center justify-between gap-3 rounded border border-industrial-700 bg-industrial-900/70 p-3"><span className="text-xs text-gray-200"><b className="mr-2 font-mono text-cyan-400">{index + 1}</b>{procedure.replaceAll('_', ' ')}</span><button disabled={busy || data?.operating_mode === 'OBSERVE' || (data?.operating_mode === 'AUTONOMOUS_SIMULATION' && data?.recovery_plan.status === 'HUMAN_VERIFICATION_REQUIRED')} onClick={() => void invoke(`procedures/${procedure}`)} className="rounded border border-emerald-700 bg-emerald-950/40 px-2 py-1 text-[10px] font-bold text-emerald-200 disabled:opacity-30">Apply</button></li>) : <li className="rounded border border-industrial-700 bg-industrial-900/50 p-3 text-xs text-gray-500">No recovery procedure is required.</li>}</ol></div></section></div>
      <section className="mt-5 rounded-lg border border-industrial-700 bg-industrial-800/70"><div className="border-b border-industrial-700 px-4 py-3"><h2 className="text-sm font-bold text-white">Audit Timeline</h2><p className="mt-1 text-xs text-gray-500">Traceability for scenarios, autonomy changes, and approved simulated procedures.</p></div><div className="divide-y divide-industrial-700/70">{(data?.audit ?? []).length ? data!.audit.map(item => <div key={item.id} className="flex gap-4 px-4 py-3 text-xs"><span className={`mt-1 h-2 w-2 rounded-full ${item.severity === 'HIGH' ? 'bg-red-400' : 'bg-cyan-400'}`} /><div><div className="font-mono text-[10px] text-cyan-300">{item.event}</div><div className="mt-1 text-gray-300">{item.detail}</div></div></div>) : <div className="px-4 py-8 text-center text-sm text-gray-500">ACAMIS audit events appear after a scenario or operating-mode change.</div>}</div></section>
    </div>
  </main>;
}

function Kpi({ label, value, accent = 'text-white' }: { label: string; value: string | number; accent?: string }) { return <div className="rounded-lg border border-industrial-700 bg-industrial-800/80 p-4"><div className="text-[10px] font-bold uppercase tracking-[0.18em] text-gray-500">{label}</div><div className={`mt-2 truncate font-mono text-lg font-bold ${accent}`}>{value}</div></div>; }
