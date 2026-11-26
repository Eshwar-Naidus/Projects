"""Multiplayer Room Engine for Agentic OS.

Zero external dependencies. Python 3.12 stdlib only.
Implements multi-tenant agent rooms, seat routing, circuit breaking,
DAG mission dependency resolution, and human review gating.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
import re
import threading
from typing import Any, Dict, List, Optional, Set
import uuid


class RoomType(str, Enum):
    RESEARCH = "RESEARCH"
    DEV = "DEV"
    OPS = "OPS"
    GROWTH = "GROWTH"
    ADVISORY = "ADVISORY"


class SeatProvider(str, Enum):
    CLAUDE_CODE = "CLAUDE_CODE"
    CODEX = "CODEX"
    CUSTOM_LLM = "CUSTOM_LLM"


class MissionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class SubscriptionSeat:
    seat_id: str
    provider: SeatProvider
    model: str
    max_concurrency: int = 1
    active_missions: int = 0
    is_healthy: bool = True
    consecutive_failures: int = 0
    total_completed: int = 0
    total_failed: int = 0


@dataclass
class RoomMission:
    mission_id: str
    room_type: RoomType
    title: str
    spec: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    assigned_seat: Optional[str] = None
    status: MissionStatus = MissionStatus.PENDING
    output: Optional[Dict[str, Any]] = None
    worktree_path: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class SeatRouter:
    """Manages subscription seats, concurrency allocation, fallbacks, and circuit breaking."""

    CIRCUIT_BREAKER_THRESHOLD: int = 3

    def __init__(self) -> None:
        self.seats: Dict[str, SubscriptionSeat] = {}
        self.provider_fallback_chain: List[SeatProvider] = [
            SeatProvider.CLAUDE_CODE,
            SeatProvider.CODEX,
            SeatProvider.CUSTOM_LLM,
        ]
        self._lock: threading.RLock = threading.RLock()

    def register_seat(self, seat: SubscriptionSeat) -> None:
        with self._lock:
            self.seats[seat.seat_id] = seat

    def get_seat(self, seat_id: str) -> Optional[SubscriptionSeat]:
        with self._lock:
            return self.seats.get(seat_id)

    def route_seat(
        self, preferred_provider: Optional[SeatProvider] = None
    ) -> Optional[SubscriptionSeat]:
        """Select healthy seat with lowest load respecting provider fallback chain."""
        with self._lock:
            chain = (
                [preferred_provider]
                + [p for p in self.provider_fallback_chain if p != preferred_provider]
                if preferred_provider
                else list(self.provider_fallback_chain)
            )

            for provider in chain:
                candidates = [
                    s
                    for s in self.seats.values()
                    if s.provider == provider
                    and s.is_healthy
                    and s.active_missions < s.max_concurrency
                ]
                if candidates:
                    # Lowest load first
                    candidates.sort(key=lambda s: (s.active_missions / s.max_concurrency))
                    return candidates[0]
            return None

    def acquire_seat(self, seat_id: str) -> bool:
        with self._lock:
            seat = self.seats.get(seat_id)
            if not seat or not seat.is_healthy or seat.active_missions >= seat.max_concurrency:
                return False
            seat.active_missions += 1
            return True

    def release_seat(self, seat_id: str, success: bool = True) -> None:
        with self._lock:
            seat = self.seats.get(seat_id)
            if not seat:
                return
            if seat.active_missions > 0:
                seat.active_missions -= 1

            if success:
                seat.consecutive_failures = 0
                seat.total_completed += 1
            else:
                seat.consecutive_failures += 1
                seat.total_failed += 1
                # Trip circuit breaker on threshold
                if seat.consecutive_failures >= self.CIRCUIT_BREAKER_THRESHOLD:
                    seat.is_healthy = False

    def reset_circuit_breaker(self, seat_id: str) -> bool:
        with self._lock:
            seat = self.seats.get(seat_id)
            if not seat:
                return False
            seat.consecutive_failures = 0
            seat.is_healthy = True
            return True


class MultiplayerRoomDAG:
    """DAG orchestrator for missions across multiplayer rooms with human review gates."""

    CONFIDENCE_THRESHOLD: float = 0.75

    def __init__(self, room_id: str, router: SeatRouter, trace_file: Optional[Path] = None) -> None:
        self.room_id: str = room_id
        self.router: SeatRouter = router
        self.missions: Dict[str, RoomMission] = {}
        self.review_inbox: List[Dict[str, Any]] = []
        self.traces: List[Dict[str, Any]] = []
        self.trace_file: Optional[Path] = trace_file

    def add_mission(self, mission: RoomMission) -> None:
        self.missions[mission.mission_id] = mission
        self._log_trace(
            event="MISSION_ADDED",
            mission_id=mission.mission_id,
            details={"title": mission.title, "depends_on": mission.depends_on},
        )

    def get_mission(self, mission_id: str) -> Optional[RoomMission]:
        return self.missions.get(mission_id)

    def get_ready_missions(self) -> List[RoomMission]:
        """Missions whose dependencies have completed successfully."""
        ready: List[RoomMission] = []
        for mission in self.missions.values():
            if mission.status != MissionStatus.PENDING:
                continue
            deps_satisfied = True
            for dep_id in mission.depends_on:
                dep = self.missions.get(dep_id)
                if not dep or dep.status != MissionStatus.COMPLETED:
                    deps_satisfied = False
                    break
            if deps_satisfied:
                ready.append(mission)
        return ready

    def dispatch_mission(
        self,
        mission_id: str,
        preferred_provider: Optional[SeatProvider] = None,
        executor_override: Optional[Any] = None,
    ) -> bool:
        """Route, allocate seat, execute or gate mission."""
        mission = self.missions.get(mission_id)
        if not mission or mission.status != MissionStatus.PENDING:
            return False

        # Route seat
        seat = self.router.route_seat(preferred_provider=preferred_provider)
        if not seat:
            self._log_trace(
                event="DISPATCH_FAILED_NO_SEAT",
                mission_id=mission_id,
                details={"reason": "No healthy seat available with free capacity"},
            )
            return False

        if not self.router.acquire_seat(seat.seat_id):
            return False

        mission.assigned_seat = seat.seat_id
        mission.status = MissionStatus.RUNNING
        mission.started_at = datetime.now(timezone.utc).isoformat()

        self._log_trace(
            event="MISSION_DISPATCHED",
            mission_id=mission_id,
            details={"seat_id": seat.seat_id, "provider": seat.provider.value},
        )

        # Execute mission
        try:
            raw_output = (
                executor_override(mission)
                if executor_override
                else self._default_mock_executor(mission)
            )

            # Check human-in-the-loop review gate
            requires_review, review_reasons = self._check_review_gate(mission, raw_output)

            if requires_review:
                mission.status = MissionStatus.NEEDS_REVIEW
                mission.output = raw_output
                review_item = {
                    "review_id": str(uuid.uuid4()),
                    "mission_id": mission.mission_id,
                    "title": mission.title,
                    "reasons": review_reasons,
                    "output": raw_output,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                self.review_inbox.append(review_item)
                self.router.release_seat(seat.seat_id, success=True)
                self._log_trace(
                    event="MISSION_GATED_FOR_REVIEW",
                    mission_id=mission_id,
                    details=review_item,
                )
                return True

            # Completed cleanly
            mission.status = MissionStatus.COMPLETED
            mission.output = raw_output
            mission.completed_at = datetime.now(timezone.utc).isoformat()
            self.router.release_seat(seat.seat_id, success=True)

            self._log_trace(
                event="MISSION_COMPLETED",
                mission_id=mission_id,
                details={"confidence": raw_output.get("confidence", 1.0)},
            )
            return True

        except Exception as exc:
            mission.status = MissionStatus.FAILED
            mission.error_message = str(exc)
            mission.completed_at = datetime.now(timezone.utc).isoformat()
            self.router.release_seat(seat.seat_id, success=False)

            self._log_trace(
                event="MISSION_FAILED",
                mission_id=mission_id,
                details={"error": str(exc), "seat_id": seat.seat_id},
            )
            return False

    def approve_review(self, mission_id: str, human_notes: str = "") -> bool:
        mission = self.missions.get(mission_id)
        if not mission or mission.status != MissionStatus.NEEDS_REVIEW:
            return False

        mission.status = MissionStatus.COMPLETED
        mission.completed_at = datetime.now(timezone.utc).isoformat()
        if mission.output:
            mission.output["human_review_approved"] = True
            mission.output["human_notes"] = human_notes

        self.review_inbox = [
            item for item in self.review_inbox if item["mission_id"] != mission_id
        ]

        self._log_trace(
            event="MISSION_REVIEW_APPROVED",
            mission_id=mission_id,
            details={"human_notes": human_notes},
        )
        return True

    def reject_review(self, mission_id: str, reason: str = "") -> bool:
        mission = self.missions.get(mission_id)
        if not mission or mission.status != MissionStatus.NEEDS_REVIEW:
            return False

        mission.status = MissionStatus.FAILED
        mission.error_message = f"Rejected in human review: {reason}"
        mission.completed_at = datetime.now(timezone.utc).isoformat()

        self.review_inbox = [
            item for item in self.review_inbox if item["mission_id"] != mission_id
        ]

        self._log_trace(
            event="MISSION_REVIEW_REJECTED",
            mission_id=mission_id,
            details={"reasons": reason},
        )
        return True

    def run_all_available(self, max_iterations: int = 20) -> int:
        """Resolve DAG step-by-step dispatching ready missions until none remain."""
        dispatched_count = 0
        iteration = 0

        while iteration < max_iterations:
            ready = self.get_ready_missions()
            if not ready:
                break
            any_dispatched = False
            for mission in ready:
                success = self.dispatch_mission(mission.mission_id)
                if success:
                    dispatched_count += 1
                    any_dispatched = True
            if not any_dispatched:
                break
            iteration += 1

        return dispatched_count

    def _check_review_gate(
        self, mission: RoomMission, output: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        reasons: List[str] = []

        # 1. Destructive operations check
        is_destructive = mission.spec.get("is_destructive", False) or output.get(
            "destructive_operation", False
        )
        if is_destructive:
            reasons.append("Destructive operation detected requiring operator signoff")

        # 2. Confidence threshold check (< 0.75)
        confidence = output.get("confidence", 1.0)
        if confidence < self.CONFIDENCE_THRESHOLD:
            reasons.append(
                f"Low confidence score ({confidence:.2f} < {self.CONFIDENCE_THRESHOLD})"
            )

        # 3. Explicit review flag
        if mission.spec.get("force_review", False):
            reasons.append("Mission marked with mandatory review flag")

        return (len(reasons) > 0, reasons)

    def _default_mock_executor(self, mission: RoomMission) -> Dict[str, Any]:
        """Default deterministic execution for spec testing."""
        safe_mission_id = re.sub(r"[^a-zA-Z0-9_-]", "_", mission.mission_id)
        return {
            "summary": f"Executed mission {mission.title}",
            "confidence": mission.spec.get("simulated_confidence", 0.95),
            "destructive_operation": mission.spec.get("is_destructive", False),
            "artifacts": [f"/tmp/artifacts/{safe_mission_id}.json"],
        }

    def _log_trace(self, event: str, mission_id: Optional[str], details: Dict[str, Any]) -> None:
        entry = {
            "trace_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "room_id": self.room_id,
            "mission_id": mission_id,
            "event": event,
            "details": details,
        }
        self.traces.append(entry)
        if self.trace_file:
            self.save_traces(self.trace_file)

    def save_traces(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.traces, f, indent=2)


if __name__ == "__main__":
    print("=== Multiplayer Room Engine Self-Test ===")

    # 1. Router & Seats Setup
    router = SeatRouter()
    seat_claude = SubscriptionSeat(
        seat_id="seat-claude-primary",
        provider=SeatProvider.CLAUDE_CODE,
        model="claude-3-7-sonnet",
        max_concurrency=2,
    )
    seat_codex = SubscriptionSeat(
        seat_id="seat-codex-fallback",
        provider=SeatProvider.CODEX,
        model="gpt-4o",
        max_concurrency=1,
    )
    router.register_seat(seat_claude)
    router.register_seat(seat_codex)

    # 2. Room & DAG Setup
    trace_path = Path("/tmp/agentic_room_trace.json")
    room_dag = MultiplayerRoomDAG(room_id="room-eng-alpha", router=router, trace_file=trace_path)

    # 3. Mission DAG:
    # M1 (Research) -> M2 (Dev) & M3 (Low Confidence Dev) -> M4 (Destructive Ops Deploy)
    m1 = RoomMission(
        mission_id="m1-research",
        room_type=RoomType.RESEARCH,
        title="Analyze Architecture Specs",
        spec={"simulated_confidence": 0.92},
    )
    m2 = RoomMission(
        mission_id="m2-dev-core",
        room_type=RoomType.DEV,
        title="Implement Core Engine",
        spec={"simulated_confidence": 0.88},
        depends_on=["m1-research"],
    )
    m3 = RoomMission(
        mission_id="m3-dev-edge",
        room_type=RoomType.DEV,
        title="Implement Ambiguous Edge Case",
        spec={"simulated_confidence": 0.60},  # Low confidence (<0.75) -> Needs review
        depends_on=["m1-research"],
    )
    m4 = RoomMission(
        mission_id="m4-ops-deploy",
        room_type=RoomType.OPS,
        title="Production Deployment Drop",
        spec={"is_destructive": True, "simulated_confidence": 0.99},  # Destructive -> Needs review
        depends_on=["m2-dev-core"],
    )

    for m in [m1, m2, m3, m4]:
        room_dag.add_mission(m)

    # 4. Resolve Stage 1 (M1 runs and finishes)
    dispatched = room_dag.run_all_available()
    print(f"[Stage 1] Dispatched missions count: {dispatched}")
    assert room_dag.get_mission("m1-research").status == MissionStatus.COMPLETED

    # 5. Resolve Stage 2 (M2 completes, M3 gated for low confidence)
    dispatched = room_dag.run_all_available()
    print(f"[Stage 2] Dispatched missions count: {dispatched}")
    assert room_dag.get_mission("m2-dev-core").status == MissionStatus.COMPLETED
    assert room_dag.get_mission("m3-dev-edge").status == MissionStatus.NEEDS_REVIEW
    print(f"[Stage 2] Review inbox size: {len(room_dag.review_inbox)}")

    # 6. Resolve Stage 3 (M4 runs because M2 is completed, but gates for destructive ops)
    dispatched = room_dag.run_all_available()
    print(f"[Stage 3] Dispatched missions count: {dispatched}")
    assert room_dag.get_mission("m4-ops-deploy").status == MissionStatus.NEEDS_REVIEW
    print(f"[Stage 3] Review inbox size: {len(room_dag.review_inbox)}")

    # 7. Operator Approval in Human-in-the-Loop Gate
    print("Approving pending reviews in Human Review Gate...")
    for item in list(room_dag.review_inbox):
        print(f" -> Approving {item['mission_id']}: {item['reasons']}")
        room_dag.approve_review(item["mission_id"], human_notes="Verified by system operator.")

    assert len(room_dag.review_inbox) == 0
    assert room_dag.get_mission("m3-dev-edge").status == MissionStatus.COMPLETED
    assert room_dag.get_mission("m4-ops-deploy").status == MissionStatus.COMPLETED

    # 8. Test Circuit Breaker
    print("Testing Circuit Breaker on seat failures...")
    test_seat = SubscriptionSeat(
        seat_id="seat-flaky",
        provider=SeatProvider.CUSTOM_LLM,
        model="custom-small",
        max_concurrency=1,
    )
    router.register_seat(test_seat)

    # Trigger 3 failures
    router.acquire_seat("seat-flaky")
    router.release_seat("seat-flaky", success=False)
    router.acquire_seat("seat-flaky")
    router.release_seat("seat-flaky", success=False)
    router.acquire_seat("seat-flaky")
    router.release_seat("seat-flaky", success=False)

    assert not test_seat.is_healthy, "Circuit breaker failed to trip after 3 failures"
    print(f"Seat healthy status after 3 failures: {test_seat.is_healthy} (tripped successfully)")

    router.reset_circuit_breaker("seat-flaky")
    assert test_seat.is_healthy, "Circuit breaker failed to reset"
    print("Circuit breaker reset successfully.")

    print("\nAll multiplayer room self-tests passed cleanly.")
