"""Comprehensive Unit Test Suite for Agentic-OS.

Tests cover:
- MultiplayerRoomDAG mission dependencies, worktree assignment, execution flow, reviews.
- SubscriptionSeat routing, active concurrency limits, and 3-strike circuit breaker fallback.
- RoastRoomSession 3-round debate pipeline with default and dynamic advisors, verdicts, and markdown generation.
- PluginRegistry dependency resolution, capability indexing, topological sorting, validation, and error handling.
- ExplorationLoop human review gate validation, confidence thresholding, atomic file locking, and schema reconciliation diffing.
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

# Ensure agentic-os directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from multiplayer_room import (
    MissionStatus,
    MultiplayerRoomDAG,
    RoomMission,
    RoomType,
    SeatProvider,
    SeatRouter,
    SubscriptionSeat,
)
from roast_room import (
    AdvisorPersona,
    RoastRoomSession,
    VoteType,
    get_default_advisors,
)
from plugin_registry import (
    PluginManifest,
    PluginRegistry,
    PluginRegistryError,
)
from exploration_loop import (
    DiscoveryItem,
    ExplorationLoop,
)


class TestSubscriptionSeatAndSeatRouter(unittest.TestCase):
    """Tests for SubscriptionSeat data structure and SeatRouter logic."""

    def setUp(self):
        self.router = SeatRouter()
        self.seat_claude_1 = SubscriptionSeat(
            seat_id="seat-claude-1",
            provider=SeatProvider.CLAUDE_CODE,
            model="claude-3-7-sonnet",
            max_concurrency=2,
        )
        self.seat_claude_2 = SubscriptionSeat(
            seat_id="seat-claude-2",
            provider=SeatProvider.CLAUDE_CODE,
            model="claude-3-5-haiku",
            max_concurrency=1,
        )
        self.seat_codex = SubscriptionSeat(
            seat_id="seat-codex-1",
            provider=SeatProvider.CODEX,
            model="codex-v2",
            max_concurrency=1,
        )
        self.seat_custom = SubscriptionSeat(
            seat_id="seat-custom-1",
            provider=SeatProvider.CUSTOM_LLM,
            model="deepseek-r1",
            max_concurrency=1,
        )

    def test_seat_registration_and_retrieval(self):
        self.router.register_seat(self.seat_claude_1)
        retrieved = self.router.get_seat("seat-claude-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.seat_id, "seat-claude-1")
        self.assertIsNone(self.router.get_seat("nonexistent-seat"))

    def test_routing_lowest_load_preference(self):
        self.router.register_seat(self.seat_claude_1)
        self.router.register_seat(self.seat_claude_2)

        # Route without preference defaults to fallback chain (CLAUDE_CODE first)
        routed = self.router.route_seat()
        self.assertIsNotNone(routed)
        self.assertEqual(routed.provider, SeatProvider.CLAUDE_CODE)

        # Acquire 1 slot on seat_claude_1 (load = 1/2 = 0.5), seat_claude_2 (load = 0/1 = 0.0)
        self.assertTrue(self.router.acquire_seat("seat-claude-1"))
        next_routed = self.router.route_seat(preferred_provider=SeatProvider.CLAUDE_CODE)
        self.assertEqual(next_routed.seat_id, "seat-claude-2")

    def test_routing_concurrency_limits(self):
        self.router.register_seat(self.seat_codex)
        self.assertTrue(self.router.acquire_seat("seat-codex-1"))
        self.assertEqual(self.seat_codex.active_missions, 1)

        # Capacity exhausted
        self.assertFalse(self.router.acquire_seat("seat-codex-1"))

        # Routing to CODEX now yields None
        routed = self.router.route_seat(preferred_provider=SeatProvider.CODEX)
        self.assertIsNone(routed)

    def test_fallback_chain_routing(self):
        self.router.register_seat(self.seat_codex)
        self.router.register_seat(self.seat_custom)

        # Preferred CLAUDE_CODE not registered -> falls back to CODEX
        routed = self.router.route_seat(preferred_provider=SeatProvider.CLAUDE_CODE)
        self.assertIsNotNone(routed)
        self.assertEqual(routed.seat_id, "seat-codex-1")

        # When CODEX is full, fallback to CUSTOM_LLM
        self.assertTrue(self.router.acquire_seat("seat-codex-1"))
        routed_fallback = self.router.route_seat(preferred_provider=SeatProvider.CLAUDE_CODE)
        self.assertIsNotNone(routed_fallback)
        self.assertEqual(routed_fallback.seat_id, "seat-custom-1")

    def test_three_strike_circuit_breaker(self):
        self.router.register_seat(self.seat_claude_1)

        # Strike 1
        self.assertTrue(self.router.acquire_seat("seat-claude-1"))
        self.router.release_seat("seat-claude-1", success=False)
        self.assertEqual(self.seat_claude_1.consecutive_failures, 1)
        self.assertTrue(self.seat_claude_1.is_healthy)

        # Strike 2
        self.assertTrue(self.router.acquire_seat("seat-claude-1"))
        self.router.release_seat("seat-claude-1", success=False)
        self.assertEqual(self.seat_claude_1.consecutive_failures, 2)
        self.assertTrue(self.seat_claude_1.is_healthy)

        # Strike 3 (Breaker trips)
        self.assertTrue(self.router.acquire_seat("seat-claude-1"))
        self.router.release_seat("seat-claude-1", success=False)
        self.assertEqual(self.seat_claude_1.consecutive_failures, 3)
        self.assertFalse(self.seat_claude_1.is_healthy)
        self.assertEqual(self.seat_claude_1.total_failed, 3)

        # Unhealthy seat cannot be acquired or routed
        self.assertFalse(self.router.acquire_seat("seat-claude-1"))
        self.assertIsNone(self.router.route_seat(preferred_provider=SeatProvider.CLAUDE_CODE))

        # Resetting circuit breaker restores health
        self.assertTrue(self.router.reset_circuit_breaker("seat-claude-1"))
        self.assertTrue(self.seat_claude_1.is_healthy)
        self.assertEqual(self.seat_claude_1.consecutive_failures, 0)
        self.assertTrue(self.router.acquire_seat("seat-claude-1"))

    def test_release_seat_success_clears_failures(self):
        self.router.register_seat(self.seat_claude_1)
        self.assertTrue(self.router.acquire_seat("seat-claude-1"))
        self.router.release_seat("seat-claude-1", success=False)
        self.assertEqual(self.seat_claude_1.consecutive_failures, 1)

        # Next run succeeds -> consecutive_failures reset to 0
        self.assertTrue(self.router.acquire_seat("seat-claude-1"))
        self.router.release_seat("seat-claude-1", success=True)
        self.assertEqual(self.seat_claude_1.consecutive_failures, 0)
        self.assertEqual(self.seat_claude_1.total_completed, 1)


class TestMultiplayerRoomDAG(unittest.TestCase):
    """Tests for MultiplayerRoomDAG orchestration, dependencies, and review gates."""

    def setUp(self):
        self.router = SeatRouter()
        self.seat = SubscriptionSeat(
            seat_id="seat-main",
            provider=SeatProvider.CLAUDE_CODE,
            model="claude-3-7-sonnet",
            max_concurrency=5,
        )
        self.router.register_seat(self.seat)
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.trace_file = Path(self.tmp_dir.name) / "traces.json"
        self.dag = MultiplayerRoomDAG(
            room_id="room-test", router=self.router, trace_file=self.trace_file
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_mission_addition_and_trace_logging(self):
        mission = RoomMission(
            mission_id="m1",
            room_type=RoomType.DEV,
            title="Setup DB schema",
            spec={"tables": ["users", "sessions"]},
            worktree_path="/tmp/worktree-m1",
        )
        self.dag.add_mission(mission)
        self.assertEqual(self.dag.get_mission("m1").title, "Setup DB schema")
        self.assertEqual(self.dag.get_mission("m1").worktree_path, "/tmp/worktree-m1")

        # Verify traces saved to disk
        self.assertTrue(self.trace_file.exists())
        with open(self.trace_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["event"], "MISSION_ADDED")

    def test_dag_dependency_resolution(self):
        m1 = RoomMission(
            mission_id="m1",
            room_type=RoomType.RESEARCH,
            title="Market analysis",
            spec={},
        )
        m2 = RoomMission(
            mission_id="m2",
            room_type=RoomType.DEV,
            title="Core feature dev",
            spec={},
            depends_on=["m1"],
        )
        m3 = RoomMission(
            mission_id="m3",
            room_type=RoomType.OPS,
            title="Deploy release",
            spec={},
            depends_on=["m2"],
        )
        self.dag.add_mission(m1)
        self.dag.add_mission(m2)
        self.dag.add_mission(m3)

        # Initially, only m1 is ready
        ready = self.dag.get_ready_missions()
        self.assertEqual([m.mission_id for m in ready], ["m1"])

        # Execute m1
        self.assertTrue(self.dag.dispatch_mission("m1"))
        self.assertEqual(self.dag.get_mission("m1").status, MissionStatus.COMPLETED)

        # Now m2 is ready
        ready = self.dag.get_ready_missions()
        self.assertEqual([m.mission_id for m in ready], ["m2"])

        # Run all remaining
        dispatched = self.dag.run_all_available()
        self.assertEqual(dispatched, 2)
        self.assertEqual(self.dag.get_mission("m2").status, MissionStatus.COMPLETED)
        self.assertEqual(self.dag.get_mission("m3").status, MissionStatus.COMPLETED)

    def test_dispatch_failed_when_no_seats_available(self):
        # Empty router
        empty_router = SeatRouter()
        dag = MultiplayerRoomDAG(room_id="room-no-seat", router=empty_router)
        m = RoomMission(mission_id="m-isolated", room_type=RoomType.DEV, title="No seats", spec={})
        dag.add_mission(m)
        self.assertFalse(dag.dispatch_mission("m-isolated"))
        self.assertEqual(dag.get_mission("m-isolated").status, MissionStatus.PENDING)

    def test_custom_executor_exception_handling(self):
        def failing_executor(mission: RoomMission):
            raise RuntimeError("Database connection timeout")

        m = RoomMission(mission_id="m-fail", room_type=RoomType.DEV, title="Fail mission", spec={})
        self.dag.add_mission(m)
        success = self.dag.dispatch_mission("m-fail", executor_override=failing_executor)

        self.assertFalse(success)
        self.assertEqual(m.status, MissionStatus.FAILED)
        self.assertIn("Database connection timeout", m.error_message)
        self.assertEqual(self.seat.consecutive_failures, 1)

    def test_human_review_gate_low_confidence(self):
        m = RoomMission(
            mission_id="m-low-conf",
            room_type=RoomType.GROWTH,
            title="Auto-generated ad campaign",
            spec={"simulated_confidence": 0.60},
        )
        self.dag.add_mission(m)
        self.assertTrue(self.dag.dispatch_mission("m-low-conf"))

        # Status should be NEEDS_REVIEW and added to review_inbox
        self.assertEqual(m.status, MissionStatus.NEEDS_REVIEW)
        self.assertEqual(len(self.dag.review_inbox), 1)
        self.assertEqual(self.dag.review_inbox[0]["mission_id"], "m-low-conf")
        self.assertTrue(any("Low confidence score" in r for r in self.dag.review_inbox[0]["reasons"]))

        # Approve review
        approved = self.dag.approve_review("m-low-conf", human_notes="Looks fine to publish")
        self.assertTrue(approved)
        self.assertEqual(m.status, MissionStatus.COMPLETED)
        self.assertTrue(m.output.get("human_review_approved"))
        self.assertEqual(m.output.get("human_notes"), "Looks fine to publish")
        self.assertEqual(len(self.dag.review_inbox), 0)

    def test_human_review_gate_destructive_operation_and_rejection(self):
        m = RoomMission(
            mission_id="m-destructive",
            room_type=RoomType.OPS,
            title="Drop staging tables",
            spec={"is_destructive": True},
        )
        self.dag.add_mission(m)
        self.dag.dispatch_mission("m-destructive")

        self.assertEqual(m.status, MissionStatus.NEEDS_REVIEW)
        self.assertTrue(
            any("Destructive operation detected" in r for r in self.dag.review_inbox[0]["reasons"])
        )

        # Reject review
        rejected = self.dag.reject_review("m-destructive", reason="Staging is still in use by QA")
        self.assertTrue(rejected)
        self.assertEqual(m.status, MissionStatus.FAILED)
        self.assertIn("Staging is still in use by QA", m.error_message)
        self.assertEqual(len(self.dag.review_inbox), 0)


class TestRoastRoomAdvisoryCouncil(unittest.TestCase):
    """Tests for RoastRoomSession 3-round debate pipeline and advisor personas."""

    def setUp(self):
        self.session = RoastRoomSession(room_id="roast-test-room")

    def test_default_advisors_initialization(self):
        advisors = self.session.advisors
        self.assertEqual(len(advisors), 4)
        self.assertIn("Jeff Bezos", advisors)
        self.assertIn("Alex Hormozi", advisors)
        self.assertIn("Warren Buffett & Charlie Munger", advisors)
        self.assertIn("Elon Musk", advisors)

    def test_custom_advisor_addition(self):
        custom = AdvisorPersona(
            name="Peter Thiel",
            core_framework="Zero to One & Monopoly Secrets",
            bias_to_attack="Incremental Copycat Competition",
            decision_axioms=["Competition is for losers", "Secrets exist"],
            key_questions=["What valuable company is nobody building?"],
            archetype_voice="Contrarian, philosophical, monopoly-focused",
            hard_boundary_rule="Never build in a crowded 1-to-N market.",
        )
        self.session.add_custom_advisor(custom)
        self.assertEqual(len(self.session.advisors), 5)
        self.assertIn("Peter Thiel", self.session.advisors)

    def test_conduct_debate_pipeline(self):
        prop = "Rebuild entire UI from scratch in Rust WebAssembly to save 5ms latency."
        record = self.session.conduct_debate(prop)

        self.assertEqual(record["room_id"], "roast-test-room")
        self.assertEqual(record["proposition"], prop)

        # Round 1: 4 critiques
        self.assertEqual(len(record["round_1_critiques"]), 4)
        for critique in record["round_1_critiques"]:
            self.assertIn("advisor", critique)
            self.assertIn("core_framework", critique)
            self.assertTrue(len(critique["critiques"]) > 0)

        # Round 2: 4 cross-examination frictions
        self.assertEqual(len(record["round_2_frictions"]), 4)
        for friction in record["round_2_frictions"]:
            self.assertIn("challenges", friction)

        # Round 3: 4 votes
        self.assertEqual(len(record["round_3_votes"]), 4)
        for vote in record["round_3_votes"]:
            self.assertIn(vote["vote"], [VoteType.APPROVE.value, VoteType.REJECT.value, VoteType.PIVOT.value])

        # Overall verdict calculation
        self.assertIn(record["overall_verdict"], [VoteType.APPROVE.value, VoteType.REJECT.value, VoteType.PIVOT.value])
        self.assertIn("Consensus Verdict:", record["verdict_summary"])

        # History updated
        self.assertEqual(len(self.session.debate_history), 1)

    def test_markdown_export_structure(self):
        prop = "Offer 100% money-back guarantee on enterprise contracts."
        record = self.session.conduct_debate(prop)
        md = self.session.to_markdown(record)

        self.assertIn("# Advisory Council Debate:", md)
        self.assertIn("## Round 1: Blind Axiom Critiques", md)
        self.assertIn("## Round 2: Adversarial Friction Points", md)
        self.assertIn("## Round 3: Final Votes & Actionable Consensus", md)
        self.assertIn("Jeff Bezos", md)


class TestPluginRegistry(unittest.TestCase):
    """Tests for PluginRegistry manifest parsing, dependency resolution, and validation."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.plugins_path = Path(self.tmp_dir.name)
        self.registry = PluginRegistry(plugins_dir=self.plugins_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _create_plugin(self, folder_name: str, manifest_data: dict, has_entrypoint: bool = True):
        plugin_folder = self.plugins_path / folder_name
        plugin_folder.mkdir(parents=True, exist_ok=True)
        manifest_file = plugin_folder / "manifest.json"
        manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")
        if has_entrypoint:
            entrypoint = manifest_data.get("entrypoint", "main.py")
            (plugin_folder / entrypoint).write_text("# entrypoint", encoding="utf-8")
        return plugin_folder

    def test_manifest_discovery_and_capability_indexing(self):
        self._create_plugin("plugin-auth", {
            "id": "plugin-auth",
            "version": "1.0.0",
            "type": "security",
            "entrypoint": "main.py",
            "provides": ["authentication", "oauth2"],
            "requires": [],
        })
        self._create_plugin("plugin-users", {
            "id": "plugin-users",
            "version": "1.2.0",
            "type": "domain",
            "entrypoint": "main.py",
            "provides": ["user-management"],
            "requires": ["plugin-auth"],
        })

        manifests = self.registry.discover_all()
        self.assertEqual(len(manifests), 2)
        self.assertIn("plugin-auth", manifests)
        self.assertIn("plugin-users", manifests)

        # Capability lookup
        auth_providers = self.registry.find_by_capability("authentication")
        self.assertEqual(len(auth_providers), 1)
        self.assertEqual(auth_providers[0].id, "plugin-auth")

    def test_dependency_resolution_topological_sort(self):
        self._create_plugin("core-db", {
            "id": "core-db",
            "provides": ["database"],
            "requires": [],
        })
        self._create_plugin("core-auth", {
            "id": "core-auth",
            "provides": ["auth"],
            "requires": ["core-db"],
        })
        self._create_plugin("app-api", {
            "id": "app-api",
            "provides": ["api"],
            "requires": ["core-auth"],
        })

        self.registry.discover_all()
        order = self.registry.resolve_dependencies("app-api")
        self.assertEqual(order, ["core-db", "core-auth", "app-api"])

    def test_circular_dependency_detection(self):
        self._create_plugin("cycle-a", {
            "id": "cycle-a",
            "requires": ["cycle-b"],
        })
        self._create_plugin("cycle-b", {
            "id": "cycle-b",
            "requires": ["cycle-a"],
        })

        self.registry.discover_all()
        with self.assertRaises(PluginRegistryError):
            self.registry.resolve_dependencies("cycle-a")

    def test_invalid_plugin_id_and_missing_dependency_validation(self):
        # Invalid plugin ID
        bad_folder = self.plugins_path / "bad-plugin"
        bad_folder.mkdir()
        (bad_folder / "manifest.json").write_text(json.dumps({"id": "BAD_ID!@#"}), encoding="utf-8")

        with self.assertRaises(PluginRegistryError):
            self.registry.discover_all()

        # Fix bad manifest to test missing dependency / missing entrypoint validation
        (bad_folder / "manifest.json").write_text(json.dumps({
            "id": "bad-plugin",
            "entrypoint": "missing.py",
            "requires": ["ghost-dependency"]
        }), encoding="utf-8")

        self.registry.discover_all()
        errors = self.registry.validate_all()
        self.assertIn("bad-plugin", errors)
        self.assertTrue(any("Missing required dependency: ghost-dependency" in e for e in errors["bad-plugin"]))
        self.assertTrue(any("Entrypoint missing.py does not exist" in e for e in errors["bad-plugin"]))


class TestExplorationLoop(unittest.TestCase):
    """Tests for ExplorationLoop human review gating, confidence thresholding, and reconciliation."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.vault_root = Path(self.tmp_dir.name)
        self.loop = ExplorationLoop(vault_root=self.vault_root)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_score_and_gate_job_search_domain(self):
        item = DiscoveryItem(
            id="job-1",
            domain="job_search",
            title="Senior Architect Role at Scale AI",
            content="Job details and link...",
            confidence_score=0.99,
        )
        allowed, reason = self.loop.score_and_gate(item)
        self.assertFalse(allowed)
        self.assertTrue(item.requires_human_gate)
        self.assertIn("Job submission gated", reason)

    def test_score_and_gate_low_confidence(self):
        item = DiscoveryItem(
            id="disc-low",
            domain="backend_patterns",
            title="Unverified caching pattern",
            content="Pattern details...",
            confidence_score=0.72,
        )
        allowed, reason = self.loop.score_and_gate(item)
        self.assertFalse(allowed)
        self.assertTrue(item.requires_human_gate)
        self.assertIn("Low confidence (0.72)", reason)

    def test_score_and_gate_high_confidence_auto_pass(self):
        item = DiscoveryItem(
            id="disc-high",
            domain="system_design",
            title="Distributed lock with Redis Redlock",
            content="Documentation on Redlock algorithm...",
            confidence_score=0.92,
        )
        allowed, reason = self.loop.score_and_gate(item)
        self.assertTrue(allowed)
        self.assertFalse(item.requires_human_gate)
        self.assertEqual(reason, "Passed auto-write criteria")

    def test_process_item_lifecycle_gated_vs_written(self):
        # 1. Process Gated Item
        gated_item = DiscoveryItem(
            id="gated-1",
            domain="job_search",
            title="Staff SRE",
            content="Apply via portal...",
            confidence_score=0.95,
        )
        res_gated = self.loop.process_item(gated_item)
        self.assertEqual(res_gated, "GATED")
        self.assertTrue(self.loop.review_inbox.exists())
        inbox_content = self.loop.review_inbox.read_text(encoding="utf-8")
        self.assertIn("GATED ITEM: Staff SRE", inbox_content)

        # 2. Process Clean Item
        clean_item = DiscoveryItem(
            id="clean-1",
            domain="algorithms",
            title="Raft Consensus Overview",
            content="# Raft Protocol\nLeader election and log replication.",
            confidence_score=0.88,
        )
        res_clean = self.loop.process_item(clean_item)
        self.assertEqual(res_clean, "WRITTEN")
        target_file = self.vault_root / "wiki" / "discoveries" / "clean-1.md"
        self.assertTrue(target_file.exists())
        self.assertEqual(target_file.read_text(encoding="utf-8"), clean_item.content)

        # Check audit log entries
        self.assertTrue(self.loop.log_file.exists())
        log_content = self.loop.log_file.read_text(encoding="utf-8")
        self.assertIn("TRACE:gated-1", log_content)
        self.assertIn("TRACE:clean-1", log_content)

    def test_reconcile_schema_critical_diff_generation(self):
        agents_file = self.vault_root / "AGENTS.md"
        agents_file.write_text("# Agents\n- backend_architect: v1.0\n", encoding="utf-8")

        new_agents_content = "# Agents\n- backend_architect: v2.0\n- ops_specialist: v1.0\n"
        normal_file = self.vault_root / "notes.md"

        proposed = {
            agents_file: new_agents_content,
            normal_file: "# Regular Note",
        }

        results = self.loop.reconcile_schema(proposed)
        self.assertEqual(results[str(agents_file)], "DIFF_QUEUED_IN_REVIEW_INBOX")
        self.assertEqual(results[str(normal_file)], "WRITTEN_AUTO")

        # Review inbox must contain unified diff
        inbox_text = self.loop.review_inbox.read_text(encoding="utf-8")
        self.assertIn("Schema/Agent Update Diff for AGENTS.md", inbox_text)
        self.assertIn("+- backend_architect: v2.0", inbox_text)
        self.assertIn("+- ops_specialist: v1.0", inbox_text)


if __name__ == "__main__":
    unittest.main()
