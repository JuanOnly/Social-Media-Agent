"""Facebook platform adapter using Playwright with human behavior."""

from typing import Optional

from .base import PlatformAdapter
from .human import HumanBehavior


class FacebookAdapter(PlatformAdapter):
    """Facebook platform adapter using Playwright with human-like behavior."""

    LOGIN_URL = "https://www.facebook.com/login"
    HOME_URL = "https://www.facebook.com/"

    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self.human: Optional[HumanBehavior] = None

    async def login(self) -> bool:
        """Login to Facebook using Playwright with human behavior."""
        try:
            await self.init_browser(headless=False)
            
            self.human = HumanBehavior(self.page)
            
            await self.page.goto(self.LOGIN_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Enter email with human-like typing
            await self.page.wait_for_selector('input[id="email"]', timeout=10000)
            email_input = await self.page.query_selector('input[id="email"]')
            
            await self.human.type_text(self.username, email_input)
            await self.human.random_delay(0.5, 1.5)
            
            # Enter password with human-like typing
            password_input = await self.page.query_selector('input[id="pass"]')
            await self.human.type_text(self.password, password_input)
            
            await self.human.random_delay(0.5, 1.0)
            
            # Click login
            login_btn = await self.page.query_selector('button[type="submit"]')
            await self.human.click_element(login_btn)
            
            # Wait for home page
            await self.page.wait_for_url(self.HOME_URL, timeout=20000)
            
            # Session warmup
            await self.human.warmup_session(duration_seconds=20)
            
            await self.save_cookies()
            self.is_logged_in = True
            return True
            
        except Exception as e:
            print(f"Facebook login error: {e}")
            return False

    async def post(self, content: str) -> bool:
        """Create a new post on Facebook with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(self.HOME_URL)
            await self.human.timing.wait_for_page_load(self.page)
            
            # Browse home briefly like human
            await self.human.random_delay(2, 4)
            
            # Click on "What's on your mind" with human movement
            create_post_btn = await self.page.query_selector('[aria-label="Create a post"]')
            await self.human.hover(create_post_btn)
            await self.human.click_element(create_post_btn)
            
            await self.human.think_delay()
            
            # Type content with human-like typing
            post_box = await self.page.query_selector('[contenteditable="true"]')
            await self.human.type_text(content, post_box)
            
            await self.human.random_delay(1, 3)
            
            # Click post button
            post_btn = await self.page.query_selector('[aria-label="Post"]')
            await self.human.click_element(post_btn)
            
            await self.human.random_delay(2, 4)
            return True
            
        except Exception as e:
            print(f"Facebook post error: {e}")
            return False

    async def like(self, post_id: str) -> bool:
        """Like a post with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.facebook.com/{post_id}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the post first
            await self.human.random_delay(2, 4)
            
            # Click like with human-like movement
            like_btn = await self.page.query_selector('[aria-label="Like"]')
            if like_btn:
                await self.human.hover(like_btn)
                await self.human.click_element(like_btn)
            
            await self.human.action_delay("like")
            return True
            
        except Exception as e:
            print(f"Facebook like error: {e}")
            return False

    async def comment(self, post_id: str, content: str) -> bool:
        """Comment on a post with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.facebook.com/{post_id}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read the post
            await self.human.random_delay(3, 5)
            
            # Click comment box with movement
            comment_box = await self.page.query_selector('[aria-label="Write a comment"]')
            await self.human.hover(comment_box)
            await self.human.click_element(comment_box)
            
            await self.human.think_delay()
            
            # Type comment with human-like typing
            await self.human.type_text(content, comment_box)
            
            await self.human.random_delay(1, 2)
            
            # Press enter to submit
            await self.page.press('[aria-label="Write a comment"]', "Enter")
            
            await self.human.action_delay("comment")
            return True
            
        except Exception as e:
            print(f"Facebook comment error: {e}")
            return False

    async def follow(self, username: str) -> bool:
        """Follow a user/page with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.facebook.com/{username}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # View profile briefly
            await self.human.random_delay(2, 4)
            
            # Click follow with movement
            follow_btn = await self.page.query_selector('[aria-label="Follow"]')
            if follow_btn:
                await self.human.hover(follow_btn)
                await self.human.click_element(follow_btn)
            
            await self.human.action_delay("follow")
            return True
            
        except Exception as e:
            print(f"Facebook follow error: {e}")
            return False

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for content/pages with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto(f"https://www.facebook.com/search/top?q={query}")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Let results load and scan
            await self.human.random_delay(2, 4)
            
            results = []
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
        """Get mentions and notifications with human-like behavior."""
        if not self.is_logged_in:
            await self.login()
        
        if not self.human:
            self.human = HumanBehavior(self.page)
        
        try:
            await self.page.goto("https://www.facebook.com/notifications")
            await self.human.timing.wait_for_page_load(self.page)
            
            # Read notifications like human
            await self.human.random_delay(2, 4)
            
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
