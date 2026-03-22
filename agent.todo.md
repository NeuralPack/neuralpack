# Agent Todo

## Workflow Snapshot

- Current Phase: G6 Ship & Learn
- Next Phase: Complete
- Scope: decouple `neuralpack-comms` behind a minimal backend interface while keeping local CLI and test flows working

## Gate Status

| Gate | Name | Status | Evidence | Skip Reason |
|------|------|--------|----------|-------------|
| G0 | Discovery | Skipped | Conversation on 2026-03-22 captured architecture direction | User requested moving directly into implementation after clarifying the target architecture in-thread |
| G1 | Requirements | Skipped | Conversation on 2026-03-22 captured backend-boundary requirements | User requested code changes rather than a standalone requirements artifact |
| G2 | Design | Passed | `neuralpack-comms/SPEC.md`; `neuralpack-comms/docs/architecture.md`; `neuralpack-comms/docs/decisions/008-backend-boundary-and-session-identity.md` | — |
| G3 | POC / Spike | N/A | Backend extraction was low-risk and validated directly through local tests/demo | No separate spike required |
| G4 | Implementation | Passed | `neuralpack-comms/backend/`; updated dispatcher/handlers/CLI/demo/tests | — |
| G5 | Review | Passed | Local `pytest`, `mypy`, `ruff`, `polyagentctl check --strict`, CLI smoke test, demo run | — |
| G6 | Ship & Learn | Not Started | — | — |

## Review Notes

- Review focus: keep `neuralpack-comms` independently runnable while reducing direct coupling to `neuralpack-tasks` at the comms boundary.
- Verification target: package tests, static checks, installed CLI smoke test, and repo strict gate.
