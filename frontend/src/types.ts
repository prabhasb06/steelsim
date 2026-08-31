export type SimulationStatus = "READY" | "RUNNING" | "PAUSED" | "COMPLETED" | "ERROR";
export type EventSeverity = "INFO" | "NOTICE" | "WARNING" | "CRITICAL";

export interface SimulationEvent {
    id: string;
    simulation_id: string;
    simulation_time: string;
    type: string;
    severity: EventSeverity;
    source: string;
    message: string;
    metadata: Record<string, any>;
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
    speed: string;
    status: SimulationStatus;
    configuration: Record<string, any>;
    events: SimulationEvent[];
}

export interface SimulationSnapshot {
    simulation_id: string;
    simulation_time: string;
    elapsed_seconds: number;
    status: SimulationStatus;
    speed: string;
    tick: number;
    seed: number;
    system_health: string;
}
