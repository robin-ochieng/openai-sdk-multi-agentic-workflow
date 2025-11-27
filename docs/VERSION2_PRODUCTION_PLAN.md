# Deep Research Agent v2.0 - Production-Ready Enhancement Plan

> **Target:** State-of-the-art AI Research Platform with Monetization
> **Branch:** `version2-enhancements`
> **Timeline:** 6-8 weeks for full implementation

---

## 📋 Executive Summary

Transform the Deep Research Agent from a prototype into a production-grade SaaS platform with:
- Enterprise-level authentication and security
- Scalable architecture supporting 10,000+ concurrent users
- Multiple monetization streams (subscriptions, API access, credits)
- Premium features that justify paid tiers

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Auth UI   │  │  Research   │  │  Dashboard  │  │   Billing   │   │
│  │  (Supabase) │  │   Console   │  │  & History  │  │  (Stripe)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │    Auth     │  │    Rate     │  │   Usage     │  │   Webhook   │   │
│  │ Middleware  │  │  Limiter    │  │  Tracker    │  │  Handlers   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CORE SERVICES LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Research   │  │   Export    │  │   Email     │  │  Scheduler  │   │
│  │   Engine    │  │   Service   │  │   Service   │  │   Service   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA & INFRASTRUCTURE                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Supabase   │  │   Redis     │  │   Celery    │  │  LangSmith  │   │
│  │  (Postgres) │  │   Cache     │  │   Queue     │  │   Tracing   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📅 Implementation Phases

### **Phase 1: Foundation (Week 1-2)**
Core infrastructure and authentication

### **Phase 2: Core Features (Week 3-4)**
Usage tracking, rate limiting, premium features

### **Phase 3: Monetization (Week 5-6)**
Stripe integration, subscription management

### **Phase 4: Polish & Launch (Week 7-8)**
Testing, optimization, deployment

---

## 🔐 Phase 1: Foundation

### 1.1 Authentication System (Supabase Auth)

**Files to Create/Modify:**
```
deep_research/
├── auth/
│   ├── __init__.py
│   ├── supabase_auth.py      # Auth service wrapper
│   ├── middleware.py          # FastAPI auth middleware
│   ├── dependencies.py        # Dependency injection
│   └── models.py              # User models
├── frontend/
│   ├── lib/
│   │   └── auth.ts           # Auth utilities
│   ├── components/
│   │   └── auth/
│   │       ├── LoginForm.tsx
│   │       ├── SignupForm.tsx
│   │       ├── AuthProvider.tsx
│   │       └── ProtectedRoute.tsx
│   └── app/
│       ├── login/page.tsx
│       ├── signup/page.tsx
│       └── dashboard/page.tsx
```

**Database Schema (Supabase):**
```sql
-- User profiles (extends Supabase auth.users)
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    subscription_status TEXT DEFAULT 'active',
    stripe_customer_id TEXT UNIQUE,
    api_key TEXT UNIQUE DEFAULT generate_api_key(),
    credits_balance INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys for programmatic access
CREATE TABLE public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    key_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);
```

**Implementation Checklist:**
- [ ] Set up Supabase Auth with email/password
- [ ] Add Google OAuth provider
- [ ] Create user profile on signup (database trigger)
- [ ] Implement JWT validation middleware in FastAPI
- [ ] Create protected API endpoints
- [ ] Build login/signup UI components
- [ ] Add session management in Next.js
- [ ] Implement API key generation for developers

---

### 1.2 Database Schema Enhancement

**Files to Create/Modify:**
```
deep_research/
├── supabase/
│   ├── schema.sql            # Updated full schema
│   ├── migrations/
│   │   ├── 001_user_profiles.sql
│   │   ├── 002_research_sessions.sql
│   │   ├── 003_usage_tracking.sql
│   │   ├── 004_subscriptions.sql
│   │   └── 005_scheduled_research.sql
│   └── seed.sql              # Test data
```

**Enhanced Research Sessions Schema:**
```sql
-- Research sessions with full metadata
CREATE TABLE public.research_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    research_depth TEXT DEFAULT 'standard' CHECK (research_depth IN ('quick', 'standard', 'deep', 'comprehensive')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')),
    
    -- Results
    report_markdown TEXT,
    report_html TEXT,
    sources JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    
    -- Usage tracking
    tokens_used INTEGER DEFAULT 0,
    search_queries_count INTEGER DEFAULT 0,
    execution_time_seconds NUMERIC(10,2),
    credits_consumed INTEGER DEFAULT 1,
    
    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Indexing
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', query || ' ' || COALESCE(report_markdown, ''))) STORED
);

CREATE INDEX idx_research_sessions_user ON public.research_sessions(user_id);
CREATE INDEX idx_research_sessions_status ON public.research_sessions(status);
CREATE INDEX idx_research_sessions_search ON public.research_sessions USING GIN(search_vector);
```

---

### 1.3 API Structure Refactoring

**New API Structure:**
```
deep_research/
├── api/
│   ├── __init__.py
│   ├── main.py               # FastAPI app factory
│   ├── config.py             # Settings management
│   ├── dependencies.py       # Shared dependencies
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py           # /api/auth/*
│   │   ├── research.py       # /api/research/*
│   │   ├── users.py          # /api/users/*
│   │   ├── billing.py        # /api/billing/*
│   │   ├── admin.py          # /api/admin/*
│   │   └── webhooks.py       # /api/webhooks/*
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication
│   │   ├── rate_limit.py     # Rate limiting
│   │   ├── logging.py        # Request logging
│   │   └── cors.py           # CORS handling
│   └── schemas/
│       ├── __init__.py
│       ├── auth.py
│       ├── research.py
│       ├── users.py
│       └── billing.py
```

**API Endpoints Design:**
```
Authentication:
  POST   /api/auth/login              # Email/password login
  POST   /api/auth/signup             # New user registration
  POST   /api/auth/logout             # Logout
  POST   /api/auth/refresh            # Refresh token
  POST   /api/auth/forgot-password    # Password reset request
  POST   /api/auth/reset-password     # Reset password
  GET    /api/auth/me                 # Current user info

Research:
  POST   /api/research/start          # Start new research
  GET    /api/research/:id            # Get research by ID
  GET    /api/research/:id/stream     # SSE stream for progress
  GET    /api/research/history        # User's research history
  DELETE /api/research/:id            # Delete research
  POST   /api/research/:id/export     # Export to PDF/Word
  POST   /api/research/:id/share      # Generate share link

Users:
  GET    /api/users/profile           # Get profile
  PATCH  /api/users/profile           # Update profile
  GET    /api/users/usage             # Usage statistics
  POST   /api/users/api-keys          # Create API key
  GET    /api/users/api-keys          # List API keys
  DELETE /api/users/api-keys/:id      # Revoke API key

Billing:
  GET    /api/billing/subscription    # Current subscription
  POST   /api/billing/checkout        # Create Stripe checkout
  POST   /api/billing/portal          # Stripe customer portal
  GET    /api/billing/invoices        # Invoice history
  POST   /api/billing/credits         # Purchase credits

Webhooks:
  POST   /api/webhooks/stripe         # Stripe webhook handler
```

---

## ⚡ Phase 2: Core Features

### 2.1 Usage Tracking & Rate Limiting

**Files to Create:**
```
deep_research/
├── services/
│   ├── __init__.py
│   ├── usage_tracker.py      # Track all usage
│   ├── rate_limiter.py       # Redis-based rate limiting
│   └── quota_manager.py      # Manage user quotas
```

**Usage Tracking Schema:**
```sql
CREATE TABLE public.usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id),
    action_type TEXT NOT NULL CHECK (action_type IN (
        'research_started', 'research_completed', 
        'api_call', 'export', 'email_sent'
    )),
    resource_id UUID,
    tokens_used INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily usage aggregates for fast queries
CREATE TABLE public.usage_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id),
    date DATE NOT NULL,
    research_count INTEGER DEFAULT 0,
    api_calls_count INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);

-- Materialized view for billing
CREATE MATERIALIZED VIEW public.monthly_usage AS
SELECT 
    user_id,
    DATE_TRUNC('month', date) as month,
    SUM(research_count) as total_research,
    SUM(api_calls_count) as total_api_calls,
    SUM(tokens_used) as total_tokens,
    SUM(credits_used) as total_credits
FROM public.usage_daily
GROUP BY user_id, DATE_TRUNC('month', date);
```

**Rate Limiting Configuration:**
```python
# Tier-based rate limits
RATE_LIMITS = {
    "free": {
        "research_per_day": 3,
        "research_per_month": 15,
        "api_calls_per_minute": 10,
        "api_calls_per_day": 100,
        "max_research_depth": "standard",
        "concurrent_research": 1,
    },
    "pro": {
        "research_per_day": 20,
        "research_per_month": 200,
        "api_calls_per_minute": 60,
        "api_calls_per_day": 5000,
        "max_research_depth": "deep",
        "concurrent_research": 3,
    },
    "enterprise": {
        "research_per_day": -1,  # Unlimited
        "research_per_month": -1,
        "api_calls_per_minute": 300,
        "api_calls_per_day": -1,
        "max_research_depth": "comprehensive",
        "concurrent_research": 10,
    }
}
```

**Implementation Checklist:**
- [ ] Set up Redis for rate limiting
- [ ] Implement sliding window rate limiter
- [ ] Create usage tracking middleware
- [ ] Build daily aggregation job
- [ ] Add usage dashboard UI
- [ ] Implement quota warnings (80%, 100%)
- [ ] Email notifications for quota limits

---

### 2.2 Background Job Processing (Celery)

**Files to Create:**
```
deep_research/
├── workers/
│   ├── __init__.py
│   ├── celery_app.py         # Celery configuration
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── research.py       # Research tasks
│   │   ├── export.py         # Export tasks
│   │   ├── email.py          # Email tasks
│   │   ├── scheduled.py      # Scheduled research
│   │   └── maintenance.py    # Cleanup tasks
│   └── schedules.py          # Celery Beat schedules
```

**Celery Configuration:**
```python
# workers/celery_app.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "deep_research",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=[
        "workers.tasks.research",
        "workers.tasks.export",
        "workers.tasks.email",
        "workers.tasks.scheduled",
        "workers.tasks.maintenance",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "aggregate-daily-usage": {
        "task": "workers.tasks.maintenance.aggregate_daily_usage",
        "schedule": crontab(hour=0, minute=5),  # 12:05 AM daily
    },
    "refresh-materialized-views": {
        "task": "workers.tasks.maintenance.refresh_views",
        "schedule": crontab(hour=1, minute=0),  # 1:00 AM daily
    },
    "cleanup-old-sessions": {
        "task": "workers.tasks.maintenance.cleanup_old_sessions",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),  # Weekly
    },
    "send-quota-warnings": {
        "task": "workers.tasks.email.send_quota_warnings",
        "schedule": crontab(hour=9, minute=0),  # 9 AM daily
    },
}
```

---

### 2.3 Premium Features

#### 2.3.1 PDF/Word Export Service

**Files to Create:**
```
deep_research/
├── services/
│   ├── export/
│   │   ├── __init__.py
│   │   ├── pdf_generator.py   # PDF export
│   │   ├── docx_generator.py  # Word export
│   │   ├── templates/
│   │   │   ├── report_template.html
│   │   │   └── styles.css
│   │   └── fonts/
```

**Export Service Design:**
```python
# services/export/pdf_generator.py
from weasyprint import HTML, CSS
from jinja2 import Template

class PDFExportService:
    def __init__(self):
        self.template = self._load_template()
    
    async def generate(
        self,
        research_session: ResearchSession,
        options: ExportOptions
    ) -> bytes:
        """Generate PDF from research session."""
        html_content = self._render_html(research_session, options)
        pdf_bytes = HTML(string=html_content).write_pdf(
            stylesheets=[self.css],
            presentational_hints=True
        )
        return pdf_bytes
    
    def _render_html(self, session, options):
        return self.template.render(
            title=session.query,
            content=session.report_html,
            sources=session.sources,
            generated_at=session.completed_at,
            branding=options.include_branding,
            table_of_contents=options.include_toc,
        )
```

#### 2.3.2 Scheduled Research

**Database Schema:**
```sql
CREATE TABLE public.scheduled_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id),
    name TEXT NOT NULL,
    query TEXT NOT NULL,
    research_depth TEXT DEFAULT 'standard',
    
    -- Schedule configuration
    schedule_type TEXT NOT NULL CHECK (schedule_type IN ('once', 'daily', 'weekly', 'monthly')),
    schedule_time TIME NOT NULL,
    schedule_day_of_week INTEGER,  -- 0-6 for weekly
    schedule_day_of_month INTEGER, -- 1-31 for monthly
    timezone TEXT DEFAULT 'UTC',
    
    -- Delivery options
    email_on_completion BOOLEAN DEFAULT true,
    compare_with_previous BOOLEAN DEFAULT false,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    run_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 2.3.3 Research Sharing & Collaboration

**Database Schema:**
```sql
CREATE TABLE public.shared_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_session_id UUID NOT NULL REFERENCES public.research_sessions(id),
    share_token TEXT UNIQUE NOT NULL DEFAULT generate_share_token(),
    
    -- Access control
    access_type TEXT DEFAULT 'view' CHECK (access_type IN ('view', 'comment', 'edit')),
    password_hash TEXT,  -- Optional password protection
    expires_at TIMESTAMPTZ,
    max_views INTEGER,
    view_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_by UUID NOT NULL REFERENCES public.user_profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.research_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_session_id UUID NOT NULL REFERENCES public.research_sessions(id),
    user_id UUID REFERENCES public.user_profiles(id),
    guest_name TEXT,  -- For non-authenticated commenters
    content TEXT NOT NULL,
    parent_comment_id UUID REFERENCES public.research_comments(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 💳 Phase 3: Monetization

### 3.1 Stripe Integration

**Files to Create:**
```
deep_research/
├── billing/
│   ├── __init__.py
│   ├── stripe_service.py     # Stripe API wrapper
│   ├── subscription.py       # Subscription management
│   ├── credits.py            # Credits system
│   ├── webhooks.py           # Webhook handlers
│   └── constants.py          # Pricing, product IDs
```

**Stripe Products Configuration:**
```python
# billing/constants.py

STRIPE_PRODUCTS = {
    "pro_monthly": {
        "price_id": "price_xxx",
        "name": "Pro Monthly",
        "amount": 2900,  # $29.00
        "interval": "month",
        "features": [
            "50 research reports/month",
            "Deep research mode",
            "PDF & Word export",
            "Priority processing",
            "Email delivery",
        ]
    },
    "pro_yearly": {
        "price_id": "price_yyy",
        "name": "Pro Yearly",
        "amount": 29000,  # $290.00 (2 months free)
        "interval": "year",
        "features": [...],
    },
    "enterprise_monthly": {
        "price_id": "price_zzz",
        "name": "Enterprise Monthly",
        "amount": 19900,  # $199.00
        "interval": "month",
        "features": [
            "Unlimited research reports",
            "Comprehensive research mode",
            "API access",
            "Custom integrations",
            "Dedicated support",
            "Team collaboration",
        ]
    }
}

CREDIT_PACKS = {
    "starter": {"credits": 25, "price": 500},    # $5
    "standard": {"credits": 100, "price": 1500}, # $15 (25% bonus)
    "bulk": {"credits": 500, "price": 5000},     # $50 (66% bonus)
}
```

**Stripe Service Implementation:**
```python
# billing/stripe_service.py
import stripe
from typing import Optional

class StripeService:
    def __init__(self, api_key: str):
        stripe.api_key = api_key
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe checkout session."""
        session = stripe.checkout.Session.create(
            customer=await self._get_or_create_customer(user_id),
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user_id},
        )
        return session.url
    
    async def create_customer_portal(self, user_id: str) -> str:
        """Create Stripe customer portal session."""
        customer_id = await self._get_customer_id(user_id)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.FRONTEND_URL}/dashboard/billing",
        )
        return session.url
    
    async def handle_webhook(self, payload: bytes, sig_header: str):
        """Handle Stripe webhook events."""
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
        }
        
        handler = handlers.get(event["type"])
        if handler:
            await handler(event["data"]["object"])
```

### 3.2 Subscription Tiers Implementation

**Database Schema:**
```sql
CREATE TABLE public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES public.user_profiles(id),
    stripe_subscription_id TEXT UNIQUE,
    stripe_price_id TEXT,
    
    tier TEXT NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
        'active', 'past_due', 'canceled', 'incomplete', 'trialing'
    )),
    
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT false,
    canceled_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id),
    amount INTEGER NOT NULL,  -- Positive = credit, Negative = debit
    balance_after INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN (
        'purchase', 'usage', 'refund', 'bonus', 'subscription_reset'
    )),
    description TEXT,
    reference_id UUID,  -- Research session ID, etc.
    stripe_payment_intent_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🎨 Phase 4: Frontend Enhancements

### 4.1 New Pages & Components

**File Structure:**
```
deep_research/frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── forgot-password/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx                    # Dashboard home
│   │   ├── research/
│   │   │   ├── page.tsx                # New research
│   │   │   ├── [id]/page.tsx           # View research
│   │   │   └── history/page.tsx        # Research history
│   │   ├── billing/
│   │   │   ├── page.tsx                # Subscription & credits
│   │   │   └── invoices/page.tsx
│   │   ├── settings/
│   │   │   ├── page.tsx                # Profile settings
│   │   │   └── api-keys/page.tsx       # API key management
│   │   └── scheduled/
│   │       └── page.tsx                # Scheduled research
│   ├── (public)/
│   │   ├── page.tsx                    # Landing page
│   │   ├── pricing/page.tsx
│   │   └── share/[token]/page.tsx      # Shared research view
│   └── api/
│       └── [...proxy]/route.ts         # API proxy
├── components/
│   ├── auth/
│   │   ├── AuthProvider.tsx
│   │   ├── LoginForm.tsx
│   │   ├── SignupForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── billing/
│   │   ├── PricingCards.tsx
│   │   ├── SubscriptionStatus.tsx
│   │   ├── CreditBalance.tsx
│   │   └── UsageChart.tsx
│   ├── research/
│   │   ├── ResearchForm.tsx
│   │   ├── ResearchProgress.tsx
│   │   ├── ResearchReport.tsx
│   │   ├── ResearchHistory.tsx
│   │   ├── ExportButton.tsx
│   │   └── ShareDialog.tsx
│   ├── dashboard/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── StatsCards.tsx
│   │   └── RecentActivity.tsx
│   └── ui/
│       └── [...existing shadcn components]
├── lib/
│   ├── auth.ts                         # Auth utilities
│   ├── api.ts                          # API client
│   ├── stripe.ts                       # Stripe utilities
│   └── hooks/
│       ├── useAuth.ts
│       ├── useSubscription.ts
│       ├── useUsage.ts
│       └── useResearch.ts
```

### 4.2 Key UI Components

**Pricing Cards Component:**
```tsx
// components/billing/PricingCards.tsx
const tiers = [
  {
    name: "Free",
    price: 0,
    features: [
      "3 research reports/month",
      "Standard depth",
      "Basic export",
    ],
    cta: "Get Started",
    popular: false,
  },
  {
    name: "Pro",
    price: 29,
    features: [
      "50 research reports/month",
      "Deep research mode",
      "PDF & Word export",
      "Priority processing",
      "Email delivery",
      "Research history",
    ],
    cta: "Upgrade to Pro",
    popular: true,
  },
  {
    name: "Enterprise",
    price: 199,
    features: [
      "Unlimited reports",
      "Comprehensive research",
      "API access",
      "Scheduled research",
      "Team collaboration",
      "Custom integrations",
      "Dedicated support",
    ],
    cta: "Contact Sales",
    popular: false,
  },
];
```

---

## 🔒 Security Checklist

### Authentication & Authorization
- [ ] Implement proper password hashing (Supabase handles this)
- [ ] Add rate limiting on auth endpoints
- [ ] Implement account lockout after failed attempts
- [ ] Add 2FA support (optional, for enterprise)
- [ ] Secure session management

### API Security
- [ ] Validate all inputs (Pydantic schemas)
- [ ] Implement request signing for webhooks
- [ ] Add API key hashing (never store plain text)
- [ ] CORS configuration
- [ ] HTTPS enforcement

### Data Protection
- [ ] Encrypt sensitive data at rest
- [ ] Implement data retention policies
- [ ] Add GDPR compliance features (data export, deletion)
- [ ] Audit logging for sensitive operations

### Prompt Security
- [ ] Input sanitization to prevent prompt injection
- [ ] Content moderation on outputs
- [ ] Rate limit on token usage

---

## 📊 Monitoring & Observability

### Logging Strategy
```python
# Structured logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        }
    },
    "loggers": {
        "deep_research": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
        "uvicorn": {
            "level": "WARNING",
        }
    }
}
```

### Metrics to Track
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Research completion time
- Token usage per request
- Active users (DAU, MAU)
- Conversion rates (free → paid)
- Revenue metrics (MRR, churn)

### Health Checks
```python
# api/routers/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "checks": {
            "database": await check_database(),
            "redis": await check_redis(),
            "openai": await check_openai(),
        }
    }
```

---

## 🚀 Deployment Architecture

### Production Stack
```
┌─────────────────────────────────────────────────────────────────┐
│                         Cloudflare CDN                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
┌───────────────────────────┐   ┌───────────────────────────────┐
│      Vercel (Frontend)     │   │      Railway/Render (API)     │
│       Next.js App          │   │         FastAPI               │
└───────────────────────────┘   └───────────────────────────────┘
                                                │
                ┌───────────────┬───────────────┼───────────────┐
                ▼               ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │  Supabase   │ │   Upstash   │ │   Celery    │ │  LangSmith  │
        │  (Postgres) │ │   (Redis)   │ │  Workers    │ │  (Tracing)  │
        └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### Environment Variables
```bash
# .env.production
# App
APP_ENV=production
APP_URL=https://deepresearch.ai
API_URL=https://api.deepresearch.ai

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx

# Redis (Upstash)
REDIS_URL=redis://xxx

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx

# OpenAI
OPENAI_API_KEY=sk-xxx

# LangSmith
LANGCHAIN_API_KEY=xxx
LANGCHAIN_PROJECT=deep-research-prod

# Sentry
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## 📝 Implementation Checklist

### Week 1: Authentication Foundation
- [ ] Set up Supabase Auth
- [ ] Create user profiles table and triggers
- [ ] Implement FastAPI auth middleware
- [ ] Build login/signup pages
- [ ] Add protected routes

### Week 2: Database & API Structure
- [ ] Create all database migrations
- [ ] Refactor API into modular routers
- [ ] Implement Pydantic schemas
- [ ] Add request validation
- [ ] Set up API documentation (OpenAPI)

### Week 3: Usage Tracking
- [ ] Set up Redis (Upstash)
- [ ] Implement rate limiter
- [ ] Create usage tracking service
- [ ] Build usage dashboard
- [ ] Add quota warnings

### Week 4: Background Jobs & Premium Features
- [ ] Set up Celery with Redis
- [ ] Implement PDF export
- [ ] Create scheduled research
- [ ] Build sharing functionality
- [ ] Add email delivery service

### Week 5: Stripe Integration
- [ ] Create Stripe products
- [ ] Implement checkout flow
- [ ] Build customer portal integration
- [ ] Set up webhook handlers
- [ ] Implement credit system

### Week 6: Billing UI & Testing
- [ ] Build pricing page
- [ ] Create subscription management UI
- [ ] Add credit purchase flow
- [ ] Write integration tests
- [ ] Load testing

### Week 7: Security & Monitoring
- [ ] Security audit
- [ ] Set up Sentry
- [ ] Add structured logging
- [ ] Create health checks
- [ ] Implement audit logging

### Week 8: Polish & Launch
- [ ] Performance optimization
- [ ] SEO optimization
- [ ] Documentation
- [ ] Marketing site
- [ ] Launch! 🚀

---

## 💰 Revenue Projections

### Pricing Model
| Tier | Monthly | Annual | Target Users |
|------|---------|--------|--------------|
| Free | $0 | $0 | 1000 |
| Pro | $29 | $290 | 200 |
| Enterprise | $199 | $1,990 | 20 |

### Monthly Revenue Potential
- **Pro Users (200):** $5,800/month
- **Enterprise (20):** $3,980/month
- **Credits Sales:** ~$500/month
- **Total MRR:** ~$10,280/month

### Growth Targets
| Month | Users | Paid Users | MRR |
|-------|-------|------------|-----|
| M1 | 500 | 20 | $1,000 |
| M3 | 2,000 | 100 | $4,000 |
| M6 | 5,000 | 300 | $12,000 |
| M12 | 15,000 | 800 | $30,000 |

---

## 🎯 Success Metrics

### Product Metrics
- **Research Quality Score:** User ratings, completion rate
- **Time to Value:** Time from signup to first research
- **Feature Adoption:** % users using premium features

### Business Metrics
- **Conversion Rate:** Free → Paid (target: 5-10%)
- **Churn Rate:** Monthly churn (target: <5%)
- **LTV/CAC Ratio:** Target 3:1
- **Net Revenue Retention:** Target >100%

### Technical Metrics
- **Uptime:** 99.9% SLA
- **API Latency:** p95 < 500ms
- **Research Completion:** p95 < 5 minutes

---

## 📚 Resources & References

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Stripe Integration Guide](https://stripe.com/docs/billing/subscriptions/build-subscriptions)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/advanced/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Next.js App Router](https://nextjs.org/docs/app)

---

> **Next Steps:** Start with Phase 1 - Authentication System. This unlocks all other features and is the foundation for monetization.

*Document Version: 1.0 | Created: November 27, 2025 | Branch: version2-enhancements*
