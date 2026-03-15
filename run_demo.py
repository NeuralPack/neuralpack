"""End-to-end demo of the NeuralPack pipeline (no LLM, no stdin required).

Simulates a full human → pipeline → gate → complete flow using:
  - neuralpack-tasks  FilesystemStore + PollingWatcher
  - neuralpack-core   MockPipeline (fake agents, real Task records)
  - neuralpack-comms  MessageDispatcher + DefaultGateHandler

Run:
    python run_demo.py
"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

# ── path bootstrap ────────────────────────────────────────────────────────────
_here = Path(__file__).parent
for _repo in ("neuralpack-tasks", "neuralpack-comms", "neuralpack-core"):
    _p = _here / _repo
    if _p.exists():
        sys.path.insert(0, str(_p))

from connectors.base import InboundMessage                   # noqa: E402
from connectors.cli import CLIConnector                      # noqa: E402
from gates.gate_handler import DefaultGateHandler            # noqa: E402
from mocks.pipeline import MockPipeline                      # noqa: E402
from models.gates import GATE_INFO                           # noqa: E402
from router.dispatcher import MessageDispatcher              # noqa: E402
from storage.filesystem import FilesystemStore               # noqa: E402
from storage.watcher import PollingWatcher                   # noqa: E402

_GATE_MAP = {"P4": 1, "P5": 2, "P6": 3}


def _gate_prompt(gate_num: int, pipeline_summary: str = "") -> str:
    """Build a gate decision prompt from GATE_INFO + optional pipeline summary."""
    gate   = GATE_INFO[str(gate_num)]
    opts   = "  |  ".join(f"{k} → {v}" for k, v in gate.options.items())
    header = f"─── Gate {gate_num}: {gate.name} ───\n{gate.question}\n"
    body   = f"{pipeline_summary}\n" if pipeline_summary else ""
    footer = f"\nReply:\n  {opts}"
    return header + body + footer


# ── pretty printer ─────────────────────────────────────────────────────────────
BOLD  = "\033[1m"
DIM   = "\033[2m"
CYAN  = "\033[36m"
GREEN = "\033[32m"
RESET = "\033[0m"


def _print_human(text: str) -> None:
    print(f"\n{BOLD}{CYAN}You:{RESET}  {text}")


def _print_system(text: str) -> None:
    for line in text.strip().splitlines():
        print(f"      {line}")


def _separator() -> None:
    print(f"\n{DIM}{'─' * 60}{RESET}")


# ── demo ───────────────────────────────────────────────────────────────────────

async def run_demo() -> None:
    with tempfile.TemporaryDirectory(prefix="np-demo-") as tmpdir:
        store     = FilesystemStore(Path(tmpdir))
        connector = CLIConnector(colour=True)

        # ── inline sender that calls the connector ─────────────────────────
        class _Sender:
            async def send_gate_summary(
                self, session_id: str, gate: int, summary: str,
                full_report_url: str | None = None,
            ) -> None:
                formatted = connector.format_gate_summary(gate, summary)
                _print_system(formatted)

            async def send_status_update(self, session_id: str, message: str) -> None:
                if message:
                    _print_system(message)

        sender       = _Sender()
        gate_handler = DefaultGateHandler(store, sender)
        dispatcher   = MessageDispatcher(store, gate_handler=gate_handler)
        pipeline     = MockPipeline(store, delay=0.4)   # fast for demo
        watcher      = PollingWatcher(store, interval=0.6)

        # ── register watcher callbacks ─────────────────────────────────────
        async def on_session_active(session) -> None:  # type: ignore[no-untyped-def]
            _print_system(f"[pipeline] Session {session.id[:8]}… starting P1 → P2 → P3")
            await pipeline.start(session.id)

        async def on_gate_waiting(session) -> None:  # type: ignore[no-untyped-def]
            gate    = _GATE_MAP.get(session.current_phase, 1)
            summary = _gate_prompt(gate)
            _separator()
            await sender.send_gate_summary(session.id, gate, summary)

        async def on_gate_decided(session, decision) -> None:  # type: ignore[no-untyped-def]
            gate = int(decision.gate_number)
            _print_system(f"[pipeline] Gate {gate} recorded — continuing…")
            await pipeline.advance(session.id, gate)

        async def on_complete(session) -> None:  # type: ignore[no-untyped-def]
            _separator()
            _print_system(f"{GREEN}🎉  Pipeline complete!  Session {session.id[:8]} → COMPLETED{RESET}")

        watcher.on_session_active    = on_session_active
        watcher.on_gate_waiting      = on_gate_waiting
        watcher.on_gate_decided      = on_gate_decided
        watcher.on_pipeline_complete = on_complete

        watch_task = asyncio.create_task(watcher.run())

        # ── helper: send a message and print reply ──────────────────────────
        async def send(text: str, wait: float = 0.0) -> None:
            _print_human(text)
            msg = InboundMessage(
                channel="cli", sender_id="demo-user",
                raw_text=text, message_id="demo",
            )
            reply = await dispatcher.dispatch(msg)
            if reply:
                _print_system(reply)
            if wait:
                await asyncio.sleep(wait)

        # ── DEMO SEQUENCE ──────────────────────────────────────────────────
        _separator()
        print(f"{BOLD}NeuralPack — end-to-end demo (mock pipeline, no LLM){RESET}")
        _separator()

        # 1. New idea
        await send("An app for emergency vet bookings", wait=0.3)

        # 2. Wait for P1→P2→P3 to complete
        #    8 agents × 0.4s = 3.2s + 0.6s poll buffer = ~4.5s
        print(f"\n{DIM}  … agents running P1 (intake + rationality) …{RESET}")
        await asyncio.sleep(1.5)
        print(f"{DIM}  … P2 (market · tech · bizmodel · devil's advocate) …{RESET}")
        await asyncio.sleep(2.5)
        print(f"{DIM}  … P3 (synthesis + verdict) …{RESET}")
        await asyncio.sleep(2.0)

        # 3. Status check mid-run (may still be running)
        await send("STATUS", wait=0.3)

        # 4. Gate 1 — wait a tick for the gate summary to appear
        await asyncio.sleep(1.0)

        # 5. Human replies GO
        await send("GO", wait=0.3)

        # Wait for P4 (2 agents × 0.4s = 0.8s + poll)
        await asyncio.sleep(2.5)

        # 6. Gate 2
        await send("APPROVE", wait=0.3)

        # Wait for P5 (1 agent × 0.4s + poll)
        await asyncio.sleep(2.0)

        # 7. Gate 3
        await send("APPROVE", wait=0.5)

        # 8. Final status
        await asyncio.sleep(1.0)
        await send("STATUS")

        watch_task.cancel()
        _separator()
        print(f"{BOLD}Demo complete.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
