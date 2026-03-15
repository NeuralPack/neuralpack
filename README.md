# NeuralPack

AI-powered idea-to-architecture pipeline. Submit an idea over WhatsApp, Discord, Slack, or CLI — NeuralPack runs P1–P5 research and design agents, pauses at three human gates, and delivers a vetted architecture ready to build.

```
Idea → P1 intake → P2 research → P3 synthesis
     ↓ Gate 1 (GO/PIVOT/DROP)
       → P4 product design
     ↓ Gate 2 (APPROVE/REVISE/PARK)
       → P5 architecture
     ↓ Gate 3 (APPROVE/REDESIGN/DESCOPE)
       → Ready to build
```

---

## Repos

| Repo | Role | Status |
|------|------|--------|
| [neuralpack-tasks](neuralpack-tasks/) | Session state · task tree · phase tracker | public |
| [neuralpack-comms](neuralpack-comms/) | WhatsApp · Discord · Slack · CLI · human gates | public |
| [neuralpack-core](neuralpack-core/) | P1–P5 agents · orchestrator · model router | private |
| [neuralpack-skills](neuralpack-skills/) | 12 SKILL.md domains loaded at agent runtime | private |
| [neuralpack-tools](neuralpack-tools/) | MCP servers: web_search · scrape · knowledge base | private |
| [neuralpack-evals](neuralpack-evals/) | Phase quality gates · LLM-as-judge scoring | private |
| [neuralpack-infra](neuralpack-infra/) | Docker · RunPod · Go CLI | private |
| [neuralpack-ui](neuralpack-ui/) | Gradio dashboard for sessions | private |

---

## Quick start

```bash
# 1. Clone with all submodules
git clone --recurse-submodules https://github.com/NeuralPack/neuralpack.git
cd neuralpack

# 2. Install into a venv
make init

# 3. Run the end-to-end demo (no LLM required)
make demo

# 4. Start the interactive CLI with mock pipeline
make run-mock
```

---

## Common commands

```bash
make help          # show all available commands

make init          # first-time setup: clone submodules + install packages
make update        # pull latest for all submodules

make demo          # scripted end-to-end demo (no stdin, no LLM)
make run           # interactive CLI, no mock
make run-mock      # interactive CLI with mock pipeline
make run-debug     # interactive CLI with mock + DEBUG logs

make inspect                  # list all sessions
make inspect-session ID=a3f2  # inspect one session by prefix

make test          # run all tests (tasks + comms)
make lint          # ruff lint + format check
```

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEURALPACK_SESSIONS_DIR` | `./sessions` | Where session JSON files are stored |
| `NEURALPACK_COMMS_MOCK_PIPELINE` | `false` | `true` to activate mock agents |
| `NEURALPACK_COMMS_LOG_LEVEL` | `WARNING` | `DEBUG` · `INFO` · `WARNING` |
| `NEURALPACK_COMMS_MOCK_DELAY` | `1.5` | Seconds per simulated agent |

Full reference: [neuralpack-comms/docs/runbook.md](neuralpack-comms/docs/runbook.md)

---

## Architecture

All services communicate through the shared task store — comms and core never call each other directly. See [ADR 008](neuralpack-tasks/docs/decisions/008-task-tree-as-message-bus.md).

```
  [Human]
     │  WhatsApp / Discord / Slack / CLI
     ▼
[neuralpack-comms]  ──write──▶  [neuralpack-tasks store]  ◀──read/write──  [neuralpack-core]
     │                                  │
     └──read (PollingWatcher)────────────┘
```
