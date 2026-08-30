"""
Pi Coding Agent Target Compiler (Stub)

Awaiting exact user specifications for Pi Coding Agent models.json schema.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
import pandas as pd

from .base import BaseHarnessCompiler, CompilerOutput


class PiCompiler(BaseHarnessCompiler):
    """Compiler target for Pi Coding Agent."""

    @property
    def target_name(self) -> str:
        return "Pi Coding Agent"

    def compile(
        self,
        pinned_df: pd.DataFrame,
        provider_name: str = "custom",
        api_base_url: str = "",
        api_key_env_var: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> CompilerOutput:
        """
        Stub: Compiles models.json for Pi Coding Agent.
        """
        # Placeholder stub until Pi schema is disclosed
        models_data = {
            "provider": provider_name,
            "baseUrl": api_base_url,
            "models": pinned_df["id"].tolist() if not pinned_df.empty and "id" in pinned_df.columns else [],
        }
        models_json = json.dumps(models_data, indent=2)
        
        return CompilerOutput(
            target_name=self.target_name,
            files={
                "models.json": models_json,
            },
            metadata={"models_count": len(pinned_df)},
        )


def compile_pi(
    pinned_df: pd.DataFrame,
    provider_name: str = "custom",
    api_base_url: str = "",
    api_key_env_var: str = "",
) -> CompilerOutput:
    """Helper function to compile Pi Coding Agent configs."""
    return PiCompiler().compile(
        pinned_df=pinned_df,
        provider_name=provider_name,
        api_base_url=api_base_url,
        api_key_env_var=api_key_env_var,
    )
