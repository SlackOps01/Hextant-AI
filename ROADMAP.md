# Hextant-AI Roadmap

This document outlines the development roadmap for Hextant-AI backend, including completed features, current priorities, and planned functionality.

---

## Milestones Overview

| Milestone | Name | Status | Priority |
|-----------|------|--------|----------|
| M0 | Foundation | COMPLETE | - |
| M1 | Core Chat | COMPLETE | High |
| M2 | Memory System | PLANNED | High |
| M3 | Artifact Generation | PLANNED | Medium |
| M4 | Billing & Quotas | IN PROGRESS | Medium |
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

**Status:** COMPLETE
**Priority:** High

Enable basic conversation functionality with LLM integration.

### Conversations Domain

#### Routes (`routes.py`)

- [x] `GET /conversations` - List user's conversations
- [x] `POST /conversations` - Create new conversation
- [x] `DELETE /conversations/{id}` - Delete conversation

#### Service (`service.py`)

- [x] `ConversationService.create()` - Create conversation
- [x] `ConversationService.list_conversations()` - User-scoped queries
- [x] `ConversationService.delete()` - Delete conversation

#### Schemas (`schemas.py`)

- [x] `ConversationResponse` - Response schema
- [x] `ConversationCreate` - Request schema

#### Tests

- [x] Conversation service tests
- [x] Conversation route tests

### Messages Domain

#### Routes (`routes.py`)

- [x] `GET /messages/{conversation_id}` - List messages
- [x] `POST /messages/{conversation_id}` - Create message

#### Service (`service.py`)

- [x] `MessageService.generate_response()` - Create message with LLM response
- [x] `MessageService.list_messages()` - Ordered list

#### Schemas (`schemas.py`)

- [x] `MessageCreate` - Request schema
- [x] `MessageResponse` - Response schema

### LLM Integration

- [x] OpenRouter client wrapper (pydantic-ai)
- [x] Model selection by model_id
- [x] Message history context (last 30 messages)
- [x] Multimodal support (images, audio, video, documents)
- [x] Tavily search tool integration
- [x] Error handling

### Language Models Domain

#### Routes (`routes.py`)

- [x] `POST /llm-models/` - Add language model (admin)
- [x] `GET /llm-models/` - List all models
- [x] `PATCH /llm-models/{id}` - Update model (admin)
- [x] `DELETE /llm-models/{id}` - Delete model (admin)

#### Service (`service.py`)

- [x] `LanguageModelService.add_language_model()` - Create model
- [x] `LanguageModelService.list_language_models()` - List models
- [x] `LanguageModelService.update_language_model()` - Update model
- [x] `LanguageModelService.delete_language_model()` - Delete model

#### Tests

- [x] LLM model service tests
- [x] LLM model route tests

### Attachments Domain

#### Routes (`routes.py`)

- [x] `POST /attachments/` - Upload file
- [x] `GET /attachments/` - List user's attachments
- [x] `GET /attachments/{id}/download` - Get presigned download URL

#### Service (`service.py`)

- [x] `AttachmentService.upload_file()` - Upload to S3
- [x] `AttachmentService.generate_download_url()` - Generate URL
- [x] `AttachmentService.list_attachments()` - User-scoped listing

### Tiers Domain

#### Routes (`routes.py`)

- [x] `POST /tiers/` - Create tier (admin)
- [x] `GET /tiers/` - List all tiers
- [x] `GET /tiers/{id}` - Get tier by ID
- [x] `PATCH /tiers/{id}` - Update tier (admin)
- [x] `DELETE /tiers/{id}` - Delete tier (admin)

#### Service (`service.py`)

- [x] `TierService.create_tier()` - Create tier
- [x] `TierService.list_tiers()` - List active tiers
- [x] `TierService.get_tier_by_id()` - Get tier details
- [x] `TierService.update_tier()` - Update tier
- [x] `TierService.delete_tier()` - Delete tier

#### Tests

- [x] Tier service tests
- [x] Tier route tests

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

**Status:** IN PROGRESS
**Priority:** Medium

Complete subscription and usage management system.

### Tiers Domain

**Status:** COMPLETE

See M1 for completed tier implementation.

### Subscriptions Domain

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
- [x] Conversation service tests
- [x] Conversation route tests
- [x] LLM model service tests
- [x] LLM model route tests
- [x] Tier service tests
- [x] Tier route tests
- [ ] Messages tests
- [ ] Attachments tests
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
| 0.2.0 | TBD | M1 Core Chat complete - messages, LLM integration, attachments, tiers |