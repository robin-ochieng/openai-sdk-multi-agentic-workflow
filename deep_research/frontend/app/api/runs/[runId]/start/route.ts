import { NextRequest } from 'next/server'

/**
 * POST /api/runs/[runId]/start
 * Start a research run with the Python backend
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { runId: string } }
) {
  const { runId } = params
  const body = await request.json()
  const { query, email } = body

  const backendUrl = process.env.BACKEND_URL || 'http://localhost:7863'

  try {
    // Call Python backend to start research
    const response = await fetch(`${backendUrl}/api/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        run_id: runId,
        query,
        email,
      }),
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    
    return Response.json({
      success: true,
      runId,
      ...data,
    })
  } catch (error) {
    console.error('[Start Run] Error:', error)
    return Response.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to start research',
      },
      { status: 500 }
    )
  }
}
