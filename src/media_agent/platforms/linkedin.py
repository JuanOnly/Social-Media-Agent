"""LinkedIn platform adapter (stub implementation)."""

from typing import Optional

from .base import PlatformAdapter


class LinkedInAdapter(PlatformAdapter):
    """LinkedIn platform adapter using Playwright."""

    async def login(self) -> bool:
        """Login to LinkedIn (stub)."""
        self.is_logged_in = True
        return True

    async def post(self, content: str) -> bool:
        """Create a new post (stub)."""
        if not self.is_logged_in:
            await self.login()
        return True

    async def like(self, post_id: str) -> bool:
        """Like a post (stub)."""
        if not self.is_logged_in:
            await self.login()
        return True

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post (stub)."""
        if not self.is_logged_in:
            await self.login()
        return True

    async def follow(self, username: str) -> bool:
        """Follow a user (stub)."""
        if not self.is_logged_in:
            await self.login()
        return True

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search (stub)."""
        return []

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get mentions (stub)."""
        return []
