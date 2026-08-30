"""
Base Compiler Interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
import pandas as pd


@dataclass
class CompilerOutput:
    """Artifacts emitted by a target compiler."""
    target_name: str
    files: Dict[str, str]  # filename -> file content string
    metadata: Dict[str, Any]


class BaseHarnessCompiler(ABC):
    """Abstract interface for all target harness config generators."""

    @property
    @abstractmethod
    def target_name(self) -> str:
        """Name of the target harness."""
        pass

    @abstractmethod
    def compile(
        self,
        pinned_df: pd.DataFrame,
        provider_name: str = "custom",
        api_base_url: str = "",
        api_key_env_var: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> CompilerOutput:
        """
        Compile pinned models into target-specific configuration manifests.
        """
        pass
