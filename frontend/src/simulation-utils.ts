import type { SimulationSnapshot } from './types';
import type { PlantGraph } from './types/topology';

const UTILITY_CLASSES = new Set([
  'UTILITY_SUBSTATION',
  'WATER_COOLING_SYSTEM',
  'ELECTRICAL_SUPPLY',
  'TRANSFORMER',
  'WATER_SYSTEM',
  'WATER_PUMP',
  'COMPRESSOR',
]);

export function isUtilityClass(componentClass: string) {
  return UTILITY_CLASSES.has(componentClass);
}

export function orderProcessNodes(nodes: PlantGraph['nodes'], edges: PlantGraph['edges']) {
  const processNodes = nodes.filter(node => !isUtilityClass(node.component_class));
  const processIds = new Set(processNodes.map(node => node.id));
  const inDegree = new Map(processNodes.map(node => [node.id, 0]));
  const adjacency = new Map(processNodes.map(node => [node.id, [] as string[]]));

  edges
    .filter(edge => edge.connection_type === 'MATERIAL' && processIds.has(edge.source_node) && processIds.has(edge.target_node))
    .forEach(edge => {
      adjacency.get(edge.source_node)?.push(edge.target_node);
      inDegree.set(edge.target_node, (inDegree.get(edge.target_node) ?? 0) + 1);
    });

  const queue = processNodes
    .filter(node => inDegree.get(node.id) === 0)
    .sort((a, b) => a.position.x - b.position.x);
  const ordered: PlantGraph['nodes'] = [];

  while (queue.length > 0) {
    const node = queue.shift()!;
    ordered.push(node);
    for (const targetId of adjacency.get(node.id) ?? []) {
      const nextDegree = (inDegree.get(targetId) ?? 1) - 1;
      inDegree.set(targetId, nextDegree);
      if (nextDegree === 0) {
        const target = processNodes.find(candidate => candidate.id === targetId);
        if (target) queue.push(target);
      }
    }
  }

  const seen = new Set(ordered.map(node => node.id));
  return [...ordered, ...processNodes.filter(node => !seen.has(node.id)).sort((a, b) => a.position.x - b.position.x)];
}

export function parseSimulationSnapshot(raw: string, expectedSimulationId: string): SimulationSnapshot {
  const parsed: unknown = JSON.parse(raw);
  if (!parsed || typeof parsed !== 'object') {
    throw new Error('Simulation stream returned a non-object payload.');
  }

  const candidate = parsed as Partial<SimulationSnapshot>;
  if (
    candidate.simulation_id !== expectedSimulationId
    || typeof candidate.state_version !== 'number'
    || typeof candidate.tick !== 'number'
    || typeof candidate.status !== 'string'
    || !candidate.plant_summary
    || !candidate.node_telemetry
    || !Array.isArray(candidate.events)
  ) {
    throw new Error('Simulation stream returned an invalid snapshot.');
  }
  return candidate as SimulationSnapshot;
}

export function shouldAcceptSnapshot(current: SimulationSnapshot | null, next: SimulationSnapshot) {
  return !current
    || current.simulation_id !== next.simulation_id
    || next.state_version >= current.state_version;
}

export function plantSimulationSignature(graph: PlantGraph) {
  return JSON.stringify({
    nodes: [...graph.nodes]
      .sort((a, b) => a.id.localeCompare(b.id))
      .map(node => ({
        id: node.id,
        component_class: node.component_class,
        ports: node.ports,
        parameters: node.parameters,
      })),
    edges: [...graph.edges]
      .sort((a, b) => a.id.localeCompare(b.id))
      .map(edge => ({
        source_node: edge.source_node,
        source_port: edge.source_port,
        target_node: edge.target_node,
        target_port: edge.target_port,
        connection_type: edge.connection_type,
      })),
  });
}
