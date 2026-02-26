"""Human-like typing simulation."""

import asyncio
import random
from typing import Optional


class TypingBehavior:
    """Human-like typing behavior simulation."""
    
    def __init__(self):
        # Typing speed range (words per minute)
        self.min_wpm = 40
        self.max_wpm = 80
        
        # Error rate (0.02 = 2% of keystrokes have typo)
        self.error_rate = 0.02
        
        # Chance to make a correction
        self.correction_rate = 0.3
    
    def _calculate_keystroke_delay(self, wpm: int) -> float:
        """Calculate delay between keystrokes in seconds."""
        return 60.0 / (wpm * 5)  # Average 5 chars per word
    
    def _should_make_error(self) -> bool:
        """Randomly decide if we should make a typo."""
        return random.random() < self.error_rate
    
    def _get_typo(self, char: str) -> str:
        """Generate a realistic typo for a character."""
        # Common keyboard substitutions
        typos = {
            'a': ['q', 'w', 's', 'z'],
            'b': ['v', 'g', 'h', 'n'],
            'c': ['x', 'd', 'f', 'v'],
            'd': ['s', 'e', 'r', 'f', 'c', 'x'],
            'e': ['w', 's', 'd', 'r'],
            'f': ['d', 'r', 't', 'g', 'v', 'c'],
            'g': ['f', 't', 'y', 'h', 'b', 'v'],
            'h': ['g', 'y', 'u', 'j', 'n', 'b'],
            'i': ['u', 'j', 'k', 'o'],
            'j': ['h', 'u', 'i', 'k', 'm', 'n'],
            'k': ['j', 'i', 'o', 'l', 'm'],
            'l': ['k', 'o', 'p'],
            'm': ['n', 'j', 'k', 'l'],
            'n': ['b', 'h', 'j', 'm'],
            'o': ['i', 'k', 'l', 'p'],
            'p': ['o', 'l'],
            'q': ['w', 'a'],
            'r': ['e', 'd', 'f', 't'],
            's': ['a', 'w', 'e', 'd', 'x', 'z'],
            't': ['r', 'f', 'g', 'y'],
            'u': ['y', 'h', 'j', 'i'],
            'v': ['c', 'f', 'g', 'b'],
            'w': ['q', 'a', 's', 'e'],
            'x': ['s', 'd', 'z', 'c'],
            'y': ['t', 'g', 'h', 'u'],
            'z': ['a', 's', 'x'],
            ' ': [' '],
        }
        
        if char.lower() in typos:
            return random.choice(typos[char.lower()])
        return char
    
    async def type_text(
        self,
        page,
        text: str,
        element = None,
        wpm: Optional[int] = None
    ):
        """Type text like a human with realistic delays and occasional errors."""
        if wpm is None:
            wpm = random.randint(self.min_wpm, self.max_wpm)
        
        base_delay = self._calculate_keystroke_delay(wpm)
        
        # Focus element first
        if element:
            await element.click()
            await asyncio.sleep(random.uniform(0.1, 0.2))
        
        for char in text:
            # Random typing speed variation
            delay = base_delay * random.uniform(0.7, 1.3)
            
            # Occasional longer pause (like thinking)
            if random.random() < 0.05:  # 5% chance
                delay += random.uniform(0.2, 0.5)
            
            # Handle special keys
            if char == '\n':
                await page.keyboard.press('Enter')
            elif char == '\t':
                await page.keyboard.press('Tab')
            elif char == ' ':
                await page.keyboard.press('Space')
            else:
                # Check if we should make a typo
                if self._should_make_error():
                    # Type wrong character
                    wrong_char = self._get_typo(char)
                    await page.keyboard.type(wrong_char, delay=delay)
                    
                    # Maybe correct it
                    if random.random() < self.correction_rate:
                        # Backspace
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                        await page.keyboard.press('Backspace')
                        await asyncio.sleep(random.uniform(0.05, 0.15))
                        
                        # Type correct character
                        await page.keyboard.type(char, delay=delay)
                else:
                    # Type normally
                    await page.keyboard.type(char, delay=delay)
        
        # Small pause after typing
        await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def type_into(
        self,
        element,
        text: str,
        wpm: Optional[int] = None
    ):
        """Type into a specific element."""
        if wpm is None:
            wpm = random.randint(self.min_wpm, self.max_wpm)
        
        base_delay = self._calculate_keystroke_delay(wpm)
        
        # Click to focus
        await element.click()
        await asyncio.sleep(random.uniform(0.1, 0.2))
        
        # Clear existing text
        await element.fill('')
        
        # Type character by character for human-like feel
        for char in text:
            delay = base_delay * random.uniform(0.7, 1.3)
            
            # Occasional pause
            if random.random() < 0.03:
                delay += random.uniform(0.15, 0.4)
            
            if char == '\n':
                await element.press('Enter')
            else:
                await element.type(char, delay=delay)
        
        await asyncio.sleep(random.uniform(0.1, 0.2))
    
    async def fill_form(
        self,
        page,
        fields: dict
    ):
        """Fill a form like a human would."""
        for selector, value in fields.items():
            element = await page.query_selector(selector)
            if element:
                # Click field
                await element.click()
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
                # Clear
                await element.fill('')
                
                # Type value
                await self.type_into(element, value)
                
                # Small pause between fields
                await asyncio.sleep(random.uniform(0.2, 0.5))
    
    def set_typing_speed(self, min_wpm: int, max_wpm: int):
        """Configure typing speed range."""
        self.min_wpm = min_wpm
        self.max_wpm = max_wpm
    
    def set_error_rate(self, rate: float):
        """Configure typo error rate (0.0 to 1.0)."""
        self.error_rate = rate
