"""Lead discovery service."""

import asyncio
import re
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.ai_engine import get_ai_engine
from ..models.database import create_lead
from ..models.models import Lead
from ..platforms import get_platform_registry


class LeadDiscovery:
    """Service for discovering potential leads."""

    def __init__(self):
        self.ai_engine = get_ai_engine()
        
        # Keywords related to link-in-bio tools
        self.product_keywords = [
            "link in bio", "linktree", "link tree", "bio link",
            "link page", "link bio", "biolink", "linktree alternative",
            "link in bio tool", "creator tools", "social media links",
            "personal brand", "influencer", "content creator"
        ]

    async def get_search_suggestions(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
    ) -> dict:
        """Get AI-powered search suggestions."""
        suggestions = await self.ai_engine.search_leads(
            product_name=product_name,
            product_description=product_description,
            target_audience=target_audience,
            search_query="",
            platform="twitter",
        )
        return suggestions

    async def search_leads_on_platform(
        self,
        platform: str,
        query: str,
        username: str = "",
        password: str = "",
        limit: int = 20,
    ) -> list[dict]:
        """Search for leads on a specific platform using Playwright."""
        try:
            registry = get_platform_registry()
            adapter = registry.get_adapter(platform, username, password)
            
            # Login if credentials provided
            if username and password:
                await adapter.login()
            
            # Search
            results = await adapter.search(query, limit=limit)
            
            # Parse and score results
            leads = []
            for result in results:
                score = self._calculate_relevance_score(result.get("text", ""), query)
                leads.append({
                    "platform": platform,
                    "username": result.get("username", ""),
                    "text": result.get("text", ""),
                    "relevance_score": score,
                })
            
            return leads
            
        except Exception as e:
            print(f"Lead search error: {e}")
            return []

    def _calculate_relevance_score(self, text: str, query: str) -> float:
        """Calculate relevance score based on keyword matching."""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        score = 0.0
        
        # Check for product keywords
        for keyword in self.product_keywords:
            if keyword in text_lower:
                score += 0.2
        
        # Check for query relevance
        if query_lower in text_lower:
            score += 0.3
        
        # Boost for multiple mentions
        count = text_lower.count(query_lower)
        if count > 1:
            score += 0.1
        
        return min(score, 1.0)

    async def search_leads(
        self,
        session,
        product_id: int,
        product_name: str,
        product_description: str,
        target_audience: str,
        query: str,
        platform: str = "twitter",
    ) -> list[dict]:
        """Search for potential leads."""
        # Get AI suggestions
        suggestions = await self.get_search_suggestions(
            product_name, product_description, target_audience
        )
        
        # Build search queries
        search_queries = [query] if query else []
        
        # Add keyword-based searches
        for keyword in self.product_keywords[:5]:
            search_queries.append(keyword)
        
        # Search for leads
        all_leads = []
        
        for search_query in search_queries[:5]:  # Limit searches
            leads = await self.search_leads_on_platform(
                platform=platform,
                query=search_query,
                limit=10,
            )
            all_leads.extend(leads)
        
        # Remove duplicates and sort by score
        seen = set()
        unique_leads = []
        for lead in all_leads:
            if lead["username"] not in seen and lead["username"]:
                seen.add(lead["username"])
                unique_leads.append(lead)
        
        unique_leads.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return unique_leads[:20]  # Return top 20

    async def save_lead(
        self,
        session: AsyncSession,
        product_id: int,
        platform: str,
        username: str,
        display_name: str = "",
        bio: str = "",
        followers: int = 0,
        relevance_score: float = 0.0,
        tags: str = "",
    ) -> Lead:
        """Save a lead to the database."""
        return await create_lead(
            session=session,
            product_id=product_id,
            platform=platform,
            username=username,
            display_name=display_name,
            bio=bio,
            followers=followers,
            relevance_score=relevance_score,
            tags=tags,
        )

    async def engage_with_lead(
        self,
        platform: str,
        username: str,
        action: str = "follow",
        message: str = "",
        username_creds: str = "",
        password_creds: str = "",
    ) -> bool:
        """Engage with a lead (follow, like, comment)."""
        try:
            registry = get_platform_registry()
            adapter = registry.get_adapter(platform, username_creds, password_creds)
            
            await adapter.login()
            
            if action == "follow":
                return await adapter.follow(username)
            elif action == "like":
                # Would need post ID
                return False
            elif action == "message" and message:
                # Would need DM capability
                return False
            
            return False
            
        except Exception as e:
            print(f"Engage error: {e}")
            return False


# Global lead discovery instance
_lead_discovery: Optional[LeadDiscovery] = None


def get_lead_discovery() -> LeadDiscovery:
    """Get lead discovery instance."""
    global _lead_discovery
    if _lead_discovery is None:
        _lead_discovery = LeadDiscovery()
    return _lead_discovery
