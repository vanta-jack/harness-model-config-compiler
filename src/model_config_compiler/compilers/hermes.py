"""
Hermes Agent Target Compiler (Stub)

Awaiting exact user specifications for Hermes Agent config.yml and .env format.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import pandas as pd

from .base import BaseHarnessCompiler, CompilerOutput


class HermesCompiler(BaseHarnessCompiler):
    """Compiler target for Hermes Agent."""

    @property
    def target_name(self) -> str:
        return "Hermes Agent"

    def compile(
        self,
        pinned_df: pd.DataFrame,
        provider_name: str = "custom",
        api_base_url: str = "",
        api_key_env_var: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> CompilerOutput:
        """
        Stub: Compiles config.yml and .env for Hermes Agent.
        """
        # Placeholder stub until Hermes schema is disclosed
        config_yml = "# Hermes Agent config.yml (Stub awaiting schema)\n"
        dot_env = f"{api_key_env_var or 'API_KEY'}=\n"
        
        return CompilerOutput(
            target_name=self.target_name,
            files={
                "config.yml": config_yml,
                ".env": dot_env,
            },
            metadata={"models_count": len(pinned_df)},
        )


def compile_hermes(
    pinned_df: pd.DataFrame,
    provider_name: str = "custom",
    api_base_url: str = "",
    api_key_env_var: str = "",
) -> CompilerOutput:
    """Helper function to compile Hermes configs."""
    return HermesCompiler().compile(
        pinned_df=pinned_df,
        provider_name=provider_name,
        api_base_url=api_base_url,
        api_key_env_var=api_key_env_var,
    )
