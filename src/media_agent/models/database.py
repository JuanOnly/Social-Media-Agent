"""Database connection and operations."""

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from ..config import get_settings
from ..models import Base, Product, Post, FAQ, Lead, PlatformCredential, ActivityLog, Analytics


class Database:
    """Database manager for SQLite operations."""

    def __init__(self):
        settings = get_settings()
        self.engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init_db(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with self.async_session_maker() as session:
            yield session

    async def get_session_context(self) -> AsyncSession:
        """Get database session context manager."""
        return self.async_session_maker()


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


# Product CRUD operations
async def create_product(
    session: AsyncSession,
    name: str,
    description: str = "",
    brand_voice: str = "friendly",
    target_audience: str = "",
) -> Product:
    """Create a new product."""
    product = Product(
        name=name,
        description=description,
        brand_voice=brand_voice,
        target_audience=target_audience,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def get_products(session: AsyncSession) -> list[Product]:
    """Get all products."""
    result = await session.execute(select(Product).order_by(Product.created_at.desc()))
    return list(result.scalars().all())


async def get_product(session: AsyncSession, product_id: int) -> Optional[Product]:
    """Get product by ID."""
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def update_product(
    session: AsyncSession,
    product_id: int,
    **kwargs,
) -> Optional[Product]:
    """Update a product."""
    product = await get_product(session, product_id)
    if product:
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        await session.commit()
        await session.refresh(product)
    return product


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    """Delete a product."""
    product = await get_product(session, product_id)
    if product:
        await session.delete(product)
        await session.commit()
        return True
    return False


# Post CRUD operations
async def create_post(
    session: AsyncSession,
    product_id: int,
    content: str,
    platform: str = "twitter",
    scheduled_at: Optional = None,
    status: str = "draft",
) -> Post:
    """Create a new post."""
    post = Post(
        product_id=product_id,
        content=content,
        platform=platform,
        scheduled_at=scheduled_at,
        status=status,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


async def get_posts(
    session: AsyncSession,
    product_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[Post]:
    """Get posts with optional filters."""
    query = select(Post).order_by(Post.scheduled_at.desc())
    if product_id:
        query = query.where(Post.product_id == product_id)
    if status:
        query = query.where(Post.status == status)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_post(
    session: AsyncSession,
    post_id: int,
    **kwargs,
) -> Optional[Post]:
    """Update a post."""
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post:
        for key, value in kwargs.items():
            if hasattr(post, key):
                setattr(post, key, value)
        await session.commit()
        await session.refresh(post)
    return post


async def delete_post(session: AsyncSession, post_id: int) -> bool:
    """Delete a post."""
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post:
        await session.delete(post)
        await session.commit()
        return True
    return False


# FAQ CRUD operations
async def create_faq(
    session: AsyncSession,
    product_id: int,
    question: str,
    answer: str,
    keywords: str = "",
) -> FAQ:
    """Create a new FAQ."""
    faq = FAQ(
        product_id=product_id,
        question=question,
        answer=answer,
        keywords=keywords,
    )
    session.add(faq)
    await session.commit()
    await session.refresh(faq)
    return faq


async def get_faqs(session: AsyncSession, product_id: int) -> list[FAQ]:
    """Get FAQs for a product."""
    result = await session.execute(
        select(FAQ).where(FAQ.product_id == product_id).order_by(FAQ.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_faq(session: AsyncSession, faq_id: int) -> bool:
    """Delete an FAQ."""
    result = await session.execute(select(FAQ).where(FAQ.id == faq_id))
    faq = result.scalar_one_or_none()
    if faq:
        await session.delete(faq)
        await session.commit()
        return True
    return False


# Lead CRUD operations
async def create_lead(
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
    """Create a new lead."""
    lead = Lead(
        product_id=product_id,
        platform=platform,
        username=username,
        display_name=display_name,
        bio=bio,
        followers=followers,
        relevance_score=relevance_score,
        tags=tags,
    )
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


async def get_leads(
    session: AsyncSession,
    product_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[Lead]:
    """Get leads with optional filters."""
    query = select(Lead).order_by(Lead.relevance_score.desc())
    if product_id:
        query = query.where(Lead.product_id == product_id)
    if status:
        query = query.where(Lead.status == status)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_lead(
    session: AsyncSession,
    lead_id: int,
    **kwargs,
) -> Optional[Lead]:
    """Update a lead."""
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if lead:
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        await session.commit()
        await session.refresh(lead)
    return lead


# Activity log operations
async def log_activity(
    session: AsyncSession,
    action: str,
    product_id: Optional[int] = None,
    platform: Optional[str] = None,
    details: str = "",
) -> ActivityLog:
    """Log an activity."""
    log = ActivityLog(
        product_id=product_id,
        action=action,
        platform=platform,
        details=details,
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def get_recent_activities(
    session: AsyncSession,
    limit: int = 20,
) -> list[ActivityLog]:
    """Get recent activities."""
    result = await session.execute(
        select(ActivityLog)
        .order_by(ActivityLog.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# Analytics operations
async def get_analytics_summary(
    session: AsyncSession,
    product_id: Optional[int] = None,
    days: int = 30,
) -> dict:
    """Get analytics summary for the specified period."""
    from datetime import timedelta
    from sqlalchemy import func
    
    # Get posts stats
    posts_query = select(
        func.count(Post.id).label('total'),
        func.sum(func.cast(Post.status == 'published', Integer)).label('published'),
        func.sum(func.cast(Post.status == 'scheduled', Integer)).label('scheduled'),
        func.sum(func.cast(Post.status == 'failed', Integer)).label('failed'),
    )
    if product_id:
        posts_query = posts_query.where(Post.product_id == product_id)
    
    posts_result = await session.execute(posts_query)
    posts_stats = posts_result.one()
    
    # Get leads stats
    leads_query = select(
        func.count(Lead.id).label('total'),
        func.sum(func.cast(Lead.status == 'engaged', Integer)).label('engaged'),
        func.sum(func.cast(Lead.status == 'converted', Integer)).label('converted'),
    )
    if product_id:
        leads_query = leads_query.where(Lead.product_id == product_id)
    
    leads_result = await session.execute(leads_query)
    leads_stats = leads_result.one()
    
    # Get activities count
    activities_query = select(func.count(ActivityLog.id))
    if product_id:
        activities_query = activities_query.where(ActivityLog.product_id == product_id)
    
    activities_result = await session.execute(activities_query)
    activities_count = activities_result.scalar()
    
    return {
        "posts_total": posts_stats.total or 0,
        "posts_published": posts_stats.published or 0,
        "posts_scheduled": posts_stats.scheduled or 0,
        "posts_failed": posts_stats.failed or 0,
        "leads_total": leads_stats.total or 0,
        "leads_engaged": leads_stats.engaged or 0,
        "leads_converted": leads_stats.converted or 0,
        "activities_total": activities_count or 0,
    }


async def get_analytics_by_platform(
    session: AsyncSession,
    product_id: Optional[int] = None,
) -> dict:
    """Get analytics grouped by platform."""
    from sqlalchemy import func
    
    # Posts by platform
    posts_query = select(
        Post.platform,
        func.count(Post.id).label('count'),
    ).where(Post.status == 'published')
    
    if product_id:
        posts_query = posts_query.where(Post.product_id == product_id)
    
    posts_query = posts_query.group_by(Post.platform)
    posts_result = await session.execute(posts_query)
    
    posts_by_platform = {}
    for row in posts_result:
        posts_by_platform[row.platform] = row.count
    
    # Leads by platform
    leads_query = select(
        Lead.platform,
        func.count(Lead.id).label('count'),
    )
    
    if product_id:
        leads_query = leads_query.where(Lead.product_id == product_id)
    
    leads_query = leads_query.group_by(Lead.platform)
    leads_result = await session.execute(leads_query)
    
    leads_by_platform = {}
    for row in leads_result:
        leads_by_platform[row.platform] = row.count
    
    return {
        "posts_by_platform": posts_by_platform,
        "leads_by_platform": leads_by_platform,
    }


async def record_analytics(
    session: AsyncSession,
    product_id: int,
    platform: str,
    posts_scheduled: int = 0,
    posts_published: int = 0,
    leads_discovered: int = 0,
    responses_sent: int = 0,
) -> Analytics:
    """Record analytics for a specific period."""
    from datetime import datetime
    
    analytics = Analytics(
        product_id=product_id,
        platform=platform,
        date=datetime.utcnow(),
        posts_scheduled=posts_scheduled,
        posts_published=posts_published,
        leads_discovered=leads_discovered,
        responses_sent=responses_sent,
    )
    session.add(analytics)
    await session.commit()
    await session.refresh(analytics)
    return analytics


# Post Templates
async def create_template(
    session: AsyncSession,
    product_id: int,
    name: str,
    content: str,
    platform: str = "twitter",
    category: str = "general",
):
    from .models import PostTemplate
    template = PostTemplate(
        product_id=product_id,
        name=name,
        content=content,
        platform=platform,
        category=category,
    )
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template


async def get_templates(session: AsyncSession, product_id: int = None):
    from sqlalchemy import select
    from .models import PostTemplate
    query = select(PostTemplate).order_by(PostTemplate.created_at.desc())
    if product_id:
        query = query.where(PostTemplate.product_id == product_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def delete_template(session: AsyncSession, template_id: int):
    from sqlalchemy import select
    from .models import PostTemplate
    result = await session.execute(select(PostTemplate).where(PostTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if template:
        await session.delete(template)
        await session.commit()
        return True
    return False


# Campaigns
async def create_campaign(
    session: AsyncSession,
    product_id: int,
    name: str,
    description: str = "",
    start_date = None,
    end_date = None,
):
    from .models import Campaign
    campaign = Campaign(
        product_id=product_id,
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
    )
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)
    return campaign


async def get_campaigns(session: AsyncSession, product_id: int = None):
    from sqlalchemy import select
    from .models import Campaign
    query = select(Campaign).order_by(Campaign.created_at.desc())
    if product_id:
        query = query.where(Campaign.product_id == product_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_campaign(session: AsyncSession, campaign_id: int, **kwargs):
    from sqlalchemy import select
    from .models import Campaign
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if campaign:
        for key, value in kwargs.items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)
        await session.commit()
        await session.refresh(campaign)
    return campaign


async def delete_campaign(session: AsyncSession, campaign_id: int):
    from sqlalchemy import select
    from .models import Campaign
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if campaign:
        await session.delete(campaign)
        await session.commit()
        return True
    return False


# Engagement Queue
async def add_to_engagement_queue(
    session: AsyncSession,
    product_id: int,
    platform: str,
    mention_type: str,
    source_user: str,
    source_content: str,
):
    from .models import EngagementQueue
    item = EngagementQueue(
        product_id=product_id,
        platform=platform,
        mention_type=mention_type,
        source_user=source_user,
        source_content=source_content,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_engagement_queue(session: AsyncSession, product_id: int = None, status: str = None):
    from sqlalchemy import select
    from .models import EngagementQueue
    query = select(EngagementQueue).order_by(EngagementQueue.created_at.desc())
    if product_id:
        query = query.where(EngagementQueue.product_id == product_id)
    if status:
        query = query.where(EngagementQueue.status == status)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_engagement_item(
    session: AsyncSession,
    item_id: int,
    generated_response: str = None,
    response_source: str = None,
    status: str = None,
):
    from sqlalchemy import select
    from .models import EngagementQueue
    from datetime import datetime
    result = await session.execute(select(EngagementQueue).where(EngagementQueue.id == item_id))
    item = result.scalar_one_or_none()
    if item:
        if generated_response:
            item.generated_response = generated_response
        if response_source:
            item.response_source = response_source
        if status:
            item.status = status
            if status == "sent":
                item.sent_at = datetime.utcnow()
        await session.commit()
        await session.refresh(item)
    return item
