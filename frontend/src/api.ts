import type { PlantGraph } from './types/topology';
import type { SimulationCommand, SimulationSnapshot, SimulationState } from './types';
import type { ValidationResult } from './types/topology';

const apiKey = import.meta.env.VITE_STEELSIM_API_KEY?.trim();

export class ApiError extends Error {
  readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const encodeWebSocketToken = (value: string) => {
  const binary = Array.from(new TextEncoder().encode(value), byte => String.fromCharCode(byte)).join('');
  return btoa(binary).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
};

export const apiRequest = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const headers = new Headers(init?.headers);
  if (apiKey) headers.set('X-SteelSim-API-Key', apiKey);
  const response = await fetch(path, { ...init, headers });
  if (!response.ok) {
    const detail = await response.json().catch(() => null) as { detail?: string } | null;
    throw new ApiError(detail?.detail ?? `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
};

export const simulationApi = {
  health: () => apiRequest<{ status: string }>('/api/health'),
  create: (plant: PlantGraph) => apiRequest<SimulationState>('/api/simulations', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plant }),
  }),
  get: (id: string) => apiRequest<SimulationState>(`/api/simulations/${id}`),
  delete: (id: string, keepalive = false) => apiRequest<{ deleted: boolean; simulation_id: string }>(`/api/simulations/${id}`, { method: 'DELETE', keepalive }),
  snapshot: (id: string) => apiRequest<SimulationSnapshot>(`/api/simulations/${id}/snapshot`),
  snapshots: (id: string) => apiRequest<SimulationSnapshot[]>(`/api/simulations/${id}/snapshots`),
  streamUrl: (id: string) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/api/simulations/${id}/stream`;
  },
  streamProtocols: () => apiKey
    ? ['steelsim', `steelsim-key.${encodeWebSocketToken(apiKey)}`]
    : null,
  command: (id: string, command: SimulationCommand, payload: Record<string, unknown> = {}) =>
    apiRequest<SimulationSnapshot>(`/api/simulations/${id}/command`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, payload }),
    }),
  validate: (plant: PlantGraph) => apiRequest<ValidationResult>('/api/plant/validate', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(plant),
  }),
  start: (id: string) => apiRequest<SimulationState>(`/api/simulations/${id}/start`, { method: 'POST' }),
  pause: (id: string) => apiRequest<SimulationState>(`/api/simulations/${id}/pause`, { method: 'POST' }),
  resume: (id: string) => apiRequest<SimulationState>(`/api/simulations/${id}/resume`, { method: 'POST' }),
  reset: (id: string) => apiRequest<SimulationState>(`/api/simulations/${id}/reset`, { method: 'POST' }),
  speed: (id: string, speed: string) => apiRequest<SimulationState>(`/api/simulations/${id}/speed`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ speed }),
  }),
};
