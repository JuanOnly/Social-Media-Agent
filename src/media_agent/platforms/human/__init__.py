"""Main human behavior module combining all features."""

from .mouse import MouseBehavior
from .typing import TypingBehavior
from .timing import TimingBehavior


class HumanBehavior:
    """Combined human behavior simulation for Playwright."""
    
    def __init__(self, page=None):
        self.page = page
        self.mouse = MouseBehavior(page) if page else None
        self.typing = TypingBehavior()
        self.timing = TimingBehavior()
    
    def set_page(self, page):
        """Set the Playwright page reference."""
        self.page = page
        self.mouse = MouseBehavior(page)
    
    # Delegate common methods for convenience
    async def random_delay(self, min_sec=None, max_sec=None):
        """Random delay between actions."""
        await self.timing.random_delay(min_sec, max_sec)
    
    async def think_delay(self):
        """Simulate thinking."""
        await self.timing.think_delay()
    
    async def action_delay(self, action_type: str):
        """Delay appropriate for action type."""
        await self.timing.action_delay(action_type)
    
    async def between_actions(self):
        """Delay between major actions."""
        await self.timing.between_actions_delay()
    
    async def type_text(self, text: str, element=None):
        """Human-like typing."""
        if element:
            await self.typing.type_into(element, text)
        elif self.page:
            await self.typing.type_text(self.page, text)
    
    async def move_to_element(self, element, duration_ms: int = 500):
        """Move mouse to element."""
        if self.mouse:
            await self.mouse.move_to_element(element, duration_ms)
    
    async def click_element(self, element=None, x=None, y=None):
        """Human-like click."""
        if self.mouse:
            await self.mouse.click(element=element, x=x, y=y)
    
    async def hover(self, element):
        """Hover over element."""
        if self.mouse:
            await self.mouse.hover(element)
    
    async def scroll_down(self, pixels: int = 300):
        """Scroll down like human."""
        if self.mouse:
            await self.mouse.scroll_down(pixels)
    
    # Configuration methods
    def set_typing_speed(self, min_wpm: int, max_wpm: int):
        """Set typing speed range."""
        self.typing.set_typing_speed(min_wpm, max_wpm)
    
    def set_error_rate(self, rate: float):
        """Set typo error rate."""
        self.typing.set_error_rate(rate)
    
    def set_delay_range(self, min_sec: float, max_sec: float):
        """Set delay range between actions."""
        self.timing.set_delay_range(min_sec, max_sec)
    
    # Session warmup
    async def warmup_session(self, duration_seconds: int = 30):
        """Browse randomly to warm up session."""
        if not self.page:
            return
        
        # Simple warmup - visit home page and scroll
        try:
            # Visit home
            await self.page.goto("https://twitter.com/home", timeout=10000)
            await self.timing.wait_for_page_load(self.page)
            
            # Scroll a few times
            for _ in range(3):
                await self.scroll_down(random.randint(200, 400))
                await self.random_delay(1, 2)
                
        except Exception:
            pass  # Warmup is optional, don't fail
    
    # Check if should act now based on time patterns
    def should_act_now(self, max_per_hour: int = 5) -> bool:
        """Check if timing is appropriate to act."""
        return self.timing.should_post_now(max_per_hour)
