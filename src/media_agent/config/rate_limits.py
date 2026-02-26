"""Rate limiting and platform settings configuration."""

from typing import Optional
from pydantic import BaseModel


class PlatformSettings(BaseModel):
    """Settings for a single platform."""
    
    platform: str
    enabled: bool = True
    posts_per_day: int = 5
    posts_per_week: int = 20
    delay_between_posts_min: int = 30  # minutes
    delay_between_posts_max: int = 120  # minutes
    active_hours_start: int = 9  # 9 AM
    active_hours_end: int = 21  # 9 PM
    max_likes_per_day: int = 50
    max_follows_per_day: int = 30
    max_comments_per_day: int = 20
    
    # Human behavior settings
    typing_speed_min_wpm: int = 40
    typing_speed_max_wpm: int = 80
    typo_error_rate: float = 0.02
    min_action_delay: float = 1.0
    max_action_delay: float = 5.0
    session_warmup: bool = True
    random_delays: bool = True


class RateLimiterSettings(BaseModel):
    """Global rate limiting settings."""
    
    # Global limits
    max_posts_per_day: int = 10
    max_posts_per_week: int = 50
    max_total_actions_per_day: int = 100
    
    # Platform-specific settings
    twitter: PlatformSettings = PlatformSettings(platform="twitter")
    instagram: PlatformSettings = PlatformSettings(platform="instagram")
    facebook: PlatformSettings = PlatformSettings(platform="facebook")
    linkedin: PlatformSettings = PlatformSettings(platform="linkedin")
    
    # Global active hours
    global_active_hours: bool = True
    global_active_start: int = 8
    global_active_end: int = 22
    
    # Rate limiting enabled
    rate_limiting_enabled: bool = True
    
    def get_platform_settings(self, platform: str) -> PlatformSettings:
        """Get settings for a specific platform."""
        return getattr(self, platform.lower(), self.twitter)
    
    def should_allow_action(
        self,
        platform: str,
        action_type: str,
        actions_today: int
    ) -> tuple[bool, str]:
        """Check if action should be allowed."""
        if not self.rate_limiting_enabled:
            return True, ""
        
        platform_settings = self.get_platform_settings(platform)
        
        if not platform_settings.enabled:
            return False, f"{platform} is disabled"
        
        # Check global daily limit
        if actions_today >= self.max_total_actions_per_day:
            return False, "Daily action limit reached"
        
        # Check platform-specific limits
        if action_type == "post":
            if actions_today >= platform_settings.posts_per_day:
                return False, f"Daily post limit for {platform} reached"
        
        elif action_type == "like":
            if actions_today >= platform_settings.max_likes_per_day:
                return False, f"Daily like limit for {platform} reached"
        
        elif action_type == "follow":
            if actions_today >= platform_settings.max_follows_per_day:
                return False, f"Daily follow limit for {platform} reached"
        
        elif action_type == "comment":
            if actions_today >= platform_settings.max_comments_per_day:
                return False, f"Daily comment limit for {platform} reached"
        
        return True, ""
    
    def get_delay_range(self, platform: str) -> tuple[int, int]:
        """Get delay range in minutes for platform."""
        settings = self.get_platform_settings(platform)
        return (settings.delay_between_posts_min, settings.delay_between_posts_max)


# Global settings instance
_rate_limiter_settings: Optional[RateLimiterSettings] = None


def get_rate_limiter_settings() -> RateLimiterSettings:
    """Get rate limiter settings instance."""
    global _rate_limiter_settings
    if _rate_limiter_settings is None:
        _rate_limiter_settings = RateLimiterSettings()
    return _rate_limiter_settings


def update_rate_limiter_settings(settings: RateLimiterSettings):
    """Update rate limiter settings."""
    global _rate_limiter_settings
    _rate_limiter_settings = settings
