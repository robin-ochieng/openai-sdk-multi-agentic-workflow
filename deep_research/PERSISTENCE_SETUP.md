# Persistence Setup Guide

This guide explains how to set up data persistence for the Deep Research Agent.

## Overview

The persistence system provides:
- **LocalStorage Persistence**: Immediate state persistence for tab navigation
- **Supabase Persistence**: Long-term cloud storage for research history

## Quick Start (LocalStorage Only)

LocalStorage persistence works out of the box with no configuration needed:
- Research state (progress, logs, evidence, reports) is automatically saved
- State is restored when you return to the app
- History of completed research runs is maintained

## Setting Up Supabase (Optional but Recommended)

Supabase provides cloud persistence for:
- Cross-device access to research history
- Permanent storage of all research runs
- Ability to share research reports

### Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Wait for the project to be provisioned

### Step 2: Run the Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Open the file `deep_research/supabase/schema.sql`
3. Copy the entire contents and paste into the SQL Editor
4. Click **Run** to create the tables

### Step 3: Get Your API Keys

1. In Supabase dashboard, go to **Settings > API**
2. Copy the following values:
   - `Project URL` (e.g., `https://xxxxx.supabase.co`)
   - `anon/public` key (safe for frontend use)

### Step 4: Configure Environment Variables

Create a `.env.local` file in the `deep_research/frontend` directory:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

For the Python backend, add to `deep_research/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

### Step 5: Restart the Application

Restart both the frontend and backend to pick up the new environment variables.

## How It Works

### LocalStorage Persistence

The app uses Zustand stores with `persist` middleware:

1. **Run Store** (`lib/runStore.ts`): Persists the current research session
   - Query, progress, logs, evidence, report
   - Survives page refreshes and tab navigation

2. **History Store** (`lib/historyStore.ts`): Persists completed research runs
   - Up to 50 most recent runs
   - Includes full reports, logs, and evidence

### Supabase Sync

When Supabase is configured:

1. **Automatic Sync on Completion**: When a research run completes, it's automatically synced to Supabase
2. **Fetch on Load**: Historical runs are fetched from Supabase when the app loads
3. **Offline Support**: Runs completed while offline are synced when back online

### Database Schema

The Supabase database has three main tables:

```
research_runs        - Main research session data
├── run_id          - Unique identifier
├── query           - Research query
├── status          - idle/running/done/error
├── report_markdown - Generated report
└── ...

research_logs        - Agent activity logs
├── run_id          - References research_runs
├── channel         - planner/web/synthesizer/editor
├── message         - Log message
└── ...

research_evidence    - Sources and citations
├── run_id          - References research_runs
├── title           - Source title
├── url             - Source URL
└── ...
```

## Troubleshooting

### LocalStorage Not Persisting

1. Check if browser allows localStorage (incognito mode may block it)
2. Clear browser cache and try again
3. Check browser console for errors

### Supabase Not Syncing

1. Verify environment variables are set correctly
2. Check browser console for Supabase errors
3. Ensure your Supabase project is active (free tier pauses after inactivity)
4. Verify the schema was applied correctly

### Data Not Showing in Reports Page

1. Complete at least one research run
2. Wait for the "done" status before navigating away
3. Check if data appears in browser localStorage:
   - Open DevTools > Application > Local Storage
   - Look for `deep-research-history` key

## Security Considerations

- The `anon` key is safe for frontend use (RLS policies protect data)
- For production, implement user authentication
- Consider adding user-specific RLS policies for multi-user deployments

## API Endpoints

The frontend provides these API routes:

- `GET /api/runs` - List all research runs
- `GET /api/runs/[runId]` - Get a specific run with logs and evidence
- `DELETE /api/runs/[runId]` - Delete a research run
- `POST /api/runs/sync` - Sync local runs to Supabase
