import React, { useState, useRef, useCallback, useEffect, useEffectEvent } from 'react';
import { 
  ReactFlow, 
  Background, 
  useNodesState, 
  useEdgesState, 
  addEdge, reconnectEdge, 
  type Connection, 
  type Edge, 
  MarkerType,
  useReactFlow,
  ReactFlowProvider,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import type { PlantGraph, PortDef, ValidationResult } from '../../types/topology';
import type { SimulationEvent, SimulationSnapshot, SimulationState } from '../../types';
import { CustomNode } from './CustomNode';
import { Undo2, Redo2, Save, FolderOpen, Wand2, Network, LayoutTemplate, RotateCcw, Crosshair, ZoomIn, ZoomOut, Maximize2, X, CheckSquare, Layers, Settings2, AlertTriangle, Focus } from 'lucide-react';
import { Inspector } from './Inspector';
import { ValidationPanel } from './ValidationPanel';
import { ContextMenu } from './ContextMenu';
import { ComponentLibrary } from './ComponentLibrary';
import { ErrorBoundary } from './ErrorBoundary';

const nodeTypes = {
  equipment: CustomNode,
};

interface BlueprintCanvasProps {
    isFocusMode: boolean;
    setIsFocusMode: (f: boolean) => void;
    isActive?: boolean;
    activeSimId?: string | null;
    simState?: SimulationState | null;
    snapshot?: SimulationSnapshot | null;
    events?: SimulationEvent[];
    onGraphChange?: (graph: PlantGraph) => void;
    onValidationChange?: (validation: ValidationResult | null) => void;
}

const BlueprintCanvas = ({ 
    isFocusMode, 
    setIsFocusMode,
    isActive = true,
    simState,
    snapshot,
    events = [],
    onGraphChange,
    onValidationChange
}: BlueprintCanvasProps) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const { screenToFlowPosition, fitView, zoomIn, zoomOut, zoomTo, getViewport } = useReactFlow();
  
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<string | null>(null);
  const [currentValidation, setCurrentValidation] = useState<ValidationResult | null>(null);
  
  
  // UI Panel States
  const [libraryOpen, setLibraryOpen] = useState(true);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [issuesOpen, setIssuesOpen] = useState(true);

  // History for Undo/Redo
  const [history, setHistory] = useState<{nodes: any[], edges: Edge[]}[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [clipboard, setClipboard] = useState<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] });
  const [contextMenu, setContextMenu] = useState<{ x: number, y: number, nodeId?: string } | null>(null);

  const updateFocusMode = useCallback((focus: boolean) => {
    if (focus) {
      setLibraryOpen(false);
      setInspectorOpen(false);
      setIssuesOpen(false);
    }
    setIsFocusMode(focus);
  }, [setIsFocusMode]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
        if (!isActive) return;
        if (e.key === 'Escape' && isFocusMode) {
            updateFocusMode(false);
        }
        if (e.key === 'f' && e.target === document.body) {
            updateFocusMode(!isFocusMode);
        }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isActive, isFocusMode, updateFocusMode]);




  const getGraph = (n = nodes, e = edges): PlantGraph => ({
      nodes: n.map((node: any) => ({
          id: node.id,
          component_class: node.data.component_class,
          name: node.data.name,
          position: node.position,
          ports: node.data.ports as PortDef[],
          parameters: node.data.parameters,
          metadata: {}
      })),
      edges: e.map((edge: Edge) => ({
          id: edge.id,
          source_node: edge.source,
          source_port: edge.sourceHandle || "",
          target_node: edge.target,
          target_port: edge.targetHandle || "",
          connection_type: (edge.data?.connection_type || "MATERIAL") as PlantGraph['edges'][number]['connection_type']
      }))
  });

  // Notify parent of graph changes
  useEffect(() => {
    if (onGraphChange) {
      onGraphChange(getGraph(nodes, edges));
    }
  }, [nodes, edges, onGraphChange]);

  const saveHistory = (n: any[], e: Edge[]) => {
      const newHistory = history.slice(0, historyIndex + 1);
      newHistory.push({ nodes: JSON.parse(JSON.stringify(n)), edges: JSON.parse(JSON.stringify(e)) });
      setHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
  };

  const handleUndo = () => {
      if (historyIndex > 0) {
          const prev = history[historyIndex - 1];
          setNodes(prev.nodes);
          setEdges(prev.edges);
          setHistoryIndex(historyIndex - 1);
          setTimeout(() => validateGraph(prev.nodes, prev.edges), 50);
      }
  };

  const handleRedo = () => {
      if (historyIndex < history.length - 1) {
          const next = history[historyIndex + 1];
          setNodes(next.nodes);
          setEdges(next.edges);
          setHistoryIndex(historyIndex + 1);
          setTimeout(() => validateGraph(next.nodes, next.edges), 50);
      }
  };

  const validateGraph = async (n = nodes, e = edges) => {
      if (n.length === 0) {
          setCurrentValidation(null);
          onValidationChange?.(null);
          return;
      }
      const graph = getGraph(n, e);
      try {
          const res = await fetch('/api/plant/validate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(graph)
          });
          const v: ValidationResult = await res.json();
          setCurrentValidation(v);
          onValidationChange?.(v);
          
          setNodes((nds) => nds.map((n) => {
              const issues = v.issues.filter(i => i.node_id === n.id);
              const hasError = issues.some(i => i.level === 'ERROR');
              const hasWarning = issues.some(i => i.level === 'WARNING');
              return { ...n, data: { ...n.data, validationStatus: hasError ? 'ERROR' : hasWarning ? 'WARNING' : 'VALID' } };
          }));
          
          // Auto expand issues drawer if fatal error
          if (!v.is_valid && !isFocusMode) {
              setIssuesOpen(true);
          } else if (v.is_valid) {
              setIssuesOpen(false);
          }
      } catch(e) {
          console.error(e);
      }
  };

  
  const onReconnect = (oldEdge: Edge, newConnection: Connection) => {
      setEdges((els) => {
          const updated = reconnectEdge(oldEdge, newConnection, els);
          setTimeout(() => { saveHistory(nodes, updated); validateGraph(nodes, updated); }, 50);
          return updated;
      });
  };

  const onConnect = (params: Connection) => {
      const sourceNode = nodes.find((n: any) => n.id === params.source);
      const targetNode = nodes.find((n: any) => n.id === params.target);
      let pTypeSource = 'MATERIAL';
      let pTypeTarget = 'MATERIAL';
      
      if (sourceNode) {
          const pt = sourceNode.data.ports.find((p: any) => p.id === params.sourceHandle);
          if (pt) pTypeSource = pt.type;
      }
      if (targetNode) {
          const pt = targetNode.data.ports.find((p: any) => p.id === params.targetHandle);
          if (pt) pTypeTarget = pt.type;
      }
      
      if (pTypeSource !== pTypeTarget) {
          alert(`CONNECTION REJECTED

Cannot connect ${pTypeSource} out to ${pTypeTarget} in.`);
          return;
      }
      
      const pType = pTypeSource;
      
      const colorMap: Record<string, string> = {
          'MATERIAL': '#3b82f6',
          'ELECTRICAL': '#eab308',
          'WATER': '#06b6d4',
          'SIGNAL': '#a855f7'
      };
      
      const newEdge = { 
          ...params, 
          data: { connection_type: pType },
          style: { stroke: colorMap[pType] || '#3b82f6', strokeWidth: 2 },
          type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: colorMap[pType] || '#3b82f6' }
      };
      setEdges((eds) => {
          const updated = addEdge(newEdge, eds);
          setTimeout(() => { saveHistory(nodes, updated); validateGraph(nodes, updated); }, 50);
          return updated;
      });
  };



  const generateEngineeringId = (c_class: string, currentNodes: any[]) => {
      const prefixes: Record<string, string> = {
          'RAW_MATERIAL_STORAGE': 'RS', 'BILLET_YARD': 'BY', 'CHARGING_TABLE': 'CT', 'REHEATING_FURNACE': 'RF',
          'ROUGHING_MILL': 'RM', 'INTERMEDIATE_MILL': 'IM', 'FINISHING_MILL': 'FM',
          'TMT_COOLING': 'TC', 'COOLING_BED': 'CB', 'CUTTING_UNIT': 'CU',
          'BUNDLING_UNIT': 'BU', 'FINISHED_GOODS': 'FG', 'TRANSFORMER': 'TR',
          'WATER_PUMP': 'WP', 'WATER_SYSTEM': 'WS', 'COMPRESSOR': 'CP',
          'MAINTENANCE_STATION': 'MS', 'QUALITY_INSPECTION': 'QI'
      };
      const prefix = prefixes[c_class] || 'EQ';
      
      let maxNum = 0;
      currentNodes.forEach(n => {
          if (n.data?.engineeringId?.startsWith(prefix + '-')) {
              const num = parseInt(n.data.engineeringId.split('-')[1]);
              if (!isNaN(num) && num > maxNum) maxNum = num;
          }
      });
      return `${prefix}-${(maxNum + 1).toString().padStart(2, '0')}`;
  };

  const addComponentToCanvas = async (c_class: string, position: { x: number, y: number }) => {
      const res = await fetch(`/api/plant/components/${c_class}`);
      if (res.ok) {
          const nodeData = await res.json();
          const newNode = {
            id: nodeData.id,
            type: 'equipment',
            position,
            
            data: { 
                component_class: nodeData.component_class,
                name: nodeData.name,
                engineeringId: generateEngineeringId(nodeData.component_class, nodes),
                ports: nodeData.ports,
                parameters: nodeData.parameters,
                validationStatus: 'VALID',
                locked: false
            },

          };
          setNodes((nds) => {
              const updated = nds.concat(newNode);
              setTimeout(() => { saveHistory(updated, edges); validateGraph(updated, edges); }, 50);
              return updated;
          });
      }
  };

  const onAddClick = (c_class: string) => {
      // get center of viewport
      const viewport = getViewport();
      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const x = reactFlowBounds ? (reactFlowBounds.width / 2 - viewport.x) / viewport.zoom : 400;
      const y = reactFlowBounds ? (reactFlowBounds.height / 2 - viewport.y) / viewport.zoom : 300;
      
      // slight jitter so multiple clicks don't perfectly overlap
      const jitterX = Math.random() * 40 - 20;
      const jitterY = Math.random() * 40 - 20;
      
      addComponentToCanvas(c_class, { x: x + jitterX, y: y + jitterY });
  };

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = async (event: React.DragEvent) => {
      event.preventDefault();
      const componentClass = event.dataTransfer.getData('application/reactflow');
      if (!componentClass) return;

      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      
      const res = await fetch(`/api/plant/components/${componentClass}`);
      if (res.ok) {
          const nodeData = await res.json();
          const newNode = {
            id: nodeData.id,
            type: 'equipment',
            position,
            
            data: { 
                component_class: nodeData.component_class,
                name: nodeData.name,
                engineeringId: generateEngineeringId(nodeData.component_class, nodes),
                ports: nodeData.ports,
                parameters: nodeData.parameters,
                validationStatus: 'VALID',
                locked: false
            },

          };
          setNodes((nds) => {
              const updated = nds.concat(newNode);
              setTimeout(() => { saveHistory(updated, edges); validateGraph(updated, edges); }, 50);
              return updated;
          });
      }
  };



  // ===================== EDITOR OPERATIONS ===================== //

  const handleDuplicate = () => {
      const selectedNodes = nodes.filter(n => n.selected);
      if (selectedNodes.length === 0) return;
      
      const newIdMap = new Map<string, string>();
      const newNodes = selectedNodes.map(original => {
          const newId = `node_${Math.random().toString(36).substr(2, 8)}`;
          newIdMap.set(original.id, newId);
          return {
              ...original,
              id: newId,
              selected: true,
              position: { x: original.position.x + 40, y: original.position.y + 40 },
              data: {
                  ...original.data,
                  // generateEngineeringId needs all nodes, we'll append to nds progressively below
              }
          };
      });
      
      const newEdges = edges.filter(e => newIdMap.has(e.source) && newIdMap.has(e.target)).map(e => ({
          ...e,
          id: `edge_${Math.random().toString(36).substr(2, 8)}`,
          source: newIdMap.get(e.source)!,
          target: newIdMap.get(e.target)!
      }));
      
      setNodes(nds => {
          let currentNds = nds.map(n => ({ ...n, selected: false }));
          newNodes.map(nn => {
              const engId = generateEngineeringId(nn.data.component_class, currentNds);
              const finalized = { ...nn, data: { ...nn.data, engineeringId: engId } };
              currentNds = currentNds.concat(finalized);
              return finalized;
          });
          
          setEdges(eds => {
              const updatedEdges = eds.concat(newEdges);
              setTimeout(() => { saveHistory(currentNds, updatedEdges); validateGraph(currentNds, updatedEdges); }, 50);
              return updatedEdges;
          });
          return currentNds;
      });
  };

  const handleCopy = () => {
      const selectedNodes = nodes.filter(n => n.selected);
      if (selectedNodes.length === 0) return;
      const selectedIds = new Set(selectedNodes.map(n => n.id));
      const internalEdges = edges.filter(e => selectedIds.has(e.source) && selectedIds.has(e.target));
      setClipboard({ 
          nodes: JSON.parse(JSON.stringify(selectedNodes)), 
          edges: JSON.parse(JSON.stringify(internalEdges)) 
      });
  };

  const handleCut = () => {
      handleCopy();
      const selectedIds = new Set(nodes.filter(n => n.selected).map(n => n.id));
      if (selectedIds.size === 0) return;
      
      setNodes(nds => {
          const updatedNodes = nds.filter(n => !selectedIds.has(n.id));
          setEdges(eds => {
              const updatedEdges = eds.filter(e => !selectedIds.has(e.source) && !selectedIds.has(e.target));
              setTimeout(() => { saveHistory(updatedNodes, updatedEdges); validateGraph(updatedNodes, updatedEdges); }, 50);
              return updatedEdges;
          });
          return updatedNodes;
      });
      setSelectedNodeId(null);
  };

  const handlePaste = () => {
      if (clipboard.nodes.length === 0) return;
      
      const newIdMap = new Map<string, string>();
      const newNodes = clipboard.nodes.map(original => {
          const newId = `node_${Math.random().toString(36).substr(2, 8)}`;
          newIdMap.set(original.id, newId);
          return {
              ...original,
              id: newId,
              selected: true,
              position: { x: original.position.x + 40, y: original.position.y + 40 }
          };
      });
      
      const newEdges = clipboard.edges.map(e => ({
          ...e,
          id: `edge_${Math.random().toString(36).substr(2, 8)}`,
          source: newIdMap.get(e.source)!,
          target: newIdMap.get(e.target)!
      }));
      
      setNodes(nds => {
          let currentNds = nds.map(n => ({ ...n, selected: false }));
          newNodes.map(nn => {
              const engId = generateEngineeringId(nn.data.component_class, currentNds);
              const finalized = { ...nn, data: { ...nn.data, engineeringId: engId } };
              currentNds = currentNds.concat(finalized);
              return finalized;
          });
          
          setEdges(eds => {
              const updatedEdges = eds.concat(newEdges);
              setTimeout(() => { saveHistory(currentNds, updatedEdges); validateGraph(currentNds, updatedEdges); }, 50);
              return updatedEdges;
          });
          return currentNds;
      });
  };

  
  const handleDeleteEdge = (edgeId: string | null) => {
      const toDelete = new Set<string>();
      if (edgeId) toDelete.add(edgeId);
      else edges.filter(e => e.selected).forEach(e => toDelete.add(e.id));
      if (toDelete.size === 0) return;
      const updatedEdges = edges.filter(e => !toDelete.has(e.id));
      setEdges(updatedEdges);
      setTimeout(() => { saveHistory(nodes, updatedEdges); validateGraph(nodes, updatedEdges); }, 50);
      if (edgeId === selectedEdge) setSelectedEdge(null);
  };

  const handleDeleteNode = (nodeId: string | null) => {
      // If nodeId provided (from context menu), delete just that one.
      // Else delete all selected.
      const toDelete = new Set<string>();
      if (nodeId) toDelete.add(nodeId);
      else nodes.filter(n => n.selected).forEach(n => toDelete.add(n.id));
      
      if (toDelete.size === 0) return;
      
      setNodes(nds => {
          const updatedNodes = nds.filter(n => !toDelete.has(n.id));
          setEdges(eds => {
              const updatedEdges = eds.filter(e => !toDelete.has(e.source) && !toDelete.has(e.target));
              setTimeout(() => { saveHistory(updatedNodes, updatedEdges); validateGraph(updatedNodes, updatedEdges); }, 50);
              return updatedEdges;
          });
          return updatedNodes;
      });
      if (nodeId === selectedNodeId) setSelectedNodeId(null);
      setSelectedEdge(null);
  };

  const handleToggleLock = () => {
      const selectedIds = new Set(nodes.filter(n => n.selected).map(n => n.id));
      if (selectedIds.size === 0) return;
      
      setNodes(nds => {
          const updated = nds.map(n => selectedIds.has(n.id) ? { ...n, data: { ...n.data, locked: !n.data.locked } } : n);
          setTimeout(() => { saveHistory(updated, edges); }, 50);
          return updated;
      });
  };

  const handleDisconnect = () => {
      const selectedIds = new Set(nodes.filter(n => n.selected).map(n => n.id));
      if (selectedIds.size === 0) return;
      
      setEdges(eds => {
          const updatedEdges = eds.filter(e => !selectedIds.has(e.source) && !selectedIds.has(e.target));
          setTimeout(() => { saveHistory(nodes, updatedEdges); validateGraph(nodes, updatedEdges); }, 50);
          return updatedEdges;
      });
  };

  const handleShowUpstream = () => {
      if (!selectedNodeId) return;
      // Very basic upstream highlight logic: select all source nodes that lead here
      const upstream = new Set<string>();
      const traverse = (nodeId: string) => {
          edges.filter(e => e.target === nodeId).forEach(e => {
              if (!upstream.has(e.source)) {
                  upstream.add(e.source);
                  traverse(e.source);
              }
          });
      };
      traverse(selectedNodeId);
      if (upstream.size > 0) {
          setNodes(nds => nds.map(n => ({ ...n, selected: upstream.has(n.id) || n.id === selectedNodeId })));
      }
  };

  const handleShowDownstream = () => {
      if (!selectedNodeId) return;
      const downstream = new Set<string>();
      const traverse = (nodeId: string) => {
          edges.filter(e => e.source === nodeId).forEach(e => {
              if (!downstream.has(e.target)) {
                  downstream.add(e.target);
                  traverse(e.target);
              }
          });
      };
      traverse(selectedNodeId);
      if (downstream.size > 0) {
          setNodes(nds => nds.map(n => ({ ...n, selected: downstream.has(n.id) || n.id === selectedNodeId })));
      }
  };

  const onNodeContextMenu = (event: React.MouseEvent, node: any) => {
      event.preventDefault();
      setContextMenu({ x: event.clientX, y: event.clientY, nodeId: node.id });
      if (selectedNodeId !== node.id) {
          setNodes(nds => nds.map(n => ({ ...n, selected: n.id === node.id })));
          setSelectedNodeId(node.id);
      }
  };

  const onPaneContextMenu = (event: React.MouseEvent | MouseEvent) => {
      event.preventDefault();
      setContextMenu({ x: event.clientX, y: event.clientY });
  };

  // Keyboard Shortcuts
  const handleEditorKeyDown = useEffectEvent((e: KeyboardEvent) => {
      if (!isActive) return;
      const target = e.target as HTMLElement;
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) || target.isContentEditable) {
          return;
      }

      if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'c') {
          handleCopy();
      } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'x') {
          handleCut();
      } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'v') {
          handlePaste();
      } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'd') {
          e.preventDefault();
          handleDuplicate();
      } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'z') {
          e.preventDefault();
          handleUndo();
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'z') {
          e.preventDefault();
          handleRedo();
      } else if (e.key === 'Delete' || e.key === 'Backspace') {
          if (selectedNodeId) handleDeleteNode(selectedNodeId);
          if (selectedEdge) handleDeleteEdge(selectedEdge);
      } else if (e.key.toLowerCase() === 'f' && selectedNodeId) {
          const node = nodes.find(n => n.id === selectedNodeId);
          if (node) zoomTo(1, { duration: 500 });
      }
  });

  useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => handleEditorKeyDown(event);
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // ===================== END EDITOR OPERATIONS ===================== //

  const handleAutoConnect = async () => {
      const graph = getGraph();
      const res = await fetch('/api/plant/auto-connect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(graph)
      });
      if (res.ok) {
          const suggested = await res.json();
          const colorMap: Record<string, string> = {
            'MATERIAL': '#3b82f6',
            'ELECTRICAL': '#eab308',
            'WATER': '#06b6d4',
            'SIGNAL': '#a855f7'
          };
          const newEdges = [...edges];
          let added = 0;
          suggested.forEach((e: any) => {
              if (!edges.some(existing => existing.source === e.source_node && existing.target === e.target_node)) {
                  newEdges.push({
                      id: `e-${e.source_node}-${e.target_node}`,
                      source: e.source_node,
                      sourceHandle: e.source_port,
                      target: e.target_node,
                      targetHandle: e.target_port,
                      data: { connection_type: e.connection_type },
                      style: { stroke: colorMap[e.connection_type] || '#3b82f6', strokeWidth: 2 },
                      type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: colorMap[e.connection_type] || '#3b82f6' }
                  });
                  added++;
              }
          });
          if (added > 0) {
              setEdges(newEdges);
              saveHistory(nodes, newEdges);
              validateGraph(nodes, newEdges);
          } else {
              alert("No new automated connections found.");
          }
      }
  };

  const handleAutoLayout = async (currentNodes: any[], currentEdges: any[] = edges) => {
      const graph = getGraph(currentNodes, currentEdges);
      const res = await fetch('/api/plant/auto-layout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(graph)
      });
      if (res.ok) {
          const layout = await res.json();
const layoutMap = new Map(layout.nodes.map((n: any) => [n.id, n.position]));
          const updatedNodes = currentNodes.map(n => ({
              ...n,
              position: n.data?.locked ? n.position : (layoutMap.get(n.id) || n.position)
          }));
          setNodes(updatedNodes);
          saveHistory(updatedNodes, currentEdges);
          validateGraph(updatedNodes, currentEdges);
          setTimeout(() => fitView({ padding: 0.2, minZoom: 0.25, maxZoom: 1.2, duration: 800 }), 100);
      }
  };

  const handleAutoSetup = async () => {
      if (nodes.length === 0) {
          alert("AUTO SETUP\n\nNo equipment has been added to the plant.\nAdd equipment manually or load a template first.");
          return;
      }
      
      const res = await fetch('/api/plant/auto-setup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(getGraph())
      });
      
      if (res.ok) {
          const proposal = await res.json();
          const newEdges = [...edges];
          let added = 0;
          
          proposal.new_edges.forEach((e: any) => {
              if (!edges.some(existing => existing.source === e.source_node && existing.target === e.target_node)) {
                  newEdges.push({
                      id: e.id,
                      source: e.source_node,
                      sourceHandle: e.source_port,
                      target: e.target_node,
                      targetHandle: e.target_port,
                      type: 'smoothstep',
                      data: { connection_type: e.connection_type },
                      style: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '5,5' },
                      markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' }
                  });
                  added++;
              }
          });
          
          if (added === 0 && proposal.missing_utilities.length === 0) {
             alert("AUTO SETUP\n\nPlant already satisfies recommended baseline topology.\nNo new connections needed.");
             return;
          }
          
          let previewMsg = `AUTO SETUP PREVIEW

Detected Components: ${nodes.length}
Proposed Connections: ${added}
`;
          if (proposal.missing_utilities.length > 0) {
              previewMsg += `
MISSING REQUIRED UTILITIES:
- ${proposal.missing_utilities.join('\n- ')}
`;
          }
          if (proposal.validation && !proposal.validation.is_valid) {
              previewMsg += `
WARNING: Proposed setup is NOT SIMULATION READY.
Errors remain.
`;
          }
          previewMsg += `
Apply Setup?`;
          
          if (window.confirm(previewMsg)) {
              setEdges(newEdges);
              await handleAutoLayout(nodes, newEdges);
          }
      }
  };

  const handleLoadTemplate = async () => {
      const res = await fetch('/api/plant/template/tmt');
      if (res.ok) {
          const tmt = await res.json();
          
          const rn = tmt.nodes.map((n: any, idx: number) => {
              return {
                  id: n.id,
                  type: 'equipment',
                  position: n.position,
                  data: {
                      component_class: n.component_class,
                      name: n.name,
                      engineeringId: `EQ-${(idx+1).toString().padStart(2, '0')}`,
                      ports: n.ports,
                      parameters: n.parameters
                  }
              };
          });

          const colorMap: Record<string, string> = {
            'MATERIAL': '#3b82f6',
            'ELECTRICAL': '#eab308',
            'WATER': '#06b6d4',
            'SIGNAL': '#a855f7'
          };
          const re = tmt.edges.map((e: any) => ({
              id: e.id,
              source: e.source_node,
              sourceHandle: e.source_port,
              target: e.target_node,
              targetHandle: e.target_port,
              data: { connection_type: e.connection_type },
              style: { stroke: colorMap[e.connection_type] || '#3b82f6', strokeWidth: 2 },
              type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: colorMap[e.connection_type] || '#3b82f6' }
          }));
          setNodes(rn);
          setEdges(re);
          setLibraryOpen(false);
          saveHistory(rn, re);
          try {
              localStorage.setItem('steelsim_plant', JSON.stringify({ nodes: tmt.nodes, edges: tmt.edges }));
          } catch {}
          setTimeout(() => fitView({ padding: 0.2, minZoom: 0.25, maxZoom: 1.2, duration: 800 }), 100);
          validateGraph(rn, re);
      }
  };

  const handleSave = () => {
      const plant = getGraph();
      localStorage.setItem('steelsim_plant', JSON.stringify(plant));
      alert("Plant topology saved locally.");
  };

  const handleLoad = () => {
      const data = localStorage.getItem('steelsim_plant');
      if (data) {
          try {
              const plant = JSON.parse(data);
              
              const rn = plant.nodes.map((n: any) => ({
                  id: n.id,
                  type: 'equipment',
                  position: n.position,
                  data: {
                      component_class: n.component_class || n.data?.component_class,
                      name: n.name || n.data?.name,
                      engineeringId: n.data?.engineeringId || n.name,
                      ports: n.ports || n.data?.ports,
                      parameters: n.parameters || n.data?.parameters,
                      locked: !!n.data?.locked
                  }
              }));

              const colorMap: Record<string, string> = {
                'MATERIAL': '#3b82f6',
                'ELECTRICAL': '#eab308',
                'WATER': '#06b6d4',
                'SIGNAL': '#a855f7'
              };
              const re = plant.edges.map((e: any) => ({
                  id: e.id,
                  source: e.source_node,
                  sourceHandle: e.source_port,
                  target: e.target_node,
                  targetHandle: e.target_port,
                  data: { connection_type: e.connection_type },
                  style: { stroke: colorMap[e.connection_type] || '#3b82f6', strokeWidth: 2 },
                  type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: colorMap[e.connection_type] || '#3b82f6' }
              }));
              setNodes(rn);
              setEdges(re);
              saveHistory(rn, re);
              setTimeout(() => fitView({ padding: 0.2, minZoom: 0.25, maxZoom: 1.2, duration: 800 }), 100);
              validateGraph(rn, re);
          } catch(e) {
              console.error(e);
          }
      }
  };

  // Re-fit view when panels change
  useEffect(() => {
    setTimeout(() => {
        fitView({ padding: 0.2, minZoom: 0.25, maxZoom: 1.2, duration: 400 });
    }, 300);
  }, [libraryOpen, inspectorOpen, issuesOpen, isFocusMode, fitView]);

  const renderedNodes = nodes.map(node => {
      const telemetry = snapshot?.node_telemetry?.[node.id];
      if (!telemetry) return node;
      return {
          ...node,
          data: { ...node.data, liveTelemetry: telemetry, simulationStatus: telemetry.status }
      };
  });

  const selectedEquipmentBase = selectedNodeId
      ? getGraph(nodes.filter(node => node.id === selectedNodeId), []).nodes[0]
      : undefined;
  const selectedEquipment = selectedEquipmentBase
      ? { ...selectedEquipmentBase, liveTelemetry: snapshot?.node_telemetry?.[selectedEquipmentBase.id] }
      : null;

  return (
    <ErrorBoundary>
    <div className={`flex-1 h-full flex flex-col bg-[#121315] ${isFocusMode ? 'fixed inset-0 z-50' : ''}`} ref={containerRef}>
      
      {/* UNIFIED TOOLBAR */}
      <div className="h-12 border-b border-industrial-700 bg-industrial-800 flex items-center justify-between px-2 flex-shrink-0">
        
        {/* Left: View Toggles & Select */}
        <div className="flex items-center gap-1">
            <button onClick={() => setLibraryOpen(!libraryOpen)} className={`px-2 py-1.5 rounded transition-colors text-xs font-semibold flex items-center gap-1.5 ${libraryOpen ? 'bg-blue-900/40 text-blue-400' : 'text-gray-400 hover:bg-industrial-700'}`}>
                <Layers className="w-3.5 h-3.5" /> <span className="hidden xl:inline">Library</span>
            </button>
            <button onClick={() => setInspectorOpen(!inspectorOpen)} className={`px-2 py-1.5 rounded transition-colors text-xs font-semibold flex items-center gap-1.5 ${inspectorOpen ? 'bg-blue-900/40 text-blue-400' : 'text-gray-400 hover:bg-industrial-700'}`}>
                <Settings2 className="w-3.5 h-3.5" /> <span className="hidden xl:inline">Inspector</span>
            </button>
            <button onClick={() => setIssuesOpen(!issuesOpen)} className={`px-2 py-1.5 rounded transition-colors text-xs font-semibold flex items-center gap-1.5 ${issuesOpen ? 'bg-blue-900/40 text-blue-400' : 'text-gray-400 hover:bg-industrial-700'}`}>
                <AlertTriangle className="w-3.5 h-3.5" /> <span className="hidden xl:inline">Issues</span>
            </button>
            
            <div className="w-px h-6 bg-industrial-700 mx-2"></div>

            <button className="px-2 py-1.5 rounded bg-industrial-700 text-gray-300 text-xs font-semibold flex items-center gap-1.5 hover:text-white">
                <Crosshair className="w-3.5 h-3.5" /> Select
            </button>
        </div>

        {/* Center: Engineering Actions */}
        <div className="flex items-center gap-1.5">
            <button onClick={handleAutoConnect} className="flex items-center px-3 py-1.5 bg-industrial-800 border border-industrial-700 text-gray-300 text-xs rounded hover:bg-industrial-700 hover:text-white transition-colors">
                <Network className="w-3.5 h-3.5 mr-2 text-cyan-500" /> Auto Connect
            </button>
            <button onClick={() => handleAutoLayout(nodes)} className="flex items-center px-3 py-1.5 bg-industrial-800 border border-industrial-700 text-gray-300 text-xs rounded hover:bg-industrial-700 hover:text-white transition-colors">
                <LayoutTemplate className="w-3.5 h-3.5 mr-2 text-blue-500" /> Auto Layout
            </button>
            <button onClick={handleAutoSetup} className="flex items-center px-3 py-1.5 bg-industrial-800 border border-industrial-700 text-gray-300 text-xs rounded hover:bg-industrial-700 hover:text-white transition-colors">
                <Wand2 className="w-3.5 h-3.5 mr-2 text-indigo-400" /> Auto Setup
            </button>
            <button onClick={() => validateGraph()} className="flex items-center px-3 py-1.5 bg-industrial-800 border border-industrial-700 text-gray-300 text-xs rounded hover:bg-industrial-700 hover:text-white transition-colors">
                <CheckSquare className="w-3.5 h-3.5 mr-2 text-green-500" /> Validate
            </button>
        </div>

        {/* Right: View & File Actions */}
        <div className="flex items-center gap-1">
            <button onClick={handleUndo} disabled={historyIndex <= 0} className="p-1.5 text-gray-400 hover:text-white hover:bg-industrial-700 rounded disabled:opacity-30">
                <Undo2 className="w-4 h-4" />
            </button>
            <button onClick={handleRedo} disabled={historyIndex >= history.length - 1} className="p-1.5 text-gray-400 hover:text-white hover:bg-industrial-700 rounded disabled:opacity-30">
                <Redo2 className="w-4 h-4" />
            </button>
            
            <div className="w-px h-6 bg-industrial-700 mx-1"></div>

            <button onClick={() => zoomIn()} className="p-1.5 text-gray-400 hover:text-white hover:bg-industrial-700 rounded" title="Zoom In">
                <ZoomIn className="w-4 h-4" />
            </button>
            <button onClick={() => zoomOut()} className="p-1.5 text-gray-400 hover:text-white hover:bg-industrial-700 rounded" title="Zoom Out">
                <ZoomOut className="w-4 h-4" />
            </button>
            <button onClick={() => fitView({ padding: 0.2, minZoom: 0.25, maxZoom: 1.2, duration: 800 })} className="p-1.5 text-gray-400 hover:text-white hover:bg-industrial-700 rounded" title="Fit Plant">
                <Maximize2 className="w-4 h-4" />
            </button>
            <button onClick={() => updateFocusMode(!isFocusMode)} className={`p-1.5 rounded ml-1 ${isFocusMode ? 'bg-amber-900/40 text-amber-400' : 'text-gray-400 hover:text-white hover:bg-industrial-700'}`} title="Focus Mode (F)">
                <Focus className="w-4 h-4" />
            </button>
            
            <div className="w-px h-6 bg-industrial-700 mx-1"></div>
            
            <button onClick={handleLoadTemplate} className="px-2 py-1.5 text-xs text-blue-400 hover:text-blue-300 font-semibold uppercase tracking-wider">
                Demo
            </button>
            <button onClick={handleSave} className="p-1.5 text-gray-400 hover:text-white hover:bg-industrial-700 rounded" title="Save">
                <Save className="w-4 h-4" />
            </button>
            <button onClick={handleLoad} className="p-1.5 text-gray-400 hover:text-white hover:bg-industrial-700 rounded" title="Load">
                <FolderOpen className="w-4 h-4" />
            </button>
            <button onClick={() => { setNodes([]); setEdges([]); setCurrentValidation(null); onValidationChange?.(null); saveHistory([], []); }} className="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded ml-1" title="Clear">
                <RotateCcw className="w-4 h-4" />
            </button>
        </div>
      </div>

      {/* WORKSPACE AREA */}
      <div className="flex-1 flex flex-row min-h-0 relative">
        <ComponentLibrary isOpen={libraryOpen} setIsOpen={setLibraryOpen} onAddClick={onAddClick} />
        
        <div className="flex-1 h-full relative flex flex-col min-w-0" ref={reactFlowWrapper}>
            <div className="flex-1 relative">
                <ReactFlow
                    nodes={renderedNodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    snapToGrid={true}
                    snapGrid={[15, 15]}
                    onEdgesChange={onEdgesChange}
onNodesDelete={() => setTimeout(() => { saveHistory(nodes, edges); validateGraph(); setSelectedNodeId(null); }, 100)}
                    onEdgesDelete={() => setTimeout(() => { saveHistory(nodes, edges); validateGraph(); setSelectedEdge(null); }, 100)}
                    onReconnect={onReconnect}
                    onEdgeClick={(_, edge) => { setSelectedEdge(edge.id); setSelectedNodeId(null); }}
                    onNodeContextMenu={onNodeContextMenu}
                    onPaneContextMenu={onPaneContextMenu}
                    onPaneClick={() => { setContextMenu(null); setSelectedNodeId(null); setSelectedEdge(null); }}
                    onSelectionChange={({ nodes: selectedNodes }) => {
                        if (selectedNodes.length > 0) {
                            setSelectedNodeId(selectedNodes[0].id);
                            setInspectorOpen(true);
                        } else {
                            setSelectedNodeId(null);
                        }
                    }}
                    onConnect={onConnect}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    nodeTypes={nodeTypes}
                    deleteKeyCode={null}
                    fitView
                    className="bg-industrial-900"
                >
                    <Background color="#34373a" gap={20} size={1} />
                
                    {nodes.length === 0 && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
                            <div className="text-center text-gray-400 p-8 rounded bg-industrial-900/50 border border-industrial-800/50 backdrop-blur-sm">
                                <h3 className="text-lg font-bold text-gray-300 mb-2">Start building your plant</h3>
                                <p className="text-sm mb-4">Drag equipment from Library or click + to add equipment</p>
                                <div className="flex justify-center gap-4 pointer-events-auto">
                                    <button onClick={() => setLibraryOpen(true)} className="px-4 py-2 bg-industrial-800 border border-industrial-700 rounded hover:bg-industrial-700 transition-colors text-sm">Open Library</button>
                                    <button onClick={handleLoadTemplate} className="px-4 py-2 bg-blue-900/40 border border-blue-900 rounded hover:bg-blue-800/50 transition-colors text-blue-400 text-sm">Load TMT Template</button>
                                </div>
                            </div>
                        </div>
                    )}

                    </ReactFlow>

                {contextMenu && (
                    <ContextMenu 
                        x={contextMenu.x} 
                        y={contextMenu.y} 
                        title={contextMenu.nodeId ? nodes.find(n => n.id === contextMenu.nodeId)?.data?.engineeringId || 'Component' : 'Canvas'}
                        subtitle={contextMenu.nodeId ? nodes.find(n => n.id === contextMenu.nodeId)?.data?.name : ''}
                        onClose={() => setContextMenu(null)}
                        actions={
                            contextMenu.nodeId ? [
                                { label: 'Inspect / Configure', onClick: () => { setInspectorOpen(true); } },
                                { label: 'Rename', onClick: () => {
                                    const newName = prompt('Enter new display name:');
                                    if (newName) {
                                        setNodes(nds => {
                                            const updated = nds.map(n => n.id === contextMenu.nodeId ? { ...n, data: { ...n.data, name: newName } } : n);
                                            setTimeout(() => { saveHistory(updated, edges); validateGraph(updated, edges); }, 50);
                                            return updated;
                                        });
                                    }
                                } },
                                { separator: true, onClick: () => {} },
                                { label: 'Duplicate', onClick: handleDuplicate },
                                { label: 'Copy', onClick: handleCopy },
                                { label: 'Cut', onClick: handleCut },
                                { separator: true, onClick: () => {} },
                                { label: 'Disconnect All', onClick: handleDisconnect },
                                { label: 'Show Upstream', onClick: handleShowUpstream },
                                { label: 'Show Downstream', onClick: handleShowDownstream },
                                { separator: true, onClick: () => {} },
                                { label: nodes.find(n => n.id === contextMenu.nodeId)?.data?.locked ? 'Unlock Position' : 'Lock Position', onClick: handleToggleLock },
                                { separator: true, onClick: () => {} },
                                { label: 'Delete', danger: true, onClick: () => handleDeleteNode(contextMenu.nodeId || null) }
                            ] : [
                                { label: 'Paste', disabled: clipboard.nodes.length === 0, onClick: handlePaste },
                                { separator: true, onClick: () => {} },
                                { label: 'Auto Connect', onClick: handleAutoConnect },
                                { label: 'Auto Layout', onClick: () => handleAutoLayout(nodes, edges) }
                            ]
                        }
                    />
                )}


                {/* FOCUS MODE EXIT OVERLAY */}
                {isFocusMode && (
                    <button 
                        onClick={() => updateFocusMode(false)}
                        className="absolute top-4 right-4 bg-industrial-800/80 backdrop-blur border border-industrial-700 text-gray-300 hover:text-white px-3 py-1.5 rounded flex items-center gap-2 text-xs font-semibold tracking-wide shadow-lg z-50 transition-colors"
                    >
                        <X className="w-4 h-4" /> EXIT FOCUS
                    </button>
                )}
            </div>

            <ValidationPanel 
                validation={currentValidation} 
                simulationStatus={snapshot?.status ?? simState?.status}
                isOpen={issuesOpen}
                setIsOpen={setIssuesOpen}
                events={events}
                onSelectNode={(id) => {
                    setNodes(nds => nds.map(n => ({ ...n, selected: n.id === id })));
                    const node = nodes.find(n => n.id === id);
                    if (node) {
                        setSelectedNodeId(node.id);
                        setInspectorOpen(true);
                        fitView({ nodes: [node], duration: 800, padding: 0.5 });
                    }
                }} 
            />
        </div>
        
        <Inspector selectedNode={selectedEquipment} selectedEdge={selectedEdge} edges={edges} nodes={nodes} onDeleteEdge={handleDeleteEdge} validation={currentValidation} isOpen={inspectorOpen} setIsOpen={setInspectorOpen} />
      </div>
    </div>
    </ErrorBoundary>
  );
}

export const Blueprint = (props: BlueprintCanvasProps) => {
    return (
        <ReactFlowProvider>
            <BlueprintCanvas {...props} />
        </ReactFlowProvider>
    );
}
