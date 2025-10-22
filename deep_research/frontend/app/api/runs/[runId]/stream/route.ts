import { NextRequest } from 'next/server'
import { unstable_noStore as noStore } from 'next/cache'

export const runtime = 'edge'
export const dynamic = 'force-dynamic'
export const revalidate = 0

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
  params: {
    runId: string
  }
}

export async function GET(request: NextRequest, { params }: RouteParams) {
  noStore()

  const query = request.nextUrl.searchParams.get('query')
  const email = request.nextUrl.searchParams.get('email')
  const { runId } = params

  if (!query) {
    return jsonError('Query parameter is required for streaming', 400)
  }

  const upstreamResponse = await fetch(`${DEFAULT_BACKEND_URL}/api/research`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    cache: 'no-store',
    body: JSON.stringify({
      run_id: runId,
      query,
      email: email || null,
    }),
  })

  if (!upstreamResponse.ok) {
    const message = await safeReadText(upstreamResponse)
    return jsonError(
      `Backend request failed (${upstreamResponse.status}): ${message || 'Unknown error'}`,
      upstreamResponse.status
    )
  }

  const upstreamBody = upstreamResponse.body

  if (!upstreamBody) {
    return jsonError('Backend did not return a readable stream', 502)
  }

  const encoder = new TextEncoder()
  const decoder = new TextDecoder()
  const reader = upstreamBody.getReader()

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      let buffer = ''
      let heartbeatTimer: ReturnType<typeof setTimeout> | null = null

      const emit = (payload: StreamPayload) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(payload)}\n\n`))
      }

      const emitError = (message: string) => {
        emit({ type: 'error', message })
      }

      const scheduleHeartbeat = () => {
        heartbeatTimer = setTimeout(() => {
          controller.enqueue(encoder.encode('event: ping\ndata: {}\n\n'))
          scheduleHeartbeat()
        }, HEARTBEAT_INTERVAL_MS)
      }

      scheduleHeartbeat()

      const pump = async () => {
        try {
          while (true) {
            const { value, done } = await reader.read()
            if (done) break
            if (!value) continue

            buffer += decoder.decode(value, { stream: true })
            buffer = flushBuffer(buffer, emit)
          }

        } catch (error) {
          console.error('[SSE] Proxy stream error:', error)
          emitError(error instanceof Error ? error.message : 'Stream interrupted')
        } finally {
          if (heartbeatTimer) {
            clearTimeout(heartbeatTimer)
          }
          controller.close()
          reader.releaseLock()
        }
      }

      pump()
    },
    cancel() {
      reader.cancel().catch(() => undefined)
    },
  })

  return new Response(stream, {
    headers: SSE_HEADERS,
  })
}

function flushBuffer(buffer: string, emit: (payload: StreamPayload) => void): string {
  let working = buffer

  while (true) {
    const boundary = working.indexOf('\n\n')
    if (boundary === -1) break

    const rawEvent = working.slice(0, boundary)
    working = working.slice(boundary + 2)

    const dataSegment = extractData(rawEvent)
    if (!dataSegment) {
      continue
    }

    if (dataSegment === '[DONE]') {
      emit({ type: 'done' })
      continue
    }

    try {
      const parsed = JSON.parse(dataSegment)
      const transformed = transformBackendEvent(parsed)
      transformed.forEach(emit)
    } catch (error) {
      console.error('[SSE] Failed to parse backend payload:', error, dataSegment)
    }
  }

  return working
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
    return [
      {
        type: 'step',
        step: mapStep(toString(data.step)),
        value: toNumber(data.percentage),
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

async function safeReadText(response: Response): Promise<string> {
  try {
    return await response.text()
  } catch (error) {
    console.error('[SSE] Failed to read upstream error body:', error)
    return ''
  }
}
