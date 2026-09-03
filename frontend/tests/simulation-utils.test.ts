import assert from 'node:assert/strict';
import test from 'node:test';

import {
  isUtilityClass,
  orderProcessNodes,
  parseSimulationSnapshot,
  plantSimulationSignature,
  shouldAcceptSnapshot,
} from '../src/simulation-utils.ts';
import type { SimulationSnapshot } from '../src/types.ts';
import type { EquipmentNode, PlantGraph } from '../src/types/topology.ts';

function node(id: string, x: number): EquipmentNode {
  return {
    id,
    component_class: 'RAW_MATERIAL_STORAGE',
    name: id,
    position: { x, y: 0 },
    ports: [],
    parameters: {},
    metadata: {},
  };
}

function snapshot(version: number): SimulationSnapshot {
  return {
    simulation_id: 'sim_test',
    id: 'sim_test',
    simulation_time: '2026-01-01T08:00:00Z',
    elapsed_seconds: version,
    status: 'RUNNING',
    speed: '1x',
    tick: version,
    state_version: version,
    seed: 42,
    system_health: 'NORMAL',
    node_telemetry: {},
    plant_summary: {
      total_power_kw: 0,
      total_power_mw: 0,
      total_water_m3h: 0,
      active_nodes: 0,
      interlocked_nodes: 0,
      total_nodes: 0,
    },
    events: [],
  };
}

test('orders process cards by material flow rather than canvas insertion order', () => {
  const source = node('source', 500);
  const middle = node('middle', 100);
  const target = node('target', 0);
  const graph: PlantGraph = {
    nodes: [target, middle, source],
    edges: [
      { id: 'e1', source_node: 'source', source_port: '', target_node: 'middle', target_port: '', connection_type: 'MATERIAL' },
      { id: 'e2', source_node: 'middle', source_port: '', target_node: 'target', target_port: '', connection_type: 'MATERIAL' },
    ],
  };

  assert.deepEqual(orderProcessNodes(graph.nodes, graph.edges).map(item => item.id), ['source', 'middle', 'target']);
  assert.equal(isUtilityClass('UTILITY_SUBSTATION'), true);
});

test('rejects malformed or cross-simulation WebSocket snapshots', () => {
  assert.throws(() => parseSimulationSnapshot('{"bad":true}', 'sim_test'));
  assert.throws(() => parseSimulationSnapshot(JSON.stringify(snapshot(1)), 'sim_other'));
  assert.equal(parseSimulationSnapshot(JSON.stringify(snapshot(1)), 'sim_test').tick, 1);
});

test('does not allow a late HTTP response to rewind live state', () => {
  assert.equal(shouldAcceptSnapshot(snapshot(5), snapshot(4)), false);
  assert.equal(shouldAcceptSnapshot(snapshot(5), snapshot(6)), true);
});

test('layout-only edits do not invalidate the running simulation', () => {
  const original: PlantGraph = { nodes: [node('source', 0)], edges: [] };
  const moved: PlantGraph = {
    nodes: [{ ...original.nodes[0], position: { x: 900, y: 400 }, name: 'Renamed label', parameters: {} }],
    edges: [],
  };

  assert.equal(plantSimulationSignature(original), plantSimulationSignature(moved));
  moved.nodes[0].parameters.throughput = {
    value: 20,
    unit: 't/h',
    category: 'MASS_FLOW',
    display_name: 'Throughput',
  };
  assert.notEqual(plantSimulationSignature(original), plantSimulationSignature(moved));
});
