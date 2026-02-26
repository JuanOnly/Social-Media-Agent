"""Twitter/X platform adapter using Playwright with human behavior."""

import asyncio
import random
from typing import Optional

from .base import PlatformAdapter
from .human import HumanBehavior


class TwitterAdapter(PlatformAdapter):
    """Twitter/X platform adapter using Playwright with human-like behavior."""

    LOGIN_URL = "https://x.com/i/flow/login"
    HOME_URL = "https://x.com/home"

    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self.human: Optional[HumanBehavior] = None

    async def login(self) -> bool:
        """Login to Twitter/X using Playwright with human behavior."""
        try:
            await self.init_browser(headless=False)
            
            # Initialize human behavior
            self.human = HumanBehavior(self.page)
            
            # Navigate to login
            await self.page.goto(self.LOGIN_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Enter username/email with human-like typing
            await self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            username_input = await self.page.query_selector('input[autocomplete="username"]')
            
            # Use the username directly (could be email or handle)
            await self.human.type_text(self.username, username_input)
            await self.human.random_delay(0.5, 1.5)
            
            next_btn = await self.page.query_selector('button:has-text("Next")')
            await self.human.click_element(next_btn)
            
            await self.human.think_delay()
            
            # Check if password or verification needed
            try:
                password_input = await self.page.wait_for_selector('input[autocomplete="current-password"]', timeout=5000)
                await self.human.type_text(self.password, password_input)
            except:
                # Need username verification - might be using email
                username_input2 = await self.page.query_selector('input[autocomplete="username"]')
                if username_input2:
                    await self.human.type_text(self.username, username_input2)
                    await self.human.click_element(next_btn)
                    await self.human.think_delay()
                    password_input = await self.page.wait_for_selector('input[autocomplete="current-password"]', timeout=5000)
                    await self.human.type_text(self.password, password_input)
            
            await self.human.random_delay(0.5, 1.0)
            
            # Click login button
            login_btn = await self.page.query_selector('button:has-text("Log in")')
            await self.human.click_element(login_btn)
            
            # Wait for home page or check for additional verification
            try:
                await self.page.wait_for_url(self.HOME_URL, timeout=15000)
            except:
                # Might need to handle email verification or 2FA
                await self.human.random_delay(5, 10)
            
            # Session warmup - browse a bit like human
            await self.human.warmup_session(duration_seconds=20)
            
            await self.save_cookies()
            self.is_logged_in = True
            return True
            
        except Exception as e:
            print(f"Twitter login error: {e}")
            return False

    async def post(self, content: str) -> bool:
        """Create a new tweet with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            # Navigate to home
            await self.page.goto(self.HOME_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Simulate reading timeline
            await self.human.random_delay(2, 4)
            
            # Click post area with human-like movement
            post_box = await self.page.wait_for_selector('div[aria-label="Post text"]', timeout=10000)
            await self.human.hover(post_box)
            await self.human.click_element(post_box)
            
            await self.human.think_delay()
            
            # Type content with human-like typing
            await self.human.type_text(content, post_box)
            
            # Think before posting
            await self.human.random_delay(1, 3)
            
            # Click post button
            post_btn = await self.page.query_selector('button[data-testid="tweetButton"]')
            await self.human.move_to_element(post_btn)
            await self.human.click_element(post_btn)
            
            # Wait and verify
            await self.human.random_delay(2, 4)
            return True
            
        except Exception as e:
            print(f"Twitter post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a tweet with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://x.com/i/status/{post_id}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the tweet first
            await self.human.random_delay(2, 4)
            
            # Click like button with movement
            like_btn = await self.page.query_selector('button[data-testid="like"]')
            if like_btn:
                await self.human.hover(like_btn)
                await self.human.click_element(like_btn)
            
            await self.human.action_delay("like")
            return True
            
        except Exception as e:
            print(f"Twitter like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a tweet with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://x.com/i/status/{post_id}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the tweet
            await self.human.random_delay(3, 5)
            
            # Click reply button
            reply_btn = await self.page.query_selector('button[data-testid="reply"]')
            await self.human.hover(reply_btn)
            await self.human.click_element(reply_btn)
            
            await self.human.think_delay()
            
            # Type comment
            post_box = await self.page.query_selector('div[aria-label="Post text"]')
            await self.human.type_text(content, post_box)
            
            await self.human.random_delay(1, 2)
            
            # Submit reply
            reply_submit = await self.page.query_selector('button[data-testid="tweetButton"]')
            await self.human.click_element(reply_submit)
            
            await self.human.action_delay("comment")
            return True
            
        except Exception as e:
            print(f"Twitter comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a user with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://x.com/{username}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # View profile briefly
            await self.human.random_delay(2, 4)
            
            # Find and click follow button
            follow_btn = await self.page.query_selector('button:has-text("Follow")')
            if follow_btn:
                await self.human.hover(follow_btn)
                await self.human.click_element(follow_btn)
            
            await self.human.action_delay("follow")
            return True
            
        except Exception as e:
            print(f"Twitter follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search tweets with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            # Navigate to search
            await self.page.goto(f"https://x.com/search?q={query}&src=typed_query")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Let results load and scan
            await self.human.random_delay(2, 4)
            
            results = []
            tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
            
            for tweet in tweets[:limit]:
                try:
                    username_elem = await tweet.query_selector('div[data-testid="User-Name"]')
                    text_elem = await tweet.query_selector('div[data-testid="tweetText"]')
                    
                    results.append({
                        "username": await username_elem.inner_text() if username_elem else "",
                        "text": await text_elem.inner_text() if text_elem else "",
                    })
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Twitter search error: {e}")
            return []

    async def get_mentions(self, since_id: Optional[str] = None) -> list[dict]:
        """Get mentions with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto("https://x.com/notifications/mentions")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read notifications like human
            await self.human.random_delay(2, 4)
            
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
