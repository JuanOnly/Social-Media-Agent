"""MediaAgent UI - Redesigned Dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nicegui import app, ui

from media_agent.config import get_settings, load_product_config, get_faqs_from_config
from media_agent.models.database import (
    get_db,
    create_product,
    get_products,
    get_product,
    delete_product,
    create_post,
    get_posts,
    delete_post,
    create_faq,
    get_faqs,
    delete_faq,
    get_leads,
    update_lead,
    log_activity,
    get_recent_activities,
    get_analytics_summary,
    get_analytics_by_platform,
)
from media_agent.agents.ai_engine import get_ai_engine
from media_agent.discovery.discovery import get_lead_discovery
from media_agent.scheduler.scheduler import start_scheduler, get_post_scheduler
from media_agent.models.database import create_lead


async def init_app():
    """Initialize the application."""
    db = get_db()
    await db.init_db()
    start_scheduler()


def navigate(page: str, product_id: int = None):
    """Navigate to a page."""
    if product_id:
        ui.navigate.to(f"/{page}/{product_id}")
    else:
        ui.navigate.to(f"/{page}")


# ============== CALENDAR PAGE ==============
@ui.page("/calendar")
async def calendar_page():
    ui.page_title("Content Calendar")
    await render_calendar()


async def render_calendar():
    """Render content calendar."""
    from datetime import datetime, timedelta
    
    # Header
    with ui.row().classes("w-full items-center justify-between mb-6"):
        with ui.row().classes("items-center gap-4"):
            ui.button(icon="arrow_back", on_click=lambda: navigate("home")).props("flat round")
            ui.label("Content Calendar").classes("text-3xl font-bold")

    # Get current month
    now = datetime.now()
    current_month = now.replace(day=1)

    # Calendar grid
    # Get days in month
    if current_month.month == 12:
        next_month = current_month.replace(year=current_month.year + 1, month=1)
    else:
        next_month = current_month.replace(month=current_month.month + 1)
    
    days_in_month = (next_month - timedelta(days=1)).day
    first_day_weekday = current_month.weekday()  # 0 = Monday
    
    # Get all scheduled posts
    db = get_db()
    async with db.async_session_maker() as session:
        posts = await get_posts(session, status="scheduled")
        
    # Create calendar
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Weekday headers
    with ui.grid(columns=7).classes("w-full gap-1 mb-2"):
        for day in weekdays:
            ui.label(day).classes("text-center font-bold text-sm text-gray-500")
    
    # Calendar days
    day_num = 1
    for week in range(6):
        with ui.grid(columns=7).classes("w-full gap-1"):
            for weekday in range(7):
                cell_index = week * 7 + weekday
                
                if cell_index < first_day_weekday or day_num > days_in_month:
                    # Empty cell
                    ui.label("").classes("h-20 p-1")
                else:
                    # Day cell
                    day_date = current_month.replace(day=day_num)
                    day_posts = [p for p in posts if p.scheduled_at and p.scheduled_at.date() == day_date.date()]
                    
                    is_today = day_date.date() == now.date()
                    
                    with ui.card().classes(f"h-20 p-1 {'bg-blue-50' if is_today else ''}"):
                        ui.label(f"{day_num}").classes(f"text-xs font-bold {'text-blue-600' if is_today else 'text-gray-500'}")
                        
                        # Show up to 2 posts
                        for post in day_posts[:2]:
                            platform_emoji = {"twitter": "🐦", "instagram": "📷", "linkedin": "💼", "facebook": "📘"}.get(post.platform, "📝")
                            ui.label(f"{platform_emoji} {post.content[:20]}...").classes("text-xs truncate")
                        
                        if len(day_posts) > 2:
                            ui.label(f"+{len(day_posts) - 2} more").classes("text-xs text-gray-400")
                    
                    day_num += 1
        
        if day_num > days_in_month:
            break
    
    # Posts list below calendar
    with ui.card().classes("w-full p-4 mt-4"):
        ui.label("Upcoming Scheduled Posts").classes("text-lg font-bold mb-4")
        
        # Get scheduled posts
        db = get_db()
        async with db.async_session_maker() as session:
            posts = await get_posts(session, status="scheduled")
            upcoming = [p for p in posts if p.scheduled_at]
            upcoming.sort(key=lambda x: x.scheduled_at)
        
        if upcoming:
            for post in upcoming[:15]:
                with ui.card().classes("p-2 mb-2 w-full"):
                    with ui.row().classes("w-full justify-between"):
                        ui.label(f"{post.scheduled_at.strftime('%Y-%m-%d %H:%M')}").classes("text-sm font-bold")
                        ui.badge(post.platform).classes("text-xs")
                    ui.label(post.content[:80] + "...").classes("text-sm")
        else:
            ui.label("No scheduled posts").classes("text-gray-500")


# ============== TEMPLATES PAGE ==============
@ui.page("/templates")
async def templates_page():
    ui.page_title("Post Templates")
    await render_templates()


async def render_templates():
    from media_agent.models.database import get_templates, create_template, delete_template
    
    with ui.row().classes("w-full items-center mb-6"):
        ui.button(icon="arrow_back", on_click=lambda: navigate("home")).props("flat round")
        ui.label("Post Templates").classes("text-3xl font-bold")
    
    ui.button("New Template", icon="add", on_click=show_template_dialog).props("color=primary")
    
    db = get_db()
    async with db.async_session_maker() as session:
        templates = await get_templates(session)
    
    if templates:
        with ui.grid(columns=2).classes("w-full gap-4 mt-4"):
            for t in templates:
                with ui.card().classes("p-4"):
                    with ui.row().classes("w-full justify-between"):
                        ui.label(t.name).classes("font-bold")
                        ui.button(icon="delete", on_click=lambda tid=t.id: del_template(tid)).props("flat size=sm")
                    ui.label(t.content[:100] + "...").classes("text-sm text-gray-500")
                    with ui.row().classes("gap-2 mt-2"):
                        ui.badge(t.platform).classes("text-xs")
                        ui.badge(t.category).classes("text-xs")
    else:
        ui.label("No templates. Create reusable post templates!").classes("text-gray-500 mt-4")


async def show_template_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("New Template").classes("text-xl font-bold mb-4")
        name = ui.input("Template Name").classes("w-full mb-2")
        content = ui.textarea("Content").classes("w-full mb-2")
        platform = ui.input("Platform", value="twitter").classes("w-full mb-2")
        category = ui.input("Category", value="general").classes("w-full mb-2")
        
        async def save():
            if name.value and content.value:
                db = get_db()
                async with db.async_session_maker() as session:
                    await create_template(session, 1, name.value, content.value, platform.value, category.value)
                dialog.close()
                ui.notify("Template created!")
                ui.navigate.to("/templates")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=save).props("color=primary")
    dialog.open()


async def del_template(tid):
    db = get_db()
    async with db.async_session_maker() as session:
        from media_agent.models.database import delete_template
        await delete_template(session, tid)
    ui.notify("Deleted")
    ui.navigate.to("/templates")


# ============== CAMPAIGNS PAGE ==============
@ui.page("/campaigns")
async def campaigns_page():
    ui.page_title("Campaigns")
    await render_campaigns()


async def render_campaigns():
    from media_agent.models.database import get_campaigns, create_campaign, delete_campaign
    
    with ui.row().classes("w-full items-center mb-6"):
        ui.button(icon="arrow_back", on_click=lambda: navigate("home")).props("flat round")
        ui.label("Campaigns").classes("text-3xl font-bold")
    
    ui.button("New Campaign", icon="add", on_click=show_campaign_dialog).props("color=primary")
    
    db = get_db()
    async with db.async_session_maker() as session:
        campaigns = await get_campaigns(session)
    
    if campaigns:
        for c in campaigns:
            with ui.card().classes("p-4 mb-4 w-full"):
                with ui.row().classes("w-full justify-between"):
                    ui.label(c.name).classes("font-bold text-lg")
                    with ui.row().classes("gap-2"):
                        ui.badge(c.status, color="green" if c.status == "active" else "orange").classes("text-xs")
                        ui.button(icon="delete", on_click=lambda cid=c.id: del_campaign(cid)).props("flat size=sm")
                if c.description:
                    ui.label(c.description).classes("text-sm text-gray-500")
    else:
        ui.label("No campaigns. Organize your posts into campaigns!").classes("text-gray-500 mt-4")


async def show_campaign_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("New Campaign").classes("text-xl font-bold mb-4")
        name = ui.input("Campaign Name").classes("w-full mb-2")
        desc = ui.textarea("Description").classes("w-full mb-2")
        
        async def save():
            if name.value:
                db = get_db()
                async with db.async_session_maker() as session:
                    await create_campaign(session, 1, name.value, desc.value or "")
                dialog.close()
                ui.notify("Campaign created!")
                ui.navigate.to("/campaigns")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=save).props("color=primary")
    dialog.open()


async def del_campaign(cid):
    db = get_db()
    async with db.async_session_maker() as session:
        from media_agent.models.database import delete_campaign
        await delete_campaign(session, cid)
    ui.notify("Deleted")
    ui.navigate.to("/campaigns")


# ============== ENGAGEMENT QUEUE PAGE ==============
@ui.page("/engagement")
async def engagement_page():
    ui.page_title("Engagement Queue")
    await render_engagement()


async def render_engagement():
    from media_agent.models.database import get_engagement_queue, update_engagement_item
    
    with ui.row().classes("w-full items-center mb-6"):
        ui.button(icon="arrow_back", on_click=lambda: navigate("home")).props("flat round")
        ui.label("Engagement Queue").classes("text-3xl font-bold")
    
    ui.label("Pending responses to mentions and comments").classes("text-gray-500 mb-4")
    
    db = get_db()
    async with db.async_session_maker() as session:
        items = await get_engagement_queue(session, status="pending")
    
    if items:
        for item in items:
            with ui.card().classes("p-4 mb-4 w-full"):
                with ui.row().classes("w-full justify-between"):
                    ui.label(f"@{item.source_user}").classes("font-bold")
                    ui.badge(item.platform).classes("text-xs")
                ui.label(f"Type: {item.mention_type}").classes("text-xs text-gray-400")
                ui.label(item.source_content[:150]).classes("text-sm mt-2")
                
                if item.generated_response:
                    ui.label("Response:").classes("text-sm font-bold mt-2")
                    ui.label(item.generated_response).classes("text-sm bg-gray-50 p-2")
                else:
                    ui.button("Generate Response", icon="auto_awesome", on_click=lambda i=item: gen_response(i)).props("size=sm color=purple mt-2")
                
                with ui.row().classes("gap-2 mt-2"):
                    ui.button("Send", on_click=lambda i=item: send_response(i)).props("size=sm color=green")
                    ui.button("Ignore", on_click=lambda i=item: ignore_item(i)).props("size=sm flat")
    else:
        ui.label("No pending engagements. They'll appear here when mentions are detected.").classes("text-gray-500")


async def gen_response(item):
    from media_agent.agents.ai_engine import get_ai_engine
    ai = get_ai_engine()
    
    db = get_db()
    async with db.async_session_maker() as session:
        from media_agent.models.database import get_product
        product = await get_product(session, item.product_id)
        
        if product:
            response = await ai.generate_response(
                product.name, product.description or "",
                product.brand_voice, item.source_content
            )
            await update_engagement_item(session, item.id, generated_response=response, response_source="ai")
            ui.notify("Response generated!")
            ui.navigate.to("/engagement")


async def send_response(item):
    db = get_db()
    async with db.async_session_maker() as session:
        await update_engagement_item(session, item.id, status="sent")
    ui.notify("Response sent!")
    ui.navigate.to("/engagement")


async def ignore_item(item):
    db = get_db()
    async with db.async_session_maker() as session:
        await update_engagement_item(session, item.id, status="ignored")
    ui.notify("Ignored")
    ui.navigate.to("/engagement")


# ============== HOME PAGE ==============
@ui.page("/")
async def home():
    ui.page_title("MediaAgent")
    await render_home()


async def render_home():
    """Main dashboard showing all products."""
    
    # Header
    with ui.row().classes("w-full items-center justify-between mb-6"):
        ui.label("My Products").classes("text-3xl font-bold")
        with ui.row().classes("gap-2"):
            ui.button("Add Product", icon="add", on_click=show_add_product_dialog).props("color=primary")
            ui.button("Settings", icon="settings", on_click=lambda: navigate("settings")).props("flat")

    db = get_db()
    async with db.async_session_maker() as session:
        products = await get_products(session)

    if not products:
        # Empty state
        with ui.card().classes("w-full p-12 text-center"):
            ui.icon("rocket_launch", size="64px").classes("text-gray-300 mb-4")
            ui.label("Welcome to MediaAgent!").classes("text-2xl font-bold mb-2")
            ui.label("Add your first product to get started").classes("text-gray-500 mb-4")
            ui.button("Add Product", icon="add", on_click=show_add_product_dialog).props("color=primary")
        return

    # Quick stats
    async with db.async_session_maker() as session:
        total_posts = await get_posts(session)
        total_leads = await get_leads(session)
        scheduled = len([p for p in total_posts if p.status == "scheduled"])

    with ui.card().classes("w-full p-4 mb-6"):
        with ui.row().classes("w-full justify-around"):
            with ui.column().classes("text-center"):
                ui.label(f"{len(products)}").classes("text-3xl font-bold text-indigo-600")
                ui.label("Products").classes("text-sm text-gray-500")
            with ui.column().classes("text-center"):
                ui.label(f"{len(total_posts)}").classes("text-3xl font-bold text-green-600")
                ui.label("Total Posts").classes("text-sm text-gray-500")
            with ui.column().classes("text-center"):
                ui.label(f"{scheduled}").classes("text-3xl font-bold text-orange-600")
                ui.label("Scheduled").classes("text-sm text-gray-500")
            with ui.column().classes("text-center"):
                ui.label(f"{len(total_leads)}").classes("text-3xl font-bold text-purple-600")
                ui.label("Leads").classes("text-sm text-gray-500")

    # Product cards
    ui.label("Products").classes("text-xl font-bold mb-4")
    
    with ui.grid(columns=2).classes("w-full gap-4"):
        for product in products:
            await render_product_card(product)


async def render_product_card(product):
    """Render a product card with stats."""
    db = get_db()
    async with db.async_session_maker() as session:
        posts = await get_posts(session, product_id=product.id)
        leads = await get_leads(session, product_id=product.id)
        faqs = await get_faqs(session, product.id)
        
        published = len([p for p in posts if p.status == "published"])
        scheduled = len([p for p in posts if p.status == "scheduled"])

    with ui.card().classes("p-4 cursor-pointer hover:shadow-lg transition-shadow").on_click(lambda p=product: navigate("product", p.id)):
        with ui.column().classes("w-full"):
            # Product name & actions
            with ui.row().classes("w-full justify-between items-center mb-3"):
                ui.label(product.name).classes("text-lg font-bold")
                ui.button(icon="delete", on_click=lambda p=product: confirm_delete_product(p)).props("flat size=sm color=negative")
            
            # Description
            if product.description:
                ui.label(product.description[:80] + "..." if len(product.description) > 80 else product.description).classes("text-sm text-gray-500 mb-3")
            
            # Stats row
            with ui.row().classes("w-full justify-between mt-2"):
                with ui.column().classes("text-center"):
                    ui.label(f"{published}").classes("text-xl font-bold text-green-600")
                    ui.label("Published").classes("text-xs text-gray-400")
                with ui.column().classes("text-center"):
                    ui.label(f"{scheduled}").classes("text-xl font-bold text-orange-600")
                    ui.label("Scheduled").classes("text-xs text-gray-400")
                with ui.column().classes("text-center"):
                    ui.label(f"{len(leads)}").classes("text-xl font-bold text-purple-600")
                    ui.label("Leads").classes("text-xs text-gray-400")
                with ui.column().classes("text-center"):
                    ui.label(f"{len(faqs)}").classes("text-xl font-bold text-blue-600")
                    ui.label("FAQs").classes("text-xs text-gray-400")


# ============== PRODUCT DETAIL PAGE ==============
@ui.page("/product/{product_id}")
async def product_detail(product_id: int):
    ui.page_title("Product Details")
    await render_product_detail(product_id)


async def render_product_detail(product_id: int):
    """Render product detail page with tabs."""
    db = get_db()
    async with db.async_session_maker() as session:
        product = await get_product(session, product_id)
        if not product:
            ui.label("Product not found").classes("text-2xl")
            return

    # Header
    with ui.row().classes("w-full items-center justify-between mb-6"):
        with ui.row().classes("items-center gap-4"):
            ui.button(icon="arrow_back", on_click=lambda: navigate("home")).props("flat round")
            ui.label(product.name).classes("text-3xl font-bold")
        with ui.row().classes("gap-2"):
            ui.button("Edit", icon="edit", on_click=lambda: edit_product_dialog(product)).props("flat")
            ui.button("New Post", icon="add", on_click=lambda: show_create_post_dialog(product_id)).props("color=primary")

    # Tab navigation for this product
    with ui.tabs().classes("w-full mb-4") as tabs:
        overview_tab = ui.tab("Overview")
        posts_tab = ui.tab("Posts")
        leads_tab = ui.tab("Leads")
        faqs_tab = ui.tab("FAQs")

    with ui.tab_panels(tabs, value=overview_tab).classes("w-full"):
        # Overview tab
        with ui.tab_panel(overview_tab):
            await render_product_overview(product)
        
        # Posts tab
        with ui.tab_panel(posts_tab):
            await render_product_posts(product_id)
        
        # Leads tab
        with ui.tab_panel(leads_tab):
            await render_product_leads(product_id)
        
        # FAQs tab
        with ui.tab_panel(faqs_tab):
            await render_product_faqs(product_id)


async def render_product_overview(product):
    """Render product overview with analytics."""
    db = get_db()
    async with db.async_session_maker() as session:
        posts = await get_posts(session, product_id=product.id)
        leads = await get_leads(session, product_id=product.id)
        faqs = await get_faqs(session, product.id)
        
        published = [p for p in posts if p.status == "published"]
        scheduled = [p for p in posts if p.status == "scheduled"]
        engaged_leads = [l for l in leads if l.status == "engaged"]

    # Stats cards
    with ui.grid(columns=4).classes("w-full gap-4 mb-6"):
        with ui.card().classes("p-4"):
            ui.label("Total Posts").classes("text-sm text-gray-500")
            ui.label(f"{len(posts)}").classes("text-2xl font-bold")
        
        with ui.card().classes("p-4"):
            ui.label("Published").classes("text-sm text-gray-500")
            ui.label(f"{len(published)}").classes("text-2xl font-bold text-green-600")
        
        with ui.card().classes("p-4"):
            ui.label("Scheduled").classes("text-sm text-gray-500")
            ui.label(f"{len(scheduled)}").classes("text-2xl font-bold text-orange-600")
        
        with ui.card().classes("p-4"):
            ui.label("Leads").classes("text-sm text-gray-500")
            ui.label(f"{len(leads)}").classes("text-2xl font-bold")

    # Quick actions
    with ui.card().classes("p-4 w-full mb-4"):
        ui.label("Quick Actions").classes("text-lg font-bold mb-4")
        with ui.row().classes("w-full gap-2"):
            ui.button("Create Post", icon="edit", on_click=lambda: show_create_post_dialog(product.id)).props("color=primary")
            ui.button("Discover Leads", icon="people", on_click=lambda: show_discover_dialog(product.id)).props("color=purple")
            ui.button("Add FAQ", icon="help", on_click=lambda: show_add_faq_dialog(product.id)).props("color=blue")

    # Brand info
    with ui.card().classes("p-4 w-full"):
        ui.label("Product Info").classes("text-lg font-bold mb-2")
        ui.label(f"Brand Voice: {product.brand_voice}").classes("text-sm")
        ui.label(f"Target: {product.target_audience or 'Not set'}").classes("text-sm text-gray-500")


async def render_product_posts(product_id):
    """Render posts for a product."""
    db = get_db()
    async with db.async_session_maker() as session:
        posts = await get_posts(session, product_id=product_id)

    with ui.row().classes("w-full justify-between mb-4"):
        ui.label(f"Posts ({len(posts)})").classes("text-xl font-bold")
        ui.button("New Post", icon="add", on_click=lambda: show_create_post_dialog(product_id)).props("color=primary")

    if not posts:
        ui.label("No posts yet. Create your first post!").classes("text-gray-500")
        return

    for post in posts:
        status_color = "green" if post.status == "published" else "orange" if post.status == "scheduled" else "gray"
        with ui.card().classes("p-3 mb-2 w-full"):
            with ui.row().classes("w-full justify-between"):
                ui.label(post.content[:100] + "...").classes("text-sm flex-1")
                ui.badge(post.status, color=status_color).classes("text-xs")
            with ui.row().classes("gap-2 mt-2"):
                ui.badge(post.platform).classes("text-xs")
                if post.scheduled_at:
                    ui.label(f"Scheduled: {post.scheduled_at.strftime('%Y-%m-%d %H:%M')}").classes("text-xs text-gray-400")


async def render_product_leads(product_id):
    """Render leads for a product."""
    db = get_db()
    async with db.async_session_maker() as session:
        leads = await get_leads(session, product_id=product_id)

    with ui.row().classes("w-full justify-between mb-4"):
        ui.label(f"Leads ({len(leads)})").classes("text-xl font-bold")
        ui.button("Discover More", icon="search", on_click=lambda: show_discover_dialog(product_id)).props("color=primary")

    if not leads:
        ui.label("No leads yet. Discover leads to find potential customers!").classes("text-gray-500")
        return

    for lead in leads:
        with ui.card().classes("p-3 mb-2 w-full"):
            with ui.row().classes("w-full justify-between"):
                ui.label(f"@{lead.username}").classes("font-bold")
                ui.badge(lead.platform).classes("text-xs")
            if lead.bio:
                ui.label(lead.bio[:80]).classes("text-xs text-gray-500 mt-1")


async def render_product_faqs(product_id):
    """Render FAQs for a product."""
    db = get_db()
    async with db.async_session_maker() as session:
        faqs = await get_faqs(session, product_id)

    with ui.row().classes("w-full justify-between mb-4"):
        ui.label(f"FAQs ({len(faqs)})").classes("text-xl font-bold")
        ui.button("Add FAQ", icon="add", on_click=lambda: show_add_faq_dialog(product_id)).props("color=primary")

    if not faqs:
        ui.label("No FAQs yet. Add FAQs for auto-responses!").classes("text-gray-500")
        return

    for faq in faqs:
        with ui.card().classes("p-3 mb-2 w-full"):
            ui.label(f"Q: {faq.question}").classes("font-bold text-sm")
            ui.label(f"A: {faq.answer}").classes("text-sm text-gray-600 mt-1")


# ============== SETTINGS PAGE ==============
@ui.page("/settings")
async def settings_page():
    ui.page_title("Settings - MediaAgent")
    await render_settings()


async def render_settings():
    """Render settings page with social account connections."""
    
    with ui.row().classes("w-full items-center mb-6"):
        ui.button(icon="arrow_back", on_click=lambda: navigate("home")).props("flat round")
        ui.label("Settings").classes("text-3xl font-bold")

    # Connected Accounts Section
    with ui.card().classes("p-6 w-full mb-6"):
        ui.label("Connected Social Accounts").classes("text-xl font-bold mb-4")
        ui.label("Connect your social media accounts to enable posting and auto-response").classes("text-sm text-gray-500 mb-4")
        
        # Twitter
        with ui.card().classes("p-4 mb-4 bg-gray-50"):
            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("tag", size="24px").classes("text-blue-400")
                    ui.label("Twitter/X").classes("font-bold")
                ui.button("Connect", icon="link", on_click=connect_twitter).props("color=blue")
        
        # Instagram
        with ui.card().classes("p-4 mb-4 bg-gray-50"):
            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("photo_camera", size="24px").classes("text-pink-500")
                    ui.label("Instagram").classes("font-bold")
                ui.button("Connect", icon="link", on_click=connect_instagram).props("color=purple")
        
        # LinkedIn
        with ui.card().classes("p-4 mb-4 bg-gray-50"):
            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("work", size="24px").classes("text-blue-700")
                    ui.label("LinkedIn").classes("font-bold")
                ui.button("Connect", icon="link", on_click=connect_linkedin).props("color=blue")

    # API Configuration
    with ui.card().classes("p-6 w-full mb-6"):
        ui.label("AI Configuration").classes("text-xl font-bold mb-4")
        settings = get_settings()
        
        api_key_input = ui.input(
            "OpenRouter API Key",
            value=settings.openrouter_api_key or "",
            placeholder="sk-..."
        ).classes("w-full mb-4")
        
        ui.label("AI Model: " + settings.openrouter_model).classes("text-sm mb-4")
        
        ui.button("Save Settings", on_click=lambda: ui.notify("Settings saved! Add to .env for persistence")).props("color=primary")

    # Scheduler
    with ui.card().classes("p-6 w-full"):
        ui.label("Automation").classes("text-xl font-bold mb-4")
        
        scheduler = get_post_scheduler()
        status = "Running" if scheduler.is_running else "Stopped"
        status_color = "green" if scheduler.is_running else "red"
        
        with ui.row().classes("w-full justify-between items-center"):
            ui.label(f"Post Scheduler:").classes("font-bold")
            with ui.row().classes("gap-2"):
                ui.badge(status, color=status_color)
                ui.button("Toggle", on_click=lambda: toggle_scheduler()).props("flat color=orange")


async def toggle_scheduler():
    scheduler = get_post_scheduler()
    if scheduler.is_running:
        scheduler.stop()
        ui.notify("Scheduler stopped")
    else:
        scheduler.start()
        ui.notify("Scheduler started")
    ui.navigate.to("/settings")


async def connect_twitter():
    """Show Twitter connection dialog."""
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Connect Twitter/X").classes("text-xl font-bold mb-4")
        
        ui.label("Enter your Twitter credentials to enable:").classes("text-sm mb-2")
        ui.label("• Automated posting").classes("text-xs text-gray-500")
        ui.label("• Auto-responding to mentions").classes("text-xs text-gray-500")
        ui.label("• Lead discovery").classes("text-xs text-gray-500 mb-4")
        
        username = ui.input("Username or Email").classes("w-full mb-4")
        password = ui.input("Password", password=True, password_toggle_button=True).classes("w-full mb-4")
        
        async def test_connection():
            if not username.value or not password.value:
                ui.notify("Please enter credentials", type="warning")
                return
            
            ui.notify("Opening browser... (Credentials will be saved after login)", type="info")
            
            from media_agent.platforms import get_platform_registry
            registry = get_platform_registry()
            adapter = registry.get_adapter("twitter", username.value, password.value)
            
            try:
                success = await adapter.login()
                if success:
                    ui.notify("Twitter connected successfully!", type="positive")
                    dialog.close()
                else:
                    ui.notify("Login failed. Check credentials.", type="negative")
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type="negative")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Connect", on_click=test_connection).props("color=blue")
    
    dialog.open()


async def connect_instagram():
    """Show Instagram connection dialog."""
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Connect Instagram").classes("text-xl font-bold mb-4")
        
        ui.label("Enter your Instagram credentials to enable:").classes("text-sm mb-2")
        ui.label("• Automated posting").classes("text-xs text-gray-500")
        ui.label("• Auto-responding to comments").classes("text-xs text-gray-500")
        
        username = ui.input("Username").classes("w-full mb-4")
        password = ui.input("Password", password=True, password_toggle_button=True).classes("w-full mb-4")
        
        async def test_connection():
            if not username.value or not password.value:
                ui.notify("Please enter credentials", type="warning")
                return
            
            ui.notify("Opening browser...", type="info")
            
            from media_agent.platforms import get_platform_registry
            registry = get_platform_registry()
            adapter = registry.get_adapter("instagram", username.value, password.value)
            
            try:
                success = await adapter.login()
                if success:
                    ui.notify("Instagram connected!", type="positive")
                    dialog.close()
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type="negative")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Connect", on_click=test_connection).props("color=purple")
    
    dialog.open()


async def connect_linkedin():
    ui.notify("LinkedIn integration coming soon!", type="info")


# ============== DIALOGS ==============

async def show_add_product_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Add New Product").classes("text-xl font-bold mb-4")
        
        name = ui.input("Product Name").classes("w-full mb-4")
        desc = ui.textarea("Description").classes("w-full mb-4")
        voice = "friendly"
        audience = ui.input("Target Audience (keywords)").classes("w-full mb-4")

        async def save():
            if not name.value:
                ui.notify("Name required", type="negative")
                return
            
            db = get_db()
            async with db.async_session_maker() as session:
                product = await create_product(session, name=name.value, description=desc.value or "", brand_voice=voice, target_audience=audience.value or "")
                
                # Check for config file FAQs
                config = load_product_config(name.value.lower())
                if config:
                    for faq in config.get("faq", []):
                        await create_faq(session, product.id, faq.get("question", ""), faq.get("answer", ""), faq.get("keywords", ""))
            
            dialog.close()
            ui.notify(f"Product '{name.value}' created!")
            ui.navigate.to("/")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=save).props("color=primary")
    
    dialog.open()


async def confirm_delete_product(product):
    with ui.dialog() as dialog, ui.card():
        ui.label(f"Delete '{product.name}'?").classes("text-lg")
        ui.label("This will delete all posts, leads, and FAQs.").classes("text-sm text-gray-500")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Delete", on_click=lambda: do_delete_product(product.id, dialog)).props("color=negative")
    
    dialog.open()


async def do_delete_product(product_id, dialog):
    db = get_db()
    async with db.async_session_maker() as session:
        await delete_product(session, product_id)
    dialog.close()
    ui.notify("Product deleted")
    ui.navigate.to("/")


async def edit_product_dialog(product):
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Edit Product").classes("text-xl font-bold mb-4")
        
        name = ui.input("Product Name", value=product.name).classes("w-full mb-4")
        desc = ui.textarea("Description", value=product.description or "").classes("w-full mb-4")
        
        async def save():
            db = get_db()
            async with db.async_session_maker() as session:
                from media_agent.models.database import update_product
                await update_product(session, product.id, name=name.value, description=desc.value or "")
            dialog.close()
            ui.notify("Product updated!")
            ui.navigate.to(f"/product/{product.id}")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=save).props("color=primary")
    
    dialog.open()


async def show_create_post_dialog(product_id):
    db = get_db()
    async with db.async_session_maker() as session:
        product = await get_product(session, product_id)

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg"):
        ui.label("Create Post").classes("text-xl font-bold mb-4")
        
        content = ui.textarea("Post Content", rows=4).classes("w-full mb-4")
        platform = ui.select("Platform", options=["twitter", "instagram", "facebook", "linkedin"], value="twitter").classes("w-full mb-4")
        
        async def generate():
            ai = get_ai_engine()
            try:
                generated = await ai.generate_post(
                    product.name, product.description or "", 
                    product.brand_voice, product.target_audience or "",
                    "promotional", "medium"
                )
                content.set_value(generated)
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type="negative")

        async def save(schedule=False):
            if not content.value:
                ui.notify("Content required", type="warning")
                return
            
            from datetime import datetime
            scheduled_at = datetime.utcnow() if not schedule else None
            
            db = get_db()
            async with db.async_session_maker() as session:
                await create_post(session, product_id=product_id, content=content.value, platform=platform.value, scheduled_at=scheduled_at, status="draft" if not schedule else "scheduled")
            
            dialog.close()
            ui.notify("Post saved!")
            ui.navigate.to(f"/product/{product_id}")

        with ui.row().classes("w-full gap-2 mb-4"):
            ui.button("Generate with AI", icon="auto_awesome", on_click=generate).props("color=purple")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Save Draft", on_click=lambda: save(False)).props("flat")
            ui.button("Save & Schedule", on_click=lambda: save(True)).props("color=primary")
    
    dialog.open()


async def show_add_faq_dialog(product_id):
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Add FAQ").classes("text-xl font-bold mb-4")
        
        question = ui.input("Question").classes("w-full mb-4")
        answer = ui.textarea("Answer").classes("w-full mb-4")
        keywords = ui.input("Keywords (for matching)").classes("w-full mb-4")

        async def save():
            if not question.value or not answer.value:
                ui.notify("Question and answer required", type="warning")
                return
            
            db = get_db()
            async with db.async_session_maker() as session:
                await create_faq(session, product_id, question.value, answer.value, keywords.value or "")
            
            dialog.close()
            ui.notify("FAQ added!")
            ui.navigate.to(f"/product/{product_id}")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=save).props("color=primary")
    
    dialog.open()


async def show_discover_dialog(product_id):
    db = get_db()
    async with db.async_session_maker() as session:
        product = await get_product(session, product_id)

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg"):
        ui.label("Discover Leads").classes("text-xl font-bold mb-4")
        
        query = ui.input("Search Query", placeholder="e.g., link in bio, linktree alternative").classes("w-full mb-4")
        platform = ui.select("Platform", options=["twitter", "instagram"], value="twitter").classes("w-full mb-4")
        
        results = ui.column().classes("w-full gap-2 mt-4")

        async def search():
            ui.notify("Searching for leads...", type="info")
            
            discovery = get_lead_discovery()
            try:
                leads = await discovery.search_leads(
                    session=db.async_session_maker().__aenter__(),
                    product_id=product_id,
                    product_name=product.name,
                    product_description=product.description or "",
                    target_audience=product.target_audience or "",
                    query=query.value or "link in bio",
                    platform=platform.value,
                )
                
                results.clear()
                ui.label(f"Found {len(leads)} potential leads").classes("font-bold mb-2")
                
                for lead in leads[:10]:
                    with results:
                        with ui.card().classes("p-2 w-full"):
                            ui.label(f"@{lead.get('username', 'unknown')}").classes("font-bold text-sm")
                            ui.label(lead.get("text", "")[:80]).classes("text-xs text-gray-500")
                            
                            async def save_lead(l=lead):
                                db = get_db()
                                async with db.async_session_maker() as s:
                                    await create_lead(s, product_id, platform.value, l.get("username", ""), relevance_score=l.get("relevance_score", 0))
                                ui.notify(f"Saved @{l.get('username', '')}")
                            
                            ui.button("Save Lead", on_click=save_lead).props("size=sm color=primary")
                            
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type="negative")

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Search", on_click=search).props("color=primary")
    
    dialog.open()


def run():
    settings = get_settings()
    app.on_startup(init_app)
    ui.run(host=settings.app_host, port=settings.app_port, title="MediaAgent", reload=False, show=True)


if __name__ == "__main__":
    run()
