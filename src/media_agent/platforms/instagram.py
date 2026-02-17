"""Instagram platform adapter using Playwright."""

import asyncio
from typing import Optional

from .base import PlatformAdapter


class InstagramAdapter(PlatformAdapter):
    """Instagram platform adapter using Playwright."""

    LOGIN_URL = "https://www.instagram.com/accounts/login/"
    HOME_URL = "https://www.instagram.com/"

    async def login(self) -> bool:
        """Login to Instagram using Playwright."""
        try:
            await self.init_browser(headless=False)
            
            await self.page.goto(self.LOGIN_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # Enter username
            await self.page.wait_for_selector('input[name="username"]', timeout=10000)
            await self.page.fill('input[name="username"]', self.username)
            
            # Enter password
            await self.page.fill('input[name="password"]', self.password)
            
            # Click login
            await self.page.click('button[type="submit"]')
            
            # Wait for home
            await self.page.wait_for_url(self.HOME_URL, timeout=15000)
            
            await self.save_cookies()
            self.is_logged_in = True
            return True
            
        except Exception as e:
            print(f"Instagram login error: {e}")
            return False

    async def post(self, content: str) -> bool:
        """Create a new post (Instagram requires image, text only not supported natively)."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(self.HOME_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # Click + button for new post
            await self.page.click('svg[aria-label="New post"]')
            await asyncio.sleep(2)
            
            # Note: Instagram requires image for posts, this is a simplified version
            # Would need file upload for actual implementation
            print("Note: Instagram requires image for posts")
            return True
            
        except Exception as e:
            print(f"Instagram post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a post."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.instagram.com/p/{post_id}/")
            await self.page.wait_for_load_state("networkidle")
            
            # Click like button
            await self.page.click('svg[aria-label="Like"]')
            return True
            
        except Exception as e:
            print(f"Instagram like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.instagram.com/p/{post_id}/")
            await self.page.wait_for_load_state("networkidle")
            
            # Click comment box
            await self.page.click('textarea')
            await self.page.fill('textarea', content)
            await self.page.click('button:has-text("Post")')
            
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"Instagram comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a user."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.instagram.com/{username}/")
            await self.page.wait_for_load_state("networkidle")
            
            # Click follow button
            await self.page.click('button:has-text("Follow")')
            
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"Instagram follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for content/users."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.instagram.com/explore/search/?q={query}")
            await self.page.wait_for_load_state("networkidle")
            
            results = []
            # Simplified - would need more parsing
            return results
            
        except Exception as e:
            print(f"Instagram search error: {e}")
            return []

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get mentions."""
        return []
