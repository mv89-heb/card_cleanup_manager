"""Provider connector foundation for authenticated account scans."""

from .base import Connector, ConnectorCapability, ConnectorResult
from .registry import ConnectorRegistry, build_default_registry

__all__ = [
    "Connector",
    "ConnectorCapability",
    "ConnectorResult",
    "ConnectorRegistry",
    "build_default_registry",
]
