# MediaAgent

An AI-powered social media agent that automates product promotion across multiple platforms. Generate content, schedule posts, discover leads, and auto-respond to engagement - all from a local dashboard.

## Features

- **Product Management** - Configure products with brand voice and target audience
- **AI Content Generation** - Generate posts using OpenRouter (free tier available)
- **Post Scheduling** - Schedule posts with calendar view
- **Lead Discovery** - Find potential customers on Twitter/Instagram
- **FAQ Auto-Response** - Automatically respond to common questions
- **Engagement Queue** - Review and approve AI-generated responses
- **Post Templates** - Save reusable content templates
- **Campaigns** - Organize posts into marketing campaigns
- **Multi-Platform** - Twitter, Instagram, Facebook, LinkedIn adapters

## Tech Stack

- **Python 3.11+**
- **NiceGUI** - Web dashboard
- **Playwright** - Browser automation
- **SQLAlchemy** - Database
- **APScheduler** - Background scheduling
- **OpenRouter** - AI content generation

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/JuanOnly/Social-Media-Agent.git
cd Social-Media-Agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install nicegui sqlalchemy aiosqlite pydantic pydantic-settings httpx apscheduler pyyaml cryptography python-dotenv playwright
python -m playwright install chromium
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

Get a free API key at [https://openrouter.ai](https://openrouter.ai)

### 5. Run the Application

```bash
python main.py
```

Open **http://localhost:8080** in your browser.

## Usage

### Adding a Product

1. Click **Add Product** on the home page
2. Enter product name, description, and target audience
3. The AI will use this context for content generation

### Connecting Social Accounts

1. Go to **Settings**
2. Click **Connect** on your preferred platform
3. Enter your credentials
4. A browser window will open for login
5. Complete any 2FA if required
6. Credentials are saved locally for automation

### Creating Posts

1. Click on a product card
2. Go to **Posts** tab
3. Click **New Post**
4. Use **Generate with AI** or write manually
5. Save as draft or schedule

### Using Templates

1. Go to **Templates** page
2. Create reusable post templates
3. Select template when creating new posts

### Discovering Leads

1. Go to a product's **Leads** tab
2. Click **Discover Leads**
3. Enter search keywords (e.g., "link in bio")
4. Save promising accounts to your leads list

## Project Structure

```
media-agent/
├── main.py                 # Entry point
├── pyproject.toml          # Dependencies
├── SPEC.md                 # Full specification
├── .env.example            # Environment template
├── config/
│   └── products/           # Product configurations
├── src/media_agent/
│   ├── agents/             # AI engine
│   ├── config/             # Settings management
│   ├── content/            # FAQ matching
│   ├── discovery/          # Lead discovery
│   ├── engagement/         # Auto-response
│   ├── models/             # Database models
│   ├── platforms/          # Platform adapters
│   └── scheduler/          # Post scheduling
├── ui/
│   └── main.py             # NiceGUI dashboard
└── tests/                  # Unit tests
```

## Configuration

### Product Config Files

Store product configs in `config/products/{name}.json`:

```json
{
  "product": {
    "name": "MyProduct",
    "description": "Product description",
    "brand_voice": "professional",
    "target_audience": "entrepreneurs, small business"
  },
  "faq": [
    {
      "question": "How does it work?",
      "answer": "Simply connect your accounts...",
      "keywords": "how, work, use"
    }
  ]
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `OPENROUTER_MODEL` | AI model to use | deepseek/deepseek-chat |
| `APP_HOST` | Dashboard host | 0.0.0.0 |
| `APP_PORT` | Dashboard port | 8080 |
| `DATABASE_URL` | SQLite database URL | sqlite+aiosqlite:///./media_agent.db |

## Available Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | All products with quick stats |
| Product | `/product/{id}` | Product details with tabs |
| Calendar | `/calendar` | Monthly scheduling view |
| Templates | `/templates` | Reusable post templates |
| Campaigns | `/campaigns` | Marketing campaign groups |
| Engagement | `/engagement` | Pending response queue |
| Settings | `/settings` | Account connections, AI config |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project uses Ruff for linting:

```bash
pip install ruff
ruff check src/ ui/
```

## Security Notes

- Credentials are stored locally in SQLite
- Cookies saved for session persistence
- No data sent to external servers (except OpenRouter API)
- API keys stored in `.env` file (not committed to git)

## Limitations

- Instagram requires image for posts (not fully supported)
- Facebook/LinkedIn adapters are stubs
- No image/video generation
- Single user (no authentication)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License

## Acknowledgments

- [NiceGUI](https://nicegui.io) - Web UI framework
- [OpenRouter](https://openrouter.ai) - AI API access
- [Playwright](https://playwright.dev/python/) - Browser automation
