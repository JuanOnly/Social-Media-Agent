"""Post scheduler service for automated publishing."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from ..models.database import get_db, get_posts, update_post, log_activity
from ..platforms import get_platform_registry

logger = logging.getLogger(__name__)


class PostScheduler:
    """Scheduler for automated post publishing."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Post scheduler started")

            # Add recurring job to check for due posts
            self.scheduler.add_job(
                self.check_due_posts,
                'interval',
                seconds=60,
                id='check_posts',
                replace_existing=True,
            )

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Post scheduler stopped")

    async def schedule_post(self, post_id: int, scheduled_at: datetime):
        """Schedule a post for future publishing."""
        job_id = f"publish_post_{post_id}"

        if job_id in [j.id for j in self.scheduler.get_jobs()]:
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            self.publish_post,
            trigger=DateTrigger(run_date=scheduled_at),
            id=job_id,
            args=[post_id],
            replace_existing=True,
        )

        logger.info(f"Scheduled post {post_id} for {scheduled_at}")

    def cancel_scheduled_post(self, post_id: int):
        """Cancel a scheduled post."""
        job_id = f"publish_post_{post_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled scheduled post {post_id}")
        except:
            pass

    async def check_due_posts(self):
        """Check for posts that are due to be published."""
        db = get_db()
        async with db.async_session_maker() as session:
            posts = await get_posts(session, status="scheduled")
            now = datetime.utcnow()

            for post in posts:
                if post.scheduled_at and post.scheduled_at <= now:
                    await self._publish_post(session, post)

    async def publish_post(self, post_id: int):
        """Publish a single post."""
        db = get_db()
        async with db.async_session_maker() as session:
            posts = await get_posts(session)
            post = next((p for p in posts if p.id == post_id), None)

            if not post:
                logger.error(f"Post {post_id} not found")
                return

            await self._publish_post(session, post)

    async def _publish_post(self, session, post):
        """Internal method to publish a post."""
        try:
            logger.info(f"Publishing post {post.id} to {post.platform}")

            registry = get_platform_registry()
            adapter = registry.get_adapter(post.platform, "", "")

            try:
                await adapter.post(post.content)
                await update_post(session, post.id, status="published")
                await log_activity(session, f"Published post {post.id}", platform=post.platform)
                logger.info(f"Successfully published post {post.id}")
            except Exception as e:
                logger.warning(f"Could not publish to {post.platform}: {e}")
                await update_post(session, post.id, status="failed")
                await log_activity(session, f"Failed to publish post {post.id}: {str(e)}", platform=post.platform)

        except Exception as e:
            logger.error(f"Error publishing post {post.id}: {e}")
            await update_post(session, post.id, status="failed")

    def get_scheduled_jobs(self):
        """Get list of scheduled jobs."""
        return self.scheduler.get_jobs()


_post_scheduler: Optional[PostScheduler] = None


def get_post_scheduler() -> PostScheduler:
    """Get post scheduler instance."""
    global _post_scheduler
    if _post_scheduler is None:
        _post_scheduler = PostScheduler()
    return _post_scheduler


def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_post_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler."""
    scheduler = get_post_scheduler()
    scheduler.stop()
