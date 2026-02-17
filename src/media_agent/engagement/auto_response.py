"""Auto-response service for monitoring and replying to engagement."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import get_db, get_products, get_faqs, update_post, log_activity
from ..platforms import get_platform_registry
from ..agents.ai_engine import get_ai_engine

logger = logging.getLogger(__name__)


class AutoResponder:
    """Service for automatically responding to mentions and comments."""

    def __init__(self):
        self.ai_engine = get_ai_engine()
        self.is_running = False
        self._check_interval = 120  # Check every 2 minutes
        self._last_check: dict = {}  # Track last check per platform

    async def start(self):
        """Start the auto-responder."""
        self.is_running = True
        logger.info("Auto-responder started")

    async def stop(self):
        """Stop the auto-responder."""
        self.is_running = False
        logger.info("Auto-responder stopped")

    async def check_and_respond(
        self,
        platform: str,
        product_id: int,
        username: str = "",
        password: str = "",
    ):
        """Check for new mentions and respond."""
        if not username or not password:
            logger.warning(f"No credentials for {platform}, skipping auto-response")
            return

        db = get_db()
        async with db.async_session_maker() as session:
            # Get product info
            products = await get_products(session)
            product = next((p for p in products if p.id == product_id), None)
            
            if not product:
                logger.warning(f"Product {product_id} not found")
                return

            # Get FAQs
            faqs = await get_faqs(session, product_id)

            # Get platform adapter
            try:
                registry = get_platform_registry()
                adapter = registry.get_adapter(platform, username, password)
                await adapter.login()

                # Get mentions
                since_id = self._last_check.get(platform)
                mentions = await adapter.get_mentions(since_id)

                # Process each mention
                for mention in mentions:
                    await self._process_mention(
                        session=session,
                        adapter=adapter,
                        product=product,
                        faqs=faqs,
                        mention=mention,
                        platform=platform,
                    )

                # Update last check
                self._last_check[platform] = datetime.utcnow().isoformat()

            except Exception as e:
                logger.error(f"Auto-response error for {platform}: {e}")

    async def _process_mention(
        self,
        session: AsyncSession,
        adapter,
        product,
        faqs,
        mention: dict,
        platform: str,
    ):
        """Process a single mention and generate response."""
        try:
            text = mention.get("text", "")
            
            # Try to find matching FAQ
            matched_faq = None
            for faq in faqs:
                if self._keyword_match(text, faq.question) or self._keyword_match(text, faq.keywords or ""):
                    matched_faq = faq
                    break

            if matched_faq:
                response = matched_faq.answer
                response_source = f"FAQ: {matched_faq.question}"
            else:
                # Use AI to generate response
                response = await self.ai_engine.generate_response(
                    product_name=product.name,
                    product_description=product.description or "",
                    brand_voice=product.brand_voice,
                    user_message=text,
                )
                response_source = "AI-generated"

            # Log the response
            await log_activity(
                session,
                action=f"Auto-responded to {platform} mention",
                product_id=product.id,
                platform=platform,
                details=f"Query: {text[:50]}... | Response: {response[:50]}... | Source: {response_source}",
            )

            logger.info(f"Generated response for {platform}: {response[:50]}...")

            # Note: Actual posting would require implementing reply functionality
            # For now, we just log it
            
            return response

        except Exception as e:
            logger.error(f"Error processing mention: {e}")
            return None

    def _keyword_match(self, text: str, keywords: str) -> bool:
        """Check if text contains any keyword."""
        if not keywords:
            return False
        
        text_lower = text.lower()
        for keyword in keywords.split(","):
            keyword = keyword.strip().lower()
            if keyword and keyword in text_lower:
                return True
        return False

    async def respond_to_comment(
        self,
        platform: str,
        post_id: str,
        comment: str,
        product_id: int,
        username: str = "",
        password: str = "",
    ) -> Optional[str]:
        """Respond to a specific comment."""
        db = get_db()
        async with db.async_session_maker() as session:
            # Get product info
            products = await get_products(session)
            product = next((p for p in products if p.id == product_id), None)
            
            if not product:
                return None

            # Get FAQs
            faqs = await get_faqs(session, product_id)

            # Try FAQ match first
            matched_faq = None
            for faq in faqs:
                if self._keyword_match(comment, faq.question) or self._keyword_match(comment, faq.keywords or ""):
                    matched_faq = faq
                    break

            if matched_faq:
                response = matched_faq.answer
            else:
                # Use AI
                response = await self.ai_engine.generate_response(
                    product_name=product.name,
                    product_description=product.description or "",
                    brand_voice=product.brand_voice,
                    user_message=comment,
                )

            # Post the response
            try:
                registry = get_platform_registry()
                adapter = registry.get_adapter(platform, username, password)
                await adapter.login()
                
                await adapter.comment(post_id, response)
                
                await log_activity(
                    session,
                    action=f"Replied to comment on {platform}",
                    product_id=product_id,
                    platform=platform,
                    details=f"Comment: {comment[:50]}... | Response: {response[:50]}...",
                )
                
                return response
                
            except Exception as e:
                logger.error(f"Error posting response: {e}")
                return None


# Global auto-responder instance
_auto_responder: Optional[AutoResponder] = None


def get_auto_responder() -> AutoResponder:
    """Get auto-responder instance."""
    global _auto_responder
    if _auto_responder is None:
        _auto_responder = AutoResponder()
    return _auto_responder
