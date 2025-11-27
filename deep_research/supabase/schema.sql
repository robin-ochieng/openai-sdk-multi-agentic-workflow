-- ============================================
-- Deep Research Agent - Supabase Schema
-- ============================================
-- Run this SQL in your Supabase SQL Editor to set up the database
-- 
-- Tables:
--   - research_runs: Main research session metadata
--   - research_logs: Agent activity logs
--   - research_evidence: Sources and evidence collected
--
-- ============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. RESEARCH RUNS TABLE
-- Main table for research sessions
-- ============================================
CREATE TABLE IF NOT EXISTS research_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id TEXT UNIQUE NOT NULL,  -- Client-generated run ID (e.g., run_1234567890_abc123def)
    
    -- Research input
    query TEXT NOT NULL,
    email TEXT,
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('idle', 'running', 'done', 'error')),
    current_step TEXT DEFAULT 'planning' CHECK (current_step IN ('planning', 'research', 'writing', 'email')),
    error_message TEXT,
    
    -- Progress (JSON object with step percentages)
    progress JSONB DEFAULT '{"planning": 0, "research": 0, "writing": 0, "email": 0}'::jsonb,
    
    -- Report content
    report_markdown TEXT,
    word_count INTEGER DEFAULT 0,
    
    -- Metadata
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- User tracking (optional - for future auth)
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_research_runs_run_id ON research_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_research_runs_user_id ON research_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_research_runs_status ON research_runs(status);
CREATE INDEX IF NOT EXISTS idx_research_runs_created_at ON research_runs(created_at DESC);

-- ============================================
-- 2. RESEARCH LOGS TABLE
-- Agent activity logs for each research run
-- ============================================
CREATE TABLE IF NOT EXISTS research_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE CASCADE,
    
    -- Log details
    channel TEXT NOT NULL CHECK (channel IN ('planner', 'web', 'synthesizer', 'editor')),
    level TEXT NOT NULL DEFAULT 'info' CHECK (level IN ('info', 'warn', 'error')),
    message TEXT NOT NULL,
    
    -- Timestamp from the agent
    log_timestamp TIMESTAMPTZ NOT NULL,
    
    -- Order tracking
    sequence_num SERIAL,
    
    -- Database timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_research_logs_run_id ON research_logs(run_id);
CREATE INDEX IF NOT EXISTS idx_research_logs_channel ON research_logs(channel);
CREATE INDEX IF NOT EXISTS idx_research_logs_sequence ON research_logs(run_id, sequence_num);

-- ============================================
-- 3. RESEARCH EVIDENCE TABLE
-- Sources and evidence collected during research
-- ============================================
CREATE TABLE IF NOT EXISTS research_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE CASCADE,
    
    -- Evidence details
    evidence_id TEXT NOT NULL,  -- Client-generated evidence ID
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    snippet TEXT,
    favicon TEXT,
    
    -- Prevent duplicates
    UNIQUE(run_id, evidence_id),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_research_evidence_run_id ON research_evidence(run_id);

-- ============================================
-- 4. AUTO-UPDATE TIMESTAMP TRIGGER
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to research_runs
DROP TRIGGER IF EXISTS update_research_runs_updated_at ON research_runs;
CREATE TRIGGER update_research_runs_updated_at
    BEFORE UPDATE ON research_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 5. ROW LEVEL SECURITY (RLS)
-- Enable for production security
-- ============================================

-- Enable RLS on all tables
ALTER TABLE research_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_evidence ENABLE ROW LEVEL SECURITY;

-- Policy for research_runs: Users can only see their own runs
-- For anonymous access (no auth), allow all
CREATE POLICY "Allow anonymous access to research_runs" ON research_runs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policy for research_logs
CREATE POLICY "Allow anonymous access to research_logs" ON research_logs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policy for research_evidence
CREATE POLICY "Allow anonymous access to research_evidence" ON research_evidence
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 6. VIEWS FOR COMMON QUERIES
-- ============================================

-- View for run summaries (for the reports list page)
CREATE OR REPLACE VIEW research_run_summaries AS
SELECT 
    r.run_id,
    r.query,
    r.email,
    r.status,
    r.word_count,
    r.started_at,
    r.completed_at,
    r.created_at,
    (SELECT COUNT(*) FROM research_evidence e WHERE e.run_id = r.run_id) as evidence_count,
    (SELECT COUNT(*) FROM research_logs l WHERE l.run_id = r.run_id) as log_count
FROM research_runs r
ORDER BY r.created_at DESC;

-- ============================================
-- 7. FUNCTIONS FOR COMMON OPERATIONS
-- ============================================

-- Function to get full run details with logs and evidence
CREATE OR REPLACE FUNCTION get_full_research_run(p_run_id TEXT)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'run', row_to_json(r),
        'logs', COALESCE((
            SELECT json_agg(row_to_json(l) ORDER BY l.sequence_num)
            FROM research_logs l
            WHERE l.run_id = p_run_id
        ), '[]'::json),
        'evidence', COALESCE((
            SELECT json_agg(row_to_json(e))
            FROM research_evidence e
            WHERE e.run_id = p_run_id
        ), '[]'::json)
    ) INTO result
    FROM research_runs r
    WHERE r.run_id = p_run_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to upsert a research run
CREATE OR REPLACE FUNCTION upsert_research_run(
    p_run_id TEXT,
    p_query TEXT,
    p_email TEXT DEFAULT NULL,
    p_status TEXT DEFAULT 'running',
    p_current_step TEXT DEFAULT 'planning',
    p_progress JSONB DEFAULT '{"planning": 0, "research": 0, "writing": 0, "email": 0}'::jsonb,
    p_report_markdown TEXT DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
)
RETURNS research_runs AS $$
DECLARE
    result research_runs;
BEGIN
    INSERT INTO research_runs (
        run_id, query, email, status, current_step, progress, 
        report_markdown, error_message, word_count,
        completed_at
    )
    VALUES (
        p_run_id, p_query, p_email, p_status, p_current_step, p_progress,
        p_report_markdown, p_error_message,
        CASE WHEN p_report_markdown IS NOT NULL 
             THEN array_length(regexp_split_to_array(p_report_markdown, '\s+'), 1)
             ELSE 0 
        END,
        CASE WHEN p_status IN ('done', 'error') THEN NOW() ELSE NULL END
    )
    ON CONFLICT (run_id) DO UPDATE SET
        status = EXCLUDED.status,
        current_step = EXCLUDED.current_step,
        progress = EXCLUDED.progress,
        report_markdown = COALESCE(EXCLUDED.report_markdown, research_runs.report_markdown),
        error_message = EXCLUDED.error_message,
        word_count = EXCLUDED.word_count,
        completed_at = CASE WHEN EXCLUDED.status IN ('done', 'error') THEN NOW() 
                            ELSE research_runs.completed_at END,
        updated_at = NOW()
    RETURNING * INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 8. SAMPLE DATA (Optional - for testing)
-- ============================================

-- Uncomment to insert sample data:
/*
INSERT INTO research_runs (run_id, query, email, status, current_step, progress, report_markdown, word_count, completed_at)
VALUES (
    'run_sample_001',
    'What are the latest advancements in AI agents?',
    'test@example.com',
    'done',
    'email',
    '{"planning": 100, "research": 100, "writing": 100, "email": 100}'::jsonb,
    '# AI Agents Research Report\n\n## Introduction\n\nThis is a sample report about AI agents...',
    150,
    NOW()
);

INSERT INTO research_evidence (run_id, evidence_id, title, url, snippet)
VALUES 
    ('run_sample_001', 'ev_1', 'OpenAI Agents', 'https://openai.com/agents', 'OpenAI releases new agent capabilities...'),
    ('run_sample_001', 'ev_2', 'Anthropic Claude', 'https://anthropic.com/claude', 'Claude 3 introduces advanced reasoning...');

INSERT INTO research_logs (run_id, channel, level, message, log_timestamp)
VALUES 
    ('run_sample_001', 'planner', 'info', 'Starting research planning...', NOW() - INTERVAL '10 minutes'),
    ('run_sample_001', 'web', 'info', 'Searching for AI agent information...', NOW() - INTERVAL '8 minutes'),
    ('run_sample_001', 'synthesizer', 'info', 'Writing comprehensive report...', NOW() - INTERVAL '5 minutes');
*/

-- ============================================
-- DONE! 
-- Your Supabase database is now ready.
-- ============================================
