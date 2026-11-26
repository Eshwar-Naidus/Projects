#!/usr/bin/env python3
"""Interactive REPL Shell for Hermes Agentic OS & Roast Room."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from multiplayer_room import MultiplayerRoomDAG, SeatRouter, RoomType, SeatProvider, SubscriptionSeat, RoomMission
from roast_room import RoastRoomSession

def print_banner():
    print("""
======================================================================
  ⚡ HERMES AGENTIC-OS: INTERACTIVE OPERATOR CONSOLE ⚡
  Commands:
    • status              - View all mission DAGs and room status
    • seats               - View BYO subscription seat pool
    • dispatch <room>     - Dispatch mission to room (RESEARCH, DEV, OPS, GROWTH, ADVISORY)
    • roast <proposal>    - Run 4-operator adversarial debate
    • help                - Show command list
    • exit                - Terminate console
======================================================================
""")

def main():
    print_banner()

    router = SeatRouter()
    router.register_seat(SubscriptionSeat(seat_id='seat-claude-01', provider=SeatProvider.CLAUDE_CODE, model='claude-opus-5-5', max_concurrency=4))
    router.register_seat(SubscriptionSeat(seat_id='seat-codex-01', provider=SeatProvider.CODEX, model='gpt-5-codex', max_concurrency=3))
    router.register_seat(SubscriptionSeat(seat_id='seat-custom-01', provider=SeatProvider.CUSTOM_LLM, model='deepseek-r1-local', max_concurrency=2))

    dag = MultiplayerRoomDAG(room_id='interactive-session', router=router)
    mission_seq = 1

    while True:
        try:
            cmd_line = input("operator@agentic-os> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Exiting interactive console.")
            break

        if not cmd_line:
            continue

        parts = cmd_line.split(" ", 1)
        action = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if action in ("exit", "quit", "q"):
            print("[INFO] Exiting interactive console.")
            break

        elif action == "seats":
            print("\n--- BYO Subscription Seats ---")
            for s in router.seats.values():
                print(f"  • {s.seat_id:<18} | Provider: {s.provider.value:<12} | Model: {s.model:<18} | Max: {s.max_concurrency}")
            print()

        elif action == "status":
            print("\n--- Active Missions DAG ---")
            if not dag.missions:
                print("  (No active missions registered)")
            for m in dag.missions.values():
                seat_str = m.assigned_seat if m.assigned_seat else "NONE"
                print(f"  • [{m.mission_id}] {m.title:<38} | Room: {m.room_type.value:<10} | Seat: {seat_str:<16} | Status: {m.status.value}")
            print()

        elif action == "dispatch":
            room_name = args.strip().upper() if args else "DEV"
            try:
                room_enum = RoomType[room_name]
            except KeyError:
                print(f"[ERROR] Unknown room '{room_name}'. Valid: {[r.name for r in RoomType]}")
                continue

            m_id = f"m-{mission_seq:03d}"
            mission_seq += 1
            mission = RoomMission(
                mission_id=m_id,
                room_type=room_enum,
                title=f"Interactive Mission in {room_enum.value}",
                spec={"source": "interactive-console"}
            )
            dag.add_mission(mission)
            dag.dispatch_mission(m_id)
            updated = dag.get_mission(m_id)
            print(f"[SUCCESS] Dispatched [{updated.mission_id}] to {updated.room_type.value} | Seat: {updated.assigned_seat} | Status: {updated.status.value}")

        elif action == "roast":
            proposal = args.strip() or "Standard Architecture Proposition"
            print(f"\n[ROAST ROOM] Convening 4-Operator Chamber on: \"{proposal}\"...")
            session = RoastRoomSession(room_id="interactive-roast")
            result = session.conduct_debate(proposal)
            print(f"  • Verdict Summary: {result['verdict_summary']}")
            for vote in result.get('round_3_votes', []):
                print(f"    - {vote['advisor']:<26}: {vote['vote']:<8} | \"{vote['rationale']}\"")
            print()

        elif action == "help":
            print_banner()

        else:
            print(f"[ERROR] Unknown command '{action}'. Type 'help' for command list.")

if __name__ == "__main__":
    main()
