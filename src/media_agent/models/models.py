"""Database models for MediaAgent."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Product(Base):
    """Product model."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    brand_voice = Column(String(50), default="friendly")  # friendly, professional, casual, authoritative
    target_audience = Column(Text, nullable=True)  # comma-separated keywords
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = relationship("Post", back_populates="product", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="product", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="product", cascade="all, delete-orphan")


class Post(Base):
    """Post model."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    content = Column(Text, nullable=False)
    platform = Column(String(50), default="twitter")  # twitter, instagram, facebook, linkedin
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="draft")  # draft, scheduled, published, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="posts")


class FAQ(Base):
    """FAQ model."""
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # comma-separated
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="faqs")


class Lead(Base):
    """Lead model."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    username = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    followers = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    tags = Column(Text, nullable=True)  # comma-separated
    status = Column(String(20), default="new")  # new, engaged, converted, ignored
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="leads")


class PlatformCredential(Base):
    """Platform credential model."""
    __tablename__ = "platform_credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False)
    username = Column(String(255), nullable=False)
    password_encrypted = Column(Text, nullable=True)
    cookies_json = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_validated = Column(DateTime, nullable=True)


class ActivityLog(Base):
    """Activity log model."""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    action = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Analytics(Base):
    """Analytics tracking model."""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)  # Daily aggregation
    platform = Column(String(50), nullable=True)
    
    # Post metrics
    posts_scheduled = Column(Integer, default=0)
    posts_published = Column(Integer, default=0)
    posts_failed = Column(Integer, default=0)
    
    # Engagement metrics
    mentions_received = Column(Integer, default=0)
    comments_received = Column(Integer, default=0)
    responses_sent = Column(Integer, default=0)
    
    # Lead metrics
    leads_discovered = Column(Integer, default=0)
    leads_engaged = Column(Integer, default=0)
    leads_converted = Column(Integer, default=0)
    
    # Platform specific
    likes_received = Column(Integer, default=0)
    shares_received = Column(Integer, default=0)


class PostTemplate(Base):
    """Post template model."""
    __tablename__ = "post_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    platform = Column(String(50), default="twitter")
    category = Column(String(50), default="general")  # promotional, educational, engagement, announcement
    created_at = Column(DateTime, default=datetime.utcnow)


class Campaign(Base):
    """Campaign model for grouping posts."""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active, paused, completed
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EngagementQueue(Base):
    """Engagement queue for pending responses."""
    __tablename__ = "engagement_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    mention_type = Column(String(50), nullable=False)  # mention, comment, dm
    source_user = Column(String(255), nullable=False)
    source_content = Column(Text, nullable=False)
    generated_response = Column(Text, nullable=True)
    response_source = Column(String(50), default="pending")  # pending, faq, ai
    status = Column(String(20), default="pending")  # pending, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
