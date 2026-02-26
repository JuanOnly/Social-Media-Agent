"""MediaAgent UI - Redesigned Dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nicegui import app, ui

from media_agent.config import get_settings, load_product_config
from media_agent.config.rate_limits import (
    get_rate_limiter_settings,
    update_rate_limiter_settings,
)
from media_agent.models.database import (
    get_db,
    create_product,
    get_products,
    get_product,
    delete_product,
    create_post,
    get_posts,
    create_faq,
    get_faqs,
    get_leads,
    save_platform_credential,
    get_connected_platforms,
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


# ============== SIDEBAR ==============
SIDEBAR_WIDTH = "260px"

# Sidebar state (in-memory)
_sidebar_visible = True

def render_sidebar():
    """Render the sidebar navigation."""
    global _sidebar_visible
    
    scheduler = get_post_scheduler()
    is_running = scheduler.is_running
    
    # Sidebar container - fixed position
    with ui.element("div").classes("fixed top-0 left-0 h-full z-40").style(f"width: {SIDEBAR_WIDTH}; background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);"):
        # Toggle button (always visible on left edge)
        with ui.button(icon="menu", on_click=toggle_sidebar).props("flat round").classes("absolute top-4 -right-3 bg-indigo-600 text-white hover:bg-indigo-700 z-50").style("border-radius: 50%;"):
            pass
        
        # Logo/Brand
        with ui.row().classes("items-center gap-3 p-4 mt-8").style("border-bottom: 1px solid #334155;"):
            ui.icon("smart_toy", size="32px").classes("text-indigo-400")
            ui.label("MediaAgent").classes("text-xl font-bold text-white")
        
        # Navigation items
        with ui.column().classes("p-2 gap-1 flex-1"):
            nav_items = [
                ("/", "Dashboard", "dashboard"),
                ("/calendar", "Calendar", "calendar_month"),
                ("/campaigns", "Campaigns", "campaign"),
                ("/templates", "Templates", "text_snippet"),
                ("/engagement", "Engagement", "forum"),
                ("/settings", "Settings", "settings"),
            ]
            
            for route, label, icon in nav_items:
                ui.button(label, icon=icon, on_click=lambda r=route: ui.navigate.to(r)).props("flat").classes("w-full justify-start gap-3 px-4 py-3 text-gray-300 hover:bg-slate-700 rounded-lg")
        
        # Bottom section - Status
        with ui.column().classes("p-4").style("border-top: 1px solid #334155;"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("circle", size="12px").classes(f"{'text-green-400' if is_running else 'text-red-400'}")
                ui.label(f"Automation: {'Running' if is_running else 'Stopped'}").classes("text-sm text-gray-300")
            
            async def toggle_automation():
                scheduler = get_post_scheduler()
                if scheduler.is_running:
                    scheduler.stop()
                    ui.notify("Automation stopped")
                else:
                    scheduler.start()
                    ui.notify("Automation started")
            
            ui.button("Toggle", on_click=toggle_automation).props("flat").classes("mt-2 w-full text-gray-400 hover:text-white")

    # Main content with left margin
    with ui.element("div").classes("ml-[260px]").style("min-height: 100vh;"):
        yield


def toggle_sidebar():
    """Toggle sidebar visibility."""
    global _sidebar_visible
    _sidebar_visible = not _sidebar_visible


def toggle_scheduler_sidebar():
    """Toggle scheduler from sidebar."""
    scheduler = get_post_scheduler()
    if scheduler.is_running:
        scheduler.stop()
        ui.notify("Automation stopped")
    else:
        scheduler.start()
        ui.notify("Automation started")


# ============== CHAT WIDGET ==============
_chat_open = False
_chat_messages = []

def render_chat_widget():
    """Render the floating chat widget."""
    global _chat_open, _chat_messages
    
    # Chat panel - always rendered but visibility toggled via JavaScript
    display_style = "display: none;" if not _chat_open else ""
    
    with ui.card().classes("fixed bottom-20 right-6 w-96 h-[450px] flex flex-col z-50").style(
        f"box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-height: 80vh; {display_style}"
    ):
        # Header
        with ui.row().classes("w-full justify-between items-center p-3 bg-indigo-600 rounded-t-lg"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("smart_toy", size="24px").classes("text-white")
                ui.label("Agent").classes("font-bold text-white")
            ui.button(icon="close", on_click=toggle_chat_js).props("flat round text-white")
        
        # Messages area
        with ui.element("div").classes("flex-1 overflow-auto p-3 bg-gray-50"):
            if not _chat_messages:
                ui.label("Hi! I'm Agent, your MediaAgent assistant.").classes("text-sm text-gray-600 mb-2")
                ui.label("I can help you with:").classes("text-sm font-bold mb-1")
                ui.label("• Creating and scheduling posts").classes("text-xs text-gray-500")
                ui.label("• Connecting social accounts").classes("text-xs text-gray-500")
                ui.label("• Getting post ideas").classes("text-xs text-gray-500")
                ui.label("• Navigating the app").classes("text-xs text-gray-500")
                ui.label("• Checking automation status").classes("text-xs text-gray-500 mb-2")
                ui.label("What would you like to do?").classes("text-sm text-gray-600")
            else:
                for msg in _chat_messages:
                    if msg["role"] == "user":
                        with ui.card().classes("p-2 mb-2 ml-8 bg-indigo-100"):
                            ui.label(msg["content"]).classes("text-sm")
                    else:
                        with ui.card().classes("p-2 mb-2 mr-8 bg-white"):
                            ui.label(msg["content"]).classes("text-sm")
        
        # Input area
        with ui.row().classes("p-2 border-t"):
            chat_input = ui.input(placeholder="Type your message...").props("dense").classes("flex-1")
            chat_input.on("keydown", lambda e: send_message(chat_input) if e.key == "Enter" else None)
            ui.button(icon="send", on_click=lambda: send_message(chat_input)).props("flat round color=indigo")

    # Toggle button (floating, always visible in bottom right)
    with ui.button(icon="chat", on_click=toggle_chat_js).props("round").classes("fixed bottom-6 right-6 z-50 w-14 h-14 bg-indigo-600 text-white hover:bg-indigo-700").style("box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4);"):
        pass


def toggle_chat_js():
    """Toggle chat panel visibility using JavaScript."""
    global _chat_open
    _chat_open = not _chat_open
    # Simple page reload to show/hide chat
    ui.run_javascript('window.location.reload()')


def send_message(chat_input):
    """Handle sending a chat message."""
    global _chat_messages
    
    if not chat_input.value:
        return
    
    user_msg = chat_input.value.strip()
    _chat_messages.append({"role": "user", "content": user_msg})
    chat_input.value = ""
    
    # Process message and get response + action
    response, action = process_chat_message(user_msg)
    _chat_messages.append({"role": "agent", "content": response})
    
    # Execute action if any
    if action and action != "none":
        execute_chat_action(action)


def process_chat_message(message: str) -> tuple[str, str]:
    """Process chat message and return (response, action_type).
    
    action_type can be: "navigate", "connect", "create_post", "status", "ideas", "none"
    """
    message_lower = message.lower()
    
    # Get app context
    db = get_db()
    products = []
    connected_platforms = []
    
    try:
        async def get_context():
            nonlocal products, connected_platforms
            async with db.async_session_maker() as session:
                products = await get_products(session)
                connected_platforms = await get_connected_platforms(session)
        
        import asyncio
        asyncio.run(get_context())
    except:
        pass
    
    product_names = [p.name for p in products] if products else []
    
    # Intent recognition
    if any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
        return """I'm your MediaAgent assistant! Here's what I can help with:

📝 **Posts** - Create, edit, or schedule posts
📅 **Scheduling** - Schedule posts for specific times
🔗 **Accounts** - Connect Twitter, Instagram, Facebook, LinkedIn
💡 **Ideas** - Get creative post ideas
⚙️ **Settings** - Configure automation and preferences
🔍 **Status** - Check automation and account status

Just tell me what you'd like to do!""", "none"
    
    # Navigation intents
    if any(word in message_lower for word in ["go to", "navigate", "show me", "open", "take me"]):
        if "dashboard" in message_lower or "home" in message_lower:
            return "Taking you to the Dashboard...", "navigate:/"
        elif "calendar" in message_lower:
            return "Opening the Calendar...", "navigate:/calendar"
        elif "campaign" in message_lower:
            return "Opening Campaigns...", "navigate:/campaigns"
        elif "template" in message_lower:
            return "Opening Templates...", "navigate:/templates"
        elif "engagement" in message_lower:
            return "Opening Engagement...", "navigate:/engagement"
        elif "setting" in message_lower:
            return "Opening Settings...", "navigate:/settings"
        elif "product" in message_lower:
            if products:
                if len(products) == 1:
                    return f"Opening {products[0].name}...", f"navigate:/product/{products[0].id}"
                else:
                    return f"You have {len(products)} products: {', '.join(product_names)}. Which one would you like to open?", "none"
            else:
                return "You don't have any products yet. Would you like to create one?", "none"
    
    # Check status intents
    if any(word in message_lower for word in ["status", "running", "automation", "connected", "check"]):
        scheduler = get_post_scheduler()
        status = "Running" if scheduler.is_running else "Stopped"
        platforms = ", ".join(connected_platforms) if connected_platforms else "No platforms connected"
        return f"""Here's your current status:

🤖 **Automation:** {status}
🔗 **Connected Platforms:** {platforms}
📦 **Products:** {len(products)}

Would you like to change anything?""", "none"
    
    # Connect account intents - go to settings for now
    if any(word in message_lower for word in ["connect", "login", "link", "add account"]) and any(word in message_lower for word in ["twitter", "instagram", "facebook", "linkedin", "social", "account"]):
        platform = None
        if "twitter" in message_lower or "x" in message_lower:
            platform = "twitter"
        elif "instagram" in message_lower:
            platform = "instagram"
        elif "facebook" in message_lower:
            platform = "facebook"
        elif "linkedin" in message_lower:
            platform = "linkedin"
        
        if platform:
            return f"Opening Settings to connect {platform.title()}...", f"connect:{platform}"
        else:
            return "Which platform would you like to connect? Twitter, Instagram, Facebook, or LinkedIn?", "none"
    
    # Create post intents
    if any(word in message_lower for word in ["create post", "new post", "write post", "make post", "post about", "write something"]):
        if not products:
            return "You need a product first before creating posts. Would you like to create one?", "none"
        
        if len(products) == 1:
            return f"Opening {products[0].name} to create a post...", f"create_post:{products[0].id}"
        else:
            return f"You have multiple products: {', '.join(product_names)}. Which one do you want to create a post for?", "none"
    
    # Get ideas intents
    if any(word in message_lower for word in ["idea", "ideas", "suggestion", "what should i post", "creative", "give me ideas", "help me think"]):
        if not products:
            return "I need a product to generate ideas for. Create a product first!", "none"
        
        product = products[0]
        return f"""Here are some creative post ideas for **{product.name}**:

1. 📸 **Feature Highlight** - Showcase a key feature
2. 💬 **Customer Testimonial** - Share a positive review
3. 🎉 **Behind the Scenes** - Give a peek into your process
4. 📚 **How-To Guide** - Teach users something useful
5. ❓ **Q&A** - Answer common questions
6. 🚀 **Announcement** - Share news or updates
7. 🤝 **Collaboration** - Mention partners

Would you like me to create any of these?""", "none"
    
    # Schedule intents
    if any(word in message_lower for word in ["schedule", "when", "post at", "post on", "calendar"]):
        if not products:
            return "You need a product to schedule a post. Create one first!", "none"
        
        return "Opening the Calendar to schedule a post...", "navigate:/calendar"
    
    # Toggle automation
    if any(word in message_lower for word in ["start automation", "stop automation", "toggle automation", "start posting", "stop posting"]):
        scheduler = get_post_scheduler()
        if scheduler.is_running:
            scheduler.stop()
            return "🛑 Automation stopped.", "none"
        else:
            scheduler.start()
            return "▶️ Automation started!", "none"
    
    # Default response
    return """I'm not sure I understood that. Here are some things I can help with:

• "Go to Dashboard" - Navigate to any page
• "Create a post" - Start writing a new post
• "Connect Twitter" - Link a social account
• "Give me ideas" - Get post inspiration
• "Check status" - See automation status

What would you like to do?""", "none"


def execute_chat_action(action_type: str):
    """Execute the action determined by the chat."""
    if not action_type or action_type == "none":
        return
    
    if action_type.startswith("navigate:"):
        path = action_type.replace("navigate:", "")
        ui.run_javascript(f'window.location.href = "{path}"')
    elif action_type.startswith("connect:"):
        platform = action_type.replace("connect:", "")
        ui.run_javascript('window.location.href = "/settings"')
    elif action_type.startswith("create_post:"):
        product_id = action_type.replace("create_post:", "")
        ui.run_javascript(f'window.location.href = "/product/{product_id}"')


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
    render_sidebar()
    render_chat_widget()
    
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
    render_sidebar()
    render_chat_widget()
    
    from media_agent.models.database import get_templates
    
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
    render_sidebar()
    render_chat_widget()
    
    from media_agent.models.database import get_campaigns
    
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
    render_sidebar()
    render_chat_widget()
    
    from media_agent.models.database import get_engagement_queue
    
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
    ui.page_title("MediaAgent - Dashboard")
    await render_home()


async def render_home():
    """Main dashboard with sidebar."""
    render_sidebar()
    render_chat_widget()
    
    # Dashboard content
    with ui.column().classes("p-6 w-full gap-6"):
        # Header
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Dashboard").classes("text-2xl font-bold text-gray-800")
            with ui.row().classes("gap-2"):
                ui.button("Add Product", icon="add", on_click=show_add_product_dialog).props("color=primary")
        
        db = get_db()
        async with db.async_session_maker() as session:
            products = await get_products(session)
        
        if not products:
            with ui.card().classes("w-full p-12 text-center").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
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
            published = len([p for p in total_posts if p.status == "published"])
        
        # Stats cards
        with ui.grid(columns=4).classes("w-full gap-4"):
            with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
                with ui.column().classes("text-center"):
                    ui.icon("inventory_2", size="32px").classes("text-indigo-500 mb-2")
                    ui.label(f"{len(products)}").classes("text-3xl font-bold text-indigo-600")
                    ui.label("Products").classes("text-sm text-gray-500")
            
            with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
                with ui.column().classes("text-center"):
                    ui.icon("publish", size="32px").classes("text-green-500 mb-2")
                    ui.label(f"{published}").classes("text-3xl font-bold text-green-600")
                    ui.label("Published Posts").classes("text-sm text-gray-500")
            
            with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
                with ui.column().classes("text-center"):
                    ui.icon("schedule", size="32px").classes("text-orange-500 mb-2")
                    ui.label(f"{scheduled}").classes("text-3xl font-bold text-orange-600")
                    ui.label("Scheduled").classes("text-sm text-gray-500")
            
            with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
                with ui.column().classes("text-center"):
                    ui.icon("people", size="32px").classes("text-purple-500 mb-2")
                    ui.label(f"{len(total_leads)}").classes("text-3xl font-bold text-purple-600")
                    ui.label("Leads").classes("text-sm text-gray-500")
        
        # Quick actions
        with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
            ui.label("Quick Actions").classes("text-lg font-bold mb-4")
            with ui.row().classes("gap-3"):
                ui.button("View Calendar", icon="calendar_month", on_click=lambda: navigate("calendar")).props("flat color=indigo")
                ui.button("Manage Templates", icon="text_snippet", on_click=lambda: navigate("templates")).props("flat color=indigo")
                ui.button("Check Engagement", icon="forum", on_click=lambda: navigate("engagement")).props("flat color=indigo")
                ui.button("Settings", icon="settings", on_click=lambda: navigate("settings")).props("flat color=indigo")
        
        # Products section
        ui.label("Your Products").classes("text-xl font-bold mt-4")
        
        with ui.grid(columns=3).classes("w-full gap-4 mt-4"):
            for product in products:
                await render_product_card_dashboard(product)
    
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

    with ui.card().classes("p-4 cursor-pointer hover:shadow-lg transition-shadow").on('click', lambda p=product: navigate("product", p.id)):
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


async def render_product_card_dashboard(product):
    """Render a product card for dashboard view."""
    db = get_db()
    async with db.async_session_maker() as session:
        posts = await get_posts(session, product_id=product.id)
        leads = await get_leads(session, product_id=product.id)
        
        published = len([p for p in posts if p.status == "published"])
        scheduled = len([p for p in posts if p.status == "scheduled"])
    
    with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
        with ui.column().classes("w-full"):
            with ui.row().classes("w-full justify-between items-center mb-2"):
                ui.label(product.name).classes("text-lg font-bold text-gray-800")
                ui.button(icon="chevron_right", on_click=lambda p=product: navigate("product", p.id)).props("flat round")
            
            if product.description:
                ui.label(product.description[:60] + "..." if len(product.description) > 60 else product.description).classes("text-sm text-gray-500 mb-3")
            
            with ui.grid(columns=3).classes("w-full gap-2 mt-2"):
                with ui.card().classes("p-2 text-center").style("background: #f0fdf4; border-radius: 8px;"):
                    ui.label(f"{published}").classes("text-lg font-bold text-green-600")
                    ui.label("Posts").classes("text-xs text-gray-500")
                with ui.card().classes("p-2 text-center").style("background: #fff7ed; border-radius: 8px;"):
                    ui.label(f"{scheduled}").classes("text-lg font-bold text-orange-600")
                    ui.label("Scheduled").classes("text-xs text-gray-500")
                with ui.card().classes("p-2 text-center").style("background: #faf5ff; border-radius: 8px;"):
                    ui.label(f"{len(leads)}").classes("text-lg font-bold text-purple-600")
                    ui.label("Leads").classes("text-xs text-gray-500")


# ============== PRODUCT DETAIL PAGE ==============
@ui.page("/product/{product_id}")
async def product_detail(product_id: int):
    ui.page_title(f"Product - {product_id}")
    await render_product_detail(product_id)


async def render_product_detail(product_id: int):
    """Render product detail page with sidebar and tabs."""
    render_sidebar()
    render_chat_widget()
    
    db = get_db()
    async with db.async_session_maker() as session:
        product = await get_product(session, product_id)
        if not product:
            with ui.column().classes("p-6"):
                ui.label("Product not found").classes("text-2xl")
            return

    # Product content
    with ui.column().classes("p-6 w-full gap-6"):
        # Header
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-4"):
                ui.label(product.name).classes("text-2xl font-bold text-gray-800")
            with ui.row().classes("gap-2"):
                ui.button("Edit", icon="edit", on_click=lambda: edit_product_dialog(product)).props("flat")
                ui.button("New Post", icon="add", on_click=lambda: show_create_post_dialog(product_id)).props("color=primary")
        
        # Tab navigation
        with ui.tabs().classes("w-full") as tabs:
            overview_tab = ui.tab("Overview")
            posts_tab = ui.tab("Posts")
            leads_tab = ui.tab("Leads")
            faqs_tab = ui.tab("FAQs")
            automation_tab = ui.tab("Automation")

        with ui.tab_panels(tabs, value=overview_tab).classes("w-full"):
            with ui.tab_panel(overview_tab):
                await render_product_overview(product)
            
            with ui.tab_panel(posts_tab):
                await render_product_posts(product_id)
            
            with ui.tab_panel(leads_tab):
                await render_product_leads(product_id)
            
            with ui.tab_panel(faqs_tab):
                await render_product_faqs(product_id)
            
            with ui.tab_panel(automation_tab):
                await render_product_automation(product)


async def render_product_overview(product):
    """Render product overview with analytics."""
    db = get_db()
    async with db.async_session_maker() as session:
        posts = await get_posts(session, product_id=product.id)
        leads = await get_leads(session, product_id=product.id)
        faqs = await get_faqs(session, product.id)
        connected_platforms = await get_connected_platforms(session)
        
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

    # Connected Social Accounts
    with ui.card().classes("p-4 w-full mb-4"):
        ui.label("Connected Accounts").classes("text-lg font-bold mb-4")
        ui.label("Connect social media accounts for this product").classes("text-sm text-gray-500 mb-4")
        
        platform_configs = [
            ("twitter", "Twitter/X", "tag", "blue", "text-blue-500"),
            ("instagram", "Instagram", "photo_camera", "pink", "text-pink-500"),
            ("facebook", "Facebook", "description", "blue", "text-blue-600"),
            ("linkedin", "LinkedIn", "work", "indigo", "text-indigo-600"),
        ]
        
        with ui.grid(columns=2).classes("w-full gap-4"):
            for platform_id, label, icon, color, icon_color in platform_configs:
                is_connected = platform_id in connected_platforms
                
                with ui.card().classes("p-3").style(f"border: 2px solid {'#22c55e' if is_connected else '#e5e7eb'};"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon(icon, size="20px").classes(icon_color)
                            ui.label(label).classes("font-bold")
                        
                        if is_connected:
                            ui.badge("Connected", color="green").classes("text-xs")
                        else:
                            ui.button("Connect", icon="link", on_click=lambda p=platform_id: connect_platform_dialog(p)).props(f"flat size=sm color={color}")

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


async def render_product_automation(product):
    """Render per-platform automation controls for a product."""
    settings = get_rate_limiter_settings()
    
    with ui.column().classes("w-full gap-6"):
        ui.label("Platform Automation").classes("text-xl font-bold")
        ui.label("Configure automation settings for each connected platform").classes("text-sm text-gray-500")
        
        platforms = [
            ("twitter", "Twitter/X", "tag", "blue"),
            ("instagram", "Instagram", "photo_camera", "pink"),
            ("facebook", "Facebook", "description", "blue"),
            ("linkedin", "LinkedIn", "work", "blue"),
        ]
        
        for platform_id, platform_name, icon, color in platforms:
            platform_settings = settings.get_platform_settings(platform_id)
            
            with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
                with ui.column().classes("w-full gap-4"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-3"):
                            ui.icon(icon, size="24px").classes(f"text-{color}-500")
                            ui.label(platform_name).classes("font-bold text-lg")
                        
                        enabled_switch = ui.switch("Enabled").props(f"color={color}")
                        enabled_switch.value = platform_settings.enabled
                    
                    with ui.grid(columns=4).classes("w-full gap-4"):
                        with ui.column():
                            ui.label("Posts/day").classes("text-xs text-gray-500")
                            posts_num = ui.number(value=platform_settings.posts_per_day, min=0, max=50).classes("w-full")
                        
                        with ui.column():
                            ui.label("Likes/day").classes("text-xs text-gray-500")
                            likes_num = ui.number(value=platform_settings.max_likes_per_day, min=0, max=200).classes("w-full")
                        
                        with ui.column():
                            ui.label("Follows/day").classes("text-xs text-gray-500")
                            follows_num = ui.number(value=platform_settings.max_follows_per_day, min=0, max=100).classes("w-full")
                        
                        with ui.column():
                            ui.label("Comments/day").classes("text-xs text-gray-500")
                            comments_num = ui.number(value=platform_settings.max_comments_per_day, min=0, max=100).classes("w-full")
                    
                    with ui.row().classes("gap-4 items-center"):
                        ui.label("Active hours:").classes("text-sm")
                        ui.label("From").classes("text-xs text-gray-500")
                        start_hour = ui.number(value=platform_settings.active_hours_start, min=0, max=23).classes("w-20")
                        ui.label("To").classes("text-xs text-gray-500")
                        end_hour = ui.number(value=platform_settings.active_hours_end, min=0, max=23).classes("w-20")
                    
                    async def save_platform_settings(p=platform_id, e=enabled_switch, po=posts_num, li=likes_num, fo=follows_num, co=comments_num, sh=start_hour, eh=end_hour):
                        s = get_rate_limiter_settings()
                        ps = s.get_platform_settings(p)
                        ps.enabled = e.value
                        ps.posts_per_day = int(po.value or 0)
                        ps.max_likes_per_day = int(li.value or 0)
                        ps.max_follows_per_day = int(fo.value or 0)
                        ps.max_comments_per_day = int(co.value or 0)
                        ps.active_hours_start = int(sh.value or 9)
                        ps.active_hours_end = int(eh.value or 21)
                        update_rate_limiter_settings(s)
                        ui.notify(f"{p.title()} settings saved!", type="positive")
                    
                    ui.button("Save Settings", icon="save", on_click=save_platform_settings).props(f"color={color}")
        
        # Advanced settings link
        with ui.card().classes("p-4").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
            with ui.row().classes("w-full justify-between items-center"):
                ui.label("Advanced Settings").classes("font-bold")
                ui.label("Human behavior, typing speed, delays").classes("text-sm text-gray-500")
                ui.button("Configure", icon="settings", on_click=lambda: navigate("settings")).props("flat")


# ============== SETTINGS PAGE ==============
@ui.page("/settings")
async def settings_page():
    ui.page_title("Settings - MediaAgent")
    await render_settings()


async def render_settings():
    """Render settings page with sidebar."""
    render_sidebar()
    render_chat_widget()
    
    with ui.column().classes("p-6 w-full gap-6"):
        ui.label("Settings").classes("text-2xl font-bold text-gray-800")
        
        # AI Configuration
        with ui.card().classes("p-6").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
            ui.label("AI Configuration").classes("text-xl font-bold mb-4")
            settings = get_settings()
            
            api_key_input = ui.input(
                "OpenRouter API Key",
                value=settings.openrouter_api_key or "",
                placeholder="sk-..."
            ).classes("w-full mb-4")
            
            ui.label("AI Model: " + settings.openrouter_model).classes("text-sm mb-4")
            
            ui.button("Save Settings", on_click=lambda: ui.notify("Settings saved! Add to .env for persistence")).props("color=primary")
        
        # Automation Settings
        with ui.card().classes("p-6").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
            ui.label("Automation & Rate Limits").classes("text-xl font-bold mb-4")
            
            current_settings = get_rate_limiter_settings()
            scheduler = get_post_scheduler()
            is_running = scheduler.is_running
            
            with ui.row().classes("w-full justify-between items-center mb-4"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("circle", size="12px").classes(f"{'text-green-500' if is_running else 'text-red-500'}")
                    ui.label(f"Automation: {'Running' if is_running else 'Stopped'}").classes("font-medium")
                ui.button("Toggle", icon="play_arrow" if not is_running else "pause", on_click=lambda: toggle_scheduler_sidebar()).props(f"color={'green' if not is_running else 'red'}")
            
            with ui.grid(columns=2).classes("w-full gap-4"):
                with ui.column():
                    ui.label("Global Posts per Day").classes("text-sm font-medium")
                    posts_per_day = ui.number(value=current_settings.max_posts_per_day, min=1, max=100).classes("w-full")
                
                with ui.column():
                    ui.label("Global Posts per Week").classes("text-sm font-medium")
                    posts_per_week = ui.number(value=current_settings.max_posts_per_week, min=1, max=500).classes("w-full")
            
            with ui.row().classes("gap-4 items-center mt-2"):
                ui.label("Active Hours:").classes("text-sm font-medium")
                active_start = ui.number(value=current_settings.global_active_start, min=0, max=23).classes("w-20")
                ui.label("to").classes("text-sm")
                active_end = ui.number(value=current_settings.global_active_end, min=0, max=23).classes("w-20")
            
            async def save_limits():
                s = get_rate_limiter_settings()
                s.max_posts_per_day = int(posts_per_day.value or 10)
                s.max_posts_per_week = int(posts_per_week.value or 50)
                s.global_active_start = int(active_start.value or 8)
                s.global_active_end = int(active_end.value or 22)
                update_rate_limiter_settings(s)
                ui.notify("Rate limits saved!", type="positive")
            
            ui.button("Save Limits", icon="save", on_click=save_limits).props("color=primary").classes("mt-4")
        
        # Human Behavior Settings
        with ui.card().classes("p-6").style("background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"):
            ui.label("Human Behavior Settings").classes("text-xl font-bold mb-4")
            ui.label("Make automation appear more human to avoid detection").classes("text-sm text-gray-500 mb-4")
            
            twitter_settings = current_settings.get_platform_settings("twitter")
            
            with ui.grid(columns=2).classes("w-full gap-4"):
                with ui.column():
                    ui.label("Typing Speed (WPM)").classes("text-sm font-medium")
                    with ui.row().classes("gap-2"):
                        typing_min = ui.number(value=twitter_settings.typing_speed_min_wpm, min=20, max=100).classes("w-full")
                        typing_max = ui.number(value=twitter_settings.typing_speed_max_wpm, min=40, max=120).classes("w-full")
                
                with ui.column():
                    ui.label("Delay Between Actions (seconds)").classes("text-sm font-medium")
                    with ui.row().classes("gap-2"):
                        delay_min = ui.number(value=twitter_settings.min_action_delay, min=1, max=10).classes("w-full")
                        delay_max = ui.number(value=twitter_settings.max_action_delay, min=2, max=30).classes("w-full")
            
            async def save_human_behavior():
                s = get_rate_limiter_settings()
                for p in ["twitter", "instagram", "facebook", "linkedin"]:
                    ps = s.get_platform_settings(p)
                    ps.typing_speed_min_wpm = int(typing_min.value or 40)
                    ps.typing_speed_max_wpm = int(typing_max.value or 80)
                    ps.min_action_delay = float(delay_min.value or 1.0)
                    ps.max_action_delay = float(delay_max.value or 5.0)
                update_rate_limiter_settings(s)
                ui.notify("Human behavior settings saved!", type="positive")
            
            ui.button("Save Human Behavior", icon="save", on_click=save_human_behavior).props("color=purple").classes("mt-4")

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
    with ui.card().classes("p-6 w-full mb-6"):
        ui.label("Automation").classes("text-xl font-bold mb-4")
        
        scheduler = get_post_scheduler()
        status = "Running" if scheduler.is_running else "Stopped"
        status_color = "green" if scheduler.is_running else "red"
        
        with ui.row().classes("w-full justify-between items-center"):
            ui.label("Post Scheduler:").classes("font-bold")
            with ui.row().classes("gap-2"):
                ui.badge(status, color=status_color)
                ui.button("Toggle", on_click=lambda: toggle_scheduler()).props("flat color=orange")

    # Rate Limiting & Human Behavior
    with ui.card().classes("p-6 w-full mb-6"):
        ui.label("Posting Limits & Human Behavior").classes("text-xl font-bold mb-4")
        ui.label("Control how often the AI posts and how human-like the behavior is").classes("text-sm text-gray-500 mb-4")
        
        # Load current settings
        current_settings = get_rate_limiter_settings()
        
        # Global limits
        with ui.card().classes("p-4 mb-4"):
            ui.label("Global Limits").classes("font-bold mb-2")
            with ui.grid(columns=2).classes("w-full gap-4"):
                ui.label("Posts per day:").classes("text-sm")
                posts_per_day = ui.number(value=current_settings.max_posts_per_day, min=1, max=100).classes("w-full")
                
                ui.label("Posts per week:").classes("text-sm")
                posts_per_week = ui.number(value=current_settings.max_posts_per_week, min=1, max=500).classes("w-full")
        
        # Twitter settings
        twitter_settings = current_settings.get_platform_settings("twitter")
        with ui.card().classes("p-4 mb-4"):
            ui.label("Twitter Settings").classes("font-bold mb-2")
            with ui.grid(columns=2).classes("w-full gap-4"):
                ui.label("Posts/day:").classes("text-sm")
                tw_posts = ui.number(value=twitter_settings.posts_per_day, min=1, max=50, step=1).classes("w-full")
                
                ui.label("Likes/day:").classes("text-sm")
                tw_likes = ui.number(value=twitter_settings.max_likes_per_day, min=0, max=200, step=10).classes("w-full")
                
                ui.label("Follows/day:").classes("text-sm")
                tw_follows = ui.number(value=twitter_settings.max_follows_per_day, min=0, max=100, step=5).classes("w-full")
                
                ui.label("Comments/day:").classes("text-sm")
                tw_comments = ui.number(value=twitter_settings.max_comments_per_day, min=0, max=100, step=5).classes("w-full")
        
        # Human behavior
        with ui.card().classes("p-4 mb-4"):
            ui.label("Human Behavior Settings").classes("font-bold mb-2")
            ui.label("Make automation appear more human to avoid detection").classes("text-xs text-gray-500 mb-2")
            
            with ui.grid(columns=2).classes("w-full gap-4"):
                ui.label("Typing speed (WPM):").classes("text-sm")
                with ui.row().classes("gap-2"):
                    typing_min = ui.number(value=twitter_settings.typing_speed_min_wpm, min=20, max=100, step=5).classes("w-full")
                    typing_max = ui.number(value=twitter_settings.typing_speed_max_wpm, min=40, max=120, step=5).classes("w-full")
                
                ui.label("Delay between actions (sec):").classes("text-sm")
                with ui.row().classes("gap-2"):
                    delay_min = ui.number(value=twitter_settings.min_action_delay, min=1, max=10, step=1).classes("w-full")
                    delay_max = ui.number(value=twitter_settings.max_action_delay, min=2, max=30, step=1).classes("w-full")
        
        # Active hours
        with ui.card().classes("p-4 mb-4"):
            ui.label("Active Hours").classes("font-bold mb-2")
            ui.label("Only post during these hours").classes("text-xs text-gray-500 mb-2")
            with ui.row().classes("gap-4"):
                ui.label("From:")
                active_start = ui.number(value=current_settings.global_active_start, min=0, max=23).classes("w-20")
                ui.label("To:")
                active_end = ui.number(value=current_settings.global_active_end, min=0, max=23).classes("w-20")
        
        async def save_limits():
            """Save rate limiting settings."""
            settings = get_rate_limiter_settings()
            
            # Global limits
            settings.max_posts_per_day = int(posts_per_day.value or 10)
            settings.max_posts_per_week = int(posts_per_week.value or 50)
            settings.global_active_start = int(active_start.value or 8)
            settings.global_active_end = int(active_end.value or 22)
            
            # Twitter settings
            twitter = settings.get_platform_settings("twitter")
            twitter.posts_per_day = int(tw_posts.value or 5)
            twitter.max_likes_per_day = int(tw_likes.value or 50)
            twitter.max_follows_per_day = int(tw_follows.value or 30)
            twitter.max_comments_per_day = int(tw_comments.value or 20)
            twitter.typing_speed_min_wpm = int(typing_min.value or 40)
            twitter.typing_speed_max_wpm = int(typing_max.value or 80)
            twitter.min_action_delay = float(delay_min.value or 1.0)
            twitter.max_action_delay = float(delay_max.value or 5.0)
            
            # Update other platforms with similar settings
            for platform in ["instagram", "facebook", "linkedin"]:
                p = settings.get_platform_settings(platform)
                p.typing_speed_min_wpm = twitter.typing_speed_min_wpm
                p.typing_speed_max_wpm = twitter.typing_speed_max_wpm
                p.min_action_delay = twitter.min_action_delay
                p.max_action_delay = twitter.max_action_delay
            
            update_rate_limiter_settings(settings)
            ui.notify("Rate limits saved!", type="positive")
        

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
    # Check if already connected
    db = get_db()
    async with db.async_session_maker() as session:
        connected_platforms = await get_connected_platforms(session)
        is_connected = "twitter" in connected_platforms
    
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-md"):
        with ui.row().classes("w-full justify-between items-center"):
            ui.label("Connect Twitter/X").classes("text-xl font-bold")
            if is_connected:
                ui.badge("Connected", color="green").classes("ml-2")
        
        if is_connected:
            ui.label("Twitter is already connected!").classes("text-green-600 mb-4")
            ui.button("Disconnect", on_click=lambda: ui.notify("Feature coming soon")).props("flat color=negative")
            ui.button("Close", on_click=dialog.close).props("flat")
            dialog.open()
            return
        
        # Option 1: Auto-login with Google credentials
        with ui.card().classes("p-4 mb-4").style("background: #f0f9ff; border: 1px solid #bae6fd;"):
            ui.label("Auto-Login with Google").classes("font-bold mb-2")
            ui.label("Enter your Google credentials to login automatically").classes("text-xs text-gray-500 mb-2")
            
            google_email = ui.input("Google Email", placeholder="your.email@gmail.com").classes("w-full mb-2")
            google_password = ui.input("Google Password", password=True, password_toggle_button=True).classes("w-full mb-2")
            
            async def login_with_google():
                if not google_email.value or not google_password.value:
                    ui.notify("Please enter Google credentials", type="warning")
                    return
                
                ui.notify("🤖 Starting automated Twitter login with Google SSO...", type="info")
                
                from media_agent.platforms import get_platform_registry
                registry = get_platform_registry()
                adapter = registry.get_adapter("twitter", google_email.value, google_password.value)
                
                async def attempt_login(max_attempts=3):
                    """Attempt login with troubleshooting."""
                    for attempt in range(max_attempts):
                        try:
                            ui.notify(f"Attempt {attempt + 1}: Opening browser...", type="info")
                            
                            # Initialize browser
                            await adapter.init_browser(headless=False)
                            await adapter.page.goto("https://x.com/i/flow/login")
                            await adapter.page.wait_for_load_state("networkidle")
                            await adapter.page.wait_for_timeout(2000)
                            
                            ui.notify(f"Attempt {attempt + 1}: Looking for sign-in options...", type="info")
                            
                            # Try to find and click "Sign in with Google" button
                            try:
                                # Multiple selectors to try
                                selectors = [
                                    'button:has-text("Sign in with Google")',
                                    'button:has-text("Continue with Google")',
                                    'a:has-text("Sign in with Google")',
                                    '[data-testid="google_sign_in_button"]',
                                ]
                                
                                google_btn = None
                                for sel in selectors:
                                    google_btn = await adapter.page.query_selector(sel)
                                    if google_btn:
                                        break
                                
                                if google_btn:
                                    ui.notify(f"Attempt {attempt + 1}: Clicking Google sign-in...", type="info")
                                    await google_btn.click()
                                    await adapter.page.wait_for_load_state("networkidle")
                                    await adapter.page.wait_for_timeout(3000)
                                else:
                                    # Maybe already on Google login page
                                    ui.notify(f"Attempt {attempt + 1}: Already on login page, checking...", type="info")
                            except Exception as e:
                                ui.notify(f"Click attempt: {str(e)[:50]}", type="info")
                            
                            # Fill Google email
                            ui.notify(f"Attempt {attempt + 1}: Entering email...", type="info")
                            email_input = await adapter.page.wait_for_selector('input[type="email"]', timeout=10000)
                            await email_input.fill(google_email.value)
                            await adapter.page.wait_for_timeout(500)
                            
                            # Click Next
                            next_btns = await adapter.page.query_selector_all('button:has-text("Next")')
                            for btn in next_btns:
                                if await btn.is_visible():
                                    await btn.click()
                                    break
                            
                            await adapter.page.wait_for_timeout(3000)
                            
                            # Handle possible phone/verification page
                            try:
                                phone_input = await adapter.page.query_selector('input[type="tel"]')
                                if phone_input and await phone_input.is_visible():
                                    ui.notify("Phone verification needed. Please enter phone manually.", type="warning")
                                    await adapter.page.wait_for_timeout(30000)  # Wait for manual input
                            except:
                                pass
                            
                            # Fill Google password
                            ui.notify(f"Attempt {attempt + 1}: Entering password...", type="info")
                            password_input = await adapter.page.wait_for_selector('input[type="password"]', timeout=10000)
                            await password_input.fill(google_password.value)
                            await adapter.page.wait_for_timeout(500)
                            
                            # Click Next
                            next_btns = await adapter.page.query_selector_all('button:has-text("Next")')
                            for btn in next_btns:
                                if await btn.is_visible():
                                    await btn.click()
                                    break
                            
                            ui.notify(f"Attempt {attempt + 1}: Logging in...", type="info")
                            await adapter.page.wait_for_timeout(5000)
                            
                            # Check if logged in
                            current_url = adapter.page.url
                            if "home" in current_url or "feed" in current_url or "x.com" in current_url:
                                ui.notify("🎉 Login successful! Saving session...", type="positive")
                                
                                # Save session
                                await adapter.save_cookies()
                                cookies = adapter.get_cookies_json()
                                
                                db = get_db()
                                async with db.async_session_maker() as session:
                                    await save_platform_credential(session, "twitter", google_email.value, cookies)
                                
                                return True
                            
                        except Exception as e:
                            ui.notify(f"Attempt {attempt + 1} failed: {str(e)[:80]}", type="warning")
                            await adapter.page.wait_for_timeout(2000)
                    
                    return False
                
                success = await attempt_login()
                
                if success:
                    ui.notify("🎉 Twitter connected successfully!", type="positive")
                    dialog.close()
                else:
                    ui.notify("Login failed after multiple attempts. Try manual login.", type="negative")
            
            ui.button("Auto-Login with Google", icon="login", on_click=login_with_google).props("color=blue w-full")
        
        # Option 2: Manual browser login
        with ui.card().classes("p-4"):
            ui.label("Or login manually in browser").classes("font-bold mb-2")
            ui.label("Open browser, login to Twitter, then click 'I logged in'").classes("text-xs text-gray-500 mb-2")
            
            async def open_browser_manual():
                from media_agent.platforms import get_platform_registry
                registry = get_platform_registry()
                adapter = registry.get_adapter("twitter", "manual", "dummy")
                
                try:
                    await adapter.init_browser(headless=False)
                    await adapter.page.goto("https://x.com/i/flow/login")
                    
                    # Show confirmation UI
                    with ui.card().classes("p-4 mt-4").style("background: #f0fdf4; border: 1px solid #bbf7d0;"):
                        ui.label("After logging in, click below:").classes("text-sm font-bold")
                        
                        async def confirm():
                            await adapter.save_cookies()
                            cookies = adapter.get_cookies_json()
                            db = get_db()
                            async with db.async_session_maker() as session:
                                await save_platform_credential(session, "twitter", "manual", cookies)
                            ui.notify("Twitter connected!", type="positive")
                            dialog.close()
                        
                        ui.button("I logged in", icon="check", on_click=confirm).props("color=green w-full")
                        
                except Exception as e:
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            ui.button("Open Browser", icon="open_in_browser", on_click=open_browser_manual).props("flat w-full")
        
        with ui.row().classes("w-full justify-end"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
    
    dialog.open()


async def connect_platform_dialog(platform: str):
    """Route to appropriate platform connection dialog."""
    if platform == "twitter":
        await connect_twitter()
    elif platform == "instagram":
        await connect_instagram()
    elif platform == "facebook":
        await connect_facebook()
    elif platform == "linkedin":
        await connect_linkedin()
    else:
        ui.notify(f"Platform {platform} not supported yet", type="warning")


async def connect_instagram():
    """Show Instagram connection dialog."""
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Connect Instagram").classes("text-xl font-bold mb-4")
        
        ui.label("Choose your login method:").classes("text-sm mb-2")
        ui.label("• Login with Facebook (recommended for Facebook SSO)").classes("text-xs text-gray-500")
        ui.label("• Or enter your Instagram username/password").classes("text-xs text-gray-500 mb-4")
        
        async def login_with_browser():
            """Open browser and let user login manually (supports Facebook SSO)."""
            ui.notify("Opening browser... Login with Facebook or username/password", type="info")
            
            from media_agent.platforms import get_platform_registry
            registry = get_platform_registry()
            adapter = registry.get_adapter("instagram", "dummy", "dummy")
            
            try:
                await adapter.init_browser(headless=False)
                await adapter.page.goto("https://www.instagram.com/accounts/login/")
                
                ui.notify("Browser opened! Login however you normally do. We'll save your session.", type="info")
                
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type="negative")
        
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
        
        ui.button("Login with Facebook (Browser)", icon="login", on_click=login_with_browser).props("color=purple w-full mb-4")
        
        ui.label("Or login with username/password:").classes("text-sm font-bold mt-4 mb-2")
        username = ui.input("Username").classes("w-full mb-2")
        password = ui.input("Password", password=True, password_toggle_button=True).classes("w-full mb-4")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Connect", on_click=test_connection).props("color=purple")
    
    dialog.open()


async def connect_linkedin():
    ui.notify("LinkedIn integration coming soon!", type="info")


async def connect_facebook():
    """Show Facebook connection dialog."""
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Connect Facebook").classes("text-xl font-bold mb-4")
        
        ui.label("Enter your Facebook credentials to enable:").classes("text-sm mb-2")
        ui.label("• Automated posting").classes("text-xs text-gray-500")
        ui.label("• Auto-responding to comments").classes("text-xs text-gray-500")
        
        async def login_with_browser():
            """Open browser and let user login manually."""
            ui.notify("Opening browser... Login however you normally do", type="info")
            
            from media_agent.platforms import get_platform_registry
            registry = get_platform_registry()
            adapter = registry.get_adapter("facebook", "dummy", "dummy")
            
            try:
                await adapter.init_browser(headless=False)
                await adapter.page.goto("https://www.facebook.com/login")
                
                ui.notify("Browser opened! Login however you normally do. We'll save your session.", type="info")
                
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type="negative")
        
        username = ui.input("Email or Phone").classes("w-full mb-2")
        password = ui.input("Password", password=True, password_toggle_button=True).classes("w-full mb-2")
        
        async def test_connection():
            if not username.value or not password.value:
                ui.notify("Please enter credentials", type="warning")
                return
            
            ui.notify("Opening browser...", type="info")
            
            from media_agent.platforms import get_platform_registry
            registry = get_platform_registry()
            adapter = registry.get_adapter("facebook", username.value, password.value)
            
            try:
                success = await adapter.login()
                if success:
                    ui.notify("Facebook connected!", type="positive")
                    dialog.close()
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type="negative")
        
        ui.button("Login with Browser", icon="login", on_click=login_with_browser).props("color=blue w-full mb-4")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Connect", on_click=test_connection).props("color=blue")
    
    dialog.open()


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
        
        # Schedule date/time
        schedule_toggle = ui.switch("Schedule for later").props("color=orange")
        schedule_date = ui.input("Schedule Date (YYYY-MM-DD)", placeholder="2024-12-31").classes("w-full mb-2")
        schedule_time = ui.input("Schedule Time (HH:MM)", placeholder="14:30").classes("w-full mb-2")
        
        # Initially hide schedule inputs
        schedule_date.visible = False
        schedule_time.visible = False
        
        def toggle_schedule():
            schedule_date.visible = schedule_toggle.value
            schedule_time.visible = schedule_toggle.value
        
        schedule_toggle.on_click(toggle_schedule)
        
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

        async def save_draft():
            if not content.value:
                ui.notify("Content required", type="warning")
                return
            
            db = get_db()
            async with db.async_session_maker() as session:
                await create_post(session, product_id=product_id, content=content.value, platform=platform.value, scheduled_at=None, status="draft")
            
            dialog.close()
            ui.notify("Post saved as draft!")
            ui.navigate.to(f"/product/{product_id}")

        async def save_schedule():
            if not content.value:
                ui.notify("Content required", type="warning")
                return
            
            from datetime import datetime
            scheduled_at = None
            status = "draft"
            
            if schedule_toggle.value and schedule_date.value and schedule_time.value:
                try:
                    scheduled_at = datetime.strptime(f"{schedule_date.value} {schedule_time.value}", "%Y-%m-%d %H:%M")
                    status = "scheduled"
                except ValueError:
                    ui.notify("Invalid date/time format. Use YYYY-MM-DD and HH:MM", type="warning")
                    return
            
            db = get_db()
            async with db.async_session_maker() as session:
                await create_post(session, product_id=product_id, content=content.value, platform=platform.value, scheduled_at=scheduled_at, status=status)
            
            dialog.close()
            if status == "scheduled":
                ui.notify("Post scheduled!")
            else:
                ui.notify("Post saved as draft!")
            ui.navigate.to(f"/product/{product_id}")
        
        with ui.row().classes("w-full gap-2 mb-4"):
            ui.button("Generate with AI", icon="auto_awesome", on_click=generate).props("color=purple")
        
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Save Draft", on_click=save_draft).props("flat")
            ui.button("Schedule Post", on_click=save_schedule).props("color=primary")
    
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
