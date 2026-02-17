"""Platforms module."""

from .base import PlatformAdapter, PlatformRegistry, get_platform_registry
from .twitter import TwitterAdapter
from .instagram import InstagramAdapter

# Register all platform adapters
registry = get_platform_registry()
registry.register("twitter", TwitterAdapter)
registry.register("instagram", InstagramAdapter)

__all__ = [
    "PlatformAdapter",
    "PlatformRegistry",
    "get_platform_registry",
    "TwitterAdapter",
    "InstagramAdapter",
]
