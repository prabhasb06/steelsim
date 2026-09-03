import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import type { PortDef, PortType, EngineeringQuantity } from '../../types/topology';
import type { NodeTelemetry } from '../../types';

const getPortColor = (type: PortType) => {
  switch (type) {
    case 'MATERIAL': return '#3b82f6'; // blue-500
    case 'ELECTRICAL': return '#eab308'; // yellow-500
    case 'WATER': return '#06b6d4'; // cyan-500
    case 'SIGNAL': return '#a855f7'; // purple-500
    case 'AIR': return '#f87171'; // red-400
    default: return '#9ca3af'; // gray-400
  }
};

export const CustomNode = ({ data, selected }: NodeProps) => {
  const ports: PortDef[] = (data.ports as PortDef[]) || [];
  const params: Record<string, EngineeringQuantity> = (data.parameters as Record<string, EngineeringQuantity>) || {};
  
  const inPorts = ports.filter(p => p.direction === 'IN' || p.direction === 'BIDIRECTIONAL');
  const outPorts = ports.filter(p => p.direction === 'OUT' || p.direction === 'BIDIRECTIONAL');

  // Intelligent extraction of up to 3 primary metrics
  const displayMetrics: EngineeringQuantity[] = [];
  
  // Prioritize throughput/capacity metrics
  if (params.throughput) displayMetrics.push(params.throughput);
  else if (params.capacity) displayMetrics.push(params.capacity);
  else if (params.feed_capacity) displayMetrics.push(params.feed_capacity);
  else if (params.dispatch) displayMetrics.push(params.dispatch);
  else if (params.available_power) displayMetrics.push(params.available_power);
  else if (params.available_flow) displayMetrics.push(params.available_flow);
  else if (params.flow) displayMetrics.push(params.flow);
  else if (params.inventory) displayMetrics.push(params.inventory);

  // Prioritize secondary process metrics (temp, power)
  if (params.temperature) displayMetrics.push(params.temperature);
  else if (params.water_flow) displayMetrics.push(params.water_flow);
  else if (params.speed) displayMetrics.push(params.speed);
  else if (params.pressure) displayMetrics.push(params.pressure);
  
  // Fill 3rd slot if available
  if (params.power && displayMetrics.length < 3) displayMetrics.push(params.power);
  if (params.utilization && displayMetrics.length < 3) displayMetrics.push(params.utilization);
  if (params.rating && displayMetrics.length < 3) displayMetrics.push(params.rating);

  // Look up node status passed from parent validation if available, else VALID
  const status = (data.validationStatus as "VALID" | "WARNING" | "ERROR") || "VALID";
  const statusColor = status === "VALID" ? "text-green-500" : status === "WARNING" ? "text-amber-500" : "text-red-500";
  
  const nodeIdStr = (data.engineeringId as string) || (data.id as string) || 'NEW';
  const isLocked = !!data.locked;
  const liveTelemetry = data.liveTelemetry as NodeTelemetry | undefined;
  const isRunning = liveTelemetry?.status === 'RUNNING';

  return (
    <div className={`bg-industrial-800 border rounded-sm shadow-[0_4px_12px_rgba(0,0,0,0.5)] w-52 transition-colors relative ${isRunning ? 'border-emerald-500/70 shadow-[0_0_12px_rgba(16,185,129,0.15)]' : selected ? 'border-blue-500 bg-industrial-800/90 shadow-[0_0_0_1px_rgba(59,130,246,1)]' : 'border-industrial-700 hover:border-industrial-500'}`}>
      
      {isLocked && (
          <div className="absolute -top-2 -right-2 bg-industrial-900 border border-industrial-700 rounded-full p-1 z-20 text-gray-400 shadow-md" title="Position Locked">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          </div>
      )}

      {/* Node Header */}
      <div className="bg-industrial-900 px-3 py-2 border-b border-industrial-700 rounded-t-sm">
        <div className="flex justify-between items-center mb-0.5">
            <span className="text-[11px] font-mono font-semibold text-gray-400">{nodeIdStr}</span>
            {liveTelemetry ? (
              <span className={`inline-flex items-center gap-1 text-[9px] font-mono font-bold tracking-wider px-1.5 py-0.2 rounded ${isRunning ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60' : 'bg-industrial-800 text-gray-400 border border-industrial-700'}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${isRunning ? 'bg-emerald-400 animate-pulse' : 'bg-gray-500'}`}></span>
                {liveTelemetry.status}
              </span>
            ) : (
              <span className={`text-[10px] font-semibold tracking-widest uppercase ${statusColor}`}>{status !== 'VALID' ? status : ''}</span>
            )}
        </div>
        <div className="text-[13px] font-semibold text-gray-100 truncate">{data.name as string}</div>
      </div>
      
      {/* Metrics Area: Live Simulation Telemetry or Static Defaults */}
      <div className="px-3 py-2 min-h-[3rem] bg-[#1a1c1e]">
         {liveTelemetry ? (
             <div className="grid grid-cols-2 gap-y-1 gap-x-2 text-[11px] font-mono">
                 {liveTelemetry.power_kw > 0 && (
                     <div className="flex items-baseline">
                         <span className="text-amber-400 font-semibold">{liveTelemetry.power_mw > 0 ? liveTelemetry.power_mw : liveTelemetry.power_kw}</span>
                         <span className="text-gray-500 text-[10px] ml-1">{liveTelemetry.power_mw > 0 ? 'MW' : 'kW'}</span>
                     </div>
                 )}
                 {liveTelemetry.temperature_c > 25 && (
                     <div className="flex items-baseline">
                         <span className="text-rose-400 font-semibold">{liveTelemetry.temperature_c}</span>
                         <span className="text-gray-500 text-[10px] ml-1">°C</span>
                     </div>
                 )}
                 {liveTelemetry.throughput_tph > 0 && (
                     <div className="flex items-baseline">
                         <span className="text-blue-400 font-semibold">{liveTelemetry.throughput_tph}</span>
                         <span className="text-gray-500 text-[10px] ml-1">t/h</span>
                     </div>
                 )}
                 {liveTelemetry.water_m3h > 0 && (
                     <div className="flex items-baseline">
                         <span className="text-cyan-400 font-semibold">{liveTelemetry.water_m3h}</span>
                         <span className="text-gray-500 text-[10px] ml-1">m³/h</span>
                     </div>
                 )}
             </div>
         ) : displayMetrics.length > 0 ? (
             <div className="grid grid-cols-2 gap-y-1.5 gap-x-2">
                 {displayMetrics.map((m, i) => (
                     <div key={i} className="flex items-baseline">
                         <span className="text-[13px] font-mono text-gray-200 font-semibold">{m.value}</span>
                         <span className="text-[10px] font-mono text-gray-500 ml-1">{m.unit}</span>
                     </div>
                 ))}
             </div>
         ) : (
             <div className="flex items-center h-full">
                 <span className="text-[10px] font-semibold tracking-widest uppercase text-amber-500/70 border border-amber-500/30 bg-amber-500/10 px-1.5 py-0.5 rounded">UNCONFIGURED</span>
             </div>
         )}
      </div>

      {/* Handles (Ports) */}
      {inPorts.map((port, i) => {
        const top = 30 + (i * 15);
        return (
          <Handle
            key={port.id}
            type="target"
            position={Position.Left}
            id={port.id}
            style={{ top, background: getPortColor(port.type), width: 12, height: 12, border: '2px solid #1a1c1e', left: -6 }}
            className="hover:scale-125 transition-transform cursor-crosshair z-10"
            title={`${port.direction} ${port.type}`}
          />
        );
      })}

      {outPorts.map((port, i) => {
        const top = 30 + (i * 15);
        return (
          <Handle
            key={port.id}
            type="source"
            position={Position.Right}
            id={port.id}
            style={{ top, background: getPortColor(port.type), width: 12, height: 12, border: '2px solid #1a1c1e', right: -6 }}
            className="hover:scale-125 transition-transform cursor-crosshair z-10"
            title={`${port.direction} ${port.type}`}
          />
        );
      })}
    </div>
  );
};
