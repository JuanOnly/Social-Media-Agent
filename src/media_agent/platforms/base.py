"""Base platform adapter with Playwright."""

import asyncio
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class PlatformAdapter(ABC):
    """Base class for social media platform adapters using Playwright."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.is_logged_in = False
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.cookies_path = self._get_cookies_path()

    def _get_cookies_path(self) -> Path:
        """Get path for storing cookies."""
        from ...config import get_project_root
        cookies_dir = get_project_root() / "config" / "cookies"
        cookies_dir.mkdir(exist_ok=True)
        return cookies_dir / f"{self.__class__.__name__}_cookies.json"

    async def init_browser(self, headless: bool = False):
        """Initialize Playwright browser."""
        if self.browser:
            return
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        
        # Load existing cookies if available
        if self.cookies_path.exists():
            try:
                self.context = await self.browser.new_context()
                with open(self.cookies_path, 'r') as f:
                    cookies = json.load(f)
                    await self.context.add_cookies(cookies)
            except:
                self.context = await self.browser.new_context()
        else:
            self.context = await self.browser.new_context()
        
        self.page = await self.context.new_page()

    async def save_cookies(self):
        """Save cookies for session persistence."""
        if self.context and self.cookies_path:
            cookies = await self.context.cookies()
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f)

    async def close_browser(self):
        """Close browser and save cookies."""
        if self.browser:
            await self.save_cookies()
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None

    async def login(self) -> bool:
        """Login to the platform. Override in subclass."""
        raise NotImplementedError

    async def post(self, content: str) -> bool:
        """Create a new post. Override in subclass."""
        raise NotImplementedError

    async def like(self, post_id: str) -> bool:
        """Like a post. Override in subclass."""
        raise NotImplementedError

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post. Override in subclass."""
        raise NotImplementedError

    async def follow(self, username: str) -> bool:
        """Follow a user. Override in subclass."""
        raise NotImplementedError

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for content/users. Override in subclass."""
        raise NotImplementedError

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get mentions since a given ID. Override in subclass."""
        raise NotImplementedError

    async def logout(self) -> bool:
        """Logout from the platform."""
        await self.close_browser()
        self.is_logged_in = False
        return True


class PlatformRegistry:
    """Registry for platform adapters."""

    def __init__(self):
        self._adapters: dict[str, type[PlatformAdapter]] = {}

    def register(self, platform: str, adapter_class: type[PlatformAdapter]):
        """Register a platform adapter."""
        self._adapters[platform.lower()] = adapter_class

    def get_adapter(self, platform: str, username: str, password: str) -> PlatformAdapter:
        """Get an adapter instance for a platform."""
        adapter_class = self._adapters.get(platform.lower())
        if not adapter_class:
            raise ValueError(f"Platform {platform} not supported")
        return adapter_class(username, password)

    def list_platforms(self) -> list[str]:
        """List available platforms."""
        return list(self._adapters.keys())


# Global registry
_platform_registry = PlatformRegistry()


def get_platform_registry() -> PlatformRegistry:
    """Get platform registry instance."""
    return _platform_registry
