import { NextRequest, NextResponse } from 'next/server'
import { researchApi, isSupabaseConfigured } from '@/lib/supabase'

/**
 * POST /api/runs/sync
 * Sync completed runs from local storage to Supabase
 */
export async function POST(request: NextRequest) {
  try {
    // Check if Supabase is configured
    if (!isSupabaseConfigured()) {
      return NextResponse.json(
        { 
          error: 'Database not configured',
          message: 'Supabase is not configured',
          synced: 0
        },
        { status: 200 }  // Return 200 to gracefully degrade
      )
    }

    const body = await request.json()
    const { runs } = body

    if (!Array.isArray(runs)) {
      return NextResponse.json(
        { error: 'runs must be an array' },
        { status: 400 }
      )
    }

    let syncedCount = 0
    const errors: Array<{ runId: string; error: string }> = []

    for (const run of runs) {
      try {
        const success = await researchApi.syncCompletedRun({
          runId: run.runId,
          query: run.query,
          email: run.email,
          status: run.status,
          step: run.step || 'writing',
          progress: run.progress || { planning: 100, research: 100, writing: 100, email: 100 },
          reportMarkdown: run.reportMarkdown,
          error: run.error,
          logs: run.logs || [],
          evidence: run.evidence || [],
          startedAt: run.startedAt,
          completedAt: run.completedAt,
        })

        if (success) {
          syncedCount++
        } else {
          errors.push({ runId: run.runId, error: 'Sync failed' })
        }
      } catch (error) {
        errors.push({ 
          runId: run.runId, 
          error: error instanceof Error ? error.message : 'Unknown error'
        })
      }
    }

    return NextResponse.json({
      success: true,
      synced: syncedCount,
      total: runs.length,
      errors: errors.length > 0 ? errors : undefined,
    })
  } catch (error) {
    console.error('[API] Error syncing runs:', error)
    return NextResponse.json(
      { 
        error: 'Failed to sync runs',
        message: error instanceof Error ? error.message : 'Unknown error',
        synced: 0
      },
      { status: 500 }
    )
  }
}
