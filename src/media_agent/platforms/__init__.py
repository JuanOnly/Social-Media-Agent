"""Platforms module."""

from .base import PlatformAdapter, PlatformRegistry, get_platform_registry
from .twitter import TwitterAdapter
from .instagram import InstagramAdapter
from .facebook import FacebookAdapter
from .linkedin import LinkedInAdapter

# Register all platform adapters
registry = get_platform_registry()
registry.register("twitter", TwitterAdapter)
registry.register("instagram", InstagramAdapter)
registry.register("facebook", FacebookAdapter)
registry.register("linkedin", LinkedInAdapter)

__all__ = [
    "PlatformAdapter",
    "PlatformRegistry",
    "get_platform_registry",
    "TwitterAdapter",
    "InstagramAdapter",
    "FacebookAdapter",
    "LinkedInAdapter",
]
