import React, { useState, useEffect, useRef } from 'react';
import { LayoutDashboard, Factory, Activity, Truck, Wrench, Shield, Zap, Cpu, Play, Pause, RotateCcw } from 'lucide-react';
import { Blueprint } from './components/PlantBuilder/Blueprint';
import { simulationApi } from './api';
import type { SimulationCommand, SimulationEvent, SimulationSnapshot, SimulationState } from './types';
import type { PlantGraph } from './types/topology';

type ViewMode = 'OVERVIEW' | 'BUILDER' | 'SIMULATION' | 'OPTIMIZATION';

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('BUILDER');
  const [isFocusMode, setIsFocusMode] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeSimId, setActiveSimId] = useState<string | null>(null);
  const [simState, setSimState] = useState<SimulationState | null>(null);
  const [backendConnected, setBackendConnected] = useState(true);
  const [currentGraph, setCurrentGraph] = useState<PlantGraph | null>(null);
  const [snapshot, setSnapshot] = useState<SimulationSnapshot | null>(null);
  const [events, setEvents] = useState<SimulationEvent[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const simulatedGraphRef = useRef<string | null>(null);

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
    if (!activeSimId) return;
    let mounted = true;
    const pollSnapshot = async () => {
      try {
        const data = await simulationApi.snapshot(activeSimId);
        if (mounted) {
          setSnapshot(data);
          setEvents(data.events);
          setBackendConnected(true);
        }
      } catch (error) {
        if (mounted) {
          setBackendConnected(false);
          setErrorMessage(error instanceof Error ? error.message : 'Unable to read simulation state.');
        }
      }
    };
    void pollSnapshot();
    const interval = window.setInterval(pollSnapshot, 1000);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, [activeSimId]);

  const applySnapshot = (next: SimulationSnapshot) => {
    setSnapshot(next);
    setEvents(next.events);
    setBackendConnected(true);
  };

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
      if (!validation.is_valid) {
        const blocking = validation.issues.filter(issue => issue.blocks_simulation).length;
        throw new Error(`Simulation blocked: resolve ${blocking || validation.issues.length} topology issue${blocking === 1 ? '' : 's'} first.`);
      }

      const graphSignature = JSON.stringify(graph);
      const graphChanged = simulatedGraphRef.current !== graphSignature;
      let simulationId = activeSimId;
      if (!simulationId || graphChanged) {
        const created = await simulationApi.create(graph);
        simulationId = created.id;
        simulatedGraphRef.current = graphSignature;
        setActiveSimId(created.id);
        setSimState(created);
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
    try {
      applySnapshot(await simulationApi.command(activeSimId, 'set_speed', { speed }));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Unable to change simulation speed.');
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
          
          <div className={`mt-8 mb-2 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider hidden md:block whitespace-nowrap ${sidebarCollapsed ? 'md:hidden' : ''}`}>Future Modules</div>
          <NavItem icon={<Cpu />} label="Optimize Plant" active={viewMode==='OPTIMIZATION'} onClick={() => setViewMode('OPTIMIZATION')} collapsed={sidebarCollapsed} />
          <NavItem icon={<Zap />} label="Energy Model" disabled collapsed={sidebarCollapsed} />
          <NavItem icon={<Wrench />} label="Maintenance" disabled collapsed={sidebarCollapsed} />
          <NavItem icon={<Shield />} label="Safety limits" disabled collapsed={sidebarCollapsed} />
          <NavItem icon={<Truck />} label="Logistics" disabled collapsed={sidebarCollapsed} />
        </div>
      </div>
      )}

      {/* MAIN WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* TOP BAR: MASTER SIMULATION CONTROLS & KPI DECK */}
        {!isFocusMode && (
        <div className="h-14 border-b border-industrial-700 bg-industrial-800 flex items-center justify-between px-4 z-10 flex-shrink-0">
          {/* Left: Brand & Plant Title */}
          <div className="flex items-center space-x-3">
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
          <div className="flex items-center gap-3">
            {/* Run / Pause / Reset Buttons */}
            <div className="flex items-center gap-1.5 bg-industrial-900/80 p-1 rounded-md border border-industrial-700">
              <button 
                onClick={handleStart}
                disabled={currentStatus === 'RUNNING' || isBusy}
                className="flex items-center gap-1.5 px-3 py-1 bg-emerald-600/20 text-emerald-400 border border-emerald-600/50 rounded hover:bg-emerald-600 hover:text-white disabled:opacity-30 disabled:hover:bg-emerald-600/20 disabled:hover:text-emerald-400 transition-colors text-xs font-bold"
                title="Run Simulation"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run</span>
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

        {/* CONTENT AREA: UNIFIED CANVAS */}
        <div className="flex-1 overflow-hidden relative bg-[#121315]">
          {errorMessage && (
            <div role="alert" className="absolute top-3 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 max-w-xl rounded border border-red-700/70 bg-red-950/95 px-4 py-2 text-xs text-red-100 shadow-xl">
              <span>{errorMessage}</span>
              <button onClick={() => setErrorMessage(null)} className="text-red-300 hover:text-white font-bold" aria-label="Dismiss error">×</button>
            </div>
          )}
          <div className="absolute inset-0 flex flex-col">
            <Blueprint 
                isFocusMode={isFocusMode} 
                setIsFocusMode={setIsFocusMode}
                activeSimId={activeSimId}
                simState={simState}
                snapshot={snapshot}
                events={events}
                onGraphChange={setCurrentGraph}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function NavItem({ icon, label, active, onClick, disabled, collapsed }: { icon: React.ReactNode, label: string, active?: boolean, onClick?: () => void, disabled?: boolean, collapsed?: boolean }) {
  return (
    <div onClick={disabled ? undefined : onClick} className={`flex items-center px-4 py-3 transition-colors ${
      active ? 'bg-blue-600/10 border-l-2 border-blue-500 text-white cursor-pointer' : 
      disabled ? 'opacity-30 cursor-not-allowed text-gray-500' : 
      'border-l-2 border-transparent text-gray-400 hover:bg-industrial-700 hover:text-gray-200 cursor-pointer'
    }`} title={collapsed ? label : undefined}>
      <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
        {icon}
      </div>
      <span className={`ml-3 font-medium text-sm whitespace-nowrap ${collapsed ? 'hidden md:hidden' : 'hidden md:inline'}`}>{label}</span>
      {disabled && !collapsed && <span className="hidden md:inline ml-auto text-[9px] bg-industrial-700 px-1.5 py-0.5 rounded uppercase tracking-widest font-bold">Future</span>}
    </div>
  );
}

export default App;
