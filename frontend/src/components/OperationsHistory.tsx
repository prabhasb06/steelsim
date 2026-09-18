import { useEffect, useState } from 'react';
import { apiRequest } from '../api';
import type { SimulationSnapshot, SimulationState } from '../types';

type Run = { id: string; name: string; created_at: string; status: string; tick: number };
export type SignalFinding = { equipment_id: string; name: string; correlated: boolean; signals: { domain: string; metric: string; actual: number; expected: number; persistence: number }[] };
type Frame = { seq: number; snapshot: SimulationSnapshot; incident: null | { title: string }; origin: string | null; recovery_plan: { status: string }; signals: SignalFinding[] };
type Detail = Run & { frame_count: number; audit: { id: string; at: string; event: string; detail: string }[] };
const button = 'rounded border border-industrial-600 px-3 py-2 text-xs text-gray-200 hover:bg-industrial-700 disabled:opacity-40';

export function SignalEvidence({ findings }: { findings: SignalFinding[] }) {
  return <section className="mt-5 rounded-lg border border-industrial-700 bg-industrial-800/60 p-4">
    <h2 className="text-sm font-bold text-white">Multivariate telemetry monitoring</h2>
    <p className="mt-1 text-xs leading-5 text-gray-400">Temperature, cooling flow and electrical demand · three consecutive running ticks · simulator baseline</p>
    {!findings.length && <p className="mt-3 text-xs text-gray-500">No persistent signal deviations recorded. Monitoring progresses while the simulation runs.</p>}
    {findings.map(f => <div key={f.equipment_id} className="mt-3 rounded border border-amber-800/60 p-3">
      <h3 className="text-xs font-bold text-amber-300">{f.name} · {f.correlated ? 'Correlated signals' : 'Signal deviation'} · review required</h3>
      {f.signals.map(s => <p key={s.domain} className="mt-1 font-mono text-xs text-gray-300">{s.metric}: {s.actual} / baseline {s.expected} · {s.persistence} ticks</p>)}
      <p className="mt-2 text-xs text-gray-400">Evidence identifies an operating deviation; it does not establish a physical root cause.</p>
    </div>)}
  </section>;
}

function PowerTrace({ frames }: { frames: Frame[] }) {
  const values = frames.map(f => f.snapshot.plant_summary.total_power_mw);
  const peak = values.reduce((maximum, value) => Math.max(maximum, value), 0);
  const max = Math.max(1, peak);
  const points = values.map((v, i) => `${i * 800 / Math.max(1, values.length - 1)},${100 - v / max * 90}`).join(' ');
  return <figure className="mt-4 rounded border border-industrial-700 p-3">
    <figcaption className="text-xs text-gray-400">Plant power · MW · recorded frames ({values.length}) · peak {peak.toFixed(2)}</figcaption>
    <svg viewBox="0 0 800 110" className="mt-2 h-28 w-full" role="img" aria-label="Plant power trend across loaded historical frames"><polyline points={points} fill="none" stroke="#60a5fa" strokeWidth="2" /></svg>
  </figure>;
}

export function OperationsHistory({ onRestore }: { onRestore: (state: SimulationState) => void }) {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selected, setSelected] = useState('');
  const [detail, setDetail] = useState<Detail | null>(null);
  const [frames, setFrames] = useState<Frame[]>([]);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [compareId, setCompareId] = useState('');
  const [comparison, setComparison] = useState<Frame[]>([]);
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    apiRequest<Run[]>('/api/history/runs', { signal: controller.signal }).then(setRuns).catch(e => { if (!controller.signal.aborted) setError(String(e)); });
    return () => controller.abort();
  }, [refresh]);
  useEffect(() => {
    if (!selected) return;
    const controller = new AbortController();
    Promise.all([apiRequest<Detail>(`/api/history/runs/${selected}`, { signal: controller.signal }), apiRequest<Frame[]>(`/api/history/runs/${selected}/frames`, { signal: controller.signal })])
      .then(([d, f]) => { if (!controller.signal.aborted) { setDetail(d); setFrames(f); } })
      .catch(e => { if (!controller.signal.aborted) setError(String(e)); });
    return () => controller.abort();
  }, [selected, refresh]);
  useEffect(() => {
    const controller = new AbortController();
    queueMicrotask(() => { if (!controller.signal.aborted) setComparison([]); });
    if (!compareId) return () => controller.abort();
    apiRequest<Frame[]>(`/api/history/runs/${compareId}/frames`, { signal: controller.signal }).then(f => { if (!controller.signal.aborted) setComparison(f); }).catch(e => { if (!controller.signal.aborted) setError(String(e)); });
    return () => controller.abort();
  }, [compareId]);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      if (index >= frames.length - 1) setPlaying(false);
      else setIndex(index + 1);
    }, 500);
    return () => window.clearInterval(timer);
  }, [playing, frames.length, index]);
  const selectRun = (id: string) => {
    if (busy) return;
    setDetail(null); setFrames([]); setIndex(0); setPlaying(false); setError('');
    setCompareId(''); setComparison([]); setSelected(id);
  };
  const frame = frames[index];
  const action = async (fn: () => Promise<void>) => { setBusy(true); setError(''); try { await fn(); } catch (e) { setError(String(e)); } finally { setBusy(false); } };
  const report = () => action(async () => {
    const data = await apiRequest(`/api/history/runs/${selected}/report`);
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `${selected}-report.json`; anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  const metrics = (items: Frame[]) => {
    const running = items.filter(f => f.snapshot.status === 'RUNNING');
    return { count: running.length, power: running.length ? running.reduce((n, f) => n + f.snapshot.plant_summary.total_power_mw, 0) / running.length : 0, incidents: items.filter(f => f.incident || f.signals.length).length };
  };
  return <main className="h-full overflow-y-auto p-6" aria-label="Operations history"><div className="mx-auto max-w-7xl">
    <div className="flex items-center justify-between border-b border-industrial-700 pb-5"><div><p className="font-mono text-xs text-blue-400">ACAMIS / TASK 4</p><h1 className="mt-2 text-2xl font-bold text-white">Operations History</h1><p className="mt-2 text-sm text-gray-400">Inspect recorded runs, replay evidence, and compare operating performance.</p></div><button disabled={busy} className={button} onClick={() => { selectRun(selected); setRefresh(v => v + 1); }}>Refresh</button></div>
    {error && <p role="alert" className="mt-4 rounded border border-red-800 p-3 text-sm text-red-300">{error}</p>}
    <div className="mt-5 grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)]"><aside className="space-y-2"><p className="text-xs text-gray-500">Most recent 100 runs · retained on the backend</p>{!runs.length && <p className="p-4 text-sm text-gray-400">Run a plant to begin recording operational history.</p>}{runs.map(r => <button key={r.id} data-run-id={r.id} disabled={busy} onClick={() => { if (r.id !== selected) selectRun(r.id); }} className={`w-full rounded border p-3 text-left ${selected === r.id ? 'border-blue-500 bg-blue-950/20' : 'border-industrial-700 bg-industrial-800'}`}><span className="block text-sm font-semibold text-white">{r.name}</span><span className="mt-1 block text-xs text-gray-400">{new Date(r.created_at).toLocaleString()} · tick {r.tick}</span><span className="text-xs text-gray-500">Last recorded: {r.status}</span></button>)}</aside>
    <section className="min-w-0">{!selected ? <p className="p-8 text-gray-400">Select a run to inspect its history.</p> : !detail ? <p className="p-8 text-gray-400">Loading recorded evidence…</p> : <>
      <div className="flex flex-wrap items-center gap-3"><h2 className="mr-auto text-lg font-bold text-white">{detail.name}</h2><button disabled={busy} className={button} onClick={() => void report()}>Download incident report</button><button disabled={busy} className={button} onClick={() => void action(async () => { const state = await apiRequest<SimulationState>(`/api/history/runs/${selected}/restore`, { method: 'POST' }); onRestore(state); })}>Restore as paused session</button></div>
      <p className="mt-3 text-xs text-gray-400">Replay is read-only. Restoring opens a separate paused session and loads its saved plant into the builder.</p>
      <PowerTrace frames={frames} />
      <div className="mt-4 flex items-center gap-3"><button className={button} disabled={!frames.length} onClick={() => { if (index === frames.length - 1) setIndex(0); setPlaying(!playing); }}>{playing ? 'Pause replay' : 'Play replay'}</button><input className="min-w-0 flex-1" aria-label="Replay frame" type="range" min={0} max={Math.max(0, frames.length - 1)} value={index} onChange={e => { setPlaying(false); setIndex(Number(e.target.value)); }} /><span className="text-xs text-gray-400">{index + 1} / {frames.length}</span></div>
      {frames.length < detail.frame_count && <button className={`${button} mt-3`} disabled={busy} onClick={() => void action(async () => { const next = await apiRequest<Frame[]>(`/api/history/runs/${selected}/frames?after=${frames.at(-1)?.seq ?? 0}`); setFrames(f => [...f, ...next]); })}>Load next 500 frames ({detail.frame_count} recorded)</button>}
      {frame && <div className="mt-4 rounded border border-industrial-700 p-4"><p className="font-mono text-xs text-blue-300">Tick {frame.snapshot.tick} · {frame.snapshot.status} · {frame.recovery_plan.status}</p><p className="mt-2 text-sm text-gray-200">{frame.incident?.title ?? 'No active recovery incident'} {frame.origin && `· ${frame.origin}`}</p><div className="mt-3 overflow-auto"><table className="w-full text-left text-xs"><thead className="text-gray-500"><tr><th>Asset</th><th>t/h</th><th>MW</th><th>°C</th><th>Water m³/h</th></tr></thead><tbody>{Object.values(frame.snapshot.node_telemetry).map(n => <tr key={n.id} className="border-t border-industrial-700 text-gray-300"><td className="py-2">{n.id}</td><td>{n.throughput_tph}</td><td>{n.power_mw}</td><td>{n.temperature_c}</td><td>{n.water_m3h}</td></tr>)}</tbody></table></div><SignalEvidence findings={frame.signals} /></div>}
      <section className="mt-5 rounded border border-industrial-700 p-4"><label className="text-sm text-gray-300">Compare run <select value={compareId} onChange={e => setCompareId(e.target.value)} className="ml-3 max-w-full rounded bg-industrial-800 p-2 text-xs"><option value="">Select another run</option>{runs.filter(r => r.id !== selected).map(r => <option value={r.id} key={r.id}>{r.name} · {new Date(r.created_at).toLocaleString()}</option>)}</select></label>{comparison.length > 0 && <><p className="mt-3 text-xs text-gray-400">Loaded-frame comparison; mean power uses running frames only. This is not an energy or savings calculation.</p><table className="mt-3 w-full text-left text-xs text-gray-300"><thead><tr><th>Run</th><th>Running frames</th><th>Mean MW</th><th>Incident frames</th></tr></thead><tbody>{[['Selected', frames], ['Comparison (first 500)', comparison]].map(([label, items]) => { const m = metrics(items as Frame[]); return <tr key={String(label)}><td className="py-2">{String(label)}</td><td>{m.count}</td><td>{m.power.toFixed(2)}</td><td>{m.incidents}</td></tr>; })}</tbody></table></>}</section>
      <h2 className="mt-5 text-sm font-bold text-white">Policy audit</h2>{detail.audit.map(a => <div key={a.id} className="mt-2 border-l border-industrial-600 pl-3 text-xs"><p className="text-blue-300">{a.event} · {new Date(a.at).toLocaleString()}</p><p className="mt-1 text-gray-400">{a.detail}</p></div>)}
    </>}</section></div>
  </div></main>;
}
