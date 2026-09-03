from typing import Dict, List, Optional
from app.engine.simulator import SteelSimEngine
from app.models.schemas import SimulationConfiguration, SimulationState, SimulationStatus

class SimulationManager:
    def __init__(self, max_simulations: int = 50):
        self._simulations: Dict[str, SteelSimEngine] = {}
        self.max_simulations = max_simulations

    def _evict_inactive_simulation(self) -> None:
        inactive = sorted(
            (
                sim for sim in self._simulations.values()
                if sim.status != SimulationStatus.RUNNING
            ),
            key=lambda sim: sim.created_at,
        )
        if not inactive:
            raise RuntimeError("Simulation capacity reached; pause or delete an active simulation")
        self.delete_simulation(inactive[0].id)

    def create_simulation(self, config: SimulationConfiguration) -> SteelSimEngine:
        while len(self._simulations) >= self.max_simulations:
            self._evict_inactive_simulation()
        sim = SteelSimEngine(config)
        self._simulations[sim.id] = sim
        return sim

    def get_simulation(self, sim_id: str) -> Optional[SteelSimEngine]:
        return self._simulations.get(sim_id)

    def list_simulations(self) -> List[SimulationState]:
        return [sim.get_state() for sim in self._simulations.values()]
        
    def delete_simulation(self, sim_id: str) -> bool:
        sim = self._simulations.get(sim_id)
        if sim:
            if sim._task and not sim._task.done():
                sim._task.cancel()
            del self._simulations[sim_id]
            return True
        return False
