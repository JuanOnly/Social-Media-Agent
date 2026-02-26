"""LinkedIn platform adapter using Playwright with human behavior."""

import asyncio
from typing import Optional

from .base import PlatformAdapter
from .human import HumanBehavior


class LinkedInAdapter(PlatformAdapter):
    """LinkedIn platform adapter using Playwright with human-like behavior."""

    LOGIN_URL = "https://www.linkedin.com/login"
    HOME_URL = "https://www.linkedin.com/feed/"

    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self.human: Optional[HumanBehavior] = None

    async def login(self) -> bool:
        """Login to LinkedIn using Playwright with human behavior."""
        try:
            await self.init_browser(headless=False)
            
            self.human = HumanBehavior(self.page)
            
            await self.page.goto(self.LOGIN_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Enter username with human-like typing
            await self.page.wait_for_selector('input[id="username"]', timeout=10000)
            username_input = await self.page.query_selector('input[id="username"]')
            
            await self.human.type_text(self.username, username_input)
            await self.human.random_delay(0.5, 1.5)
            
            # Enter password with human-like typing
            password_input = await self.page.query_selector('input[id="password"]')
            await self.human.type_text(self.password, password_input)
            
            await self.human.random_delay(0.5, 1.0)
            
            # Click login
            login_btn = await self.page.query_selector('button[type="submit"]')
            await self.human.click_element(login_btn)
            
            # Wait for home page
            await self.page.wait_for_url("*linkedin.com/feed*", timeout=20000)
            
            # Session warmup
            await self.human.warmup_session(duration_seconds=20)
            
            await self.save_cookies()
            self.is_logged_in = True
            return True
            
        except Exception as e:
            print(f"LinkedIn login error: {e}")
            return False

    async def post(self, content: str) -> bool:
        """Create a new post on LinkedIn with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(self.HOME_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Browse feed briefly like human
            await self.human.random_delay(2, 4)
            
            # Click "Start a post" with human movement
            start_post_btn = await self.page.query_selector('button:has-text("Start a post")')
            await self.human.hover(start_post_btn)
            await self.human.click_element(start_post_btn)
            
            await self.human.think_delay()
            
            # Type content with human-like typing
            post_box = await self.page.query_selector('[contenteditable="true"]')
            await self.human.type_text(content, post_box)
            
            await self.human.random_delay(1, 3)
            
            # Click post button
            post_btn = await self.page.query_selector('button:has-text("Post")')
            await self.human.click_element(post_btn)
            
            await self.human.random_delay(2, 4)
            return True
            
        except Exception as e:
            print(f"LinkedIn post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a post with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.linkedin.com/posts/{post_id}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the post first
            await self.human.random_delay(2, 4)
            
            # Click like with human-like movement
            like_btn = await self.page.query_selector('button[aria-label="Like"]')
            if like_btn:
                await self.human.hover(like_btn)
                await self.human.click_element(like_btn)
            
            await self.human.action_delay("like")
            return True
            
        except Exception as e:
            print(f"LinkedIn like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.linkedin.com/posts/{post_id}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the post
            await self.human.random_delay(3, 5)
            
            # Click comment button with movement
            comment_btn = await self.page.query_selector('button[aria-label="Comment"]')
            await self.human.hover(comment_btn)
            await self.human.click_element(comment_btn)
            
            await self.human.think_delay()
            
            # Type comment with human-like typing
            comment_box = await self.page.query_selector('[contenteditable="true"]')
            await self.human.type_text(content, comment_box)
            
            await self.human.random_delay(1, 2)
            
            # Click post button
            post_btn = await self.page.query_selector('button:has-text("Post")')
            await self.human.click_element(post_btn)
            
            await self.human.action_delay("comment")
            return True
            
        except Exception as e:
            print(f"LinkedIn comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a company/person with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.linkedin.com/company/{username}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # View profile briefly
            await self.human.random_delay(2, 4)
            
            # Click follow with movement
            follow_btn = await self.page.query_selector('button:has-text("Follow")')
            if follow_btn:
                await self.human.hover(follow_btn)
                await self.human.click_element(follow_btn)
            
            await self.human.action_delay("follow")
            return True
            
        except Exception as e:
            print(f"LinkedIn follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for people/companies with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.linkedin.com/search/results/all/?keywords={query}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Let results load and scan
            await self.human.random_delay(2, 4)
            
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
        """Get notifications with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto("https://www.linkedin.com/notifications")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read notifications like human
            await self.human.random_delay(2, 4)
            
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
