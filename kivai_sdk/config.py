"""
Execution configuration for Kivai runtime.
Defines operational behavior modes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionConfig:
    strict: bool = False


# Default configuration (development mode)
DEFAULT_EXECUTION_CONFIG = ExecutionConfig(strict=False)
