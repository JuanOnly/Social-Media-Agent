"""Instagram platform adapter using Playwright with human behavior."""

import asyncio
from typing import Optional

from .base import PlatformAdapter
from .human import HumanBehavior


class InstagramAdapter(PlatformAdapter):
    """Instagram platform adapter using Playwright with human-like behavior."""

    LOGIN_URL = "https://www.instagram.com/accounts/login/"
    HOME_URL = "https://www.instagram.com/"

    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self.human: Optional[HumanBehavior] = None

    async def login(self) -> bool:
        """Login to Instagram using Playwright with human behavior."""
        try:
            await self.init_browser(headless=False)
            
            self.human = HumanBehavior(self.page)
            
            await self.page.goto(self.LOGIN_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Enter username with human-like typing
            await self.page.wait_for_selector('input[name="username"]', timeout=10000)
            username_input = await self.page.query_selector('input[name="username"]')
            
            await self.human.type_text(self.username, username_input)
            await self.human.random_delay(0.5, 1.5)
            
            # Enter password with human-like typing
            password_input = await self.page.query_selector('input[name="password"]')
            await self.human.type_text(self.password, password_input)
            
            await self.human.random_delay(0.5, 1.0)
            
            # Click login
            login_btn = await self.page.query_selector('button[type="submit"]')
            await self.human.click_element(login_btn)
            
            # Wait for home
            await self.page.wait_for_url(self.HOME_URL, timeout=20000)
            
            # Session warmup
            await self.human.warmup_session(duration_seconds=20)
            
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
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(self.HOME_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Browse home briefly like human
            await self.human.random_delay(2, 4)
            
            # Click + button with human movement
            new_post_btn = await self.page.query_selector('svg[aria-label="New post"]')
            await self.human.hover(new_post_btn)
            await self.human.click_element(new_post_btn)
            
            await self.human.think_delay()
            
            # Note: Instagram requires image for posts
            print("Note: Instagram requires image for posts")
            return True
            
        except Exception as e:
            print(f"Instagram post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a post with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.instagram.com/p/{post_id}/")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the post first
            await self.human.random_delay(2, 4)
            
            # Click like with human-like movement
            like_btn = await self.page.query_selector('svg[aria-label="Like"]')
            if like_btn:
                await self.human.hover(like_btn)
                await self.human.click_element(like_btn)
            
            await self.human.action_delay("like")
            return True
            
        except Exception as e:
            print(f"Instagram like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.instagram.com/p/{post_id}/")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the post
            await self.human.random_delay(3, 5)
            
            # Click comment box with movement
            comment_box = await self.page.query_selector('textarea')
            await self.human.hover(comment_box)
            await self.human.click_element(comment_box)
            
            await self.human.think_delay()
            
            # Type comment
            await self.human.type_text(content, comment_box)
            
            await self.human.random_delay(1, 2)
            
            # Submit
            post_btn = await self.page.query_selector('button:has-text("Post")')
            await self.human.click_element(post_btn)
            
            await self.human.action_delay("comment")
            return True
            
        except Exception as e:
            print(f"Instagram comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a user with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.instagram.com/{username}/")
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
            print(f"Instagram follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for content/users with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.instagram.com/explore/search/?q={query}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Let results load and scan
            await self.human.random_delay(2, 4)
            
            results = []
            return results
            
        except Exception as e:
            print(f"Instagram search error: {e}")
            return []

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get mentions with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto("https://www.instagram.com/notifications/")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read notifications like human
            await self.human.random_delay(2, 4)
            
            return []
            
        except Exception as e:
            print(f"Instagram mentions error: {e}")
            return []
