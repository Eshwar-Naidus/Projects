"""Roast Room Advisory Council Engine.

Pure Python 3.12 stdlib implementation of an adversarial advisory council.
Evaluates propositions through core mental models and decision frameworks
of elite operators (Bezos, Hormozi, Buffett/Munger, Musk, custom).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from typing import Any, Dict, List, Optional


class VoteType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PIVOT = "PIVOT"


@dataclass
class AdvisorPersona:
    name: str
    core_framework: str
    bias_to_attack: str
    decision_axioms: List[str]
    key_questions: List[str]
    archetype_voice: str
    hard_boundary_rule: str

    def evaluate_proposition(self, proposition: str) -> Dict[str, Any]:
        critiques = []
        for axiom in self.decision_axioms:
            critiques.append(f"[{self.name} Axiom: '{axiom}'] Evaluated against: {proposition[:100]}...")
        
        return {
            "advisor": self.name,
            "core_framework": self.core_framework,
            "critiques": critiques,
            "attacking_bias": self.bias_to_attack,
            "key_question": self.key_questions[0] if self.key_questions else "What is the true bottleneck?",
            "hard_boundary": self.hard_boundary_rule
        }

    def cross_examine(self, peer_critique: Dict[str, Any]) -> str:
        return (
            f"{self.name} challenges {peer_critique['advisor']}: "
            f"Over-indexing on '{peer_critique['core_framework']}' ignores our hard boundary: '{self.hard_boundary_rule}'."
        )

    def cast_final_vote(self, proposition: str, debate_summary: List[str]) -> Dict[str, Any]:
        if "reversibility" in self.core_framework.lower():
            vote = VoteType.APPROVE
            rationale = "Type 2 decision: high reversibility and speed beats perfect information."
        elif "moat" in self.core_framework.lower():
            vote = VoteType.PIVOT
            rationale = "Lacks durable pricing power and long-term defensible moat."
        elif "physics" in self.core_framework.lower():
            vote = VoteType.PIVOT
            rationale = "Idiot index too high: delete at least 2 steps before committing capital."
        else:
            vote = VoteType.APPROVE
            rationale = "Value equation positive assuming execution discipline."

        return {
            "advisor": self.name,
            "vote": vote.value,
            "rationale": rationale
        }


def get_default_advisors() -> List[AdvisorPersona]:
    return [
        AdvisorPersona(
            name="Jeff Bezos",
            core_framework="Day 1 Customer Obsession & Reversibility Velocity",
            bias_to_attack="Process-as-Proxy & Slow Type 2 Decisions",
            decision_axioms=[
                "Customer obsession over competitor obsession",
                "Type 1 (one-way doors) vs Type 2 (two-way doors) decision taxonomy",
                "Day 1 mindset: Day 2 is stasis, followed by irrelevance, followed by death",
                "Work backwards from customer pain with a 6-page narrative PR/FAQ"
            ],
            key_questions=[
                "Is this a Type 1 or Type 2 decision?",
                "Are we inventing on behalf of the customer or defending sunk cost?"
            ],
            archetype_voice="Ruthless, high-velocity, structured, long-term",
            hard_boundary_rule="Never allow consensus process to slow down two-way door decisions."
        ),
        AdvisorPersona(
            name="Alex Hormozi",
            core_framework="Grand Slam Offer & Leverage Equation",
            bias_to_attack="Low-Margin Activity & Zero-Leverage Complexity",
            decision_axioms=[
                "Value Equation = (Dream Outcome x Perceived Likelihood) / (Time Delay x Effort & Sacrifice)",
                "Make offers so good people feel stupid saying no",
                "Price to value, never price to cost",
                "Solve one problem for one avatar before horizontal expansion"
            ],
            key_questions=[
                "How does this directly compress time delay or perceived effort for the buyer?",
                "What is the payback period and gross margin per unit?"
            ],
            archetype_voice="Direct, quantified, no-nonsense operator",
            hard_boundary_rule="Kill all low-margin, high-friction product variants immediately."
        ),
        AdvisorPersona(
            name="Warren Buffett & Charlie Munger",
            core_framework="Economic Moats & Inversion",
            bias_to_attack="Overconfidence & Operating Outside Circle of Competence",
            decision_axioms=[
                "Invert, always invert: tell me where I'm going to die so I don't go there",
                "Invest only inside a strictly defined Circle of Competence",
                "Demand an undeniable economic moat (pricing power, switching costs, network effects)",
                "Margin of safety: assume everything goes wrong at once"
            ],
            key_questions=[
                "What kills this enterprise in 10 years?",
                "Does this business have genuine pricing power if inflation doubles?"
            ],
            archetype_voice="Wise, cynical, patient, uncompromising on risk",
            hard_boundary_rule="Never invest in things we cannot understand or without a wide moat."
        ),
        AdvisorPersona(
            name="Elon Musk",
            core_framework="First Principles Physics & The 5-Step Algorithm",
            bias_to_attack="Analogy-Thinking & Unquestioned Requirements",
            decision_axioms=[
                "Step 1: Make your requirements less dumb (everyone is wrong, including smart people)",
                "Step 2: Delete the part or process step (if you don't add back 10%, you didn't delete enough)",
                "Step 3: Simplify and optimize",
                "Step 4: Accelerate cycle time",
                "Step 5: Automate (only after steps 1-4)"
            ],
            key_questions=[
                "What are the irreducible fundamental physics constraints here?",
                "Why can't this be done in 1/10th the time at 1/10th the cost?"
            ],
            archetype_voice="Hyper-intense, engineering-first, zero-bureaucracy",
            hard_boundary_rule="Never optimize a step that should be deleted."
        )
    ]


class RoastRoomSession:
    def __init__(self, room_id: str = "roast-room-core"):
        self.room_id = room_id
        self.advisors: Dict[str, AdvisorPersona] = {adv.name: adv for adv in get_default_advisors()}
        self.debate_history: List[Dict[str, Any]] = []

    def add_custom_advisor(self, persona: AdvisorPersona) -> None:
        self.advisors[persona.name] = persona

    def conduct_debate(self, proposition: str) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        
        round_1_critiques = [
            advisor.evaluate_proposition(proposition)
            for advisor in self.advisors.values()
        ]

        round_2_frictions = []
        critique_list = list(round_1_critiques)
        for i, advisor in enumerate(self.advisors.values()):
            peer = critique_list[(i + 1) % len(critique_list)]
            round_2_frictions.append(advisor.cross_examine(peer))

        round_3_votes = [
            advisor.cast_final_vote(proposition, round_2_frictions)
            for advisor in self.advisors.values()
        ]

        votes_count = {VoteType.APPROVE.value: 0, VoteType.REJECT.value: 0, VoteType.PIVOT.value: 0}
        for v in round_3_votes:
            votes_count[v["vote"]] += 1

        overall_verdict = (
            VoteType.APPROVE.value if votes_count[VoteType.APPROVE.value] > len(round_3_votes) / 2
            else VoteType.PIVOT.value if votes_count[VoteType.PIVOT.value] > 0
            else VoteType.REJECT.value
        )

        session_record = {
            "room_id": self.room_id,
            "timestamp": timestamp,
            "proposition": proposition,
            "round_1_critiques": round_1_critiques,
            "round_2_frictions": round_2_frictions,
            "round_3_votes": round_3_votes,
            "overall_verdict": overall_verdict,
            "verdict_summary": f"Consensus Verdict: {overall_verdict} ({votes_count[VoteType.APPROVE.value]} Approve, {votes_count[VoteType.PIVOT.value]} Pivot, {votes_count[VoteType.REJECT.value]} Reject)"
        }

        self.debate_history.append(session_record)
        return session_record

    def to_markdown(self, session_record: Dict[str, Any]) -> str:
        lines = [
            "---",
            "type: doc",
            "status: active",
            "tags: [roast-room, advisory-council, debate-transcript, consensus]",
            f"relatedTo: [{self.room_id}]",
            "---",
            f"# Advisory Council Debate: {session_record['proposition']}",
            f"**Timestamp:** {session_record['timestamp']}",
            f"**Overall Verdict:** `{session_record['overall_verdict']}`",
            "",
            "## Round 1: Blind Axiom Critiques",
            ""
        ]
        for c in session_record["round_1_critiques"]:
            lines.append(f"### {c['advisor']} ({c['core_framework']})")
            lines.append(f"- **Key Question:** *{c['key_question']}*")
            lines.append(f"- **Attacking Bias:** {c['attacking_bias']}")
            for crit in c["critiques"]:
                lines.append(f"  - {crit}")
            lines.append("")

        lines.extend([
            "## Round 2: Adversarial Friction Points",
            ""
        ])
        for friction in session_record["round_2_frictions"]:
            lines.append(f"- {friction}")
        lines.append("")

        lines.extend([
            "## Round 3: Final Votes & Actionable Consensus",
            ""
        ])
        for v in session_record["round_3_votes"]:
            lines.append(f"- **{v['advisor']}**: `{v['vote']}` — {v['rationale']}")
        lines.append("")
        lines.append(f"**Final Conclusion:** {session_record['verdict_summary']}")

        return "\n".join(lines)


if __name__ == "__main__":
    session = RoastRoomSession()
    test_prop = "Migrate entire monolith to 50 serverless microservices to increase team deployment velocity."
    print(f"Running Roast Room Advisory Council on: '{test_prop}'\n")
    record = session.conduct_debate(test_prop)
    md_output = session.to_markdown(record)
    print("--- Debate Result ---")
    print(record["verdict_summary"])
    print(f"Generated Markdown report ({len(md_output)} characters).")
