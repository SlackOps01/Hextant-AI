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
  - Registration, list, get by ID/email/username, delete

- **Conversations** - Chat conversation management
  - Create, list, and delete conversations
  - User-scoped conversation queries
  - Protected routes with authentication

- **Messages** - AI-powered messaging with LLM integration
  - Create and list messages per conversation
  - OpenRouter API integration via pydantic-ai
  - Multimodal support (text, images, audio, video, documents)
  - Tavily search tool integration
  - Message history context window (last 30 messages)

- **LLM Models** - Language model configuration (admin)
  - Add, list, update, delete language models
  - Model API identifier and metadata management

- **Tiers** - Subscription tier management
  - Create, list, get, update, delete tiers
  - Admin-protected write operations

- **Attachments** - File upload and storage
  - Upload files to S3
  - Presigned URL generation for downloads
  - User-scoped attachment listing

### Models Defined (Routes Pending)

- **Memories** - Long-term memory extraction from conversations
- **Artifacts** - AI-generated files (images, code, documents)
- **Billing** - Complete subscription infrastructure:
  - Subscriptions - User subscription management
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

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app
```

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
│   ├── attachments/       # File attachments
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
├── utils/                 # Helper functions
│   ├── create_admin.py    # Admin user creation
│   └── password.py        # Password hashing
│
└── tests/
    └── unit/              # Unit tests by domain
```

## API Reference

### Authentication

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/auth/login` | OAuth2 password flow login | 1/sec |
| POST | `/auth/logout` | Revoke current session | 1/sec |
| POST | `/auth/refresh` | Refresh access token | None |

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users/register` | Register new user | None |
| GET | `/users/` | List users | Admin |
| GET | `/users/{id}` | Get user by ID | Owner/Admin |
| GET | `/users/email/{email}` | Get user by email | Admin |
| GET | `/users/username/{username}` | Get user by username | Admin |
| DELETE | `/users/{id}` | Delete user | Owner/Admin |

### Conversations

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/conversations/` | Create new conversation | 20/min |
| GET | `/conversations/` | List user's conversations | 60/min |
| DELETE | `/conversations/{id}` | Delete conversation | 5/hour |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/messages/{conversation_id}` | Create message with LLM response |
| GET | `/messages/{conversation_id}` | List conversation messages |

### LLM Models (Admin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/llm-models/` | Add language model |
| GET | `/llm-models/` | List all models |
| PATCH | `/llm-models/{id}` | Update model |
| DELETE | `/llm-models/{id}` | Delete model |

### Tiers

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/tiers/` | Create tier | Admin |
| GET | `/tiers/` | List all tiers | None |
| GET | `/tiers/{id}` | Get tier details | None |
| PATCH | `/tiers/{id}` | Update tier | Admin |
| DELETE | `/tiers/{id}` | Delete tier | Admin |

### Attachments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/attachments/` | Upload file |
| GET | `/attachments/` | List user's attachments |
| GET | `/attachments/{id}/download` | Get download URL |

## Domain Models

### Relationships

```
User
├── auth_sessions[]      # Login sessions
├── conversations[]      # Chat conversations
├── artifacts[]          # AI-generated files
├── attachments[]        # File attachments
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