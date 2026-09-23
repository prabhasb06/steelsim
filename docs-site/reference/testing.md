# 45. Testing

Run these checks from the SteelSim repository root after installing the dependencies described in [Quick start](/getting-started/quick-start).

```powershell
python -m pytest backend/tests -q
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix docs-site run docs:build
```

The browser smoke test needs a running frontend and backend, or a single backend serving the built frontend:

```powershell
npm --prefix frontend run test:e2e
```

The test covers Builder demo loading, simulation controls, ACAMIS scenarios and approval gates, model connection through a local test provider, history replay, and paused restoration. It uses a synthetic key and does not consume provider quota.

At the last implementation verification, 85 backend tests, four frontend utility tests, the browser smoke test, lint, type checking, and the production build passed. The Vite build had a non-blocking large-bundle warning. A separate live-site check is still required before a public demonstration.

VitePress builds the documentation and search index. A successful build checks compilation and page rendering; it does not prove every external link or the public deployment is available.
