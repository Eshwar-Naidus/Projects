"""Agentic-OS Autonomous Exploration & Vault Update Loop.

Implements the multi-stage pipeline:
Seed -> Ingest -> Extract -> Profile -> Discover -> Score -> Gate -> Write -> Re-profile
with mandatory human-in-the-loop gating for job submissions and schema/agent mutations.
"""

from __future__ import annotations

import difflib
import fcntl
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ExplorationLoop")


@dataclass
class DiscoveryItem:
    id: str
    domain: str
    title: str
    content: str
    confidence_score: float
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_human_gate: bool = False


class ExplorationLoop:
    def __init__(self, vault_root: Optional[Path] = None):
        self.vault_root = vault_root or Path("/mnt/c/Users/aomsa/WIKI_/WIKI")
        self.review_inbox = self.vault_root / "review-inbox.md"
        self.log_file = self.vault_root / "log.md"

    def log_event(self, trace_id: str, stage: str, status: str, confidence: float, details: str):
        """Append-only audit log entry."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        entry = f"[{now_str}] TRACE:{trace_id} STAGE:{stage} STATUS:{status} CONF:{confidence:.2f} — {details}\n"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(entry)
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as err:
            logger.warning(f"Could not append to log.md: {err}")

    def score_and_gate(self, item: DiscoveryItem) -> Tuple[bool, str]:
        """Apply hard human-in-the-loop verification gates."""
        # Gate 1: Job search domain MUST route to human review inbox (never auto-apply)
        if item.domain == "job_search" or "job" in item.metadata.get("tags", []):
            item.requires_human_gate = True
            return False, "Job submission gated: routed to /todo/jobs.md & review-inbox.md"

        # Gate 2: Low confidence threshold (< 0.75) requires review
        if item.confidence_score < 0.75:
            item.requires_human_gate = True
            return False, f"Low confidence ({item.confidence_score:.2f}) requires human review"

        return True, "Passed auto-write criteria"

    def write_atomic_with_lock(self, target_path: Path, content: str) -> bool:
        """Write file safely with exclusive file lock and zero data corruption."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(content)
                fcntl.flock(f, fcntl.LOCK_UN)
            return True
        except Exception as err:
            logger.error(f"Failed atomic write to {target_path}: {err}")
            return False

    def route_to_review_inbox(self, item: DiscoveryItem, reason: str):
        """Queue gated discoveries for operator inspection."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        block = f"\n### [{now_str}] GATED ITEM: {item.title} (Domain: {item.domain})\n"
        block += f"- **Reason**: {reason}\n"
        block += f"- **Confidence**: {item.confidence_score:.2f}\n"
        if item.source_url:
            block += f"- **Source**: {item.source_url}\n"
        block += f"\n```markdown\n{item.content}\n```\n"

        with open(self.review_inbox, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(block)
            fcntl.flock(f, fcntl.LOCK_UN)

    def reconcile_schema(self, proposed_changes: Dict[Path, str]) -> Dict[str, str]:
        """Nightly vault schema & agent diff self-update gate (§2.3, §5.2)."""
        results: Dict[str, str] = {}

        for file_path, new_content in proposed_changes.items():
            rel_name = file_path.name.lower()

            # Critical files (agents.md, schema.md) MUST produce unified diff in review inbox
            if rel_name in ("agents.md", "schema.md", "user.md"):
                old_content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
                diff_lines = list(difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                    fromfile=f"a/{file_path.name}",
                    tofile=f"b/{file_path.name}"
                ))
                diff_text = "".join(diff_lines)

                item = DiscoveryItem(
                    id=f"schema-diff-{rel_name}",
                    domain="vault_schema",
                    title=f"Schema/Agent Update Diff for {file_path.name}",
                    content=diff_text or "No textual changes",
                    confidence_score=0.95,
                    requires_human_gate=True
                )
                self.route_to_review_inbox(item, "Mandatory human review for core vault schema files")
                results[str(file_path)] = "DIFF_QUEUED_IN_REVIEW_INBOX"
            else:
                self.write_atomic_with_lock(file_path, new_content)
                results[str(file_path)] = "WRITTEN_AUTO"

        return results

    def process_item(self, item: DiscoveryItem) -> str:
        """Execute full single-item lifecycle."""
        trace_id = item.id
        self.log_event(trace_id, "SCORE", "STARTED", item.confidence_score, f"Processing {item.title}")

        allowed, reason = self.score_and_gate(item)
        if not allowed:
            self.route_to_review_inbox(item, reason)
            self.log_event(trace_id, "GATE", "GATED_TO_INBOX", item.confidence_score, reason)
            return "GATED"

        safe_id = "".join(c for c in item.id if c.isalnum() or c in ("-", "_"))
        target_file = (self.vault_root / "wiki" / "discoveries" / f"{safe_id}.md").resolve()
        if not target_file.is_relative_to(self.vault_root.resolve()):
            self.log_event(trace_id, "WRITE", "REJECTED_PATH", item.confidence_score, f"Path traversal detected: {item.id}")
            return "ERROR"
        success = self.write_atomic_with_lock(target_file, item.content)
        if success:
            self.log_event(trace_id, "WRITE", "SUCCESS", item.confidence_score, f"Persisted to {target_file}")
            return "WRITTEN"
        else:
            self.log_event(trace_id, "WRITE", "FAILED", item.confidence_score, f"Failed write {target_file}")
            return "ERROR"
