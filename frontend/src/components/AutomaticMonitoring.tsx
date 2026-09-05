export type Monitoring = {
  active: boolean; state: string; required_ticks: number; threshold_percent: number;
  suspended_by_manual_incident: boolean; demo_active: boolean;
  equipment: { equipment_id: string; name: string; actual_tph: number; expected_tph: number; lower_bound_tph: number; persistence: number }[];
  evidence: { equipment_id: string; actual_tph: number; expected_tph: number; deviation_percent: number; first_detected_tick: number; persistence_count: number }[];
};

export function AutomaticMonitoring({ monitor, busy, hasIncident, onDemo, onClear, onLocate }: {
  monitor?: Monitoring; busy: boolean; hasIncident: boolean;
  onDemo: () => void; onClear: () => void;
  onLocate: (view: 'BUILDER' | 'SIMULATION', nodeId: string) => void;
}) {
  if (!monitor) return null;
  return <section aria-label="Automatic Monitoring" className="mt-4 rounded-lg border border-industrial-600 bg-industrial-800/70 p-4">
    <div className="flex flex-wrap items-center justify-between gap-2"><h2 className="text-sm font-bold text-white">Automatic Monitoring</h2><span role="status" className="text-xs font-bold text-cyan-200">{monitor.active ? 'Active' : 'Standby'} · {monitor.state}</span></div>
    <p className="mt-2 text-xs text-gray-300">Rolling throughput deviation · more than {monitor.threshold_percent}% below expected for {monitor.required_ticks} running ticks.</p>
    <p className="mt-1 text-xs text-gray-400">{monitor.suspended_by_manual_incident ? 'Monitoring is suspended while a manual incident is active.' : !monitor.equipment.length ? 'No compatible rolling mill in this plant.' : 'Expected range follows the configured plant capacity, upstream flow, and current simulation load.'}</p>
    <div className="mt-3 max-h-56 space-y-2 overflow-y-auto">{monitor.equipment.map(row => <div key={row.equipment_id} className="rounded border border-industrial-700 p-3 text-xs"><div className="font-bold text-white">{row.name}</div><div className="mt-1 text-gray-300">Actual {row.actual_tph} t/h · expected {row.lower_bound_tph}–{row.expected_tph} t/h · persistence {row.persistence}/{monitor.required_ticks}</div><div className="mt-2 flex gap-4 text-cyan-300"><button onClick={() => onLocate('BUILDER', row.equipment_id)}>Locate in plant</button><button onClick={() => onLocate('SIMULATION', row.equipment_id)}>Inspect simulation</button></div></div>)}</div>
    {monitor.evidence.map(item => <p key={item.equipment_id} className="mt-2 text-xs text-amber-200">Telemetry detector · {monitor.equipment.find(row => row.equipment_id === item.equipment_id)?.name ?? 'Rolling mill'}: {item.actual_tph} versus {item.expected_tph} t/h ({item.deviation_percent}% below baseline), starting at tick {item.first_detected_tick}, persisted {item.persistence_count} ticks. {monitor.state === 'Recovered' ? 'Historical detection evidence.' : 'Evidence captured when detected.'}</p>)}
    <div className="mt-3 flex flex-wrap gap-2"><button disabled={busy || !monitor.active || hasIncident || monitor.demo_active} onClick={onDemo} className="rounded border border-cyan-700 px-3 py-2 text-xs text-cyan-200 disabled:opacity-40">Demonstrate telemetry drift</button><button disabled={busy || (!monitor.demo_active && !monitor.evidence.length)} onClick={onClear} className="rounded border border-industrial-600 px-3 py-2 text-xs disabled:opacity-40">Clear monitoring demo</button></div>
    <p className="mt-2 text-xs text-gray-500">Demo reduces simulated mill capacity by 50%. The monitor independently evaluates the resulting readings; no incident is created by the demo button.</p>
  </section>;
}
