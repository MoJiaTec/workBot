"""
discovery.py - Auto-discovery module for Skills and MCP servers

Scans the skills/ directory for SKILL.md metadata and mcp_config.json
for MCP server definitions, then registers them as agent tools automatically.
"""

import os
import json
import importlib.util
import logging
import re
from typing import List, Dict, Callable, Optional, Tuple, Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# YAML front-matter parser (lightweight, no external dependency)
# ---------------------------------------------------------------------------

def _parse_yaml_frontmatter(content: str) -> Optional[Dict]:
    """
    Parse YAML front-matter block from a Markdown file.
    Supports simple key/value, lists, and nested mappings (one level).
    """
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    raw = match.group(1)
    result: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_list: Optional[list] = None
    current_dict_key: Optional[str] = None

    for line in raw.splitlines():
        # Skip empty lines
        if not line.strip():
            continue

        # Top-level key: value
        top_match = re.match(r'^(\w[\w\-]*)\s*:\s*(.*)', line)
        if top_match and not line.startswith(' ') and not line.startswith('\t'):
            current_key = top_match.group(1)
            value = top_match.group(2).strip().strip('"').strip("'")
            if value:
                result[current_key] = value
                current_list = None
                current_dict_key = None
            else:
                # Will be filled by sub-items
                result[current_key] = []
                current_list = result[current_key]
                current_dict_key = None
            continue

        # List item under current key: "  - value"
        list_match = re.match(r'^\s{2,}-\s+(.*)', line)
        if list_match and current_key:
            item_str = list_match.group(1).strip()
            # Check if it's a mapping item "key: value"
            kv_match = re.match(r'^(\w[\w\-]*)\s*:\s*(.*)', item_str)
            if kv_match:
                # Start of a new dict item in a list
                if not isinstance(result.get(current_key), list):
                    result[current_key] = []
                    current_list = result[current_key]
                new_dict: Dict[str, Any] = {kv_match.group(1): kv_match.group(2).strip().strip('"').strip("'")}
                current_list.append(new_dict)  # type: ignore
                current_dict_key = str(len(current_list) - 1)
            else:
                if not isinstance(result.get(current_key), list):
                    result[current_key] = []
                    current_list = result[current_key]
                current_list.append(item_str.strip('"').strip("'"))  # type: ignore
            continue

        # Nested key under a list dict item: "    key: value"
        nested_match = re.match(r'^\s{4,}(\w[\w\-]*)\s*:\s*(.*)', line)
        if nested_match and current_list and isinstance(current_list[-1], dict):
            current_list[-1][nested_match.group(1)] = nested_match.group(2).strip().strip('"').strip("'")
            continue

    return result


# ---------------------------------------------------------------------------
# SkillDiscovery
# ---------------------------------------------------------------------------

class DiscoveredSkill:
    """Represents a discovered skill with its metadata and callable tools."""

    def __init__(self, name: str, version: str, description: str,
                 skill_dir: str, tools: List[Dict]):
        self.name = name
        self.version = version
        self.description = description
        self.skill_dir = skill_dir
        self.tools = tools  # list of {name, description, func}

    def __repr__(self):
        return f"<DiscoveredSkill name={self.name} version={self.version} tools={[t['name'] for t in self.tools]}>"


class SkillDiscovery:
    """
    Scans the skills/ directory tree for SKILL.md files,
    parses their YAML front-matter, and loads the entry-point module
    to resolve callable tool functions.
    """

    def __init__(self, skills_root: str):
        """
        Args:
            skills_root: Absolute path to the skills/ directory.
        """
        self.skills_root = skills_root

    def discover(self) -> List[DiscoveredSkill]:
        """Scan skills_root and return all discovered skills."""
        discovered: List[DiscoveredSkill] = []

        if not os.path.isdir(self.skills_root):
            logger.warning(f"Skills root not found: {self.skills_root}")
            return discovered

        for entry in os.scandir(self.skills_root):
            if not entry.is_dir():
                continue
            skill_md = os.path.join(entry.path, "SKILL.md")
            if not os.path.isfile(skill_md):
                continue

            skill = self._load_skill(entry.path, skill_md)
            if skill:
                discovered.append(skill)
                logger.info(f"[SkillDiscovery] Loaded skill: {skill.name} v{skill.version} ({len(skill.tools)} tools)")

        return discovered

    def _load_skill(self, skill_dir: str, skill_md_path: str) -> Optional[DiscoveredSkill]:
        """Parse SKILL.md and load the skill's tool functions."""
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            meta = _parse_yaml_frontmatter(content)
            if not meta:
                logger.debug(f"No YAML front-matter in {skill_md_path}, skipping.")
                return None

            name = meta.get("name", os.path.basename(skill_dir))
            version = meta.get("version", "0.0.0")
            description = meta.get("description", "")
            entry_point = meta.get("entry_point", "")
            raw_tools = meta.get("tools", [])

            # Load entry-point module to resolve functions
            tool_module = None
            if entry_point:
                module_path = os.path.join(skill_dir, entry_point)
                tool_module = self._load_module(name, module_path)

            # Build tool list
            tools: List[Dict] = []
            for t in raw_tools:
                if not isinstance(t, dict):
                    continue
                tool_name = t.get("name", "")
                tool_desc = t.get("description", "")
                if not tool_name:
                    continue

                func = self._resolve_func(tool_module, tool_name)
                tools.append({
                    "name": tool_name,
                    "description": tool_desc,
                    "func": func,
                })

            return DiscoveredSkill(
                name=name,
                version=version,
                description=description,
                skill_dir=skill_dir,
                tools=tools,
            )

        except Exception as e:
            logger.error(f"Failed to load skill from {skill_dir}: {e}")
            return None

    def _load_module(self, skill_name: str, module_path: str):
        """Dynamically load a Python module from a file path."""
        if not os.path.isfile(module_path):
            logger.warning(f"Entry point not found: {module_path}")
            return None
        try:
            spec = importlib.util.spec_from_file_location(
                f"skill_{skill_name}", module_path
            )
            module = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(module)  # type: ignore
            return module
        except Exception as e:
            logger.warning(f"Failed to load module {module_path}: {e}")
            return None

    def _resolve_func(self, module, tool_name: str) -> Optional[Callable]:
        """Try to find a callable for the given tool name in the module."""
        if module is None:
            return None
        # Try exact name first, then common patterns
        for candidate in [tool_name, f"run_{tool_name}", f"execute_{tool_name}"]:
            func = getattr(module, candidate, None)
            if callable(func):
                return func
        return None


# ---------------------------------------------------------------------------
# MCPDiscovery
# ---------------------------------------------------------------------------

class DiscoveredMCPServer:
    """Represents a discovered MCP server with its tools."""

    def __init__(self, name: str, description: str, tools: List[Dict]):
        self.name = name
        self.description = description
        self.tools = tools  # list of {name, description, func}

    def __repr__(self):
        return f"<DiscoveredMCPServer name={self.name} tools={[t['name'] for t in self.tools]}>"


class MCPDiscovery:
    """
    Reads mcp_config.json and wraps each enabled server's tools
    as callable agent tools via the existing MCPManager.
    """

    def __init__(self, config_path: str, mcp_manager=None):
        """
        Args:
            config_path: Absolute path to mcp_config.json.
            mcp_manager: An existing MCPManager instance (optional).
                         If None, a new one will be created.
        """
        self.config_path = config_path
        self._mcp_manager = mcp_manager

    def _get_manager(self):
        if self._mcp_manager is None:
            # Lazy import to avoid circular dependency
            from tools.mcp_tools import get_mcp_manager
            self._mcp_manager = get_mcp_manager()
        return self._mcp_manager

    def discover(self) -> List[DiscoveredMCPServer]:
        """Read mcp_config.json and return all enabled MCP servers."""
        discovered: List[DiscoveredMCPServer] = []

        if not os.path.isfile(self.config_path):
            logger.warning(f"MCP config not found: {self.config_path}")
            return discovered

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read MCP config: {e}")
            return discovered

        manager = self._get_manager()

        for server in config.get("servers", []):
            if not server.get("enabled", True):
                continue

            server_name = server.get("name", "")
            server_desc = server.get("description", "")
            raw_tools = server.get("tools", [])

            tools: List[Dict] = []
            for t in raw_tools:
                tool_name = t.get("name", "")
                tool_desc = t.get("description", "")
                if not tool_name:
                    continue

                # Build a closure that captures server_name and tool_name
                func = self._make_tool_func(manager, server_name, tool_name)
                agent_tool_name = f"mcp_{server_name}_{tool_name}"
                tools.append({
                    "name": agent_tool_name,
                    "description": f"[MCP:{server_name}] {tool_desc}",
                    "func": func,
                })

            server_obj = DiscoveredMCPServer(
                name=server_name,
                description=server_desc,
                tools=tools,
            )
            discovered.append(server_obj)
            logger.info(f"[MCPDiscovery] Loaded MCP server: {server_name} ({len(tools)} tools)")

        return discovered

    @staticmethod
    def _make_tool_func(manager, server_name: str, tool_name: str) -> Callable:
        """Create a closure that calls manager.call_tool with fixed server/tool."""
        def _func(**kwargs):
            return manager.call_tool(server_name, tool_name, **kwargs)
        _func.__name__ = f"mcp_{server_name}_{tool_name}"
        _func.__doc__ = f"Call MCP tool '{tool_name}' on server '{server_name}'"
        return _func


# ---------------------------------------------------------------------------
# Unified discovery entry point
# ---------------------------------------------------------------------------

class AutoDiscovery:
    """
    Unified auto-discovery: scans both skills/ and mcp_config.json,
    returns a flat list of (tool_name, description, func) tuples
    ready to be registered with the agent.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.skills_root = os.path.join(project_root, "skills")
        # Prefer mcp/config.json; fall back to legacy mcp_config.json
        mcp_config = os.path.join(project_root, "mcp", "config.json")
        legacy_config = os.path.join(project_root, "mcp_config.json")
        self.mcp_config_path = mcp_config if os.path.isfile(mcp_config) else legacy_config

    def discover_all(self) -> List[Tuple[str, str, Optional[Callable]]]:
        """
        Discover all skills and MCP tools.

        Returns:
            List of (tool_name, description, func) tuples.
            func may be None if the entry point could not be loaded.
        """
        results: List[Tuple[str, str, Optional[Callable]]] = []

        # --- Skills ---
        skill_discovery = SkillDiscovery(self.skills_root)
        skills = skill_discovery.discover()
        for skill in skills:
            for tool in skill.tools:
                results.append((tool["name"], tool["description"], tool["func"]))

        # --- MCP ---
        mcp_discovery = MCPDiscovery(self.mcp_config_path)
        mcp_servers = mcp_discovery.discover()
        for server in mcp_servers:
            for tool in server.tools:
                results.append((tool["name"], tool["description"], tool["func"]))

        logger.info(
            f"[AutoDiscovery] Total discovered: {len(results)} tools "
            f"({len(skills)} skills, {len(mcp_servers)} MCP servers)"
        )
        return results

    def summary(self) -> str:
        """Return a human-readable discovery summary."""
        lines = []

        # Skills
        skill_discovery = SkillDiscovery(self.skills_root)
        skills = skill_discovery.discover()
        lines.append(f"📦 Skills ({len(skills)} found):")
        for skill in skills:
            lines.append(f"  ✓ {skill.name} v{skill.version} — {skill.description[:60]}")
            for tool in skill.tools:
                status = "✅" if tool["func"] else "⚠️ (no func)"
                lines.append(f"      {status} {tool['name']}: {tool['description']}")

        # MCP
        mcp_discovery = MCPDiscovery(self.mcp_config_path)
        servers = mcp_discovery.discover()
        lines.append(f"\n🔌 MCP Servers ({len(servers)} found):")
        for server in servers:
            lines.append(f"  ✓ {server.name} — {server.description}")
            for tool in server.tools:
                lines.append(f"      ✅ {tool['name']}: {tool['description']}")

        return "\n".join(lines)
