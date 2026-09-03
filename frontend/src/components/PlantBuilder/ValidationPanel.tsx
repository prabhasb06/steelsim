import { useState } from 'react';
import type { ValidationResult, ValidationIssue } from '../../types/topology';
import { AlertTriangle, XCircle, CheckCircle, Info, ChevronUp, ChevronDown, Terminal } from 'lucide-react';
import { useNodes } from '@xyflow/react';
import type { SimulationEvent } from '../../types';
import type { SimulationStatus } from '../../types';

export const ValidationPanel = ({ 
    validation, 
    onSelectNode,
    isOpen,
    setIsOpen,
    simulationStatus,
    events = []
}: { 
    validation: ValidationResult | null, 
    onSelectNode?: (nodeId: string) => void,
    isOpen: boolean,
    setIsOpen: (open: boolean) => void,
    simulationStatus?: SimulationStatus,
    events?: SimulationEvent[]
}) => {
    const nodes = useNodes();
    const [activeTab, setActiveTab] = useState<'ISSUES' | 'EVENTS'>('ISSUES');
    
    const errors = validation?.issues.filter(i => i.level === 'ERROR') || [];
    const warnings = validation?.issues.filter(i => i.level === 'WARNING') || [];
    
    
    // Config validation
    const unconfiguredNodes = nodes.filter((n: any) => !n.data.parameters || Object.keys(n.data.parameters).length === 0).length;
    
    const topologyStatus = validation?.is_valid 
        ? (warnings.length > 0 ? 'VALID WITH WARNINGS' : 'VALID') 
        : (validation ? 'INVALID' : 'NO TOPOLOGY');
        
    const topologyColor = validation?.is_valid 
        ? (warnings.length > 0 ? 'text-amber-500' : 'text-green-500') 
        : (validation ? 'text-red-500' : 'text-gray-500');

    const configStatus = unconfiguredNodes > 0 ? `${unconfiguredNodes} INCOMPLETE` : 'COMPLETE';
    const configColor = unconfiguredNodes > 0 ? 'text-amber-500' : 'text-green-500';
    const simulationLabel = simulationStatus ?? (validation?.is_valid && unconfiguredNodes === 0 ? 'READY' : 'NOT READY');
    const simulationReady = simulationStatus === 'RUNNING' || simulationStatus === 'PAUSED' || (validation?.is_valid && unconfiguredNodes === 0);

    const renderIssue = (issue: ValidationIssue, idx: number) => {
        const bg = issue.level === 'ERROR' ? 'bg-red-900/10 border-red-900/40 hover:border-red-900/80' :
                   issue.level === 'WARNING' ? 'bg-amber-900/10 border-amber-900/40 hover:border-amber-900/80' :
                   'bg-blue-900/10 border-blue-900/40 hover:border-blue-900/80';
                   
        const textClass = issue.level === 'ERROR' ? 'text-red-300' :
                          issue.level === 'WARNING' ? 'text-amber-300' : 'text-blue-300';
                          
        const Icon = issue.level === 'ERROR' ? XCircle :
                     issue.level === 'WARNING' ? AlertTriangle : Info;

        return (
            <li 
                key={idx} 
                onClick={() => {
                    if (issue.node_id && onSelectNode) onSelectNode(issue.node_id);
                }}
                className={`p-1.5 rounded border cursor-pointer transition-colors ${bg} ${textClass} text-[10px]`}
            >
                <div className="flex items-start">
                    <Icon className="w-3 h-3 mr-1.5 flex-shrink-0 mt-0.5 opacity-80" />
                    <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                            <span className="font-bold tracking-wider truncate">{issue.issue_code}</span>
                            {issue.node_id && (
                                <span className="flex items-center text-[9px] font-mono ml-2">
                                    [{issue.node_id}]
                                </span>
                            )}
                        </div>
                        <div className="text-gray-200 mt-0.5 truncate">{issue.message}</div>
                        {issue.engineering_reason && (
                            <div className="opacity-70 truncate">
                                {issue.engineering_reason}
                            </div>
                        )}
                    </div>
                </div>
            </li>
        );
    };

    return (
        <div className={`bg-industrial-800 border-t border-industrial-700 flex flex-col shadow-[0_-4px_12px_rgba(0,0,0,0.3)] transition-all duration-300 ${isOpen ? 'h-[30vh] max-h-[45vh]' : 'h-8'} flex-shrink-0 z-20`}>
            {/* COLLAPSED BAR / HEADER */}
            <div 
                className="h-8 border-b border-industrial-700 flex items-center px-4 justify-between bg-industrial-900 cursor-pointer hover:bg-industrial-800 transition-colors"
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="flex items-center divide-x divide-industrial-700">
                    <div className="flex items-center pr-4">
                        <div className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mr-3">Topology</div>
                        <div className={`text-[9px] font-semibold px-1.5 py-0.5 rounded border ${topologyColor} ${validation?.is_valid ? (warnings.length > 0 ? 'bg-amber-900/20 border-amber-900/50' : 'bg-green-900/20 border-green-900/50') : (validation ? 'bg-red-900/20 border-red-900/50' : 'bg-gray-800 border-gray-700')}`}>
                            {topologyStatus}
                        </div>
                    </div>
                    
                    <div className="flex items-center pl-4 pr-4">
                        <div className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mr-3">Config</div>
                        <div className={`text-[9px] font-semibold px-1.5 py-0.5 rounded border ${configColor} ${unconfiguredNodes > 0 ? 'bg-amber-900/20 border-amber-900/50' : 'bg-green-900/20 border-green-900/50'}`}>
                            {configStatus}
                        </div>
                    </div>
                    
                    <div className="flex items-center pl-4 hidden md:flex">
                        <div className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mr-3">Simulation</div>
                        <div className={`text-[9px] font-semibold px-1.5 py-0.5 rounded border ${simulationReady ? 'bg-blue-900/20 border-blue-900/50 text-blue-400' : 'bg-gray-800 border-gray-700 text-gray-500'}`}>
                            {simulationLabel}
                        </div>
                    </div>
                </div>

                <div className="flex gap-4 text-[10px] font-semibold tracking-wider items-center">
                    {errors.length > 0 && <span className="text-red-400">{errors.length} ERRORS</span>}
                    {warnings.length > 0 && <span className="text-amber-400">{warnings.length} WARNINGS</span>}
                    
                    <div className="text-gray-500 ml-2">
                        {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                    </div>
                </div>
            </div>
            
            {/* EXPANDED CONTENT */}
            {isOpen && (
                <div className="flex-1 overflow-hidden flex flex-col bg-industrial-900">
                    {/* SUB TABS */}
                    <div className="flex border-b border-industrial-700 bg-industrial-800/80 px-3">
                        <button
                            onClick={(e) => { e.stopPropagation(); setActiveTab('ISSUES'); }}
                            className={`px-3 py-1.5 text-xs font-semibold border-b-2 transition-colors ${activeTab === 'ISSUES' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}`}
                        >
                            Topology Issues {errors.length > 0 ? `(${errors.length})` : ''}
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); setActiveTab('EVENTS'); }}
                            className={`px-3 py-1.5 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5 ${activeTab === 'EVENTS' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}`}
                        >
                            <Terminal className="w-3 h-3" /> Event Console {events.length > 0 ? `(${events.length})` : ''}
                        </button>
                    </div>

                    {activeTab === 'ISSUES' ? (
                        <div className="flex-1 overflow-y-auto p-3">
                            {!validation || validation.issues.length === 0 ? (
                                <div className="flex flex-col items-center justify-center h-full text-green-500/70">
                                    <CheckCircle className="w-6 h-6 mb-2 opacity-50" />
                                    <div className="text-xs font-medium">No topology issues detected.</div>
                                </div>
                            ) : (
                                <div className="flex gap-4">
                                    {/* Errors Column */}
                                    {errors.length > 0 && (
                                        <div className="flex-1 min-w-0">
                                            <div className="text-[9px] font-semibold uppercase tracking-widest text-red-500/70 mb-1.5 pl-1">Critical Errors</div>
                                            <ul className="space-y-1.5">
                                                {errors.map((iss, i) => renderIssue(iss, i))}
                                            </ul>
                                        </div>
                                    )}
                                    
                                    {/* Warnings Column */}
                                    {warnings.length > 0 && (
                                        <div className="flex-1 min-w-0">
                                            <div className="text-[9px] font-semibold uppercase tracking-widest text-amber-500/70 mb-1.5 pl-1">Warnings</div>
                                            <ul className="space-y-1.5">
                                                {warnings.map((iss, i) => renderIssue(iss, i))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex-1 overflow-y-auto p-2 font-mono text-[11px]">
                            {events.length === 0 ? (
                                <div className="p-4 text-center text-gray-500">No simulation events recorded yet. Click Run ▶ to start.</div>
                            ) : (
                                <table className="w-full text-left border-collapse">
                                    <thead className="sticky top-0 bg-industrial-800 text-[9px] uppercase tracking-wider text-gray-400">
                                        <tr>
                                            <th className="p-1.5 w-40">Time</th>
                                            <th className="p-1.5 w-20">Severity</th>
                                            <th className="p-1.5 w-36">Source</th>
                                            <th className="p-1.5">Message</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {events.slice().reverse().map((evt, i) => (
                                            <tr key={i} className="border-b border-industrial-800/60 hover:bg-industrial-800/40">
                                                <td className="p-1.5 text-gray-400">{evt.simulation_time ? evt.simulation_time.replace('T', ' ').substring(0, 19) : '—'}</td>
                                                <td className="p-1.5">
                                                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                                                        evt.severity === 'CRITICAL' ? 'bg-red-900/50 text-red-400' :
                                                        evt.severity === 'WARNING' ? 'bg-amber-900/50 text-amber-400' :
                                                        'bg-blue-900/50 text-blue-400'
                                                    }`}>
                                                        {evt.severity}
                                                    </span>
                                                </td>
                                                <td className="p-1.5 text-gray-300">{evt.source}</td>
                                                <td className="p-1.5 text-gray-200">{evt.message}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
