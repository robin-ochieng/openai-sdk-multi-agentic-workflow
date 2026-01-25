-- ============================================
-- Migration 001: User Profiles and API Keys
-- Deep Research Agent v2.0 - Production Setup
-- ============================================
-- Run this migration in your Supabase SQL Editor
-- This adds user profile management and API key support
-- ============================================

-- ============================================
-- 1. HELPER FUNCTIONS
-- ============================================

-- Function to generate a secure random API key
CREATE OR REPLACE FUNCTION generate_api_key()
RETURNS TEXT AS $$
DECLARE
    key TEXT;
BEGIN
    -- Generate a 32-character random key with prefix
    key := 'drk_' || encode(gen_random_bytes(24), 'base64');
    -- Remove special characters that might cause issues
    key := replace(replace(replace(key, '+', 'x'), '/', 'y'), '=', '');
    RETURN key;
END;
$$ LANGUAGE plpgsql;

-- Function to hash API keys using SHA-256
CREATE OR REPLACE FUNCTION hash_api_key(key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(sha256(key::bytea), 'hex');
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 2. USER PROFILES TABLE
-- Extends Supabase auth.users with app-specific data
-- ============================================

CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    
    -- Subscription & billing
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    subscription_status TEXT DEFAULT 'active' CHECK (subscription_status IN ('active', 'past_due', 'canceled', 'incomplete', 'trialing')),
    stripe_customer_id TEXT UNIQUE,
    
    -- Usage tracking
    credits_balance INTEGER DEFAULT 10,
    daily_research_count INTEGER DEFAULT 0,
    last_research_date DATE,
    
    -- API access
    primary_api_key TEXT UNIQUE,  -- Hashed
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_stripe ON public.user_profiles(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_tier ON public.user_profiles(subscription_tier);

-- Auto-update timestamp trigger
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 3. API KEYS TABLE
-- Multiple API keys per user for programmatic access
-- ============================================

CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    
    -- Key identification
    key_hash TEXT NOT NULL UNIQUE,  -- SHA-256 hash of the actual key
    key_prefix TEXT NOT NULL,       -- First 8 chars for identification (e.g., "drk_abc1")
    name TEXT NOT NULL,             -- User-provided name for the key
    
    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    
    -- Expiration & status
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    
    -- Permissions (for future granular access)
    scopes TEXT[] DEFAULT ARRAY['research:read', 'research:write'],
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON public.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON public.api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON public.api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON public.api_keys(is_active) WHERE is_active = true;

-- ============================================
-- 4. USAGE LOGS TABLE
-- Track all API usage for rate limiting and billing
-- ============================================

CREATE TABLE IF NOT EXISTS public.usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE SET NULL,
    
    -- Action details
    action_type TEXT NOT NULL CHECK (action_type IN (
        'research_started', 'research_completed', 
        'api_call', 'export', 'email_sent'
    )),
    resource_id UUID,  -- e.g., research_run id
    
    -- Usage metrics
    tokens_used INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    api_key_id UUID REFERENCES public.api_keys(id) ON DELETE SET NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for querying usage
CREATE INDEX IF NOT EXISTS idx_usage_logs_user ON public.usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_action ON public.usage_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created ON public.usage_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_date ON public.usage_logs(user_id, created_at);

-- ============================================
-- 5. ROW LEVEL SECURITY POLICIES
-- ============================================

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_logs ENABLE ROW LEVEL SECURITY;

-- User Profiles: Users can only access their own profile
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- API Keys: Users can manage their own keys
CREATE POLICY "Users can view own API keys" ON public.api_keys
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own API keys" ON public.api_keys
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own API keys" ON public.api_keys
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own API keys" ON public.api_keys
    FOR DELETE USING (auth.uid() = user_id);

-- Usage Logs: Users can view their own logs (read-only)
CREATE POLICY "Users can view own usage logs" ON public.usage_logs
    FOR SELECT USING (auth.uid() = user_id);

-- Service role can insert usage logs
CREATE POLICY "Service role can insert usage logs" ON public.usage_logs
    FOR INSERT WITH CHECK (true);  -- Will be restricted via service key only

-- ============================================
-- 6. UPDATE RESEARCH_RUNS RLS POLICIES
-- ============================================

-- Drop existing permissive policies
DROP POLICY IF EXISTS "Allow anonymous access to research_runs" ON research_runs;
DROP POLICY IF EXISTS "Allow anonymous access to research_logs" ON research_logs;
DROP POLICY IF EXISTS "Allow anonymous access to research_evidence" ON research_evidence;

-- New policies: Users can see their own runs + anonymous runs (user_id IS NULL)
CREATE POLICY "Users can view own and anonymous research runs" ON public.research_runs
    FOR SELECT USING (
        user_id IS NULL  -- Anonymous runs are public
        OR auth.uid() = user_id  -- User's own runs
    );

CREATE POLICY "Users can create research runs" ON public.research_runs
    FOR INSERT WITH CHECK (
        user_id IS NULL  -- Anonymous
        OR auth.uid() = user_id  -- Authenticated user
    );

CREATE POLICY "Users can update own research runs" ON public.research_runs
    FOR UPDATE USING (
        user_id IS NULL 
        OR auth.uid() = user_id
    );

CREATE POLICY "Users can delete own research runs" ON public.research_runs
    FOR DELETE USING (auth.uid() = user_id);

-- Research logs follow parent run access
CREATE POLICY "Users can view research logs" ON public.research_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.research_runs r 
            WHERE r.run_id = research_logs.run_id 
            AND (r.user_id IS NULL OR auth.uid() = r.user_id)
        )
    );

CREATE POLICY "Service can insert research logs" ON public.research_logs
    FOR INSERT WITH CHECK (true);

-- Research evidence follows parent run access
CREATE POLICY "Users can view research evidence" ON public.research_evidence
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.research_runs r 
            WHERE r.run_id = research_evidence.run_id 
            AND (r.user_id IS NULL OR auth.uid() = r.user_id)
        )
    );

CREATE POLICY "Service can insert research evidence" ON public.research_evidence
    FOR INSERT WITH CHECK (true);

-- ============================================
-- 7. AUTO-CREATE PROFILE ON SIGNUP
-- Trigger function to create user profile when auth.users row is inserted
-- ============================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger on auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- 8. HELPER FUNCTIONS FOR RATE LIMITING
-- ============================================

-- Function to check and update daily research count
CREATE OR REPLACE FUNCTION check_daily_research_limit(p_user_id UUID, p_tier TEXT)
RETURNS JSONB AS $$
DECLARE
    profile RECORD;
    daily_limit INTEGER;
    can_research BOOLEAN;
BEGIN
    -- Define limits per tier
    daily_limit := CASE p_tier
        WHEN 'free' THEN 2
        WHEN 'pro' THEN 20
        WHEN 'enterprise' THEN -1  -- Unlimited
        ELSE 2
    END;
    
    -- Get current profile
    SELECT * INTO profile FROM public.user_profiles WHERE id = p_user_id;
    
    IF profile IS NULL THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'User not found');
    END IF;
    
    -- Reset counter if new day
    IF profile.last_research_date IS NULL OR profile.last_research_date < CURRENT_DATE THEN
        UPDATE public.user_profiles 
        SET daily_research_count = 0, last_research_date = CURRENT_DATE
        WHERE id = p_user_id;
        profile.daily_research_count := 0;
    END IF;
    
    -- Check limit (-1 = unlimited)
    can_research := daily_limit = -1 OR profile.daily_research_count < daily_limit;
    
    IF can_research THEN
        -- Increment counter
        UPDATE public.user_profiles 
        SET daily_research_count = daily_research_count + 1,
            last_research_date = CURRENT_DATE
        WHERE id = p_user_id;
    END IF;
    
    RETURN jsonb_build_object(
        'allowed', can_research,
        'current_count', profile.daily_research_count,
        'daily_limit', daily_limit,
        'tier', p_tier,
        'reason', CASE WHEN can_research THEN 'OK' ELSE 'Daily limit reached' END
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate API key and get user
CREATE OR REPLACE FUNCTION validate_api_key(p_key TEXT)
RETURNS JSONB AS $$
DECLARE
    key_record RECORD;
    user_record RECORD;
    key_hash TEXT;
BEGIN
    -- Hash the provided key
    key_hash := encode(sha256(p_key::bytea), 'hex');
    
    -- Find the key
    SELECT * INTO key_record 
    FROM public.api_keys 
    WHERE api_keys.key_hash = validate_api_key.key_hash
    AND is_active = true
    AND (expires_at IS NULL OR expires_at > NOW());
    
    IF key_record IS NULL THEN
        RETURN jsonb_build_object('valid', false, 'reason', 'Invalid or expired API key');
    END IF;
    
    -- Get user profile
    SELECT * INTO user_record 
    FROM public.user_profiles 
    WHERE id = key_record.user_id;
    
    -- Update last used
    UPDATE public.api_keys 
    SET last_used_at = NOW(), usage_count = usage_count + 1
    WHERE id = key_record.id;
    
    RETURN jsonb_build_object(
        'valid', true,
        'user_id', key_record.user_id,
        'email', user_record.email,
        'tier', user_record.subscription_tier,
        'key_name', key_record.name,
        'scopes', key_record.scopes
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 9. GRANT PERMISSIONS
-- ============================================

-- Grant usage to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.user_profiles TO authenticated;
GRANT ALL ON public.api_keys TO authenticated;
GRANT SELECT ON public.usage_logs TO authenticated;

-- Grant to service role (for backend operations)
GRANT ALL ON public.user_profiles TO service_role;
GRANT ALL ON public.api_keys TO service_role;
GRANT ALL ON public.usage_logs TO service_role;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================
-- After running this migration:
-- 1. Existing users need profiles created manually (run backfill below)
-- 2. Test signup flow to verify trigger works
-- 3. Test API key generation
-- ============================================

-- Optional: Backfill profiles for existing users
-- INSERT INTO public.user_profiles (id, email, full_name, avatar_url)
-- SELECT 
--     id, 
--     email, 
--     COALESCE(raw_user_meta_data->>'full_name', raw_user_meta_data->>'name'),
--     raw_user_meta_data->>'avatar_url'
-- FROM auth.users
-- WHERE id NOT IN (SELECT id FROM public.user_profiles)
-- ON CONFLICT (id) DO NOTHING;
