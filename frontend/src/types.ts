import type { PlantGraph } from './types/topology';

export type SimulationStatus = "READY" | "RUNNING" | "PAUSED" | "COMPLETED" | "ERROR";
export type EventSeverity = "INFO" | "NOTICE" | "WARNING" | "CRITICAL";
export type SimulationCommand = "start" | "run" | "resume" | "pause" | "reset" | "set_speed";

export interface SimulationEvent {
    id: string;
    simulation_id: string;
    simulation_time: string;
    type: string;
    severity: EventSeverity;
    source: string;
    message: string;
    metadata: Record<string, unknown>;
}

export interface NodeTelemetry {
    id: string;
    status: "OFF" | "IDLE" | "PREHEATING" | "RUNNING" | "INTERLOCKED";
    power_kw: number;
    power_mw: number;
    water_m3h: number;
    temperature_c: number;
    throughput_tph: number;
}

export interface PlantSummary {
    total_power_kw: number;
    total_power_mw: number;
    total_water_m3h: number;
    active_nodes: number;
    interlocked_nodes: number;
    total_nodes: number;
}

export interface SimulationConfiguration {
    name: string;
    seed: number;
    plant: PlantGraph;
}

export interface SimulationState {
    id: string;
    name: string;
    created_at: string;
    seed: number;
    initial_time: string;
    current_time: string;
    elapsed_seconds: number;
    tick: number;
    state_version: number;
    speed: string;
    status: SimulationStatus;
    configuration: SimulationConfiguration;
    events: SimulationEvent[];
    node_telemetry: Record<string, NodeTelemetry>;
    plant_summary: PlantSummary;
}

export interface SimulationSnapshot {
    acamis_impact?: {
        origin?: string;
        scenario: string;
        state: 'ACTIVE' | 'RECOVERED';
        tick: number;
        recovery_tick: number | null;
        equipment: Record<string, Record<string, { baseline: number; actual: number }>>;
    } | null;
    simulation_id: string;
    id: string;
    simulation_time: string;
    elapsed_seconds: number;
    status: SimulationStatus;
    speed: string;
    tick: number;
    state_version: number;
    seed: number;
    system_health: string;
    node_telemetry: Record<string, NodeTelemetry>;
    plant_summary: PlantSummary;
    events: SimulationEvent[];
}
