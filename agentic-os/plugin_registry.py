"""Agentic-OS Plugin Registry Engine.

Zero-external-dependency (stdlib only) manifest loader, topological dependency resolver,
and validation engine for Hermes/Agentic-OS plugins.
"""

from __future__ import annotations

import graphlib
import json
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set


ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


@dataclass(frozen=True)
class PluginManifest:
    id: str
    version: str
    type: str
    entrypoint: str
    provides: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    verify: Optional[str] = None
    root_path: Optional[Path] = None


class PluginRegistryError(Exception):
    """Base error for plugin registry operations."""
    pass


class PluginRegistry:
    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins_dir = plugins_dir or Path(".hermes/plugins")
        self._plugins: Dict[str, PluginManifest] = {}
        self._capability_index: Dict[str, List[str]] = {}

    def load_manifest_file(self, manifest_path: Path) -> PluginManifest:
        """Parse manifest from JSON or YAML-subset using stdlib."""
        raw_text = manifest_path.read_text(encoding="utf-8")
        data: Dict[str, Any] = {}

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            current_list_key: Optional[str] = None
            for line in raw_text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("- ") and current_list_key:
                    data.setdefault(current_list_key, []).append(line[2:].strip().strip("\"'"))
                    continue
                current_list_key = None
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip("\"'")
                    if not val:
                        current_list_key = key
                        data[key] = []
                    else:
                        data[key] = val

        plugin_id = data.get("id", "")
        if not ID_PATTERN.match(plugin_id):
            raise PluginRegistryError(f"Invalid plugin id '{plugin_id}' in {manifest_path}")

        manifest = PluginManifest(
            id=plugin_id,
            version=str(data.get("version", "1.0.0")),
            type=str(data.get("type", "standard")),
            entrypoint=str(data.get("entrypoint", "main.py")),
            provides=list(data.get("provides", [])),
            requires=list(data.get("requires", [])),
            verify=data.get("verify"),
            root_path=manifest_path.parent
        )
        return manifest

    def discover_all(self) -> Dict[str, PluginManifest]:
        """Scan plugins_dir and index all manifests."""
        self._plugins.clear()
        self._capability_index.clear()

        if not self.plugins_dir.exists():
            return self._plugins

        for manifest_file in self.plugins_dir.glob("*/manifest.*"):
            if manifest_file.suffix in (".yaml", ".yml", ".json"):
                try:
                    manifest = self.load_manifest_file(manifest_file)
                    self._plugins[manifest.id] = manifest
                    for cap in manifest.provides:
                        self._capability_index.setdefault(cap, []).append(manifest.id)
                except Exception as err:
                    raise PluginRegistryError(f"Failed loading {manifest_file}: {err}") from err

        return self._plugins

    def get_plugin(self, plugin_id: str) -> PluginManifest:
        if plugin_id not in self._plugins:
            raise KeyError(f"Plugin '{plugin_id}' not found in registry")
        return self._plugins[plugin_id]

    def find_by_capability(self, capability: str) -> List[PluginManifest]:
        plugin_ids = self._capability_index.get(capability, [])
        return [self._plugins[pid] for pid in plugin_ids if pid in self._plugins]

    def resolve_dependencies(self, plugin_id: str) -> List[str]:
        """Topologically sort dependencies for plugin_id."""
        manifest = self.get_plugin(plugin_id)
        graph: Dict[str, Set[str]] = {}

        def visit(pid: str):
            if pid in graph:
                return
            p = self.get_plugin(pid)
            graph[pid] = set(p.requires)
            for req in p.requires:
                visit(req)

        visit(plugin_id)
        sorter = graphlib.TopologicalSorter(graph)
        try:
            return list(sorter.static_order())
        except graphlib.CycleError as err:
            raise PluginRegistryError(f"Circular dependency detected for {plugin_id}: {err}") from err

    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all loaded plugins for missing dependencies and entrypoint files."""
        errors: Dict[str, List[str]] = {}
        for pid, manifest in self._plugins.items():
            errs: List[str] = []
            if manifest.root_path:
                entry = manifest.root_path / manifest.entrypoint
                if not entry.exists():
                    errs.append(f"Entrypoint {manifest.entrypoint} does not exist")
            for req in manifest.requires:
                if req not in self._plugins:
                    errs.append(f"Missing required dependency: {req}")
            if errs:
                errors[pid] = errs
        return errors
