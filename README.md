# Hextant-AI

A FastAPI backend for AI-powered conversation platform with LLM integration, user management, and subscription-based billing.

## Overview

Hextant-AI is a domain-driven backend service designed to support an AI chat/conversation platform. It provides user authentication, conversation management, MulTI LLMs model integration, memory systems, and a complete subscription billing infrastructure.

## Features

### Implemented

- **Authentication** - JWT-based OAuth2 password flow with session tracking
  - Login, logout, and token refresh endpoints
  - Device/session tracking with user-agent parsing
  - Token revocation via Redis
  - HttpOnly cookie for refresh tokens
  - Rate limiting on sensitive endpoints

- **User Management** - User model with role-based access (admin/user)

- **Conversations** - Chat conversation management
  - Create, list, update, and delete conversations
  - User-scoped conversation queries
  - Auto-title support

### In Progress (Models Defined)

- **Messages** - Message storage with support for text, image, and research types
- **Memories** - Long-term memory extraction from conversations
- **Artifacts** - AI-generated files (images, code, documents)
- **LLM Models** - Language model configuration and pricing
- **Billing** - Complete subscription infrastructure:
  - Tiers - Subscription tiers with usage limits
  - Orders - Payment processing
  - Coupons - Discount codes
  - Quotas - Usage tracking and limits

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Cache | Redis |
| Authentication | JWT (python-jose) |
| LLM Integration | OpenRouter API (pydantic-ai)|
| Rate Limiting | SlowAPI |
| Cloud Storage | AWS S3 (boto3) |

## Project Structure

```
app/
├── core/                  # Core infrastructure
│   ├── config.py          # Settings management (Pydantic)
│   ├── database.py        # SQLAlchemy setup
│   ├── deps.py            # Dependency injection
│   ├── limiter.py         # Rate limiting setup
│   ├── logging.py         # Logging configuration
│   ├── oauth2.py          # JWT token handling
│   └── tokens.py          # Token revocation (Redis)
│
├── domains/               # Business domains (DDD)
│   ├── auth/              # Authentication (COMPLETE)
│   ├── users/             # User management
│   ├── conversations/     # Chat conversations
│   ├── messages/          # Messages in conversations
│   ├── memories/          # Extracted memories
│   ├── artifacts/         # AI-generated files
│   ├── llm_models/        # LLM configuration
│   ├── subscriptions/     # User subscriptions
│   ├── tiers/             # Subscription tiers
│   ├── orders/            # Payment orders
│   ├── coupons/           # Discount codes
│   └── quotas/            # Usage quotas
│
├── shared/                # Shared utilities
│   ├── enums.py           # Common enumerations
│   └── schemas.py         # Shared Pydantic schemas
│
└── utils/                 # Helper functions
    ├── create_admin.py    # Admin user creation
    └── password.py        # Password hashing
```

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 6+

## Environment Setup

Create a `.env` file in the project root:

```env
# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hextant

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
SECURE_COOKIES=false

# External APIs
OPENROUTER_API_KEY=your_openrouter_key
```

## Running

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Run production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Reference

### Authentication

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/auth/login` | OAuth2 password flow login | 1/sec |
| POST | `/auth/logout` | Revoke current session | 1/sec |
| POST | `/auth/refresh` | Refresh access token | None |

### Users

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| GET | `/users/` | List users | TBD |
| GET | `/users/{id}` | Get user by ID | TBD |
| POST | `/users/` | Create user | TBD |

### Conversations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/conversations/` | Create new conversation | Yes |
| GET | `/conversations/` | List user's conversations | Yes |
| GET | `/conversations/{id}` | Get conversation details | Yes |
| PATCH | `/conversations/{id}` | Update conversation title | Yes |
| DELETE | `/conversations/{id}` | Delete conversation | Yes |

## Domain Models

### Relationships

```
User
├── auth_sessions[]      # Login sessions
├── conversations[]      # Chat conversations
├── artifacts[]          # AI-generated files
├── subscriptions[]      # Subscription history
├── orders[]             # Payment history
└── quotas[]             # Usage quotas

Conversation
├── user                 # Owner
└── messages[]           # Chat messages

Message
├── conversation         # Parent conversation
├── memories[]           # Extracted memories
└── artifacts[]          # AI-generated files
```

## License

Business Source License 1.1 - See [LICENSE.md](LICENSE.md) for details.

- Free to use for non-competing purposes
- Converts to Apache 2.0 after 4 years
- Commercial license required for competitive use

## Contact

For commercial licensing inquiries:

- GitHub: [SlackOps01](https://github.com/SlackOps01)
- Email: o-sholarin@hextantlabs.com