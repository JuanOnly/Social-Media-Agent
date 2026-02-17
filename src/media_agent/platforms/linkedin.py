"""LinkedIn platform adapter using Playwright."""

import asyncio
from typing import Optional

from .base import PlatformAdapter


class LinkedInAdapter(PlatformAdapter):
    """LinkedIn platform adapter using Playwright."""

    LOGIN_URL = "https://www.linkedin.com/login"
    HOME_URL = "https://www.linkedin.com/feed/"

    async def login(self) -> bool:
        """Login to LinkedIn using Playwright."""
        try:
            await self.init_browser(headless=False)
            
            await self.page.goto(self.LOGIN_URL)
            await self.page.wait_for_load_state("networkidle")
            
            await self.page.wait_for_selector('input[id="username"]', timeout=10000)
            await self.page.fill('input[id="username"]', self.username)
            await self.page.fill('input[id="password"]', self.password)
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_url("*linkedin.com/feed*", timeout=20000)
            
            await self.save_cookies()
            self.is_logged_in = True
            return True
            
        except Exception as e:
            print(f"LinkedIn login error: {e}")
            return False

    async def post(self, content: str) -> bool:
        """Create a new post on LinkedIn."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(self.HOME_URL)
            await self.page.wait_for_load_state("networkidle")
            
            await self.page.click('button:has-text("Start a post")')
            await asyncio.sleep(2)
            await self.page.fill('[contenteditable="true"]', content)
            await self.page.click('button:has-text("Post")')
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            print(f"LinkedIn post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a post."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.linkedin.com/posts/{post_id}")
            await self.page.wait_for_load_state("networkidle")
            await self.page.click('button[aria-label="Like"]')
            return True
            
        except Exception as e:
            print(f"LinkedIn like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.linkedin.com/posts/{post_id}")
            await self.page.wait_for_load_state("networkidle")
            await self.page.click('button[aria-label="Comment"]')
            await asyncio.sleep(1)
            await self.page.fill('[contenteditable="true"]', content)
            await self.page.click('button:has-text("Post")')
            
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"LinkedIn comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a company/person."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.linkedin.com/company/{username}")
            await self.page.wait_for_load_state("networkidle")
            await self.page.click('button:has-text("Follow")')
            
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"LinkedIn follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for people/companies."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.linkedin.com/search/results/all/?keywords={query}")
            await self.page.wait_for_load_state("networkidle")
            
            results = []
            items = await self.page.query_selector_all('.entity-result__title')
            
            for item in items[:limit]:
                try:
                    text = await item.inner_text()
                    results.append({"username": text.strip(), "text": text.strip()})
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"LinkedIn search error: {e}")
            return []

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get notifications."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto("https://www.linkedin.com/notifications")
            await self.page.wait_for_load_state("networkidle")
            
            mentions = []
            items = await self.page.query_selector_all('.notification-list-item')
            
            for item in items[:20]:
                try:
                    text = await item.inner_text()
                    mentions.append({"text": text})
                except:
                    continue
            
            return mentions
            
        except Exception as e:
            print(f"LinkedIn mentions error: {e}")
            return []
