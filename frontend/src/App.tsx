import React, { useState, useEffect, useRef, useCallback } from 'react';
import { LayoutDashboard, Factory, Activity, Truck, Wrench, Shield, Zap, Cpu, Play, Pause, RotateCcw, ArrowRight, CheckCircle2, AlertTriangle, Clock3, BookOpenText, ExternalLink } from 'lucide-react';
import { Blueprint } from './components/PlantBuilder/Blueprint';
import { ApiError, simulationApi } from './api';
import { AcamisConsole } from './components/AcamisConsole';
import { IncidentImpact } from './components/IncidentImpact';
import type { SimulationCommand, SimulationEvent, SimulationSnapshot, SimulationState } from './types';
import type { PlantGraph, ValidationResult } from './types/topology';
import { isUtilityClass, orderProcessNodes, parseSimulationSnapshot, plantSimulationSignature, shouldAcceptSnapshot } from './simulation-utils';

type ViewMode = 'OVERVIEW' | 'BUILDER' | 'SIMULATION' | 'OPTIMIZATION' | 'ACAMIS';
type StreamStatus = 'IDLE' | 'CONNECTING' | 'LIVE' | 'RECONNECTING';
const STEELSIM_DOCS_URL = 'https://steelsim-docs.onrender.com/';

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('BUILDER');
  const [isFocusMode, setIsFocusMode] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeSimId, setActiveSimId] = useState<string | null>(null);
  const [simState, setSimState] = useState<SimulationState | null>(null);
  const [backendConnected, setBackendConnected] = useState(true);
  const [streamStatus, setStreamStatus] = useState<StreamStatus>('IDLE');
  const [currentGraph, setCurrentGraph] = useState<PlantGraph | null>(null);
  const [topologyValidation, setTopologyValidation] = useState<ValidationResult | null>(null);
  const [snapshot, setSnapshot] = useState<SimulationSnapshot | null>(null);
  const [events, setEvents] = useState<SimulationEvent[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [focusRequest, setFocusRequest] = useState<{ nodeId: string; nonce: number } | null>(null);
  const locateEquipment = (view: 'BUILDER' | 'SIMULATION', nodeId: string) => {
    setFocusRequest({ nodeId, nonce: Date.now() });
    setViewMode(view);
  };
  const simulatedGraphRef = useRef<string | null>(null);
  const latestSnapshotRef = useRef<SimulationSnapshot | null>(null);

  const applySnapshot = useCallback((next: SimulationSnapshot) => {
    if (!shouldAcceptSnapshot(latestSnapshotRef.current, next)) return;
    latestSnapshotRef.current = next;
    setSnapshot(next);
    setEvents(next.events);
    setBackendConnected(true);
  }, []);

  useEffect(() => {
    let mounted = true;
    const checkHealth = async () => {
      try {
        await simulationApi.health();
        if (mounted) setBackendConnected(true);
      } catch {
        if (mounted) setBackendConnected(false);
      }
    };
    void checkHealth();
    const interval = window.setInterval(checkHealth, 10_000);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    if (!activeSimId) {
      return;
    }
    let mounted = true;
    let socket: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let hasConnected = false;

    const refreshSnapshot = async () => {
      try {
        const data = await simulationApi.snapshot(activeSimId);
        if (mounted) {
          applySnapshot(data);
        }
      } catch (error) {
        if (mounted) {
          if (error instanceof ApiError && error.status === 404) {
            latestSnapshotRef.current = null;
            simulatedGraphRef.current = null;
            setActiveSimId(null);
            setSimState(null);
            setSnapshot(null);
            setEvents([]);
            setStreamStatus('IDLE');
            setErrorMessage('The backend simulation session ended. Your plant remains loaded; click Run to start a new session and reconnect your model if needed.');
            return;
          }
          setBackendConnected(false);
          setErrorMessage(error instanceof Error ? error.message : 'Unable to read simulation state.');
        }
      }
    };

    const connect = () => {
      if (!mounted) return;
      setStreamStatus(hasConnected ? 'RECONNECTING' : 'CONNECTING');
      const protocols = simulationApi.streamProtocols();
      socket = protocols
        ? new WebSocket(simulationApi.streamUrl(activeSimId), protocols)
        : new WebSocket(simulationApi.streamUrl(activeSimId));
      socket.onopen = () => {
        hasConnected = true;
        if (mounted) setStreamStatus('LIVE');
      };
      socket.onmessage = event => {
        if (!mounted) return;
        try {
          applySnapshot(parseSimulationSnapshot(event.data, activeSimId));
        } catch (error) {
          setErrorMessage(error instanceof Error ? error.message : 'Invalid simulation stream payload.');
          socket?.close();
        }
      };
      socket.onerror = () => socket?.close();
      socket.onclose = () => {
        if (!mounted) return;
        setStreamStatus('RECONNECTING');
        reconnectTimer = window.setTimeout(connect, 2_000);
      };
    };

    void refreshSnapshot();
    connect();
    const fallbackInterval = window.setInterval(refreshSnapshot, 5_000);
    return () => {
      mounted = false;
      socket?.close();
      if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
      window.clearInterval(fallbackInterval);
    };
  }, [activeSimId, applySnapshot]);

  useEffect(() => {
    if (!activeSimId || !currentGraph || !simulatedGraphRef.current) return;
    if (plantSimulationSignature(currentGraph) === simulatedGraphRef.current) return;

    simulatedGraphRef.current = null;
    latestSnapshotRef.current = null;
    setActiveSimId(null);
    setSimState(null);
    setSnapshot(null);
    setEvents([]);
    setStreamStatus('IDLE');
  }, [activeSimId, currentGraph]);

  useEffect(() => {
    if (!activeSimId) return;
    return () => {
      void simulationApi.delete(activeSimId, true).catch(() => undefined);
    };
  }, [activeSimId]);

  const handleStart = async () => {
    if (isBusy) return;
    setErrorMessage(null);
    setIsBusy(true);
    try {
      const graph = currentGraph;
      if (!graph?.nodes.length) {
        throw new Error('Build or load a plant before starting the simulation.');
      }

      const validation = await simulationApi.validate(graph);
      setTopologyValidation(validation);
      if (!validation.is_valid) {
        const blocking = validation.issues.filter(issue => issue.blocks_simulation).length;
        throw new Error(`Simulation blocked: resolve ${blocking || validation.issues.length} topology issue${blocking === 1 ? '' : 's'} first.`);
      }

      const graphSignature = plantSimulationSignature(graph);
      const graphChanged = simulatedGraphRef.current !== graphSignature;
      let simulationId = activeSimId;
      if (!simulationId || graphChanged) {
        const created = await simulationApi.create(graph);
        simulationId = created.id;
        simulatedGraphRef.current = graphSignature;
        setActiveSimId(created.id);
        setSimState(created);
        latestSnapshotRef.current = null;
        setSnapshot(null);
        setEvents(created.events);
      }

      const current = graphChanged ? 'READY' : (snapshot?.status ?? simState?.status ?? 'READY');
      const next = await simulationApi.command(simulationId, current === 'PAUSED' ? 'resume' : 'start');
      applySnapshot(next);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Unable to start the simulation.');
    } finally {
      setIsBusy(false);
    }
  };

  const handleCommand = async (command: SimulationCommand) => {
    if (!activeSimId || isBusy) return;
    setErrorMessage(null);
    setIsBusy(true);
    try {
      applySnapshot(await simulationApi.command(activeSimId, command));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : `Unable to ${command} the simulation.`);
    } finally {
      setIsBusy(false);
    }
  };

  const handleSpeed = async (speed: string) => {
    if (!activeSimId || isBusy) return;
    setErrorMessage(null);
    setIsBusy(true);
    try {
      applySnapshot(await simulationApi.command(activeSimId, 'set_speed', { speed }));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Unable to change simulation speed.');
    } finally {
      setIsBusy(false);
    }
  };

  const currentStatus = snapshot?.status || simState?.status || 'READY';
  const currentSpeed = snapshot?.speed || simState?.speed || '1x';

  return (
    <div className="flex h-screen w-full bg-industrial-900 text-gray-300 overflow-hidden font-sans selection:bg-blue-900 selection:text-blue-100">
      
      {/* LEFT NAV */}
      {!isFocusMode && (
      <div className={`border-r border-industrial-700 bg-industrial-800 flex flex-col transition-all duration-300 z-10 relative shadow-xl ${sidebarCollapsed ? 'w-16' : 'w-16 md:w-64'}`}>
        <div 
            className="h-14 flex items-center justify-center md:justify-start px-4 border-b border-industrial-700 font-bold text-white tracking-wider cursor-pointer hover:bg-industrial-700 transition-colors"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        >
          <Factory className="w-6 h-6 md:mr-3 text-blue-500 flex-shrink-0" />
          <span className={`hidden md:inline whitespace-nowrap ${sidebarCollapsed ? 'md:hidden' : ''}`}>SteelSim</span>
        </div>
        
        <div className="flex-1 py-4 overflow-y-auto">
          <NavItem icon={<LayoutDashboard />} label="Overview" active={viewMode==='OVERVIEW'} onClick={() => setViewMode('OVERVIEW')} collapsed={sidebarCollapsed} />
          <NavItem icon={<Factory />} label="Plant Builder" active={viewMode==='BUILDER'} onClick={() => setViewMode('BUILDER')} collapsed={sidebarCollapsed} />
          <NavItem icon={<Activity />} label="Simulation" active={viewMode==='SIMULATION'} onClick={() => setViewMode('SIMULATION')} collapsed={sidebarCollapsed} />
          <NavItem icon={<Cpu />} label="ACAMIS Intelligence" active={viewMode==='ACAMIS'} onClick={() => setViewMode('ACAMIS')} collapsed={sidebarCollapsed} />
          
          <div className={`mt-8 mb-2 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider hidden md:block whitespace-nowrap ${sidebarCollapsed ? 'md:hidden' : ''}`}>Future Modules</div>
          <NavItem icon={<Cpu />} label="Optimize Plant" active={viewMode==='OPTIMIZATION'} onClick={() => setViewMode('OPTIMIZATION')} collapsed={sidebarCollapsed} />
          <NavItem icon={<Zap />} label="Energy Model" disabled collapsed={sidebarCollapsed} />
          <NavItem icon={<Wrench />} label="Maintenance" disabled collapsed={sidebarCollapsed} />
          <NavItem icon={<Shield />} label="Safety limits" disabled collapsed={sidebarCollapsed} />
          <NavItem icon={<Truck />} label="Logistics" disabled collapsed={sidebarCollapsed} />
        </div>
        <a
          href={STEELSIM_DOCS_URL}
          target="_blank"
          rel="noreferrer"
          aria-label="Inside SteelSim — open the engineering reference"
          title={sidebarCollapsed ? 'Inside SteelSim' : undefined}
          className="group mx-2 mb-3 flex items-center gap-3 rounded-md border border-cyan-950 bg-cyan-950/20 px-3 py-2.5 text-cyan-200 transition-colors hover:border-cyan-800 hover:bg-cyan-950/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500"
        >
          <BookOpenText className="h-4 w-4 flex-none text-cyan-400" />
          <span className={`min-w-0 flex-1 ${sidebarCollapsed ? 'hidden' : 'hidden md:block'}`}>
            <span className="block text-[11px] font-bold">Inside SteelSim</span>
            <span className="block truncate font-mono text-[8px] uppercase tracking-wider text-gray-500">Engineering reference</span>
          </span>
          {!sidebarCollapsed && <ExternalLink className="hidden h-3 w-3 flex-none text-gray-600 transition-colors group-hover:text-cyan-300 md:block" />}
        </a>
      </div>
      )}

      {/* MAIN WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* TOP BAR: MASTER SIMULATION CONTROLS & KPI DECK */}
        {!isFocusMode && (
        <div className="h-14 overflow-x-auto border-b border-industrial-700 bg-industrial-800 flex items-center justify-between gap-4 px-4 z-10 flex-shrink-0">
          {/* Left: Brand & Plant Title */}
          <div className="flex shrink-0 items-center space-x-3">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white tracking-wider text-base">SteelSim</span>
              <span className="hidden 2xl:inline text-xs bg-industrial-700 text-gray-300 px-2 py-0.5 rounded font-mono">TMT Mini-Mill</span>
            </div>
            
            {/* Status Badge */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-industrial-900 border border-industrial-700 text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${
                currentStatus === 'RUNNING' ? 'bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]' :
                currentStatus === 'PAUSED' ? 'bg-amber-400' : 'bg-blue-400'
              }`}></span>
              <span className="font-bold tracking-wider text-white">{currentStatus}</span>
            </div>
          </div>

          {/* Center: Master Simulation Controls */}
          <div className="flex shrink-0 items-center gap-3">
            {/* Run / Pause / Reset Buttons */}
            <div className="flex items-center gap-1.5 bg-industrial-900/80 p-1 rounded-md border border-industrial-700">
              <button 
                onClick={handleStart}
                disabled={currentStatus === 'RUNNING' || isBusy}
                className="flex items-center gap-1.5 px-3 py-1 bg-emerald-600/20 text-emerald-400 border border-emerald-600/50 rounded hover:bg-emerald-600 hover:text-white disabled:opacity-30 disabled:hover:bg-emerald-600/20 disabled:hover:text-emerald-400 transition-colors text-xs font-bold"
                title="Run Simulation"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{isBusy ? 'Working…' : currentStatus === 'RUNNING' ? 'Running' : currentStatus === 'PAUSED' ? 'Resume' : 'Run'}</span>
              </button>
              <button 
                onClick={() => handleCommand('pause')}
                disabled={currentStatus !== 'RUNNING' || isBusy}
                className="flex items-center gap-1.5 px-3 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/50 rounded hover:bg-amber-500 hover:text-white disabled:opacity-30 disabled:hover:bg-amber-500/20 disabled:hover:text-amber-400 transition-colors text-xs font-bold"
                title="Pause Simulation"
              >
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>Pause</span>
              </button>
              <button 
                onClick={() => handleCommand('reset')}
                disabled={!activeSimId || isBusy}
                className="flex items-center gap-1.5 px-2.5 py-1 bg-red-500/10 text-red-400 border border-red-500/30 rounded hover:bg-red-500 hover:text-white disabled:opacity-30 disabled:hover:bg-red-500/10 disabled:hover:text-red-400 transition-colors text-xs font-bold"
                title="Reset Simulation"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            </div>

            {/* Speed Multiplier */}
            <div className="flex bg-industrial-900 rounded border border-industrial-700 p-0.5 text-xs font-mono">
              {['1x', '5x', '10x', '60x'].map(spd => (
                <button
                  key={spd}
                  onClick={() => handleSpeed(spd)}
                  disabled={!activeSimId || isBusy}
                  className={`px-2 py-0.5 rounded transition-colors disabled:opacity-30 ${currentSpeed === spd ? 'bg-blue-600 text-white font-bold' : 'text-gray-400 hover:text-white'}`}
                >
                  {spd}
                </button>
              ))}
            </div>

            {/* Real-time Telemetry Readout */}
            <div className="flex items-center gap-2 2xl:gap-4 bg-industrial-900/60 px-3 py-1 rounded border border-industrial-700/80 text-xs font-mono">
              <div>
                <span className="text-gray-500 text-[10px] uppercase mr-1.5">Tick</span>
                <span className="text-gray-200 font-bold">{snapshot?.tick ?? simState?.tick ?? 0}</span>
              </div>
              <div className="w-px h-4 bg-industrial-700"></div>
              <div>
                <span className="text-gray-500 text-[10px] uppercase mr-1.5">Power</span>
                <span className="text-amber-400 font-bold">
                  {snapshot?.plant_summary?.total_power_mw ? `${snapshot.plant_summary.total_power_mw} MW` : '0.0 MW'}
                </span>
              </div>
              <div className="w-px h-4 bg-industrial-700"></div>
              <div>
                <span className="text-gray-500 text-[10px] uppercase mr-1.5">Water</span>
                <span className="text-cyan-400 font-bold">
                  {snapshot?.plant_summary?.total_water_m3h ? `${snapshot.plant_summary.total_water_m3h} m³/h` : '0.0 m³/h'}
                </span>
              </div>
              <div className="w-px h-4 bg-industrial-700"></div>
              <div>
                <span className="text-gray-500 text-[10px] uppercase mr-1.5">Active</span>
                <span className="text-emerald-400 font-bold">
                  {snapshot?.plant_summary?.active_nodes ?? 0}/{snapshot?.plant_summary?.total_nodes ?? 0}
                </span>
              </div>
            </div>
          </div>

          {/* Right: API Health Status */}
          <div className="flex items-center space-x-2" title={backendConnected ? 'Engine Online' : 'Engine Offline'}>
             <span className={`w-2 h-2 rounded-full ${backendConnected ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 animate-pulse'}`}></span>
             <span className="hidden 2xl:inline text-[10px] font-bold uppercase tracking-widest text-gray-400">
               {backendConnected ? 'Engine Online' : 'Engine Offline'}
             </span>
          </div>
        </div>
        )}

        {/* CONTENT AREA */}
        <div className="flex-1 overflow-hidden relative bg-[#121315]">
          {errorMessage && (
            <div role="alert" className="absolute top-3 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 max-w-xl rounded border border-red-700/70 bg-red-950/95 px-4 py-2 text-xs text-red-100 shadow-xl">
              <span>{errorMessage}</span>
              <button onClick={() => setErrorMessage(null)} className="text-red-300 hover:text-white font-bold" aria-label="Dismiss error">×</button>
            </div>
          )}
          <div
            className={`absolute inset-0 flex flex-col ${viewMode === 'BUILDER' ? 'translate-x-0' : 'pointer-events-none translate-x-[200%]'}`}
            data-testid="builder-layer"
            aria-hidden={viewMode !== 'BUILDER'}
            inert={viewMode !== 'BUILDER'}
          >
            <Blueprint 
                isFocusMode={isFocusMode} 
                setIsFocusMode={setIsFocusMode}
                isActive={viewMode === 'BUILDER'}
                activeSimId={activeSimId}
                simState={simState}
                snapshot={snapshot}
                events={events}
                onGraphChange={setCurrentGraph}
                onValidationChange={setTopologyValidation}
                focusRequest={focusRequest}
            />
          </div>
          {viewMode === 'OVERVIEW' && (
            <OverviewView
              graph={currentGraph}
              validation={topologyValidation}
              snapshot={snapshot}
              status={currentStatus}
              backendConnected={backendConnected}
              events={events}
              onOpenBuilder={() => setViewMode('BUILDER')}
              onOpenSimulation={() => setViewMode('SIMULATION')}
            />
          )}
          {viewMode === 'SIMULATION' && (
            <SimulationView
              graph={currentGraph}
              snapshot={snapshot}
              events={events}
              status={currentStatus}
              streamStatus={streamStatus}
              isBusy={isBusy}
              onRun={handleStart}
              focusRequest={focusRequest}
              onLocate={locateEquipment}
              onOpenBuilder={() => setViewMode('BUILDER')}
            />
          )}
          {viewMode === 'OPTIMIZATION' && (
            <OptimizationView onOpenBuilder={() => setViewMode('BUILDER')} />
          )}
          {viewMode === 'ACAMIS' && (
            <AcamisConsole simulationId={activeSimId} snapshot={snapshot} graph={currentGraph} onLocate={locateEquipment} onOpenSimulation={() => setViewMode('SIMULATION')} />
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, detail, accent = 'text-white' }: { label: string; value: string | number; detail: string; accent?: string }) {
  return (
    <div className="rounded-lg border border-industrial-700 bg-industrial-800/80 p-4 shadow-lg">
      <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-gray-500">{label}</div>
      <div className={`mt-2 text-2xl font-bold font-mono ${accent}`}>{value}</div>
      <div className="mt-1 text-xs text-gray-500">{detail}</div>
    </div>
  );
}

function RecentEvents({ events }: { events: SimulationEvent[] }) {
  const recent = [...events].reverse().slice(0, 6);
  return (
    <div className="divide-y divide-industrial-700/70">
      {recent.length === 0 ? (
        <div className="px-4 py-8 text-center text-sm text-gray-500">Simulation events will appear here after a run starts.</div>
      ) : recent.map(event => (
        <div key={event.id} className="flex gap-3 px-4 py-3 text-xs">
          <span className={`mt-1 h-2 w-2 flex-shrink-0 rounded-full ${
            event.severity === 'CRITICAL' ? 'bg-red-500' :
            event.severity === 'WARNING' ? 'bg-amber-400' :
            event.severity === 'NOTICE' ? 'bg-blue-400' : 'bg-gray-500'
          }`} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-3">
              <span className="truncate font-semibold text-gray-300">{event.source}</span>
              <span className="whitespace-nowrap font-mono text-gray-600">{event.simulation_time}</span>
            </div>
            <p className="mt-1 text-gray-500">{event.message}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function OverviewView({
  graph,
  validation,
  snapshot,
  status,
  backendConnected,
  events,
  onOpenBuilder,
  onOpenSimulation,
}: {
  graph: PlantGraph | null;
  validation: ValidationResult | null;
  snapshot: SimulationSnapshot | null;
  status: string;
  backendConnected: boolean;
  events: SimulationEvent[];
  onOpenBuilder: () => void;
  onOpenSimulation: () => void;
}) {
  const nodeCount = graph?.nodes.length ?? 0;
  const edgeCount = graph?.edges.length ?? 0;
  const blockingIssues = validation?.issues.filter(issue => issue.blocks_simulation).length ?? 0;
  const topologyLabel = nodeCount === 0 ? 'Not configured' : validation === null ? 'Not validated' : validation.is_valid ? 'Ready' : `${blockingIssues} blocker${blockingIssues === 1 ? '' : 's'}`;

  return (
    <main className="h-full w-full overflow-x-hidden overflow-y-auto p-5 lg:p-7" aria-label="Plant overview">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col gap-4 border-b border-industrial-700 pb-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400">Operations Center</div>
            <h1 className="mt-1 text-2xl font-bold text-white">Plant Overview</h1>
            <p className="mt-1 text-sm text-gray-500">Topology readiness and live TMT mini-mill performance in one place.</p>
          </div>
          <div className="flex gap-2">
            <button type="button" onClick={onOpenBuilder} className="rounded border border-industrial-600 bg-industrial-800 px-4 py-2 text-xs font-bold text-gray-200 hover:bg-industrial-700">Open Plant Builder</button>
            <button type="button" onClick={onOpenSimulation} className="flex items-center gap-2 rounded bg-blue-600 px-4 py-2 text-xs font-bold text-white hover:bg-blue-500">Open Simulation <ArrowRight className="h-3.5 w-3.5" /></button>
          </div>
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Equipment" value={nodeCount} detail={`${edgeCount} configured connections`} accent="text-blue-300" />
          <MetricCard label="Plant Power" value={`${snapshot?.plant_summary.total_power_mw ?? 0} MW`} detail="Current simulated demand" accent="text-amber-400" />
          <MetricCard label="Water Flow" value={`${snapshot?.plant_summary.total_water_m3h ?? 0} m³/h`} detail="Current simulated circulation" accent="text-cyan-400" />
          <MetricCard label="Active Units" value={`${snapshot?.plant_summary.active_nodes ?? 0}/${snapshot?.plant_summary.total_nodes ?? nodeCount}`} detail={`Engine state: ${status}`} accent="text-emerald-400" />
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.4fr)]">
          <section className="rounded-lg border border-industrial-700 bg-industrial-800/70">
            <div className="border-b border-industrial-700 px-4 py-3">
              <h2 className="text-sm font-bold text-white">Operational Readiness</h2>
            </div>
            <div className="space-y-1 p-3">
              <ReadinessRow label="Simulation engine" value={backendConnected ? 'Online' : 'Offline'} ready={backendConnected} />
              <ReadinessRow label="Plant topology" value={topologyLabel} ready={Boolean(validation?.is_valid)} neutral={nodeCount === 0 || validation === null} />
              <ReadinessRow label="Simulation state" value={status} ready={status === 'RUNNING'} neutral={status === 'READY' || status === 'PAUSED'} />
            </div>
            {nodeCount === 0 && (
              <div className="m-3 mt-0 rounded border border-blue-900/70 bg-blue-950/30 p-3 text-xs text-blue-200">
                Start in Plant Builder and load the TMT template or assemble your own process line.
              </div>
            )}
          </section>

          <section className="overflow-hidden rounded-lg border border-industrial-700 bg-industrial-800/70">
            <div className="flex items-center justify-between border-b border-industrial-700 px-4 py-3">
              <h2 className="text-sm font-bold text-white">Recent Engine Events</h2>
              <span className="font-mono text-[10px] uppercase tracking-wider text-gray-500">{events.length} total</span>
            </div>
            <RecentEvents events={events} />
          </section>
        </div>

        <EngineeringDiscovery />
      </div>
    </main>
  );
}

function EngineeringDiscovery() {
  return (
    <a
      href={STEELSIM_DOCS_URL}
      target="_blank"
      rel="noreferrer"
      aria-label="Explore the engineering behind SteelSim"
      className="engineering-discovery group mt-5 block overflow-hidden rounded-lg border border-industrial-600 px-5 py-5 transition-colors hover:border-cyan-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 sm:px-6 sm:py-6"
    >
      <div className="relative z-10 grid gap-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
        <div className="max-w-4xl">
          <div className="flex items-center gap-3 font-mono text-[9px] font-bold uppercase tracking-[0.22em] text-cyan-400">
            <span className="h-px w-8 bg-cyan-700" />
            Architecture / Engineering Reference
          </div>
          <h2 className="mt-4 text-xl font-bold tracking-tight text-white sm:text-2xl">
            Explore the Engineering Behind SteelSim
            <ArrowRight className="ml-2 inline h-5 w-5 text-cyan-400 transition-transform duration-300 group-hover:translate-x-1" />
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-gray-400">
            Go beyond the interface. Explore SteelSim’s plant architecture, industrial component model, connection system, simulation engine, validation pipeline, and the engineering principles behind building deterministic virtual factories.
          </p>
        </div>
        <div className="border-l border-industrial-600 pl-4 font-mono text-[9px] font-bold uppercase leading-5 tracking-[0.16em] lg:text-right">
          <div className="text-gray-300">SteelSim creates the factory.</div>
          <div className="text-cyan-400">ACAMIS understands the factory.</div>
        </div>
      </div>
    </a>
  );
}

function ReadinessRow({ label, value, ready, neutral = false }: { label: string; value: string; ready: boolean; neutral?: boolean }) {
  return (
    <div className="flex items-center justify-between rounded px-2 py-3 hover:bg-industrial-700/40">
      <span className="text-xs text-gray-400">{label}</span>
      <span className={`flex items-center gap-2 text-xs font-bold ${neutral ? 'text-gray-400' : ready ? 'text-emerald-400' : 'text-red-400'}`}>
        {neutral ? <Clock3 className="h-4 w-4" /> : ready ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
        {value}
      </span>
    </div>
  );
}

function SimulationView({ graph, snapshot, events, status, streamStatus, isBusy, onRun, onOpenBuilder, focusRequest, onLocate }: {
  focusRequest: { nodeId: string; nonce: number } | null;
  onLocate: (view: 'BUILDER' | 'SIMULATION', nodeId: string) => void;
  graph: PlantGraph | null;
  snapshot: SimulationSnapshot | null;
  events: SimulationEvent[];
  status: string;
  streamStatus: StreamStatus;
  isBusy: boolean;
  onRun: () => void;
  onOpenBuilder: () => void;
}) {
  const nodes = graph?.nodes ?? [];
  const edges = graph?.edges ?? [];
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  useEffect(() => {
    if (!focusRequest) return;
    const timer = window.setTimeout(() => {
      setSelectedNodeId(focusRequest.nodeId);
      document.getElementById(`process-${focusRequest.nodeId}`)?.scrollIntoView({ block: 'center', inline: 'center', behavior: 'smooth' });
    }, 0);
    return () => window.clearTimeout(timer);
  }, [focusRequest]);
  const processNodes = orderProcessNodes(nodes, edges);
  const utilityNodes = nodes.filter(node => isUtilityClass(node.component_class));
  const selectedNode = nodes.find(node => node.id === selectedNodeId) ?? null;
  const canRun = nodes.length > 0 && status !== 'RUNNING' && !isBusy;
  const utilization = nodes.length > 0 ? Math.round(((snapshot?.plant_summary.active_nodes ?? 0) / nodes.length) * 1000) / 10 : 0;
  const streamLabel = streamStatus === 'IDLE' ? 'AWAITING RUN' : streamStatus === 'LIVE' ? 'LIVE BACKEND' : streamStatus;

  return (
    <main className="h-full w-full overflow-x-hidden overflow-y-auto p-5 lg:p-7" aria-label="Simulation console">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col gap-4 border-b border-industrial-700 pb-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-400">SteelSim / Task 2</div>
            <h1 className="mt-1 text-2xl font-bold text-white">Simulation Control Center</h1>
            <p className="mt-1 text-sm text-gray-500">Backend-authoritative deterministic virtual factory · TMT 25 t/h baseline</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2 rounded border border-industrial-700 bg-industrial-900 px-3 py-2 font-mono text-[10px] font-bold tracking-wider text-gray-300">
              <span className={`h-2 w-2 rounded-full ${streamStatus === 'LIVE' ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]' : streamStatus === 'IDLE' ? 'bg-gray-500' : 'animate-pulse bg-amber-400'}`} />
              {streamLabel}
            </div>
            <button type="button" onClick={onOpenBuilder} className="rounded border border-industrial-600 bg-industrial-800 px-4 py-2 text-xs font-bold text-gray-200 hover:bg-industrial-700">Edit Plant</button>
            <button type="button" onClick={onRun} disabled={!canRun} className="flex items-center gap-2 rounded bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-40">
              <Play className="h-3.5 w-3.5 fill-current" /> {status === 'PAUSED' ? 'Resume Simulation' : 'Run Simulation'}
            </button>
          </div>
        </div>

        {nodes.length === 0 ? (
          <section className="mt-12 rounded-lg border border-dashed border-industrial-600 bg-industrial-800/40 px-6 py-14 text-center">
            <Factory className="mx-auto h-10 w-10 text-gray-600" />
            <h2 className="mt-4 text-lg font-bold text-white">No plant is configured</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">Create or load a valid plant in Plant Builder. Your design remains intact when you return to this console.</p>
            <button type="button" onClick={onOpenBuilder} className="mt-5 rounded bg-blue-600 px-5 py-2 text-xs font-bold text-white hover:bg-blue-500">Go to Plant Builder</button>
          </section>
        ) : (
          <>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              <MetricCard label="Lifecycle" value={status} detail={`Version ${snapshot?.state_version ?? 0} · ${snapshot?.speed ?? '1x'}`} accent={status === 'RUNNING' ? 'text-emerald-400' : status === 'PAUSED' ? 'text-amber-400' : 'text-blue-300'} />
              <MetricCard label="Simulation Time" value={`${snapshot?.elapsed_seconds ?? 0} s`} detail={`Clock tick ${snapshot?.tick ?? 0}`} />
              <MetricCard label="Utilization" value={`${utilization}%`} detail={`${snapshot?.plant_summary.active_nodes ?? 0} of ${nodes.length} units active`} accent="text-emerald-400" />
              <MetricCard label="Plant Power" value={`${snapshot?.plant_summary.total_power_mw ?? 0} MW`} detail="Total electrical demand" accent="text-amber-400" />
              <MetricCard label="Cooling Water" value={`${snapshot?.plant_summary.total_water_m3h ?? 0} m³/h`} detail="Total circulation rate" accent="text-cyan-400" />
            </div>

            <IncidentImpact snapshot={snapshot} graph={graph} onLocate={onLocate} />
            <section className="mt-5 overflow-hidden rounded-lg border border-industrial-700 bg-industrial-800/60">
              <div className="flex items-center justify-between border-b border-industrial-700 px-4 py-3">
                <h2 className="text-sm font-bold text-white">Process Flow Diagram</h2>
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-cyan-400">Live Plant Topology</span>
              </div>
              <div className="overflow-x-auto p-4">
                <div className="flex min-w-max items-center gap-2">
                  {processNodes.map((node, index) => (
                    <React.Fragment key={node.id}>
                      {index > 0 && <ArrowRight className="h-5 w-5 flex-none text-blue-500" />}
                      <ProcessCard node={node} snapshot={snapshot} selected={selectedNodeId === node.id} onSelect={() => setSelectedNodeId(node.id)} />
                    </React.Fragment>
                  ))}
                </div>
                {utilityNodes.length > 0 && (
                  <div className="mt-4 flex min-w-max items-center gap-3 border-t border-dashed border-industrial-700 pt-4">
                    <span className="mr-1 font-mono text-[10px] font-bold uppercase tracking-wider text-gray-600">Utilities</span>
                    {utilityNodes.map(node => <ProcessCard key={node.id} node={node} snapshot={snapshot} selected={selectedNodeId === node.id} onSelect={() => setSelectedNodeId(node.id)} compact />)}
                  </div>
                )}
              </div>
            </section>

            {selectedNode && (
              <EquipmentInspector node={selectedNode} snapshot={snapshot} onClose={() => setSelectedNodeId(null)} />
            )}

            <div className="mt-5 grid gap-5 xl:grid-cols-2">
              <section className="overflow-hidden rounded-lg border border-industrial-700 bg-industrial-800/70">
                <div className="flex items-center justify-between border-b border-industrial-700 px-4 py-3">
                  <h2 className="text-sm font-bold text-white">State Trace</h2>
                  <span className="font-mono text-[10px] uppercase tracking-wider text-gray-500">Authoritative Snapshot</span>
                </div>
                <pre className="max-h-72 overflow-auto p-4 font-mono text-[11px] leading-5 text-cyan-100/75">{JSON.stringify(snapshot ? {
                  simulation_id: snapshot.simulation_id,
                  lifecycle: snapshot.status,
                  speed: snapshot.speed,
                  tick: snapshot.tick,
                  simulated_seconds: snapshot.elapsed_seconds,
                  state_version: snapshot.state_version,
                  system_health: snapshot.system_health,
                  plant: { summary: snapshot.plant_summary },
                } : { lifecycle: 'READY', plant: { nodes: nodes.length, connections: edges.length } }, null, 2)}</pre>
              </section>

              <section className="overflow-hidden rounded-lg border border-industrial-700 bg-industrial-800/70">
                <div className="flex items-center justify-between border-b border-industrial-700 px-4 py-3">
                  <h2 className="text-sm font-bold text-white">Event Journal</h2>
                  <span className="font-mono text-[10px] uppercase tracking-wider text-gray-500">Traceability</span>
                </div>
                <RecentEvents events={events} />
              </section>
            </div>
          </>
        )}
      </div>
    </main>
  );
}

function telemetryStatusClass(status?: string) {
  if (status === 'RUNNING') return 'border-emerald-500 text-emerald-400 bg-emerald-950/50';
  if (status === 'INTERLOCKED') return 'border-red-500 text-red-400 bg-red-950/50';
  if (status === 'PREHEATING') return 'border-amber-500 text-amber-400 bg-amber-950/50';
  return 'border-industrial-600 text-gray-400 bg-industrial-900';
}

function ProcessCard({ node, snapshot, selected, onSelect, compact = false }: {
  node: PlantGraph['nodes'][number];
  snapshot: SimulationSnapshot | null;
  selected: boolean;
  onSelect: () => void;
  compact?: boolean;
}) {
  const telemetry = snapshot?.node_telemetry[node.id];
  const status = telemetry?.status ?? 'IDLE';
  const impacted = snapshot?.acamis_impact?.state === 'ACTIVE' && !!snapshot.acamis_impact.equipment[node.id];
  return (
    <button id={`process-${node.id}`} type="button" onClick={onSelect} className={`${compact ? 'w-56' : 'w-60'} flex-none rounded border p-3 text-left transition-colors ${impacted ? 'border-amber-400 bg-amber-950/30 ring-1 ring-amber-500' : selected ? 'border-blue-400 bg-blue-950/30 shadow-[0_0_0_1px_rgba(96,165,250,0.35)]' : status === 'RUNNING' ? 'border-emerald-700 bg-industrial-900/80 hover:border-emerald-500' : status === 'INTERLOCKED' ? 'border-red-700 bg-red-950/20 hover:border-red-500' : 'border-industrial-600 bg-industrial-900/80 hover:border-blue-600'}`}>
      {impacted && <div className="mb-2 text-[10px] font-bold text-amber-300">ACAMIS · AFFECTED</div>}
      <div className="font-mono text-[10px] text-blue-300">{String(node.metadata.engineering_id ?? node.id).toUpperCase()}</div>
      <div className="mt-1 min-h-9 text-xs font-bold leading-4 text-white">{node.name}</div>
      <span className={`mt-3 inline-flex rounded border px-2 py-0.5 font-mono text-[9px] font-bold tracking-wider ${telemetryStatusClass(status)}`}>{status}</span>
      <div className="mt-2 flex gap-3 font-mono text-[10px] text-gray-400">
        <span>{telemetry?.throughput_tph ?? 0} t/h</span>
        <span>{telemetry?.power_mw ?? 0} MW</span>
      </div>
    </button>
  );
}

function EquipmentInspector({ node, snapshot, onClose }: { node: PlantGraph['nodes'][number]; snapshot: SimulationSnapshot | null; onClose: () => void }) {
  const telemetry = snapshot?.node_telemetry[node.id];
  const status = telemetry?.status ?? 'IDLE';
  const category = String(node.metadata.category ?? (isUtilityClass(node.component_class) ? 'UTILITY' : 'PROCESS'));
  return (
    <section className="mt-5 overflow-hidden rounded-lg border border-blue-900/70 bg-blue-950/10">
      <div className="flex items-center justify-between border-b border-industrial-700 px-4 py-3">
        <div><div className="text-[10px] font-bold uppercase tracking-wider text-blue-400">Equipment Inspector</div><h2 className="mt-0.5 text-sm font-bold text-white">{node.name}</h2></div>
        <button type="button" onClick={onClose} aria-label="Close equipment inspector" className="text-xl text-gray-500 hover:text-white">×</button>
      </div>
      <div className="grid gap-px bg-industrial-700 sm:grid-cols-2 lg:grid-cols-4">
        <InspectorField label="Engineering ID" value={String(node.metadata.engineering_id ?? node.id)} />
        <InspectorField label="Component Class" value={node.component_class.replaceAll('_', ' ')} />
        <InspectorField label="Category" value={category} />
        <InspectorField label="Status" value={status} accent={status === 'RUNNING' ? 'text-emerald-400' : status === 'INTERLOCKED' ? 'text-red-400' : 'text-gray-300'} />
        <InspectorField label="Actual Throughput" value={`${telemetry?.throughput_tph ?? 0} t/h`} />
        <InspectorField label="Power Draw" value={`${telemetry?.power_mw ?? 0} MW`} accent="text-amber-400" />
        <InspectorField label="Water Flow" value={`${telemetry?.water_m3h ?? 0} m³/h`} accent="text-cyan-400" />
        <InspectorField label="Temperature" value={`${telemetry?.temperature_c ?? 25} °C`} />
      </div>
      <div className="flex flex-wrap gap-2 p-4">
        {node.ports.map(port => <span key={port.id} className="rounded border border-industrial-600 bg-industrial-900 px-2 py-1 font-mono text-[9px] text-gray-400"><b className="text-gray-200">{port.direction}</b> {port.id} <span className={port.type === 'MATERIAL' ? 'text-blue-400' : port.type === 'ELECTRICAL' ? 'text-amber-400' : port.type === 'WATER' ? 'text-cyan-400' : 'text-purple-400'}>{port.type}</span></span>)}
      </div>
    </section>
  );
}

function InspectorField({ label, value, accent = 'text-gray-200' }: { label: string; value: string; accent?: string }) {
  return <div className="bg-industrial-800/90 p-3"><div className="text-[9px] font-bold uppercase tracking-wider text-gray-600">{label}</div><div className={`mt-1 font-mono text-xs ${accent}`}>{value}</div></div>;
}

function OptimizationView({ onOpenBuilder }: { onOpenBuilder: () => void }) {
  return (
    <main className="flex h-full w-full items-center justify-center overflow-y-auto p-6" aria-label="Plant optimization">
      <section className="w-full max-w-2xl rounded-xl border border-industrial-700 bg-industrial-800/80 p-8 text-center shadow-2xl">
        <Cpu className="mx-auto h-11 w-11 text-indigo-400" />
        <div className="mt-4 text-[10px] font-bold uppercase tracking-[0.2em] text-indigo-400">Planned Module</div>
        <h1 className="mt-2 text-2xl font-bold text-white">Plant Optimization</h1>
        <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-gray-400">Optimization is reserved for the ACAMIS agent layer. It will compare operating scenarios and recommend parameter changes without pretending unfinished controls are active today.</p>
        <div className="mt-6 grid gap-3 text-left sm:grid-cols-3">
          {['Scenario comparison', 'Constraint-aware tuning', 'Auditable recommendations'].map(item => <div key={item} className="rounded border border-industrial-700 bg-industrial-900/60 p-3 text-xs text-gray-400">{item}</div>)}
        </div>
        <button type="button" onClick={onOpenBuilder} className="mt-7 rounded bg-blue-600 px-5 py-2 text-xs font-bold text-white hover:bg-blue-500">Return to Plant Builder</button>
      </section>
    </main>
  );
}

function NavItem({ icon, label, active, onClick, disabled, collapsed }: { icon: React.ReactNode, label: string, active?: boolean, onClick?: () => void, disabled?: boolean, collapsed?: boolean }) {
  return (
    <button type="button" disabled={disabled} onClick={onClick} aria-label={label} className={`w-full flex items-center px-4 py-3 transition-colors text-left ${
      active ? 'bg-blue-600/10 border-l-2 border-blue-500 text-white cursor-pointer' : 
      disabled ? 'opacity-30 cursor-not-allowed text-gray-500' : 
      'border-l-2 border-transparent text-gray-400 hover:bg-industrial-700 hover:text-gray-200 cursor-pointer'
    }`} title={disabled ? `${label} is a planned module` : collapsed ? label : undefined}>
      <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
        {icon}
      </div>
      <span className={`ml-3 font-medium text-sm whitespace-nowrap ${collapsed ? 'hidden md:hidden' : 'hidden md:inline'}`}>{label}</span>
      {disabled && !collapsed && <span className="hidden md:inline ml-auto text-[9px] bg-industrial-700 px-1.5 py-0.5 rounded uppercase tracking-widest font-bold">Future</span>}
    </button>
  );
}

export default App;
