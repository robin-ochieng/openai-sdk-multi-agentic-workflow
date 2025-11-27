import { NextRequest } from 'next/server'
import { unstable_noStore as noStore } from 'next/cache'
import http from 'http'

// Use nodejs runtime for reliable localhost connections
export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'
export const revalidate = 0
// Disable response size limit for streaming
export const maxDuration = 300 // 5 minutes max

const DEFAULT_BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:7863'
const HEARTBEAT_INTERVAL_MS = 15_000

const SSE_HEADERS: Record<string, string> = {
  'Content-Type': 'text/event-stream; charset=utf-8',
  'Cache-Control': 'no-cache, no-transform',
  Connection: 'keep-alive',
  'X-Accel-Buffering': 'no',
  'x-vercel-no-compression': '1',
}

type StreamPayload = { type: string; [key: string]: unknown }

type RouteParams = {
  params: Promise<{
    runId: string
  }>
}

export async function GET(request: NextRequest, { params }: RouteParams) {
  noStore()

  const { runId } = await params
  const query = request.nextUrl.searchParams.get('query')
  const email = request.nextUrl.searchParams.get('email')

  console.log('[SSE Route] Request received:', { runId, query, email })

  if (!query) {
    console.log('[SSE Route] Missing query parameter')
    return jsonError('Query parameter is required for streaming', 400)
  }

  console.log('[SSE Route] Connecting to backend:', DEFAULT_BACKEND_URL)

  // Use native http module for proper streaming support
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      let isClosed = false
      let heartbeatTimer: ReturnType<typeof setTimeout> | null = null

      const safeClose = () => {
        if (!isClosed) {
          isClosed = true
          if (heartbeatTimer) {
            clearTimeout(heartbeatTimer)
            heartbeatTimer = null
          }
          try {
            controller.close()
          } catch (e) {
            // Controller already closed
          }
        }
      }

      const emit = (payload: StreamPayload) => {
        if (isClosed) return
        try {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(payload)}\n\n`))
        } catch (e) {
          // Controller closed
        }
      }

      const scheduleHeartbeat = () => {
        if (isClosed) return
        heartbeatTimer = setTimeout(() => {
          if (isClosed) return
          try {
            controller.enqueue(encoder.encode('event: ping\ndata: {}\n\n'))
          } catch (e) {
            // Controller closed
          }
          scheduleHeartbeat()
        }, HEARTBEAT_INTERVAL_MS)
      }

      // Parse backend URL
      const backendUrl = new URL(`${DEFAULT_BACKEND_URL}/api/research`)
      
      const postData = JSON.stringify({
        run_id: runId,
        query,
        email: email || null,
      })

      const options: http.RequestOptions = {
        hostname: backendUrl.hostname,
        port: backendUrl.port || 80,
        path: backendUrl.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData),
          'Accept': 'text/event-stream',
        },
      }

      console.log('[SSE Route] Making HTTP request to backend')

      const req = http.request(options, (res) => {
        console.log('[SSE Route] Backend response status:', res.statusCode)

        if (res.statusCode !== 200) {
          emit({ type: 'error', message: `Backend returned status ${res.statusCode}` })
          safeClose()
          return
        }

        scheduleHeartbeat()

        let buffer = ''
        let chunkCount = 0

        res.on('data', (chunk: Buffer) => {
          if (isClosed) return
          
          chunkCount++
          const chunkStr = chunk.toString()
          console.log(`[SSE Route] Chunk #${chunkCount}:`, chunkStr.substring(0, 80))
          buffer += chunkStr

          // Process complete events from buffer
          let boundary = buffer.indexOf('\n\n')
          while (boundary !== -1) {
            const rawEvent = buffer.slice(0, boundary)
            buffer = buffer.slice(boundary + 2)

            const dataSegment = extractData(rawEvent)
            if (dataSegment) {
              if (dataSegment === '[DONE]') {
                console.log('[SSE Route] Received [DONE], closing stream')
                emit({ type: 'done' })
              } else {
                try {
                  const parsed = JSON.parse(dataSegment)
                  console.log('[SSE Route] Parsed event:', parsed.type)
                  const transformed = transformBackendEvent(parsed)
                  transformed.forEach(emit)
                } catch (error) {
                  console.error('[SSE Route] Failed to parse:', error)
                }
              }
            }

            boundary = buffer.indexOf('\n\n')
          }
        })

        res.on('end', () => {
          console.log(`[SSE Route] Backend stream ended after ${chunkCount} chunks`)
          safeClose()
        })

        res.on('error', (error) => {
          console.error('[SSE Route] Response error:', error)
          emit({ type: 'error', message: error.message || 'Response error' })
          safeClose()
        })
      })

      req.on('error', (error) => {
        console.error('[SSE Route] Request error:', error)
        emit({ type: 'error', message: error.message || 'Request error' })
        safeClose()
      })

      req.write(postData)
      req.end()
    },
  })

  return new Response(stream, {
    headers: SSE_HEADERS,
  })
}

function extractData(rawEvent: string): string | null {
  const dataLines = rawEvent
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())

  if (dataLines.length === 0) {
    return null
  }

  return dataLines.join('\n')
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const toString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : fallback

const toNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' ? value : fallback

function transformBackendEvent(data: unknown): StreamPayload[] {
  if (!isRecord(data)) {
    return []
  }

  const eventType = toString(data.type)

  if (eventType === 'log' && Array.isArray(data.logs)) {
    return data.logs
      .map((log): StreamPayload | null => {
        if (!isRecord(log)) {
          return null
        }

        const message = toString(log.message)

        return {
          type: 'log',
          channel: determineChannel(message),
          ts: toString(log.timestamp),
          level: toString(log.type, 'info'),
          text: message,
        }
      })
      .filter((entry): entry is StreamPayload => entry !== null)
  }

  if (eventType === 'progress') {
    const mappedStep = mapStep(toString(data.step))
    console.log('[SSE Transform] Progress event:', { original: data.step, mapped: mappedStep, value: data.percentage })
    return [
      {
        type: 'step',
        step: mappedStep,
        value: toNumber(data.percentage),
      },
    ]
  }

  // Handle direct evidence events from backend
  if (eventType === 'evidence') {
    const url = toString(data.url)
    if (!url) return []
    
    return [
      {
        type: 'evidence',
        id: toString(data.id, `evidence-${Date.now()}`),
        title: toString(data.title, 'Untitled Source'),
        url: url,
        snippet: toString(data.snippet, ''),
        favicon: data.favicon as string | null | undefined,
      },
    ]
  }

  if (eventType === 'searching_complete' && Array.isArray(data.results)) {
    return data.results
      .map((result, index): StreamPayload | null => {
        if (!isRecord(result)) {
          return null
        }

        return {
          type: 'evidence',
          id: `search-${Date.now()}-${index}`,
          title: toString(result.query, `Search Result ${index + 1}`),
          url: toString(result.url, '#'),
          snippet: toString(result.summary),
          favicon: result.favicon as string | null | undefined,
        }
      })
      .filter((entry): entry is StreamPayload => entry !== null)
  }

  if (eventType === 'writing_complete' && isRecord(data.report)) {
    const report = data.report
    return [
      {
        type: 'report',
        markdown: toString(report.markdown_report, toString(report.content)),
      },
    ]
  }

  if (eventType === 'complete') {
    return [
      {
        type: 'done',
        traceUrl: toString(data.trace_url) || null,
      },
    ]
  }

  if (eventType === 'error') {
    return [
      {
        type: 'error',
        message: toString(data.error, toString(data.message, 'Unknown error')),
      },
    ]
  }

  if (eventType === 'planning_complete' || eventType === 'email_sent') {
    return []
  }

  console.log('[SSE] Unhandled backend event:', data)
  return []
}

function determineChannel(message: string | undefined): 'planner' | 'web' | 'synthesizer' | 'editor' {
  const fallback = 'planner' as const
  if (!message) return fallback

  const lower = message.toLowerCase()

  if (lower.includes('plan') || lower.includes('strategy') || lower.includes('step 1')) {
    return 'planner'
  }
  if (lower.includes('search') || lower.includes('web') || lower.includes('step 2')) {
    return 'web'
  }
  if (lower.includes('synthesiz') || lower.includes('writing') || lower.includes('step 3')) {
    return 'synthesizer'
  }
  if (lower.includes('email') || lower.includes('send') || lower.includes('step 4')) {
    return 'editor'
  }

  return fallback
}

function mapStep(step: string | undefined): 'planning' | 'research' | 'writing' | 'email' {
  const value = (step || '').toLowerCase()

  if (value.includes('search') || value.includes('web')) {
    return 'research'
  }
  if (value.includes('writ') || value.includes('report') || value.includes('synthesiz')) {
    return 'writing'
  }
  if (value.includes('email') || value.includes('send')) {
    return 'email'
  }

  return 'planning'
}

function jsonError(message: string, status = 500): Response {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
    },
  })
}
