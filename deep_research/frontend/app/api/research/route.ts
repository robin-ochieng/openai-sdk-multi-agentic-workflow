import { NextRequest } from 'next/server'

// Python backend URL
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:7863'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { query, email } = body

    console.log('Forwarding request to Python backend:', PYTHON_API_URL)

    // Forward request to Python backend
    const response = await fetch(`${PYTHON_API_URL}/api/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, email }),
    })

    console.log('Python backend response status:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Python backend error:', errorText)
      return new Response(
        JSON.stringify({ 
          error: 'Failed to start research',
          details: errorText 
        }),
        {
          status: response.status,
          headers: { 'Content-Type': 'application/json' },
        }
      )
    }

    // Stream the response from Python backend to client
    const stream = response.body

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
      },
    })
  } catch (error) {
    console.error('API Error:', error)
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }
}

export async function GET() {
  return new Response(
    JSON.stringify({ message: 'Deep Research API - Use POST to start research' }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  )
}
