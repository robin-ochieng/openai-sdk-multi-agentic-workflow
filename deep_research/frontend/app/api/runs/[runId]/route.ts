import { NextRequest, NextResponse } from 'next/server'
import { researchApi, isSupabaseConfigured } from '@/lib/supabase'

interface RouteParams {
  params: Promise<{
    runId: string
  }>
}

/**
 * GET /api/runs/[runId]
 * Get a specific research run with logs and evidence
 */
export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const { runId } = await params

    if (!runId) {
      return NextResponse.json(
        { error: 'Run ID is required' },
        { status: 400 }
      )
    }

    // Check if Supabase is configured
    if (!isSupabaseConfigured()) {
      return NextResponse.json(
        { 
          error: 'Database not configured',
          message: 'Supabase is not configured'
        },
        { status: 503 }
      )
    }

    const run = await researchApi.getFullRun(runId)
    
    if (!run) {
      return NextResponse.json(
        { error: 'Run not found' },
        { status: 404 }
      )
    }

    return NextResponse.json(run)
  } catch (error) {
    console.error('[API] Error getting run:', error)
    return NextResponse.json(
      { 
        error: 'Failed to get run',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/runs/[runId]
 * Delete a research run
 */
export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    const { runId } = await params

    if (!runId) {
      return NextResponse.json(
        { error: 'Run ID is required' },
        { status: 400 }
      )
    }

    // Check if Supabase is configured
    if (!isSupabaseConfigured()) {
      return NextResponse.json(
        { 
          error: 'Database not configured',
          message: 'Supabase is not configured'
        },
        { status: 503 }
      )
    }

    const success = await researchApi.deleteRun(runId)
    
    if (!success) {
      return NextResponse.json(
        { error: 'Failed to delete run' },
        { status: 500 }
      )
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('[API] Error deleting run:', error)
    return NextResponse.json(
      { 
        error: 'Failed to delete run',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
