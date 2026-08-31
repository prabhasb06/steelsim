from typing import Dict, List, Optional
from app.engine.simulator import SteelSimEngine
from app.models.schemas import SimulationConfiguration, SimulationState

class SimulationManager:
    def __init__(self):
        self._simulations: Dict[str, SteelSimEngine] = {}

    def create_simulation(self, config: SimulationConfiguration) -> SteelSimEngine:
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
