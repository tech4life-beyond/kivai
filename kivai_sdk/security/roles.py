"""
Role model for Kivai security layer (v0.6).

This defines canonical roles for authorization evaluation.
Extensible in future versions.
"""

from typing import Literal

# Canonical roles (v0.6 baseline)
Role = Literal[
    "owner",
    "admin",
    "user",
    "service",
]

# Future:
# - hierarchical roles
# - role inheritance
# - dynamic policy backends
