import { NextRequest } from 'next/server'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

/**
 * SSE Streaming endpoint for research runs
 * GET /api/runs/[runId]/stream
 * Proxies to Python backend at http://localhost:7863/api/research
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { runId: string } }
) {
  const { runId } = params
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:7863'

  console.log(`[SSE] Connecting to backend for runId: ${runId}`)

  try {
    // Get query and email from URL params (passed from frontend)
    const searchParams = request.nextUrl.searchParams
    const query = searchParams.get('query')
    const email = searchParams.get('email')

    if (!query) {
      return new Response(
        JSON.stringify({ error: 'Query parameter is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Call Python backend SSE endpoint
    const response = await fetch(`${backendUrl}/api/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        query,
        email: email || null,
      }),
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    if (!response.body) {
      throw new Error('No response body from backend')
    }

    // Transform backend events to match frontend contract
    const transformStream = new TransformStream({
      async transform(chunk, controller) {
        const text = new TextDecoder().decode(chunk)
        const lines = text.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataContent = line.slice(6).trim()
            
            // Handle [DONE] marker
            if (dataContent === '[DONE]') {
              console.log('[SSE Transform] Received [DONE] marker')
              continue // Skip [DONE], we'll send 'done' event from 'complete' type
            }
            
            try {
              const data = JSON.parse(dataContent)
              
              // Transform Python backend format to frontend format (returns array)
              const transformedEvents = transformBackendEvent(data)
              
              // Send each transformed event
              for (const transformed of transformedEvents) {
                const message = `data: ${JSON.stringify(transformed)}\n\n`
                controller.enqueue(new TextEncoder().encode(message))
              }
            } catch (e) {
              console.error('[SSE Transform] Parse error for line:', dataContent, e)
            }
          }
        }
      },
    })

    // Pipe the response through the transform
    const transformedStream = response.body.pipeThrough(transformStream)

    // Return SSE response
    return new Response(transformedStream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
      },
    })
  } catch (error) {
    console.error('[SSE] Error:', error)
    
    // Return error as SSE
    const encoder = new TextEncoder()
    const errorMessage = `data: ${JSON.stringify({ 
      type: 'error', 
      message: error instanceof Error ? error.message : 'Connection failed' 
    })}\n\n`
    
    return new Response(errorMessage, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
    })
  }
}

/**
 * Transform Python backend event format to frontend contract
 * Returns an array because some backend events map to multiple frontend events
 */
function transformBackendEvent(data: any): any[] {
  // Backend sends: { type: 'log', logs: [{...}] }
  // Frontend expects: { type: 'log', channel, ts, level, text }
  
  if (data.type === 'log' && data.logs && data.logs.length > 0) {
    // Transform ALL logs, not just the first one
    return data.logs.map((log: any) => ({
      type: 'log',
      channel: determineChannel(log.message),
      ts: log.timestamp,
      level: log.type || 'info',
      text: log.message,
    }))
  }
  
  // Backend sends: { type: 'progress', step, percentage }
  // Frontend expects: { type: 'step', step, value }
  if (data.type === 'progress') {
    return [{
      type: 'step',
      step: mapStep(data.step),
      value: data.percentage,
    }]
  }
  
  // Backend sends: { type: 'searching_complete', results: [{query, summary}] }
  // Frontend expects: { type: 'evidence', id, title, url, snippet, favicon }
  if (data.type === 'searching_complete' && data.results && data.results.length > 0) {
    // Transform ALL search results into evidence items
    return data.results.map((result: any, index: number) => ({
      type: 'evidence',
      id: `search-${Date.now()}-${index}`,
      title: result.query || `Search Result ${index + 1}`,
      url: '#', // No URL for search summaries
      snippet: result.summary || '',
      favicon: null,
    }))
  }
  
  // Backend sends: { type: 'writing_complete', report: { markdown_report: '...' } }
  // Frontend expects: { type: 'report', markdown: '...' }
  if (data.type === 'writing_complete' && data.report) {
    return [{
      type: 'report',
      markdown: data.report.markdown_report || data.report.content || '',
    }]
  }
  
  // Backend sends: { type: 'complete' }
  // Frontend expects: { type: 'done' }
  if (data.type === 'complete' || data.type === 'done') {
    return [{ type: 'done' }]
  }
  
  // Handle planning_complete, email_sent - just log them
  if (data.type === 'planning_complete' || data.type === 'email_sent') {
    console.log(`[SSE Transform] Received ${data.type}:`, data)
    return [] // Don't send to frontend, we're using logs for these
  }
  
  // Backend sends: { type: 'error', error: '...' }
  // Frontend expects: { type: 'error', message: '...' }
  if (data.type === 'error') {
    return [{
      type: 'error',
      message: data.error || data.message || 'Unknown error',
    }]
  }
  
  // Unknown event type - log and skip
  console.log('[SSE Transform] Unknown event type:', data.type, data)
  return []
}

/**
 * Determine channel from log message content
 */
function determineChannel(message: string): 'planner' | 'web' | 'synthesizer' | 'editor' {
  const lower = message.toLowerCase()
  
  if (lower.includes('plan') || lower.includes('strategy') || lower.includes('step 1')) {
    return 'planner'
  }
  if (lower.includes('search') || lower.includes('web') || lower.includes('step 2')) {
    return 'web'
  }
  if (lower.includes('synthesiz') || lower.includes('writing') || lower.includes('report') || lower.includes('step 3')) {
    return 'synthesizer'
  }
  if (lower.includes('email') || lower.includes('send') || lower.includes('step 4')) {
    return 'editor'
  }
  
  return 'planner' // default
}

/**
 * Map backend step names to frontend format
 */
function mapStep(step: string): 'planning' | 'research' | 'writing' | 'email' {
  const lower = step.toLowerCase()
  
  if (lower.includes('search') || lower.includes('web')) {
    return 'research'
  }
  if (lower.includes('writ') || lower.includes('report') || lower.includes('synthesiz')) {
    return 'writing'
  }
  if (lower.includes('email') || lower.includes('send')) {
    return 'email'
  }
  
  return 'planning' // default
}

/**
 * Simulate research workflow
 * TODO: Replace with actual backend integration
 */
async function simulateResearchWorkflow(sendEvent: (data: any) => Promise<void>) {
  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  // Planning phase
  await sendEvent({ 
    type: 'log', 
    channel: 'planner', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Starting research planning...' 
  })
  await sleep(500)
  
  await sendEvent({ type: 'step', step: 'planning', value: 30 })
  await sleep(800)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'planner', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Analyzing query and generating search strategy...' 
  })
  await sleep(600)
  
  await sendEvent({ type: 'step', step: 'planning', value: 60 })
  await sleep(900)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'planner', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Created 5-search plan with targeted queries' 
  })
  await sleep(700)
  
  await sendEvent({ type: 'step', step: 'planning', value: 100 })

  // Research phase
  await sleep(800)
  await sendEvent({ 
    type: 'log', 
    channel: 'web', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Beginning web search phase...' 
  })
  await sleep(600)
  
  await sendEvent({ type: 'step', step: 'research', value: 20 })
  await sleep(1000)
  
  await sendEvent({ 
    type: 'evidence', 
    id: '1', 
    title: 'Understanding Quantum Computing Principles',
    url: 'https://example.com/quantum-basics',
    snippet: 'Quantum computing leverages quantum mechanical phenomena like superposition and entanglement...',
    favicon: 'https://example.com/favicon.ico'
  })
  await sleep(800)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'web', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Found 3 relevant sources from search 1/5' 
  })
  await sleep(700)
  
  await sendEvent({ type: 'step', step: 'research', value: 40 })
  await sleep(1200)
  
  await sendEvent({ 
    type: 'evidence', 
    id: '2', 
    title: 'Quantum Cryptography Applications',
    url: 'https://example.com/quantum-crypto',
    snippet: 'Post-quantum cryptography aims to develop encryption methods resistant to quantum attacks...',
  })
  await sleep(900)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'web', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Search 2/5 complete - 4 sources extracted' 
  })
  await sleep(800)
  
  await sendEvent({ type: 'step', step: 'research', value: 60 })
  await sleep(1000)
  
  await sendEvent({ 
    type: 'evidence', 
    id: '3', 
    title: 'IBM Quantum Experience Platform',
    url: 'https://quantum-computing.ibm.com',
    snippet: 'IBM provides cloud-based access to real quantum processors for research and development...',
  })
  await sleep(1100)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'web', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Completed all 5 searches - 12 total sources found' 
  })
  await sleep(600)
  
  await sendEvent({ type: 'step', step: 'research', value: 100 })

  // Writing phase
  await sleep(900)
  await sendEvent({ 
    type: 'log', 
    channel: 'synthesizer', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Synthesizing research findings...' 
  })
  await sleep(1200)
  
  await sendEvent({ type: 'step', step: 'writing', value: 25 })
  await sleep(1000)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'synthesizer', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Organizing information by themes and importance...' 
  })
  await sleep(1300)
  
  await sendEvent({ type: 'step', step: 'writing', value: 50 })
  await sleep(1100)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'synthesizer', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Generating comprehensive report with citations...' 
  })
  await sleep(1200)
  
  await sendEvent({ type: 'step', step: 'writing', value: 75 })
  await sleep(1000)
  
  await sendEvent({ 
    type: 'report', 
    markdown: `# Research Report: Quantum Computing

## Executive Summary
Quantum computing represents a paradigm shift in computational capabilities, leveraging quantum mechanical phenomena to solve complex problems that are intractable for classical computers.

## Key Findings

### 1. Fundamental Principles
Quantum computers utilize superposition and entanglement to process information in fundamentally different ways than classical computers. This allows them to explore multiple solution paths simultaneously.

### 2. Current Applications
- **Cryptography**: Post-quantum cryptographic methods are being developed to secure systems against quantum attacks
- **Drug Discovery**: Simulation of molecular interactions for pharmaceutical development
- **Optimization**: Solving complex logistics and scheduling problems

### 3. Industry Leaders
IBM, Google, and other tech giants are providing cloud-based access to quantum processors, democratizing access to this cutting-edge technology.

## Challenges

Despite significant progress, quantum computing faces several hurdles:
- Quantum decoherence and error rates
- Scalability of quantum systems
- Need for extremely low temperatures
- Limited algorithm development

## Future Outlook

The field is rapidly evolving, with experts predicting practical quantum advantage for specific applications within the next 5-10 years. Investment in quantum research continues to grow across academia and industry.

## Sources

1. Understanding Quantum Computing Principles - example.com
2. Quantum Cryptography Applications - example.com
3. IBM Quantum Experience Platform - quantum-computing.ibm.com

---

*Report generated by Deep Research Agent*`
  })
  await sleep(800)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'synthesizer', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Report generation complete - 2,847 words' 
  })
  await sleep(500)
  
  await sendEvent({ type: 'step', step: 'writing', value: 100 })

  // Email phase
  await sleep(700)
  await sendEvent({ 
    type: 'log', 
    channel: 'editor', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Preparing email delivery...' 
  })
  await sleep(800)
  
  await sendEvent({ type: 'step', step: 'email', value: 50 })
  await sleep(1000)
  
  await sendEvent({ 
    type: 'log', 
    channel: 'editor', 
    ts: new Date().toISOString(), 
    level: 'info', 
    text: 'Email sent successfully!' 
  })
  await sleep(500)
  
  await sendEvent({ type: 'step', step: 'email', value: 100 })
}
