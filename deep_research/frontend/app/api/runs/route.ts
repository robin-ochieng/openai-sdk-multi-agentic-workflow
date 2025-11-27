import { NextRequest, NextResponse } from 'next/server'
import { researchApi, isSupabaseConfigured } from '@/lib/supabase'

/**
 * GET /api/runs
 * Get list of research runs
 */
export async function GET(request: NextRequest) {
  try {
    // Check if Supabase is configured
    if (!isSupabaseConfigured()) {
      return NextResponse.json(
        { 
          error: 'Database not configured',
          message: 'Supabase is not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY environment variables.',
          runs: []
        },
        { status: 200 }  // Return 200 with empty array to gracefully degrade
      )
    }

    const searchParams = request.nextUrl.searchParams
    const limit = parseInt(searchParams.get('limit') || '50', 10)
    const status = searchParams.get('status') || undefined

    const runs = await researchApi.getRunSummaries(limit)
    
    return NextResponse.json({
      runs,
      count: runs.length,
    })
  } catch (error) {
    console.error('[API] Error getting runs:', error)
    return NextResponse.json(
      { 
        error: 'Failed to get runs',
        message: error instanceof Error ? error.message : 'Unknown error',
        runs: []
      },
      { status: 500 }
    )
  }
}
