import React, { useState, useEffect, useRef } from 'react';
import { LayoutDashboard, Factory, Activity, Truck, Wrench, Shield, Zap, Cpu, Play, Pause, RotateCcw } from 'lucide-react';
import { Blueprint } from './components/PlantBuilder/Blueprint';

type ViewMode = 'OVERVIEW' | 'BUILDER' | 'SIMULATION' | 'OPTIMIZATION';

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('BUILDER');
  const [isFocusMode, setIsFocusMode] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [topologyValidation, setTopologyValidation] = useState<any>(null);
  const [activeSimId, setActiveSimId] = useState<string | null>(null);
  const [simState, setSimState] = useState<any>(null);
  const [backendConnected, setBackendConnected] = useState(true);
  
  const [snapshot, setSnapshot] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const eventsEndRef = useRef<HTMLTableRowElement>(null);

  useEffect(() => {
    fetch('/api/health')
      .then(res => setBackendConnected(res.ok))
      .catch(() => setBackendConnected(false));
  }, []);

  useEffect(() => {
    if (!activeSimId) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/simulations/${activeSimId}`);
        if (res.ok) {
          const data = await res.json();
          setSnapshot(data);
          if (data.events && data.events.length > events.length) {
              setEvents(data.events);
          }
        }
      } catch (e) {
        console.error(e);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [activeSimId, events.length]);

  useEffect(() => {
      eventsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const handleCreate = async () => {
    if (!topologyValidation?.is_valid) {
      alert("Cannot start simulation. Plant topology has fatal errors.");
      return;
    }
    const graphStr = localStorage.getItem('steelsim_plant');
    if (!graphStr) return;
    
    try {
      const graph = JSON.parse(graphStr);
      const res = await fetch('/api/simulations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plant_graph: graph })
      });
      if (res.ok) {
        const data = await res.json();
        setActiveSimId(data.id);
        setSimState(data);
        setViewMode('SIMULATION');
      }
    } catch(e) {
      console.error(e);
    }
  };

  const handleCommand = async (command: string) => {
    if (!activeSimId) return;
    const res = await fetch(`/api/simulations/${activeSimId}/command`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, payload: {} })
    });
    if (res.ok) {
        const state = await res.json();
        setSimState(state);
    }
  };

  const handleSpeed = async (speed: string) => {
    if (!activeSimId) return;
    const res = await fetch(`/api/simulations/${activeSimId}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'set_speed', payload: { speed } })
    });
    if (res.ok) {
        const state = await res.json();
        setSimState(state);
        setSnapshot(null);
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
        
        {/* TOP BAR */}
        {!isFocusMode && (
        <div className="h-14 border-b border-industrial-700 bg-industrial-800 flex items-center justify-between px-6 z-0 flex-shrink-0">
          <div className="flex items-center space-x-4">
            <h1 className="text-lg font-semibold text-white">
              {viewMode === 'BUILDER' ? 'Interactive Plant Builder' : 
               viewMode === 'SIMULATION' ? 'Simulation Console' : viewMode === 'OPTIMIZATION' ? 'AI Optimization & Setup' : 'Overview'}
            </h1>
          </div>
          <div className="flex items-center space-x-4 text-sm">
            {viewMode === 'BUILDER' && (
                <button onClick={handleCreate}  className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm font-semibold transition-colors disabled:opacity-30 disabled:hover:bg-blue-600 shadow-[0_0_12px_rgba(37,99,235,0.2)]">
                  Simulate Plant Topology
                </button>
            )}
            {viewMode === 'SIMULATION' && !activeSimId && (
              <button onClick={() => setViewMode('BUILDER')} className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm font-semibold transition-colors">
                Back to Builder
              </button>
            )}
            <div className="flex items-center space-x-2">
               <span className={`w-2 h-2 rounded-full ${backendConnected ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 animate-pulse'}`}></span>
               <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                 {backendConnected ? 'API Connected' : 'Connection Lost'}
               </span>
            </div>
          </div>
        </div>
        )}

        {/* CONTENT AREA */}
        <div className="flex-1 overflow-hidden relative bg-[#121315]">
          
          {/* BUILDER VIEW */}
          {viewMode === 'BUILDER' && (
            <div className="absolute inset-0 flex flex-col">
              <Blueprint 
                  setValidation={setTopologyValidation} 
                  isFocusMode={isFocusMode} 
                  setIsFocusMode={setIsFocusMode} 
              />
            </div>
          )}

          {/* SIMULATION VIEW */}
          {viewMode === 'SIMULATION' && (
            <div className="absolute inset-0 flex flex-col p-6 space-y-6 overflow-y-auto">
              
              {/* TOP PANELS */}
              <div className="flex gap-6 h-28">
                
                {/* HUD */}
                <div className="flex-1 bg-industrial-800 border border-industrial-700 rounded-md flex items-center px-8 justify-between shadow-lg">
                  <div className="flex items-center gap-12">
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Plant Status</div>
                      <div className="flex items-center gap-2">
                        <span className={`w-3 h-3 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)] ${
                          currentStatus === 'READY' ? 'bg-blue-500' : 
                          currentStatus === 'RUNNING' ? 'bg-green-500' : 
                          currentStatus === 'PAUSED' ? 'bg-amber-500' : 'bg-red-500'
                        }`}></span>
                        <span className="font-bold tracking-wider text-white">{currentStatus}</span>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Sim Time</div>
                      <div className="font-mono text-lg text-blue-400">
                        {(snapshot?.simulation_time || simState?.current_time) ? (snapshot?.simulation_time || simState?.current_time)?.replace('T', ' ').substring(0, 19) : '0000-00-00 00:00:00'}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Tick</div>
                      <div className="font-mono text-lg text-gray-300">
                        {snapshot?.tick ?? simState?.tick ?? 0}
                      </div>
                    </div>
                  </div>

                  {/* CONTROLS */}
                  <div className="flex items-center gap-4">
                    <div className="flex bg-industrial-900 rounded border border-industrial-700 p-1">
                      {['1x', '5x', '10x', '60x', 'MAX'].map(spd => (
                        <button
                          key={spd}
                          onClick={() => handleSpeed(spd)}
                          disabled={!activeSimId}
                          className={`px-3 py-1 text-xs font-bold rounded transition-colors ${currentSpeed === spd ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white disabled:opacity-50 disabled:hover:text-gray-400'}`}
                        >
                          {spd}
                        </button>
                      ))}
                    </div>

                    <div className="h-8 w-px bg-industrial-700 mx-2"></div>

                    <div className="flex gap-2">
                      <button 
                        onClick={() => handleCommand(currentStatus === 'READY' ? 'start' : 'resume')}
                        disabled={!activeSimId || currentStatus === 'RUNNING'}
                        className="flex items-center justify-center w-10 h-10 bg-green-600/20 text-green-500 border border-green-600/50 rounded hover:bg-green-600 hover:text-white disabled:opacity-30 disabled:hover:bg-green-600/20 disabled:hover:text-green-500 transition-colors"
                        title="Run"
                      >
                        <Play className="w-5 h-5 fill-current" />
                      </button>
                      <button 
                        onClick={() => handleCommand('pause')}
                        disabled={!activeSimId || currentStatus !== 'RUNNING'}
                        className="flex items-center justify-center w-10 h-10 bg-amber-500/20 text-amber-500 border border-amber-500/50 rounded hover:bg-amber-500 hover:text-white disabled:opacity-30 disabled:hover:bg-amber-500/20 disabled:hover:text-amber-500 transition-colors"
                        title="Pause"
                      >
                        <Pause className="w-5 h-5 fill-current" />
                      </button>
                      <button 
                        onClick={() => handleCommand('reset')}
                        disabled={!activeSimId}
                        className="flex items-center justify-center w-10 h-10 bg-red-500/10 text-red-400 border border-red-500/30 rounded hover:bg-red-500 hover:text-white disabled:opacity-30 transition-colors"
                        title="Reset"
                      >
                        <RotateCcw className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* EVENT CONSOLE */}
              <div className="flex-1 bg-industrial-800 border border-industrial-700 rounded-md flex flex-col overflow-hidden min-h-[300px] shadow-lg">
                <div className="h-10 bg-industrial-700/50 border-b border-industrial-700 flex items-center px-4">
                  <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Event Console</span>
                </div>
                <div className="flex-1 overflow-auto bg-[#121315] p-0">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead className="sticky top-0 bg-industrial-800 shadow text-gray-400 text-[10px] uppercase tracking-widest z-10">
                      <tr>
                        <th className="px-4 py-2 font-semibold border-b border-industrial-700 w-48">Time</th>
                        <th className="px-4 py-2 font-semibold border-b border-industrial-700 w-24">Severity</th>
                        <th className="px-4 py-2 font-semibold border-b border-industrial-700 w-48">Source</th>
                        <th className="px-4 py-2 font-semibold border-b border-industrial-700">Message</th>
                      </tr>
                    </thead>
                    <tbody className="font-mono text-[11px]">
                      {events.length === 0 ? (
                        <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-600">No events recorded.</td></tr>
                      ) : (
                        events.map((evt, i) => (
                          <tr key={i} className="border-b border-industrial-800/50 hover:bg-industrial-800/80 transition-colors">
                            <td className="px-4 py-2 text-gray-400 whitespace-nowrap">{evt.simulation_time.replace('T', ' ')}</td>
                            <td className="px-4 py-2">
                              <span className={`px-2 py-0.5 rounded text-[9px] font-bold tracking-wider ${
                                evt.severity === 'INFO' ? 'bg-blue-900/50 text-blue-400' :
                                evt.severity === 'WARNING' ? 'bg-amber-900/50 text-amber-400' :
                                evt.severity === 'CRITICAL' ? 'bg-red-900/50 text-red-400' : 'bg-gray-700 text-gray-300'
                              }`}>
                                {evt.severity}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-gray-300 whitespace-nowrap">{evt.source}</td>
                            <td className="px-4 py-2 text-gray-300">{evt.message}</td>
                          </tr>
                        ))
                      )}
                      <tr ref={eventsEndRef} />
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

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
