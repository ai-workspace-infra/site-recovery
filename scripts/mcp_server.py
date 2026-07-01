#!/usr/bin/env python3
"""
MCP Server for Site Migration Toolkit.
Exposes toolkit actions (migrate, backup, restore) as AI-driven MCP tools.

Dependencies:
    pip install mcp
"""

import subprocess
import os
import sys
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("[ERROR] 'mcp' package not found. Install it with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize FastMCP Server
mcp = FastMCP(
    name="Site-Migration-Toolkit-MCP",
    dependencies=["mcp"]
)

TOOLKIT_ROOT = Path(__file__).resolve().parent.parent
RUN_SCRIPT = TOOLKIT_ROOT / "scripts" / "run_toolkit.py"

def run_toolkit_action(action: str, extra_args: str = "") -> str:
    """Helper to execute the run_toolkit.py script"""
    cmd = [sys.executable, str(RUN_SCRIPT), action]
    if extra_args:
        # Split args safely (assuming simple space separation for now)
        import shlex
        cmd.extend(shlex.split(extra_args))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Action '{action}' completed successfully.\n\nOutput:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Action '{action}' failed with exit code {e.returncode}.\n\nError Output:\n{e.stderr}\n\nStandard Output:\n{e.stdout}"


@mcp.tool()
def migrate_site(target_domain: str, source_domain: str) -> str:
    """
    Execute full site migration from source to target.
    
    Args:
        target_domain: The base domain of the target environment (e.g. onwalk.net)
        source_domain: The base domain of the source environment (e.g. svc.plus)
    """
    args = f"-e target_domain={target_domain} -e migration_flow.source.domain_base={source_domain}"
    return run_toolkit_action("migrate", args)


@mcp.tool()
def backup_site() -> str:
    """
    Execute offline cold backup of the AI Workspace site.
    """
    return run_toolkit_action("backup")


@mcp.tool()
def restore_site() -> str:
    """
    Execute offline restore of the AI Workspace site from a backup archive.
    """
    return run_toolkit_action("restore")


if __name__ == "__main__":
    # Start the stdio MCP server for agent integration
    mcp.run()
