"""SQLite operational journal. Explicit allowlists keep model credentials out of storage."""
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

FIELDS = ("acamis_scenario", "acamis_autonomy", "acamis_last_resolution", "acamis_recovery_tick",
          "acamis_impact", "rolling_monitor", "rolling_disturbance", "signal_monitor")


class HistoryStore:
    def __init__(self, path=None):
        self.path = str(path or os.getenv("STEELSIM_HISTORY_DB", str(Path(__file__).resolve().parents[2] / "data" / "operations.sqlite3")))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, simulation_id TEXT NOT NULL,
                  name TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  status TEXT NOT NULL, tick INTEGER NOT NULL, config TEXT NOT NULL, checkpoint TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS frames (seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  run_id TEXT NOT NULL, tick INTEGER NOT NULL, version INTEGER NOT NULL, data TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS frames_run ON frames(run_id, seq);
                CREATE TABLE IF NOT EXISTS audit (id TEXT PRIMARY KEY, run_id TEXT NOT NULL, data TEXT NOT NULL);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def attach(self, sim):
        sim.history_run_id = f"run_{uuid4().hex}"
        sim._history_store = self
        sim.persist_history()

    def record(self, sim):
        from app.acamis.service import status
        assessment = status(sim)
        checkpoint = {key: getattr(sim, key) for key in FIELDS}
        checkpoint["acamis_mitigations"] = sorted(sim.acamis_mitigations)
        checkpoint["state"] = sim.get_state().model_dump(mode="json")
        # No gateway metadata, model replies, prompts, or credentials are archived.
        frame = {"snapshot": assessment["snapshot"], "incident": assessment["incident"],
                 "origin": assessment["incident_origin"], "evidence": assessment["incident_evidence"],
                 "recovery_plan": assessment["recovery_plan"], "signals": sim.signal_monitor["findings"]}
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as db:
            db.execute('''INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at, status=excluded.status,
                tick=excluded.tick, checkpoint=excluded.checkpoint''',
                (sim.history_run_id, sim.id, sim.name, now, now, sim.status.value, sim.tick,
                 sim.config.model_dump_json(), json.dumps(checkpoint)))
            encoded = json.dumps(frame)
            previous = db.execute("SELECT data FROM frames WHERE run_id=? ORDER BY seq DESC LIMIT 1", (sim.history_run_id,)).fetchone()
            if not previous or previous["data"] != encoded:
                db.execute("INSERT INTO frames(run_id,tick,version,data) VALUES (?,?,?,?)",
                           (sim.history_run_id, sim.tick, sim.state_version, encoded))
            for entry in sim.acamis_audit:
                # Provider error text can contain remote output. Keep only policy audit events.
                if not entry["event"].startswith("MODEL_"):
                    db.execute("INSERT OR IGNORE INTO audit VALUES (?,?,?)", (entry["id"], sim.history_run_id, json.dumps(entry)))

    def runs(self, limit=100, offset=0):
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT id,simulation_id,name,created_at,updated_at,status,tick FROM runs ORDER BY updated_at DESC LIMIT ? OFFSET ?", (limit, offset))]

    def detail(self, run_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["config"] = json.loads(result["config"])
            result["checkpoint"] = json.loads(result["checkpoint"])
            result["audit"] = [json.loads(r["data"]) for r in db.execute("SELECT data FROM audit WHERE run_id=? ORDER BY rowid", (run_id,))]
            result["frame_count"] = db.execute("SELECT count(*) FROM frames WHERE run_id=?", (run_id,)).fetchone()[0]
            return result

    def frames(self, run_id, after=0, limit=500):
        with self.connect() as db:
            return [{"seq": row["seq"], **json.loads(row["data"])} for row in db.execute(
                "SELECT seq,data FROM frames WHERE run_id=? AND seq>? ORDER BY seq LIMIT ?", (run_id, after, limit))]

    def restore(self, run_id, manager):
        from app.models.schemas import SimulationConfiguration, SimulationStatus, SimulationEvent
        record = self.detail(run_id)
        if record is None:
            raise KeyError(run_id)
        saved = record["checkpoint"]
        sim = manager.create_simulation(SimulationConfiguration.model_validate(record["config"]))
        for key in FIELDS:
            setattr(sim, key, saved[key])
        sim.acamis_mitigations = set(saved["acamis_mitigations"])
        state = saved["state"]
        sim.initial_time = datetime.fromisoformat(state["initial_time"])
        for key in ("tick", "elapsed_seconds", "speed", "state_version"):
            setattr(sim, key, state[key])
        sim.current_time = datetime.fromisoformat(state["current_time"])
        sim.events = [SimulationEvent.model_validate(e) for e in state["events"]]
        # Previous policy entries belong to the source run, not the new session.
        sim.acamis_audit = []
        sim.status = SimulationStatus.PAUSED
        sim._calculate_telemetry()
        from app.acamis.service import _audit
        _audit(sim, "RUN_RESTORED", f"Restored {run_id} at tick {sim.tick}; resume explicitly to continue.")
        sim._state_changed()
        return sim
