# Hextant-AI Roadmap

This document outlines the development roadmap for Hextant-AI backend, including completed features, current priorities, and planned functionality.

---

## Milestones Overview

| Milestone | Name | Status | Priority |
|-----------|------|--------|----------|
| M0 | Foundation | COMPLETE | - |
| M1 | Core Chat | IN PROGRESS | High |
| M2 | Memory System | PLANNED | High |
| M3 | Artifact Generation | PLANNED | Medium |
| M4 | Billing & Quotas | PLANNED | Medium |
| M5 | Admin & Polish | PLANNED | Low |

---

## M0: Foundation

**Status:** COMPLETE

Core infrastructure and authentication system.

### Completed

- [x] Project structure (domain-driven architecture)
- [x] FastAPI application setup with lifespan management
- [x] PostgreSQL database integration (SQLAlchemy)
- [x] Redis caching layer
- [x] Configuration management (Pydantic Settings)
- [x] Logging setup (Rich handler)
- [x] Rate limiting (SlowAPI)
- [x] JWT authentication with OAuth2 password flow
- [x] Token refresh mechanism
- [x] Session tracking with device metadata
- [x] Token revocation via Redis
- [x] Admin user seeding

---

## M1: Core Chat

**Status:** IN PROGRESS
**Priority:** High

Enable basic conversation functionality with LLM integration.

### Conversations Domain

#### Routes (`routes.py`)

- [x] `GET /conversations` - List user's conversations
- [x] `POST /conversations` - Create new conversation
- [ ] `GET /conversations/{id}` - Get conversation details
- [x] `PATCH /conversations/{id}` - Update conversation (title) *(service only, route pending)*
- [x] `DELETE /conversations/{id}` - Delete conversation

#### Service (`service.py`)

- [x] `ConversationService.create()` - Create conversation
- [x] `ConversationService.list_conversations()` - User-scoped queries
- [x] `ConversationService.update()` - Title updates
- [x] `ConversationService.delete()` - Delete conversation

#### Schemas (`schemas.py`)

- [x] `ConversationResponse` - Response schema
- [x] `ConversationUpdate` - Request schema

### Messages Domain

#### Routes (`routes.py`)

- [ ] `GET /conversations/{id}/messages` - List messages (paginated)
- [ ] `POST /conversations/{id}/messages` - Create message
- [ ] `GET /messages/{id}` - Get single message

#### Service (`service.py`)

- [ ] `MessageService.create()` - Create and process
- [ ] `MessageService.get_conversation_messages()` - Ordered list
- [ ] `MessageService.stream_response()` - Stream LLM response

#### Schemas (`schemas.py`)

- [ ] `MessageCreate` - Request schema
- [ ] `MessageResponse` - Response schema
- [ ] `MessageList` - Paginated response

### LLM Integration

- [ ] OpenRouter client wrapper
- [ ] Model selection by tier/quota
- [ ] Streaming response support
- [ ] Token counting for quotas
- [ ] Error handling and retries

---

## M2: Memory System

**Status:** PLANNED
**Priority:** High

Long-term memory extraction and retrieval for contextual conversations.

### Memories Domain

#### Routes (`routes.py`)

- [ ] `GET /memories` - List user's memories (filterable)
- [ ] `GET /conversations/{id}/memories` - Conversation memories
- [ ] `POST /memories` - Create manual memory
- [ ] `DELETE /memories/{id}` - Delete memory

#### Service (`service.py`)

- [ ] `MemoryService.extract()` - Extract memories from message using LLM
- [ ] `MemoryService.get_relevant()` - Retrieve relevant memories for context
- [ ] `MemoryService.categorize()` - Auto-categorize (FACT/PREFERENCE/EXPERIENCE)

#### Schemas (`schemas.py`)

- [ ] `MemoryCreate` - Request schema
- [ ] `MemoryResponse` - Response schema
- [ ] `MemoryList` - Paginated response

### Context Integration

- [ ] Memory injection into LLM prompts
- [ ] Priority weighting for memories
- [ ] Memory deduplication

---

## M3: Artifact Generation

**Status:** PLANNED
**Priority:** Medium

AI-generated content storage and retrieval system.

### Artifacts Domain

#### Routes (`routes.py`)

- [ ] `GET /artifacts/{id}` - Get artifact metadata
- [ ] `GET /artifacts/{id}/download` - Download artifact
- [ ] `DELETE /artifacts/{id}` - Delete artifact

#### Service (`service.py`)

- [ ] `ArtifactService.create()` - Create from LLM response
- [ ] `ArtifactService.get_presigned_url()` - Generate download URL
- [ ] `ArtifactService.delete()` - Remove from S3 and DB

#### Schemas (`schemas.py`)

- [ ] `ArtifactCreate` - Request schema
- [ ] `ArtifactResponse` - Response schema

### Generation Integration

- [ ] S3 bucket configuration
- [ ] Artifact creation from LLM responses
- [ ] Content type handling (code, image, document)
- [ ] Size limit enforcement

---

## M4: Billing & Quotas

**Status:** PLANNED
**Priority:** Medium

Complete subscription and usage management system.

### Tiers Domain

#### Routes (`routes.py`)

- [ ] `GET /tiers` - List available tiers
- [ ] `GET /tiers/{id}` - Get tier details

#### Service (`service.py`)

- [ ] `TierService.list_active()` - Get active tiers

#### Schemas (`schemas.py`)

- [ ] `TierResponse` - Response schema

### Subscriptions Domain

#### Routes (`routes.py`)

- [ ] `GET /subscriptions` - Get user's subscription
- [ ] `POST /subscriptions` - Create subscription (after payment)
- [ ] `DELETE /subscriptions` - Cancel subscription

#### Service (`service.py`)

- [ ] `SubscriptionService.create()` - Create after order
- [ ] `SubscriptionService.cancel()` - Cancel subscription
- [ ] `SubscriptionService.check_expired()` - Check expiration

#### Schemas (`schemas.py`)

- [ ] `SubscriptionCreate` - Request schema
- [ ] `SubscriptionResponse` - Response schema

### Orders Domain

#### Routes (`routes.py`)

- [ ] `POST /orders` - Create order (initiate payment)
- [ ] `POST /orders/webhook` - Payment webhook (Paystack)
- [ ] `GET /orders/{reference}` - Get order status

#### Service (`service.py`)

- [ ] `OrderService.create()` - Create pending order
- [ ] `OrderService.confirm_payment()` - Process webhook
- [ ] `OrderService.apply_coupon()` - Apply discount

#### Schemas (`schemas.py`)

- [ ] `OrderCreate` - Request schema
- [ ] `OrderResponse` - Response schema

### Coupons Domain

#### Routes (`routes.py`)

- [ ] `POST /coupons` - Create coupon (admin)
- [ ] `GET /coupons/{code}/validate` - Validate coupon
- [ ] `DELETE /coupons/{id}` - Delete coupon (admin)

#### Service (`service.py`)

- [ ] `CouponService.validate()` - Check validity
- [ ] `CouponService.redeem()` - Apply redemption

#### Schemas (`schemas.py`)

- [ ] `CouponCreate` - Request schema
- [ ] `CouponValidate` - Request schema

### Quotas Domain

#### Routes (`routes.py`)

- [ ] `GET /quotas` - Get user's current quotas
- [ ] `GET /quotas/usage` - Get usage summary

#### Service (`service.py`)

- [ ] `QuotaService.check_limit()` - Check if action allowed
- [ ] `QuotaService.increment()` - Increment usage
- [ ] `QuotaService.reset()` - Reset on period end

#### Schemas (`schemas.py`)

- [ ] `QuotaResponse` - Response schema
- [ ] `UsageResponse` - Usage summary

---

## M5: Admin & Polish

**Status:** PLANNED
**Priority:** Low

Administrative endpoints, validation, logging, and testing.

### Admin Endpoints

- [ ] `GET /admin/users` - List all users
- [ ] `PATCH /admin/users/{id}` - Update user role
- [ ] `DELETE /admin/users/{id}` - Deactivate user
- [ ] `GET /admin/orders` - List all orders
- [ ] `GET /admin/subscriptions` - List all subscriptions
- [ ] `POST /admin/models` - Add LLM model
- [ ] `PUT /admin/models/{id}` - Update model pricing

### Input Validation

- [ ] Request schema validation
- [ ] Custom validators (email, password strength)
- [ ] Error response standardization

### Logging & Monitoring

- [ ] Request ID tracking
- [ ] Structured logging
- [ ] Error tracking integration (Sentry)

### Testing

- [x] Unit tests setup (pytest, pytest-mock, pytest-asyncio)
- [x] Auth service tests
- [x] Auth route tests
- [x] User service tests
- [x] User route tests
- [ ] Conversation tests
- [ ] Integration tests
- [ ] API tests (TestClient)
- [ ] Coverage reporting

### Documentation

- [ ] OpenAPI schema completion
- [ ] API examples and descriptions
- [ ] Error code documentation

---

## Future Considerations

### Potential Features

- **Team/Organization Support** - Multi-user collaboration
- **API Keys** - Machine-to-machine authentication
- **Webhooks** - Event notifications for external systems
- **Analytics** - Usage analytics dashboard
- **Rate Limits by Tier** - Different limits per subscription

### Scalability Improvements

- Database read replicas
- Caching strategies (Redis caching layer)
- Background task queue (Celery/RQ)
- WebSocket for real-time updates

---

## Contributing

See individual milestone tasks for contribution opportunities. Each task can be claimed by opening an issue or pull request.

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | TBD | M0 Foundation complete, M1 partially complete (conversations CRUD) |