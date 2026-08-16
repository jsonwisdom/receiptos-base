from __future__ import annotations

import shutil
import subprocess
from typing import Any, Dict

from agents.money_loop.harnesses.base.adapter import HarnessAdapter, MissionEnvelope


class DeepSeekDSHAdapter001(HarnessAdapter):
    adapter_id = "deepseek/dsh-001"
    upstream_repository = "deepseek-ai/deepseek-harness"
    license = "MIT"
    preset_names = ["standard", "ptc", "minimal", "creation"]
    launch_command = ["npx", "@deepseek-ai/dsh", "web"]
    default_ui = "http://127.0.0.1:3080"

    def available(self) -> Dict[str, Any]:
        npx = shutil.which("npx")
        return {
            "adapter_id": self.adapter_id,
            "dsh_available": bool(npx),
            "npx_path": npx,
            "dsh_executed": False,
            "mission_completed": False,
            "money_made": False,
            "authority_created": False,
        }

    def execute(self, mission: MissionEnvelope) -> Dict[str, Any]:
        if mission.authority_created:
            raise ValueError("mission envelope cannot create authority")
        if not shutil.which("npx"):
            return {
                "adapter_id": self.adapter_id,
                "mission_id": mission.mission_id,
                "status": "BLOCKED_HARNESS_UNAVAILABLE",
                "dsh_available": False,
                "dsh_executed": False,
                "mission_completed": False,
                "money_made": False,
                "authority_created": False,
            }

        # Intentionally do not launch the web server from CI or library import.
        # Production execution must be explicitly invoked by a runtime controller
        # that can capture process, network, artifact, and cost receipts.
        return {
            "adapter_id": self.adapter_id,
            "mission_id": mission.mission_id,
            "status": "AVAILABLE_NOT_EXECUTED",
            "launch_command": "npx @deepseek-ai/dsh web",
            "default_ui": self.default_ui,
            "dsh_available": True,
            "dsh_executed": False,
            "mission_completed": False,
            "money_made": False,
            "authority_created": False,
        }
