# Agentic Coding Session Guide

## BLUF
Every session follows three phases: **Scope → Execute → Close**. Define what you're changing before you start, work within that boundary, and leave the project cleaner than you found it.

---

## Phase 1: Scope (Before Touching Code)

### 1. State Your Goal in One Sentence
Bad: "Work on the dashboard"  
Good: "Add a fan speed indicator to the GpuInfoCard component"

### 2. Load the Right Context
Always read:
- `CLAUDE.md` (or `GEMINI.md`) — system overview, ports, build commands

Then read the relevant scope file:
- `docs/context-scopes/web_monitor.md` — for dashboard/Flask/React work
- `docs/context-scopes/data_gobbler.md` — for engineering workbench work
- `docs/context-scopes/infrastructure.md` — for Docker/deploy/networking work

### 3. Check the Decision Log
Skim `docs/DECISIONS.md` if your task touches an established pattern. Don't reinvent what's already been decided.

### 4. Identify the Blast Radius
Which files will you touch? Which services need rebuilding? Write it down.

```markdown
## Session Plan
**Goal**: Add fan speed to GPU card
**Files**: web_monitor/frontend/src/components/GpuInfoCard.tsx, web_monitor/frontend/src/hooks/useGpuInfo.ts
**Blast Radius**: Frontend only, no backend changes
**Build**: `cd web_monitor/frontend && npm run build`
**Test**: Check PC dashboard at localhost:5000, verify GPU card renders fan speed
```

---

## Phase 2: Execute

### Rules During Execution
1. **Stay in scope** — If you discover something unrelated that needs fixing, note it in a `TODO` comment or the session close notes. Don't context-switch.
2. **Small commits** — Commit after each logical change, not at the end of a marathon session.
3. **Test before committing** — At minimum, verify the build succeeds. For backend changes, hit the relevant API endpoint.
4. **Don't refactor while feature-building** — Separate refactor commits from feature commits.

### Commit Format
```
feat(web_monitor): Add fan speed display to GPU card
fix(data_gobbler): Prevent crash on empty subsystem directory
refactor(web_monitor): Extract network polling into shared hook
docs: Update ARCHITECTURE.md with new port mapping
chore: Bump dash-bootstrap-components to 1.6
```

---

## Phase 3: Close

### Session Close Checklist
- [ ] All changes committed with semantic messages
- [ ] Build succeeds (`npm run build` / `docker compose build`)
- [ ] No `console.log` / `print()` debug statements left in
- [ ] Updated relevant context scope file if architecture changed
- [ ] Added ADR entry if a significant design decision was made
- [ ] Noted any follow-up tasks discovered during the session

### Session Close Notes Template
Add this to your commit message or a scratch file:

```markdown
## Session Close — [DATE]
**Goal**: [What you set out to do]
**Result**: [What actually got done]
**Follow-ups**:
- [ ] [Thing discovered but not addressed]
- [ ] [Thing that needs testing on actual hardware]
**Decisions Made**: [Any new ADRs to log]
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Do This Instead |
|---|---|---|
| "Let me just quickly fix this too" | Scope creep kills context clarity | Note it, do it next session |
| Refactoring + features in one commit | Impossible to review or revert cleanly | Separate commits |
| Editing docker-compose.yml "to test something" | Forgotten temp changes break deploys | Use `docker compose -f override.yml` or revert |
| Skipping the build step | "It looks right" ≠ "it works" | Always build, always verify |
| Reading the entire repo into context | Wastes tokens, confuses the agent | Use context scope files |

---

## Quick Reference: Common Session Types

### "Add a UI feature to the dashboard"
```
Read: CLAUDE.md → context-scopes/web_monitor.md
Edit: frontend/src/components/ and frontend/src/hooks/
Build: cd web_monitor/frontend && npm run build
Test: Open browser, check the feature
Deploy: git push → deploy.sh → "Restart All EXCEPT Ollama"
```

### "Add a new API endpoint"
```
Read: CLAUDE.md → context-scopes/web_monitor.md
Edit: web_monitor/app.py + corresponding frontend hook/component
Build: Frontend build + docker rebuild
Test: curl the endpoint, check frontend integration
Deploy: Same as above
```

### "Work on data_gobbler"
```
Read: CLAUDE.md → context-scopes/data_gobbler.md
Edit: data_gobbler/pages/, components/, or utils/
Build: docker compose up -d --build data_gobbler
Test: Open browser at :8052
```

### "Change Docker infrastructure"
```
Read: CLAUDE.md → context-scopes/infrastructure.md → DECISIONS.md
Edit: docker-compose.yml, deploy.sh, Dockerfiles
Build: docker compose up --build -d
Test: docker compose ps, check all services healthy
```
