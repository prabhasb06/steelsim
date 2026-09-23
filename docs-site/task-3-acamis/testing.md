# 35. ACAMIS testing

ACAMIS is tested against the simulator, detector, policy gates, model gateway, and history API. Run the backend suite from the repository root:

```powershell
python -m pytest backend/tests -q
```

The root `pytest.ini` adds `backend/` to the Python path. The test fixture writes history to an isolated temporary SQLite database so verification does not alter operator recordings.

The suite checks that normal and transient readings do not raise incidents, sustained rolling-throughput deficits raise one incident, pause freezes detection and scheduled recovery, reset clears detector state, and high-risk procedures require explicit human verification. It also checks that provider keys are omitted from public status and history, a real generation response is required to verify a connection, and live simulated telemetry reaches the advisory provider. Provider tests use controlled local responses and a local HTTP test server; they do not validate a user's actual paid provider key.

At the last code verification, the full backend suite passed 85 tests. The [general testing guide](/reference/testing) covers frontend, browser, and documentation checks.
