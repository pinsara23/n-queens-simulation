# N-Queens Watch Mode API

This project solves N-Queens with the standard recursive backtracking
algorithm and exposes its real search events through a FastAPI service. A web
client can play the returned trace as a visualization.

## Project layout

```text
app/
  app/main.py              FastAPI application
  schemas.py              Pydantic v2 request and response models
  api/routes.py           HTTP endpoints and rate limiting
  core/tracing.py         Solver-to-API trace adapter
algorithms/               Solver abstraction and backtracking implementation
utils/                    Board validation helpers
tests/                    Solver and API tests
```

Only the implemented backtracking algorithm is advertised. The former desktop
frontend has been removed; the solver remains usable without a GUI.

## Local development with Conda

Python 3.11 is required. Use the existing `nqueens` environment:

```powershell
conda activate nqueens
uvicorn app.main:app --reload
```

The interactive API documentation is available at
<http://127.0.0.1:8000/docs>.

Run tests with:

```powershell
conda activate nqueens
pytest -q
```

## API

- `GET /health` -> `{"status":"ok"}`
- `GET /api/algorithms` -> available algorithm metadata
- `POST /api/trace` -> step-by-step `place`, `reject`, `backtrack`, and
  `solution` events
- `POST /api/solve` -> solutions up to the requested limit
- `GET /docs` -> OpenAPI documentation

Example trace request:

```powershell
curl -X POST http://127.0.0.1:8000/api/trace `
  -H "Content-Type: application/json" `
  -d '{"n":8,"algorithm":"backtracking","max_steps":20000,"stop_after_first_solution":true}'
```

Example solve request:

```powershell
curl -X POST http://127.0.0.1:8000/api/solve `
  -H "Content-Type: application/json" `
  -d '{"n":8,"algorithm":"backtracking","max_solutions":10}'
```

`n` must be 4 through 12, `max_steps` is capped at 50,000, and
`max_solutions` is capped at 1,000. Responses report `truncated` when a
request reaches a configured limit.

## Environment variables

Copy `.env.example` for local reference:

- `ALLOWED_ORIGINS`: comma-separated allowed browser origins. Defaults to
  `http://localhost:3000`; set an explicit production origin, never `*`.
- `RATE_LIMIT`: per-IP slowapi limit, default `60/minute`.
- `SOLVER_TIME_LIMIT_SECONDS`: hard solver limit per request, default `5`.

## Deploy to Render with Docker

1. Push this branch to GitHub.
2. In Render, choose **New > Blueprint** and select the repository, or create a
   Docker web service manually.
3. Use the included `render.yaml`, which selects the free plan and
   `/health` health check.
4. In the Render dashboard, set `ALLOWED_ORIGINS` to the exact URL of the web
   visualization. Do not use a wildcard in production.
5. Deploy. Render supplies `PORT`; the Docker command binds to it automatically.
6. Verify `/health` and `/docs` on the generated Render URL.

No deployment is performed by this repository task.
