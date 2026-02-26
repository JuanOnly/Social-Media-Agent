"""Human-like timing and delays."""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional


class TimingBehavior:
    """Human-like timing and delay simulation."""
    
    def __init__(self):
        self.min_delay = 1.0  # seconds
        self.max_delay = 5.0  # seconds
        
        # Peak hours for posting (24-hour format)
        self.peak_hours = [9, 10, 11, 12, 13, 17, 18, 19, 20]
        
        # Activity probability by hour
        self.hourly_activity = {
            # Early morning - low
            0: 0.1, 1: 0.05, 2: 0.02, 3: 0.02, 4: 0.02, 5: 0.05,
            # Morning - increasing
            6: 0.15, 7: 0.3, 8: 0.5, 9: 0.8, 10: 0.9, 11: 0.9,
            # Lunch - slightly lower
            12: 0.8, 13: 0.7,
            # Afternoon - building
            14: 0.8, 15: 0.85, 16: 0.9,
            # Evening - peak
            17: 0.95, 18: 1.0, 19: 1.0, 20: 0.95, 21: 0.85,
            # Night - declining
            22: 0.6, 23: 0.3,
        }
    
    async def random_delay(
        self,
        min_seconds: Optional[float] = None,
        max_seconds: Optional[float] = None
    ):
        """Wait for a random duration like human would."""
        if min_seconds is None:
            min_seconds = self.min_delay
        if max_seconds is None:
            max_seconds = self.max_delay
        
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def think_delay(self):
        """Simulate thinking time before acting."""
        # Random think time between actions
        await self.random_delay(0.5, 2.0)
    
    async def reading_delay(self, text_length: int):
        """Simulate reading time based on content length."""
        # Average reading speed: 200-250 words per minute
        # Average 5 characters per word
        words = text_length / 5
        reading_time = words / random.uniform(200, 250)  # in minutes
        
        # Add some randomness
        actual_delay = reading_time * random.uniform(0.8, 1.2)
        
        # Cap at reasonable maximum
        actual_delay = min(actual_delay, 5.0)  # Max 5 seconds simulated reading
        
        if actual_delay > 0.1:
            await asyncio.sleep(actual_delay)
    
    def get_activity_factor(self) -> float:
        """Get activity factor based on time of day."""
        hour = datetime.now().hour
        return self.hourly_activity.get(hour, 0.5)
    
    def should_post_now(self, max_posts_per_hour: int = 5) -> bool:
        """Decide if we should post now based on time patterns."""
        # Check if within active hours
        hour = datetime.now().hour
        
        # Not active during sleeping hours
        if hour < 6 or hour > 23:
            return False
        
        # Check activity factor
        activity = self.get_activity_factor()
        
        # Probability of posting now
        posts_probability = (max_posts_per_hour / 60) * activity
        
        return random.random() < posts_probability
    
    def get_optimal_post_time(self, preferred_hours: list = None) -> datetime:
        """Get optimal time to post based on settings."""
        now = datetime.now()
        
        if preferred_hours is None:
            preferred_hours = self.peak_hours
        
        # Find next preferred hour
        for hour in preferred_hours:
            if hour > now.hour:
                return now.replace(hour=hour, minute=random.randint(0, 59), second=0)
        
        # If no hours left today, return tomorrow's first preferred hour
        return now.replace(hour=preferred_hours[0], minute=random.randint(0, 59), second=0) + timedelta(days=1)
    
    async def wait_for_page_load(self, page):
        """Wait for page to load like human would."""
        # Wait for network idle
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass
        
        # Simulate reading time before proceeding
        await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def between_actions_delay(self):
        """Delay between actions to seem natural."""
        # Longer delay between major actions
        await self.random_delay(2.0, 5.0)
    
    def set_delay_range(self, min_sec: float, max_sec: float):
        """Configure delay range."""
        self.min_delay = min_sec
        self.max_delay = max_sec
    
    def is_active_hours(self) -> bool:
        """Check if current time is within active hours."""
        hour = datetime.now().hour
        return 7 <= hour <= 22
    
    def get_min_delay_for_action(self, action_type: str) -> float:
        """Get minimum delay for specific action type."""
        delays = {
            'like': 1.0,
            'comment': 3.0,
            'follow': 2.0,
            'post': 5.0,
            'message': 5.0,
            'search': 2.0,
            'view_profile': 3.0,
        }
        return delays.get(action_type, 2.0)
    
    async def action_delay(self, action_type: str):
        """Delay appropriate for specific action type."""
        min_delay = self.get_min_delay_for_action(action_type)
        max_delay = min_delay * 2
        await self.random_delay(min_delay, max_delay)
