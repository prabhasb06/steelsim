import type { PlantGraph } from './types/topology';
import type { SimulationState } from './types';

const request = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(path, init);
  if (!response.ok) {
    const detail = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(detail?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
};

export const simulationApi = {
  health: () => request<{ status: string }>('/api/health'),
  create: (plant: PlantGraph) => request<SimulationState>('/api/simulations', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plant }),
  }),
  get: (id: string) => request<SimulationState>(`/api/simulations/${id}`),
  start: (id: string) => request<SimulationState>(`/api/simulations/${id}/start`, { method: 'POST' }),
  pause: (id: string) => request<SimulationState>(`/api/simulations/${id}/pause`, { method: 'POST' }),
  resume: (id: string) => request<SimulationState>(`/api/simulations/${id}/resume`, { method: 'POST' }),
  reset: (id: string) => request<SimulationState>(`/api/simulations/${id}/reset`, { method: 'POST' }),
  speed: (id: string, speed: string) => request<SimulationState>(`/api/simulations/${id}/speed`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ speed }),
  }),
};
