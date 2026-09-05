# 18. Deterministic engine

The deterministic virtual-factory engine is implemented in `backend/app/engine/simulator.py` under the `SteelSimEngine` class.

## Determinism mechanics

### 1. Seeded pseudo-random generation
The engine initializes a dedicated pseudo-random generator (`random.Random(self.seed)`) using the integer seed supplied in the simulation configuration. This guarantees that small operational variations (such as minor thermal fluctuations or load variations) are 100% reproducible across test runs and presentations.

### 2. Monotonic state versioning
Every simulation tick, manual command execution, or speed change increments `state_version` by exactly 1.
```python
def _state_changed(self) -> None:
    self.state_version += 1
    self._publish_snapshot()
```
The client checks this version before applying any update:
$$v_{	ext{new}} ge v_{	ext{current}}$$
This prevents race conditions where an asynchronous HTTP poll could overwrite a newer WebSocket frame.

### 3. Discrete tick progression
The simulated clock advances in discrete time steps ($Delta t = 1	ext{ second}$). The simulated clock is decoupled from real-world wall-clock time, allowing execution to run at accelerated speeds without altering mathematical behavior.

### 4. Speed multipliers

| Speed Setting | Real Time per Simulated Second | Application |
| :--- | :--- | :--- |
| **`1x`** | $1.0	ext{ s}$ | Real-time observation matching physical clock speed. |
| **`5x`** | $0.2	ext{ s}$ | Accelerated engineering evaluation. |
| **`10x`** | $0.1	ext{ s}$ | Rapid throughput batch verification. |
| **`60x`** | $approx 0.0167	ext{ s}$ | One simulated hour per real minute. |
| **`MAX`** | Unthrottled (capped at 240 ticks/s)| API-only benchmark mode with a CPU-safe governor. |
