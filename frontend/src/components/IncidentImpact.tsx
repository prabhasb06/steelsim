import type { SimulationSnapshot } from '../types';
import type { PlantGraph } from '../types/topology';

export function IncidentImpact({ snapshot, graph, onLocate }: {
  snapshot: SimulationSnapshot | null;
  graph: PlantGraph | null;
  onLocate: (view: 'BUILDER' | 'SIMULATION', nodeId: string) => void;
}) {
  const impact = snapshot?.acamis_impact;
  if (!impact) return null;
  const recovered = impact.state === 'RECOVERED';
  const units: Record<string, string> = { throughput_tph: 't/h', temperature_c: '°C', power_mw: 'MW', water_m3h: 'm³/h' };
  return <section aria-label="Incident impact" className={`my-4 rounded-lg border p-4 ${recovered ? 'border-emerald-800 bg-emerald-950/20' : 'border-amber-700 bg-amber-950/20'}`}>
    <h2 className="text-sm font-bold text-white">{impact.scenario.replaceAll('_', ' ')} · {recovered ? 'Recovered — recorded impact' : 'Active equipment impact'}</h2>
    <p className="mt-1 text-xs text-cyan-200">{impact.origin ?? 'Manual scenario'}</p>
    <p className="mt-1 text-xs text-gray-300">{recovered ? `Historical comparison at tick ${impact.tick}; current live readings are restored.` : `Comparison captured at tick ${impact.tick} against that tick's simulated baseline; includes downstream and mitigation effects.`}</p>
    {!recovered && impact.recovery_tick != null && <p role="status" className="mt-2 text-xs text-cyan-200">{snapshot?.status !== 'RUNNING' ? 'Recovery paused — resume simulation.' : `Autonomous simulated recovery in ${Math.max(0, impact.recovery_tick - (snapshot?.tick ?? 0))} simulation ticks.`}</p>}
    <div className="mt-3 grid max-h-72 gap-2 overflow-y-auto md:grid-cols-2 xl:grid-cols-3">
      {Object.entries(impact.equipment).map(([id, changes]) => {
        const node = graph?.nodes.find(item => item.id === id);
        return <article key={id} className="min-w-0 rounded border border-industrial-600 bg-industrial-900 p-3">
          <h3 className="text-xs font-bold text-white">{node?.name ?? id}</h3>
          <div className="mt-2 space-y-1 font-mono text-[11px] text-gray-300">{Object.entries(changes).map(([metric, values]) => <div key={metric}>{metric.replaceAll('_', ' ')}: {values.baseline} → <span className="text-amber-200">{values.actual}</span> {units[metric]}</div>)}</div>
          <div className="mt-3 flex flex-wrap gap-3 text-xs text-cyan-300"><button onClick={() => onLocate('BUILDER', id)}>Locate in plant</button><button onClick={() => onLocate('SIMULATION', id)}>Inspect simulation</button></div>
        </article>;
      })}
    </div>
    {!Object.keys(impact.equipment).length && <p className="mt-3 text-xs text-amber-200">No measurable impact in this snapshot. Check that the plant contains compatible equipment and is running.</p>}
  </section>;
}
