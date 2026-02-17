"""AI Engine for OpenRouter integration."""

from typing import Optional

import httpx

from ..config import get_settings


class AIEngine:
    """AI Engine using OpenRouter API."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = self.settings.openrouter_model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using OpenRouter API."""
        if not self.settings.openrouter_api_key:
            raise ValueError("OpenRouter API key not configured")

        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8080",
            "X-Title": "MediaAgent",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_post(
        self,
        product_name: str,
        product_description: str,
        brand_voice: str,
        target_audience: str,
        post_type: str = "promotional",
        length: str = "medium",
    ) -> str:
        """Generate a social media post."""
        length_guide = {
            "short": "Keep it brief, under 100 characters",
            "medium": "Around 150-280 characters",
            "long": "Detailed post, up to 500 characters",
        }

        tone_map = {
            "friendly": "warm, approachable, use emojis occasionally",
            "professional": "formal, informative, business-oriented",
            "casual": "relaxed, conversational, like talking to a friend",
            "authoritative": "confident, knowledgeable, expert tone",
        }

        system_prompt = f"""You are a social media content generator. 
Create engaging posts tailored to the specified brand voice and audience.
Always include relevant hashtags. Don't make up specific numbers or claims."""

        prompt = f"""Generate a {post_type} social media post for a product called "{product_name}".
Product description: {product_description}
Brand voice: {tone_map.get(brand_voice, brand_voice)}
Target audience interests: {target_audience}
Length: {length_guide.get(length, length_guide['medium'])}

Create only the post content, no explanations or prefixes."""

        return await self.generate(prompt, system_prompt=system_prompt, max_tokens=600)

    async def generate_response(
        self,
        product_name: str,
        product_description: str,
        brand_voice: str,
        user_message: str,
    ) -> str:
        """Generate a response to user engagement."""
        tone_map = {
            "friendly": "warm and approachable",
            "professional": "formal and helpful",
            "casual": "casual and friendly",
            "authoritative": "confident and expert",
        }

        system_prompt = f"""You are a social media manager responding to user comments/messages.
Keep responses {tone_map.get(brand_voice, 'friendly')} and helpful.
Stay authentic and don't be overly salesy.
If you don't know something, be honest about it."""

        prompt = f"""Product: {product_name}
Product info: {product_description}

User message/comment: "{user_message}"

Write a natural, engaging response."""

        return await self.generate(prompt, system_prompt=system_prompt, max_tokens=300)

    async def search_leads(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        search_query: str,
        platform: str = "twitter",
    ) -> list[dict]:
        """Generate search suggestions for lead discovery."""
        system_prompt = """You are a social media marketing expert helping find potential customers.
Generate relevant search queries to find people interested in similar products."""

        prompt = f"""Product: {product_name}
Description: {product_description}
Target audience: {target_audience}
Platform: {platform}

Generate 5 specific hashtags and 5 specific keywords/accounts to search for.
Format as a simple list, one per line.
Focus on people who would be interested in this type of product."""

        result = await self.generate(prompt, system_prompt=system_prompt, max_tokens=300)
        return {"suggestions": result}


# Global AI engine instance
_ai_engine: Optional[AIEngine] = None


def get_ai_engine() -> AIEngine:
    """Get AI engine instance."""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine
