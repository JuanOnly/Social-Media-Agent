"""FAQ matcher service."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import get_faqs


class FAQMatcher:
    """Match incoming questions to FAQ database."""

    def __init__(self):
        self.min_score_threshold = 0.3

    def _calculate_keyword_score(self, query: str, faq_keywords: str) -> float:
        """Calculate keyword matching score."""
        if not faq_keywords:
            return 0.0

        query_lower = query.lower()
        keywords = [k.strip().lower() for k in faq_keywords.split(",")]

        matches = sum(1 for kw in keywords if kw in query_lower)
        return matches / len(keywords) if keywords else 0.0

    def _calculate_text_similarity(self, query: str, question: str) -> float:
        """Calculate simple text similarity."""
        query_words = set(query.lower().split())
        question_words = set(question.lower().split())

        if not query_words or not question_words:
            return 0.0

        intersection = query_words.intersection(question_words)
        return len(intersection) / max(len(query_words), len(question_words))

    async def find_matching_faq(
        self,
        session: AsyncSession,
        product_id: int,
        query: str,
    ) -> Optional[tuple]:
        """Find the best matching FAQ for a query."""
        faqs = await get_faqs(session, product_id)

        best_match = None
        best_score = 0.0

        for faq in faqs:
            keyword_score = self._calculate_keyword_score(query, faq.keywords or "")
            similarity_score = self._calculate_text_similarity(query, faq.question)
            combined_score = (keyword_score * 0.6) + (similarity_score * 0.4)

            if combined_score > best_score:
                best_score = combined_score
                best_match = faq

        if best_score >= self.min_score_threshold:
            return best_match, best_score

        return None


# Global FAQ matcher instance
_faq_matcher: Optional[FAQMatcher] = None


def get_faq_matcher() -> FAQMatcher:
    """Get FAQ matcher instance."""
    global _faq_matcher
    if _faq_matcher is None:
        _faq_matcher = FAQMatcher()
    return _faq_matcher
