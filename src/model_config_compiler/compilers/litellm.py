"""
LiteLLM Target Compiler (Stub - Deferred)
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import pandas as pd

from .base import BaseHarnessCompiler, CompilerOutput


class LiteLLMCompiler(BaseHarnessCompiler):
    """Compiler target for LiteLLM proxy config.yaml (Deferred)."""

    @property
    def target_name(self) -> str:
        return "LiteLLM"

    def compile(
        self,
        pinned_df: pd.DataFrame,
        provider_name: str = "custom",
        api_base_url: str = "",
        api_key_env_var: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> CompilerOutput:
        """
        Stub: Compiles config.yaml for LiteLLM.
        """
        config_yaml = "# LiteLLM config.yaml (Deferred)\nmodel_list: []\n"
        
        return CompilerOutput(
            target_name=self.target_name,
            files={
                "config.yaml": config_yaml,
            },
            metadata={"status": "deferred"},
        )


def compile_litellm(
    pinned_df: pd.DataFrame,
    provider_name: str = "custom",
    api_base_url: str = "",
    api_key_env_var: str = "",
) -> CompilerOutput:
    """Helper function to compile LiteLLM configs."""
    return LiteLLMCompiler().compile(
        pinned_df=pinned_df,
        provider_name=provider_name,
        api_base_url=api_base_url,
        api_key_env_var=api_key_env_var,
    )
