"""Facebook platform adapter using Playwright."""

import asyncio
from typing import Optional

from .base import PlatformAdapter


class FacebookAdapter(PlatformAdapter):
    """Facebook platform adapter using Playwright."""

    LOGIN_URL = "https://www.facebook.com/login"
    HOME_URL = "https://www.facebook.com/"

    async def login(self) -> bool:
        """Login to Facebook using Playwright."""
        try:
            await self.init_browser(headless=False)
            
            await self.page.goto(self.LOGIN_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # Enter email
            await self.page.wait_for_selector('input[id="email"]', timeout=10000)
            await self.page.fill('input[id="email"]', self.username)
            
            # Enter password
            await self.page.fill('input[id="pass"]', self.password)
            
            # Click login
            await self.page.click('button[type="submit"]')
            
            # Wait for home page
            await self.page.wait_for_url(self.HOME_URL, timeout=15000)
            
            await self.save_cookies()
            self.is_logged_in = True
            return True
            
        except Exception as e:
            print(f"Facebook login error: {e}")
            return False

    async def post(self, content: str) -> bool:
        """Create a new post on Facebook."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(self.HOME_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # Click on "What's on your mind"
            await self.page.click('[aria-label="Create a post"]')
            await asyncio.sleep(2)
            
            # Type content
            await self.page.fill('[contenteditable="true"]', content)
            
            # Click post button
            await self.page.click('[aria-label="Post"]')
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            print(f"Facebook post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a post."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.facebook.com/{post_id}")
            await self.page.wait_for_load_state("networkidle")
            
            # Click like button
            await self.page.click('[aria-label="Like"]')
            return True
            
        except Exception as e:
            print(f"Facebook like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.facebook.com/{post_id}")
            await self.page.wait_for_load_state("networkidle")
            
            # Click comment box
            await self.page.click('[aria-label="Write a comment"]')
            await self.page.fill('[aria-label="Write a comment"]', content)
            await self.page.press('[aria-label="Write a comment"]', "Enter")
            
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"Facebook comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a user/page."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.facebook.com/{username}")
            await self.page.wait_for_load_state("networkidle")
            
            # Click follow button
            await self.page.click('[aria-label="Follow"]')
            
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"Facebook follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for content/pages."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://www.facebook.com/search/top?q={query}")
            await self.page.wait_for_load_state("networkidle")
            
            results = []
            # Parse search results
            posts = await self.page.query_selector_all('[role="article"]')
            
            for post in posts[:limit]:
                try:
                    text = await post.inner_text()
                    results.append({"text": text[:200]})
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Facebook search error: {e}")
            return []

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get mentions and notifications."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto("https://www.facebook.com/notifications")
            await self.page.wait_for_load_state("networkidle")
            
            mentions = []
            notifications = await self.page.query_selector_all('[role="listitem"]')
            
            for notif in notifications[:20]:
                try:
                    text = await notif.inner_text()
                    mentions.append({"text": text})
                except:
                    continue
            
            return mentions
            
        except Exception as e:
            print(f"Facebook mentions error: {e}")
            return []
