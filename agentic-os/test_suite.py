import unittest
from pathlib import Path
import tempfile
import json

from exploration_loop import ExplorationLoop, DiscoveryItem
from multiplayer_room import (
    SeatRouter,
    SubscriptionSeat,
    MultiplayerRoomDAG,
    RoomMission,
    RoomType,
    SeatProvider,
    MissionStatus
)
from roast_room import RoastRoomSession, AdvisorPersona, VoteType, get_default_advisors
from plugin_registry import PluginRegistry, PluginManifest


class TestAgenticOS(unittest.TestCase):
    def test_roast_room_execution(self):
        session = RoastRoomSession()
        record = session.conduct_debate(
            proposition="Refactor monolith to 50 microservices"
        )
        self.assertIn("overall_verdict", record)
        self.assertIn("verdict_summary", record)
        self.assertEqual(len(record["round_1_critiques"]), 4)
        self.assertEqual(len(record["round_3_votes"]), 4)

        md = session.to_markdown(record)
        self.assertIn("Advisory Council Debate", md)

    def test_multiplayer_room_dag_and_routing(self):
        router = SeatRouter()
        seat = SubscriptionSeat(
            seat_id="seat-claude-1",
            provider=SeatProvider.CLAUDE_CODE,
            model="claude-opus-5-5",
            max_concurrency=2
        )
        router.register_seat(seat)
        self.assertTrue(seat.is_healthy)

        # Test routing
        routed = router.route_seat(preferred_provider=SeatProvider.CLAUDE_CODE)
        self.assertIsNotNone(routed)
        self.assertEqual(routed.seat_id, "seat-claude-1")

        # Test DAG
        dag = MultiplayerRoomDAG(room_id="dev-room-01", router=router)
        m1 = RoomMission(
            mission_id="m1",
            room_type=RoomType.DEV,
            title="Step 1",
            spec={"task": "init"}
        )
        m2 = RoomMission(
            mission_id="m2",
            room_type=RoomType.DEV,
            title="Step 2",
            spec={"task": "execute"},
            depends_on=["m1"]
        )
        dag.add_mission(m1)
        dag.add_mission(m2)

        ready = dag.get_ready_missions()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].mission_id, "m1")

    def test_plugin_registry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            manifest_file = p / "plugin.json"
            manifest_file.write_text(json.dumps({
                "id": "test-plugin",
                "version": "1.0.0",
                "type": "tool",
                "entrypoint": "main.py",
                "provides": ["testing"],
                "requires": []
            }))

            registry = PluginRegistry(plugins_dir=p)
            manifest = registry.load_manifest_file(manifest_file)
            self.assertEqual(manifest.id, "test-plugin")
            self.assertEqual(manifest.provides, ["testing"])


if __name__ == "__main__":
    unittest.main()
