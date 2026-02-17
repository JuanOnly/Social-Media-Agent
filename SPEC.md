# MediaAgent - Social Media AI Agent

## Project Overview

**Project Name:** MediaAgent  
**Project Type:** Desktop Application (Local AI Agent)  
**Core Functionality:** An AI-powered social media agent that promotes products through multiple social media accounts, handles scheduling, engages with users, responds to FAQs, and discovers potential leads.  
**Target Users:** Small business owners, marketers, and individuals who want to automate social media promotion for 1-3 products.

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Language** | Python 3.11+ | AI libraries, cross-platform |
| **UI Framework** | NiceGUI | Python-only web UI, modern, built-in automation support |
| **AI Provider** | OpenRouter | Free tier available, multiple models |
| **Browser Automation** | Playwright | Stable, cross-platform, better than Puppeteer on Windows |
| **Database** | SQLite | Local storage, no server needed |
| **Scheduling** | APScheduler | Python-native, handles scheduling |
| **Package Manager** | pip/uv | Modern, fast Python package manager |

---

## User Stories

### US001: Product Management
**As a** user  
**I want to** configure a product with name, description, tone, and target audience  
**So that** the AI can generate contextually appropriate content

**Acceptance Criteria:**
- [ ] User can add a product with: name, description, brand voice, target audience keywords
- [ ] User can edit existing product configuration
- [ ] User can delete a product
- [ ] Product config persists in SQLite database

### US002: AI Content Generation
**As a** user  
**I want the AI to** generate social media posts based on product info  
**So that** I don't have to write content manually

**Acceptance Criteria:**
- [ ] AI generates posts using OpenRouter API
- [ ] Posts are tailored to product description and brand voice
- [ ] User can specify post length (short/medium/long)
- [ ] User can regenerate if unsatisfied with output
- [ ] Generated posts can be saved to draft queue

### US003: Post Scheduling
**As a** user  
**I want to** schedule posts for future publishing  
**So that** I can maintain consistent social media presence

**Acceptance Criteria:**
- [ ] User can select date and time for each post
- [ ] User can select which platforms to post to (Twitter, Instagram, Facebook, LinkedIn)
- [ ] Scheduled posts display in a calendar view
- [ ] User can edit or delete scheduled posts
- [ ] Posts queue in SQLite until published

### US004: FAQ Management
**As a** user  
**I want to** add FAQ questions and answers  
**So that** the AI can automatically respond to common questions

**Acceptance Criteria:**
- [ ] User can add Q&A pairs with question, answer, and optional keywords
- [ ] User can edit and delete FAQ entries
- [ ] FAQ database is product-specific
- [ ] AI matches incoming questions to FAQ using keyword similarity

### US005: Auto-Response to Engagement
**As a** user  
**I want the agent to** respond to comments and mentions automatically  
**So that** I don't miss engagement opportunities

**Acceptance Criteria:**
- [ ] Agent monitors configured social accounts for new comments/mentions
- [ ] Matching questions trigger FAQ responses
- [ ] Non-FAQ queries generate AI responses using product context
- [ ] User can enable/disable auto-response per platform
- [ ] All responses logged for review

### US006: Lead Discovery
**As a** user  
**I want to** find social media accounts interested in similar products  
**So that** I can engage with potential customers

**Acceptance Criteria:**
- [ ] User can search by hashtags, keywords, or competitor accounts
- [ ] Results show account name, follower count, engagement rate
- [ ] User can save promising accounts to leads list
- [ ] Leads can be tagged and categorized

### US007: Platform Credentials
**As a** user  
**I want to** configure login credentials for social platforms  
**So that** the agent can post and engage on my behalf

**Acceptance Criteria:**
- [ ] User can store platform credentials (username/password)
- [ ] Credentials stored encrypted in SQLite
- [ ] User can test credential validity
- [ ] Credentials used by Playwright for login

### US008: Dashboard Overview
**As a** user  
**I want to** see an overview of agent activity  
**So that** I can monitor performance

**Acceptance Criteria:**
- [ ] Dashboard shows: total posts scheduled, posts published, engagement count
- [ ] Shows recent activity log
- [ ] Quick access to all features via navigation

---

## Functional Requirements

### FR001: Configuration Management
- Load product config from YAML/JSON files
- Store in SQLite with encryption for sensitive data
- Support multiple products (expandable architecture)

### FR002: AI Engine
- Connect to OpenRouter API using free tier
- Support model selection (default: deepseek/deepseek-chat)
- Implement prompt templates for different content types
- Handle rate limiting gracefully

### FR003: Content Generator
- Generate posts: promotional, educational, engagement, announcement
- Adapt tone based on product brand_voice setting
- Include relevant hashtags based on target_audience keywords

### FR004: Scheduler
- Store scheduled posts in SQLite
- Execute publishing at scheduled time
- Retry failed posts up to 3 times
- Log all publishing attempts

### FR005: Platform Adapters (Playwright)
- Twitter/X: Post, like, comment, follow, search
- Instagram: Post, like, comment, follow, search (limited API)
- Facebook: Post, comment (Page API)
- LinkedIn: Post, comment (personal profile)
- All adapters implement common interface

### FR006: FAQ Matcher
- Store FAQs with keywords in SQLite
- Use keyword matching + simple similarity scoring
- Fall back to AI generation for non-FAQ queries
- Include product context in response generation

### FR007: Lead Discovery
- Search platforms for hashtags/keywords
- Extract: username, bio, follower count, recent posts
- Score leads by relevance
- Save to leads table with tags

### FR008: Engagement Handler
- Poll platforms for new mentions/comments
- Queue responses for processing
- Apply rate limiting per platform
- Log all interactions

---

## Data Models

### Product
```
- id: INTEGER PRIMARY KEY
- name: TEXT NOT NULL
- description: TEXT
- brand_voice: TEXT (friendly, professional, casual, authoritative)
- target_audience: TEXT (comma-separated keywords)
- created_at: DATETIME
- updated_at: DATETIME
```

### Post
```
- id: INTEGER PRIMARY KEY
- product_id: INTEGER FOREIGN KEY
- content: TEXT NOT NULL
- platform: TEXT (twitter, instagram, facebook, linkedin)
- scheduled_at: DATETIME
- published_at: DATETIME
- status: TEXT (draft, scheduled, published, failed)
- created_at: DATETIME
```

### FAQ
```
- id: INTEGER PRIMARY KEY
- product_id: INTEGER FOREIGN KEY
- question: TEXT NOT NULL
- answer: TEXT NOT NULL
- keywords: TEXT (comma-separated)
- created_at: DATETIME
```

### Lead
```
- id: INTEGER PRIMARY KEY
- product_id: INTEGER FOREIGN KEY
- platform: TEXT
- username: TEXT
- display_name: TEXT
- bio: TEXT
- followers: INTEGER
- relevance_score: REAL
- tags: TEXT (comma-separated)
- status: TEXT (new, engaged, converted, ignored)
- created_at: DATETIME
```

### PlatformCredential
```
- id: INTEGER PRIMARY KEY
- platform: TEXT
- username: TEXT
- password_encrypted: TEXT
- cookies_json: TEXT
- is_active: BOOLEAN
- last_validated: DATETIME
```

### ActivityLog
```
- id: INTEGER PRIMARY KEY
- product_id: INTEGER FOREIGN KEY
- action: TEXT
- platform: TEXT
- details: TEXT
- timestamp: DATETIME
```

---

## UI/UX Specification

### Layout Structure
- **Single page application** with sidebar navigation
- **Sidebar:** 200px wide, dark theme, contains nav items
- **Main content:** Fluid width, light theme
- **Header:** 60px, contains current section title + user actions

### Color Palette
| Role | Color | Hex |
|------|-------|-----|
| Primary | Deep Purple | #6366F1 |
| Secondary | Slate | #475569 |
| Accent | Emerald | #10B981 |
| Background | White | #FFFFFF |
| Surface | Gray 50 | #F8FAFC |
| Text Primary | Gray 900 | #0F172A |
| Text Secondary | Gray 500 | #64748B |
| Error | Red | #EF4444 |
| Success | Green | #22C55E |

### Typography
- **Font Family:** Inter (via Google Fonts)
- **Headings:** 24px (h1), 20px (h2), 16px (h3)
- **Body:** 14px
- **Small:** 12px

### Components

#### Navigation Sidebar
- Logo/Brand at top
- Nav items: Dashboard, Products, Posts, FAQs, Leads, Settings
- Active state: highlighted background (#EEF2FF), primary color text

#### Product Card
- White background, rounded corners (8px)
- Product name in bold
- Description truncated to 2 lines
- Edit/Delete actions on hover

#### Post Editor
- Textarea for content (auto-expand)
- Platform selector (checkboxes)
- Date/time picker
- Generate AI button
- Save as Draft / Schedule buttons

#### Calendar View
- Monthly grid layout
- Posts shown as colored dots
- Click to see post details
- Different colors per platform

#### FAQ List
- Accordion style (expand/collapse)
- Question in bold
- Answer below when expanded
- Edit/Delete buttons

#### Lead Card
- Username and display name
- Platform icon
- Follower count
- Relevance score badge
- Action buttons: View, Engage, Ignore

---

## Acceptance Criteria Checklist

### Core Functionality
- [ ] Application launches with NiceGUI dashboard
- [ ] Can add/edit/delete a product
- [ ] AI generates contextual posts via OpenRouter
- [ ] Posts can be scheduled with date/time
- [ ] FAQ entries can be added and matched
- [ ] Lead discovery returns relevant accounts
- [ ] Platform credentials can be stored

### UI/UX
- [ ] All pages load without errors
- [ ] Navigation works between all sections
- [ ] Forms validate input appropriately
- [ ] Loading states shown during async operations
- [ ] Error messages displayed clearly

### Data Persistence
- [ ] All data persists after app restart
- [ ] Database created automatically on first run

### Error Handling
- [ ] Network errors handled gracefully
- [ ] Invalid credentials show clear error
- [ ] Failed posts can be retried

---

## Non-Functional Requirements

### Performance
- Dashboard loads in < 2 seconds
- AI generation completes in < 30 seconds
- Platform operations complete in < 60 seconds

### Security
- Credentials encrypted at rest
- No sensitive data logged
- API keys stored in environment variables

### Maintainability
- Modular architecture for easy extension
- Clear separation of concerns
- Comprehensive logging

---

## Out of Scope (Phase 1)

- Actual posting to live platforms (browser automation stubs only)
- Multiple simultaneous accounts per platform
- Image/video content generation
- Analytics dashboards
- User authentication (local use only)
- Cloud deployment

---

## Implementation Phases

### Phase 1: Foundation
- Project setup with pyproject.toml
- Database models and migrations
- Basic NiceGUI layout
- Product CRUD

### Phase 2: AI Integration
- OpenRouter client implementation
- Content generator service
- FAQ matcher service

### Phase 3: Scheduling
- Post scheduler service
- Calendar UI
- Queue management

### Phase 4: Platform Stubs
- Platform adapter interface
- Playwright setup
- Credential storage

### Phase 5: Discovery & Engagement
- Lead discovery service
- Engagement handler stubs
- Activity logging
