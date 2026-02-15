# Coding Conventions

## BLUF
Semantic commits on `master`. Flask for APIs, Dash+Bootstrap for data apps, React+Tailwind+Shadcn for the main dashboard. Each service owns its own requirements.txt and Dockerfile. Keep it simple — no unnecessary abstraction.

---

## General Rules

### Simplicity First
- Prefer `subprocess` and HTTP calls over complex orchestration frameworks
- Prefer flat file storage (CSV) over databases for analytics data
- Don't add abstraction layers unless you've felt the pain of not having them

### Git
- **Branch**: `master` for everything. Feature branches for larger work (>1 session)
- **Commits**: Semantic format — `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- **Scope optional**: `feat(web_monitor): Add power mode switching`

---

## Python (Flask / Dash)

### Style
- Functions use `snake_case`
- Classes use `PascalCase`
- Constants use `UPPER_SNAKE_CASE`
- Every function gets a docstring explaining **why**, not just what
- Type hints encouraged but not enforced

### Flask (web_monitor)
- All API routes prefixed with `/api/`
- Platform detection via `sys.platform.startswith('win')`
- Remote forwarding pattern: PC routes call `http://{MONITOR_TARGET_HOST}:{PORT}/api/local_*`
- Use `app_logger` (module-level logger), not `print()`
- Environment config via `.env` + `python-dotenv`

### Dash (data_gobbler / data_analyzer)
- **Hidden DOM Rule**: Never conditionally render components that contain `Input` IDs. Render everything at boot, toggle with `style={'display': 'none'}`
- **allow_duplicate**: When multiple callbacks target the same output, use `allow_duplicate=True` with `prevent_initial_call='initial_duplicate'`
- **Pattern Matching**: Use `MATCH`/`ALL` for dynamic component sets (plot cards, etc.)
- **Guard Clauses**: Every callback starts with an early return check
- **Consolidation**: If multiple components share inputs, use a single callback with multiple outputs
- Bind to `0.0.0.0:8050` in containers

### Dependencies
- Each service has its own `requirements.txt`
- No shared virtual environments between services
- Use `pip install --no-cache-dir` in Dockerfiles

---

## TypeScript / React (web_monitor frontend)

### Stack
- React 19, Vite (aliased to rolldown-vite), TypeScript
- Tailwind CSS 4 (PostCSS plugin, NOT `@tailwindcss/vite`)
- Shadcn UI (New York style, Slate base, CSS variables)
- Lucide icons
- Path alias: `@/` → `./src/`

### Patterns
- Custom hooks in `src/hooks/` — one hook per data source (`useSystemInfo`, `useGpuInfo`, etc.)
- UI components in `src/components/` — one file per card/widget
- Shadcn primitives in `src/components/ui/`
- All API calls go through custom hooks, never directly in components
- Polling intervals: 5s for system metrics, 3s for Docker services, 30s for power mode, 60s for config

### Naming
- Components: `PascalCase.tsx`
- Hooks: `camelCase.ts` prefixed with `use`
- UI primitives: `lowercase.tsx` (Shadcn convention)

### Build
- `npm run build` → `frontend/dist/` → served by Flask
- Flask serves `dist/assets/` at `/assets` and `dist/index.html` at `/`

---

## Docker

### Compose Conventions
- `docker-compose.yml` is the single source of truth for Jetson state
- Container names are explicit (`home_ai_dashboard`, `ollama_jetson`, etc.)
- All custom services use `restart: always`
- Data persistence via named volumes or host bind mounts
- GPU access via `runtime: nvidia` + device reservations

### Dockerfile Conventions
- Multi-stage builds for web_monitor (Node builder → Python runtime)
- `python:3.10-slim` base for Dash services
- `nvcr.io/nvidia/l4t-base:r36.2.0` base for Jetson dashboard (GPU access)

---

## File Organization

```
home_ai_project/
├── CLAUDE.md              # Root context for Claude Code
├── GEMINI.md              # Root context for Gemini CLI
├── docs/                  # ← This knowledge framework
│   ├── README.md          # Framework index
│   ├── ARCHITECTURE.md    # System design
│   ├── CONVENTIONS.md     # This file
│   ├── DECISIONS.md       # ADR log
│   ├── ROADMAP.md         # Priorities
│   ├── SESSION_GUIDE.md   # How to run agentic sessions
│   ├── adr/               # Individual decision records
│   └── context-scopes/    # Per-service context files
├── web_monitor/           # Dashboard service
├── data_gobbler/          # Engineering workbench
├── data_analyzer/         # Legacy analytics
├── scripts/               # Shared utility scripts
├── homepage/              # Homepage dashboard config
├── netdata/               # Netdata config
├── docker-compose.yml     # Orchestration
└── deploy.sh              # Deployment menu script
```
