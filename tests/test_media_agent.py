"""Unit tests for MediaAgent."""

import pytest
from datetime import datetime


class TestModels:
    """Test database models."""

    def test_product_model(self):
        from src.media_agent.models.models import Product
        
        product = Product(
            name="Test Product",
            description="A test product",
            brand_voice="friendly",
            target_audience="testers",
        )
        
        assert product.name == "Test Product"
        assert product.description == "A test product"
        assert product.brand_voice == "friendly"
        assert product.target_audience == "testers"

    def test_post_model(self):
        from src.media_agent.models.models import Post
        
        post = Post(
            product_id=1,
            content="Test post content",
            platform="twitter",
            status="draft",
        )
        
        assert post.product_id == 1
        assert post.content == "Test post content"
        assert post.platform == "twitter"
        assert post.status == "draft"

    def test_faq_model(self):
        from src.media_agent.models.models import FAQ
        
        faq = FAQ(
            product_id=1,
            question="How does it work?",
            answer="It works great!",
            keywords="how, work",
        )
        
        assert faq.question == "How does it work?"
        assert faq.answer == "It works great!"
        assert faq.keywords == "how, work"

    def test_lead_model(self):
        from src.media_agent.models.models import Lead
        
        lead = Lead(
            product_id=1,
            platform="twitter",
            username="testuser",
            display_name="Test User",
            followers=1000,
            relevance_score=0.85,
            status="new",
        )
        
        assert lead.username == "testuser"
        assert lead.platform == "twitter"
        assert lead.followers == 1000
        assert lead.relevance_score == 0.85


class TestFAQMatcher:
    """Test FAQ matching logic."""

    def test_keyword_match(self):
        from src.media_agent.content.faq_matcher import FAQMatcher
        
        matcher = FAQMatcher()
        
        # Test keyword matching
        score = matcher._calculate_keyword_score(
            "How does this product work?",
            "how, work, product"
        )
        assert score > 0
        
        # Test no match
        score = matcher._calculate_keyword_score(
            "Hello world",
            "pricing, cost, buy"
        )
        assert score == 0.0

    def test_text_similarity(self):
        from src.media_agent.content.faq_matcher import FAQMatcher
        
        matcher = FAQMatcher()
        
        score = matcher._calculate_text_similarity(
            "How does it work?",
            "How does this work?"
        )
        assert score > 0


class TestAIEngine:
    """Test AI engine."""

    def test_ai_engine_initialization(self):
        from src.media_agent.agents.ai_engine import AIEngine
        
        engine = AIEngine()
        assert engine.model is not None
        assert engine.base_url == "https://openrouter.ai/api/v1"


class TestPlatformRegistry:
    """Test platform registry."""

    def test_registry_lists_platforms(self):
        from src.media_agent.platforms import get_platform_registry
        
        registry = get_platform_registry()
        platforms = registry.list_platforms()
        
        assert "twitter" in platforms
        assert "instagram" in platforms

    def test_get_twitter_adapter(self):
        from src.media_agent.platforms import get_platform_registry
        from src.media_agent.platforms.twitter import TwitterAdapter
        
        registry = get_platform_registry()
        adapter = registry.get_adapter("twitter", "user", "pass")
        
        assert isinstance(adapter, TwitterAdapter)
        assert adapter.username == "user"


class TestScheduler:
    """Test post scheduler."""

    def test_scheduler_initialization(self):
        from src.media_agent.scheduler.scheduler import PostScheduler
        
        scheduler = PostScheduler()
        assert scheduler.is_running == False


class TestConfig:
    """Test configuration."""

    def test_settings_defaults(self):
        from src.media_agent.config import get_settings
        
        settings = get_settings()
        
        assert settings.app_port == 8080
        assert settings.openrouter_model == "deepseek/deepseek-chat"

    def test_project_root(self):
        from src.media_agent.config import get_project_root
        
        root = get_project_root()
        assert root.exists()


class TestDatabase:
    """Test database operations."""

    @pytest.mark.asyncio
    async def test_database_initialization(self):
        from src.media_agent.models.database import Database
        
        db = Database()
        assert db.engine is not None
