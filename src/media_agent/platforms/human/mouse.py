"""Human-like mouse movement simulation."""

import asyncio
import random
from typing import List, Tuple
from playwright.async_api import Page


class MouseBehavior:
    """Human-like mouse movement simulation."""
    
    def __init__(self, page: Page):
        self.page = page
        self.min_speed = 0.5  # pixels per ms
        self.max_speed = 2.0
    
    def _bezier_curve(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        control1: Tuple[float, float],
        control2: Tuple[float, float],
        steps: int = 20
    ) -> List[Tuple[float, float]]:
        """Generate bezier curve points between start and end."""
        points = []
        for t in range(steps + 1):
            t = t / steps
            # Cubic bezier formula
            x = (1-t)**3 * start[0] + 3*(1-t)**2*t * control1[0] + 3*(1-t)*t**2 * control2[0] + t**3 * end[0]
            y = (1-t)**3 * start[1] + 3*(1-t)**2*t * control1[1] + 3*(1-t)*t**2 * control2[1] + t**3 * end[1]
            points.append((x, y))
        return points
    
    def _generate_control_points(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float]
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Generate random control points for bezier curve."""
        # Calculate midpoint with some randomness
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Add random offset for control points
        offset_range = 100
        control1 = (
            mid_x + random.uniform(-offset_range, offset_range),
            start[1] + random.uniform(-offset_range, offset_range)
        )
        control2 = (
            mid_x + random.uniform(-offset_range, offset_range),
            end[1] + random.uniform(-offset_range, offset_range)
        )
        return control1, control2
    
    async def move_to(
        self,
        x: float,
        y: float,
        duration_ms: int = 500
    ):
        """Move mouse to position with human-like curve."""
        # Get current position
        current = await self.page.mouse.position()
        
        if current == (x, y):
            return
        
        # Generate bezier curve
        control1, control2 = self._generate_control_points(
            (current['x'], current['y']),
            (x, y)
        )
        
        points = self._bezier_curve(
            (current['x'], current['y']),
            (x, y),
            control1,
            control2,
            steps=random.randint(15, 30)
        )
        
        # Move along curve with varying speed
        for i, (px, py) in enumerate(points):
            await self.page.mouse.move(px, py)
            # Vary speed - slow at start/end, faster in middle
            progress = i / len(points)
            if progress < 0.2 or progress > 0.8:
                await asyncio.sleep(0.02)  # Slow at edges
            else:
                await asyncio.sleep(random.uniform(0.01, 0.015))  # Faster in middle
    
    async def move_to_element(self, element, duration_ms: int = 500):
        """Move mouse to an element."""
        box = await element.bounding_box()
        if not box:
            return
        
        # Move to center of element with some random offset
        offset_x = random.uniform(-box['width']/3, box['width']/3)
        offset_y = random.uniform(-box['height']/3, box['height']/3)
        
        target_x = box['x'] + box['width']/2 + offset_x
        target_y = box['y'] + box['height']/2 + offset_y
        
        await self.move_to(target_x, target_y, duration_ms)
    
    async def click(
        self,
        x: float = None,
        y: float = None,
        element = None,
        button: str = "left"
    ):
        """Human-like click with small movement before/after."""
        if element:
            await self.move_to_element(element, duration_ms=random.randint(300, 600))
            box = await element.bounding_box()
            x = box['x'] + box['width']/2
            y = box['y'] + box['height']/2
        elif x and y:
            await self.move_to(x, y, duration_ms=random.randint(200, 400))
        
        # Small pause before click
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Click with slight randomness
        await self.page.mouse.down(x=x, y=y, button=button)
        await asyncio.sleep(random.uniform(0.03, 0.08))
        await self.page.mouse.up(x=x, y=y, button=button)
        
        # Tiny movement after click (natural)
        await asyncio.sleep(0.1)
        await self.page.mouse.move(x + random.uniform(-2, 2), y + random.uniform(-2, 2))
    
    async def double_click(self, element=None):
        """Human-like double click."""
        await self.click(element=element)
        await asyncio.sleep(random.uniform(0.05, 0.1))
        await self.click(element=element)
    
    async def right_click(self, element=None):
        """Right click context menu."""
        if element:
            await self.move_to_element(element)
            box = await element.bounding_box()
            x = box['x'] + box['width']/2
            y = box['y'] + box['height']/2
            await self.page.mouse.click(x, y, button="right")
        else:
            await self.page.mouse.click(button="right")
    
    async def hover(self, element, duration_ms: int = 500):
        """Hover over element like a human."""
        await self.move_to_element(element, duration_ms)
        # Small pause after hovering
        await asyncio.sleep(random.uniform(0.3, 0.8))
    
    async def scroll_down(self, pixels: int = 300):
        """Human-like scroll."""
        # Scroll in small increments
        for _ in range(random.randint(2, 4)):
            await self.page.mouse.wheel(0, pixels // 3)
            await asyncio.sleep(random.uniform(0.1, 0.2))
    
    async def scroll_to_element(self, element):
        """Scroll element into view like human."""
        await element.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.2, 0.4))
        
        # Center element on screen
        box = await element.bounding_box()
        if box:
            target_y = box['y'] + box['height']/2 - 400  # Center-ish
            await self.page.mouse.wheel(0, target_y)
            await asyncio.sleep(random.uniform(0.3, 0.5))
