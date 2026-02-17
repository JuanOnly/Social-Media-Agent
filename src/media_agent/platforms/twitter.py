"""Twitter/X platform adapter using Playwright."""

import asyncio
from typing import Optional

from .base import PlatformAdapter


class TwitterAdapter(PlatformAdapter):
    """Twitter/X platform adapter using Playwright."""

    LOGIN_URL = "https://x.com/i/flow/login"
    HOME_URL = "https://x.com/home"

    async def login(self) -> bool:
        """Login to Twitter/X using Playwright."""
        try:
            await self.init_browser(headless=False)
            
            # Navigate to login
            await self.page.goto(self.LOGIN_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # Enter username
            await self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            await self.page.fill('input[autocomplete="username"]', self.username)
            await self.page.click('button:has-text("Next")')
            
            await asyncio.sleep(2)
            
            # Check if password field or username verification
            try:
                # Try password field
                await self.page.wait_for_selector('input[autocomplete="current-password"]', timeout=5000)
                await self.page.fill('input[autocomplete="current-password"]', self.password)
            except:
                # Might need username verification first
                await self.page.fill('input[autocomplete="username"]', self.username)
                await self.page.click('button:has-text("Next")')
                await asyncio.sleep(2)
                await self.page.wait_for_selector('input[autocomplete="current-password"]', timeout=5000)
                await self.page.fill('input[autocomplete="current-password"]', self.password)
            
            await self.page.click('button:has-text("Log in")')
            
            # Wait for home page
            await self.page.wait_for_url(self.HOME_URL, timeout=15000)
            
            await self.save_cookies()
            self.is_logged_in = True
            return True
            
        except Exception as e:
            print(f"Twitter login error: {e}")
            return False

    async def post(self, content: str) -> bool:
        """Create a new tweet."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(self.HOME_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # Click the post button / tweet box
            await self.page.wait_for_selector('div[aria-label="Post text"]', timeout=10000)
            await self.page.click('div[aria-label="Post text"]')
            
            # Type content
            await self.page.fill('div[aria-label="Post text"]', content)
            
            # Click post button
            await self.page.click('button[data-testid="tweetButton"]')
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            print(f"Twitter post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a tweet."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            # Navigate to tweet
            await self.page.goto(f"https://x.com/i/status/{post_id}")
            await self.page.wait_for_load_state("networkidle")
            
            # Click like button
            await self.page.click('button[data-testid="like"]')
            return True
            
        except Exception as e:
            print(f"Twitter like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a tweet."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://x.com/i/status/{post_id}")
            await self.page.wait_for_load_state("networkidle")
            
            # Click reply button
            await self.page.click('button[data-testid="reply"]')
            
            # Type comment
            await self.page.fill('div[aria-label="Post text"]', content)
            
            # Click reply
            await self.page.click('button[data-testid="tweetButton"]')
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            print(f"Twitter comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a user."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://x.com/{username}")
            await self.page.wait_for_load_state("networkidle")
            
            # Click follow button
            await self.page.click('button:has-text("Follow")')
            
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"Twitter follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search tweets."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto(f"https://x.com/search?q={query}&src=typed_query")
            await self.page.wait_for_load_state("networkidle")
            
            results = []
            tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
            
            for tweet in tweets[:limit]:
                try:
                    username = await tweet.query_selector('div[data-testid="User-Name"]')
                    text = await tweet.query_selector('div[data-testid="tweetText"]')
                    
                    results.append({
                        "username": await username.inner_text() if username else "",
                        "text": await text.inner_text() if text else "",
                    })
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Twitter search error: {e}")
            return []

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get mentions."""
        if not self.is_logged_in:
            await self.login()
        
        try:
            await self.page.goto("https://x.com/notifications/mentions")
            await self.page.wait_for_load_state("networkidle")
            
            mentions = []
            notifications = await self.page.query_selector_all('div[data-testid="notification"]')
            
            for notif in notifications[:20]:
                try:
                    text = await notif.inner_text()
                    mentions.append({"text": text})
                except:
                    continue
            
            return mentions
            
        except Exception as e:
            print(f"Twitter mentions error: {e}")
            return []
