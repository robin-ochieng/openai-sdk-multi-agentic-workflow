'use client'

import { Suspense, useEffect, useState, useRef, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { AlertCircle, FileText } from 'lucide-react'
import Link from 'next/link'

import { useRunStore, type ResearchStep, type Channel, type LogEntry, type EvidenceItem } from '@/lib/runStore'
import { useHistoryStore, createHistoryRunFromState } from '@/lib/historyStore'
import { startSSE, StreamEvent } from '@/lib/streamClient'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'

import { PageHeader } from '@/components/live/PageHeader'
import { ProgressPanel } from '@/components/live/ProgressPanel'
import { AgentConsole } from '@/components/live/AgentConsole'
import { EvidencePanel } from '@/components/live/EvidencePanel'
import {
  ProgressPanelSkeleton,
  AgentConsoleSkeleton,
  EvidencePanelSkeleton,
  PageHeaderSkeleton,
} from '@/components/live/skeletons'

const STEP_ORDER: ResearchStep[] = ['planning', 'research', 'writing', 'email']

const initialProgress: Record<ResearchStep, number> = {
  planning: 0,
  research: 0,
  writing: 0,
  email: 0,
}

function LiveResearchContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [isInitializing, setIsInitializing] = useState(true)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [isMounted, setIsMounted] = useState(false)
  const hasStartedStreaming = useRef(false)
  const hasSavedToHistory = useRef(false)
  
  // LOCAL STATE for real-time updates (not persisted)
  const [localStep, setLocalStep] = useState<ResearchStep>('planning')
  const [localProgress, setLocalProgress] = useState<Record<ResearchStep, number>>({ ...initialProgress })
  const [localLogs, setLocalLogs] = useState<LogEntry[]>([])
  const [localEvidence, setLocalEvidence] = useState<EvidenceItem[]>([])
  const [localReport, setLocalReport] = useState<string | undefined>(undefined)
  const [localStatus, setLocalStatus] = useState<'idle' | 'running' | 'done' | 'error'>('idle')
  const [localError, setLocalError] = useState<string | undefined>(undefined)
  const [localActiveChannel, setLocalActiveChannel] = useState<Channel>('planner')

  // Ensure client-side hydration
  useEffect(() => {
    setIsMounted(true)
  }, [])

  // Get store functions for persistence (not for reading during stream)
  const storeReset = useRunStore((state) => state.reset)
  const storeApplyEvent = useRunStore((state) => state.applyEvent)
  const storeRunId = useRunStore((state) => state.runId)
  const storeQuery = useRunStore((state) => state.query)
  const storeEmail = useRunStore((state) => state.email)
  const storeStatus = useRunStore((state) => state.status)
  const storeLogs = useRunStore((state) => state.logs)

  const { addRun } = useHistoryStore()

  // Get runId from URL or store
  const urlRunId = searchParams.get('runId')
  const urlQuery = searchParams.get('query')
  const urlEmail = searchParams.get('email')
  const isNewRun = searchParams.get('new') === '1'
  const effectiveRunId = urlRunId || storeRunId
  
  // Use URL query as fallback if store query is empty (hydration timing issue)
  const effectiveQuery = storeQuery || urlQuery || ''
  const effectiveEmail = storeEmail || urlEmail || undefined

  // Apply event to LOCAL state for immediate UI updates
  const applyEventLocally = useCallback((event: StreamEvent) => {
    console.log('[Live] Applying event locally:', event.type, event)
    
    // Also persist to store for history
    try {
      storeApplyEvent(event)
    } catch (e) {
      console.error('[Live] Store update failed:', e)
    }
    
    switch (event.type) {
      case 'step': {
        const stepIndex = STEP_ORDER.indexOf(event.step)
        setLocalStep(event.step)
        setLocalProgress(prev => {
          const updated = { ...prev, [event.step]: event.value }
          // Ensure earlier phases are marked complete
          if (stepIndex > 0) {
            for (let i = 0; i < stepIndex; i++) {
              const key = STEP_ORDER[i]
              if (updated[key] < 100) {
                updated[key] = 100
              }
            }
          }
          console.log('[Live] Updated local progress:', updated)
          return updated
        })
        break
      }
      case 'log':
        setLocalLogs(prev => [...prev, {
          channel: event.channel,
          ts: event.ts,
          level: event.level,
          text: event.text,
        }])
        // Auto-switch channel based on log
        const channelMap: Record<Channel, ResearchStep> = {
          planner: 'planning',
          web: 'research',
          synthesizer: 'writing',
          editor: 'email',
        }
        if (channelMap[event.channel]) {
          setLocalActiveChannel(event.channel)
        }
        break
      case 'evidence':
        setLocalEvidence(prev => [...prev, {
          id: event.id,
          title: event.title,
          url: event.url,
          snippet: event.snippet,
          favicon: event.favicon,
        }])
        break
      case 'report':
        setLocalReport(event.markdown)
        break
      case 'done':
        setLocalStatus('done')
        // Mark all steps complete
        setLocalProgress({
          planning: 100,
          research: 100,
          writing: 100,
          email: 100,
        })
        break
      case 'error':
        setLocalStatus('error')
        setLocalError(event.message)
        break
    }
  }, [storeApplyEvent])

  // Save to history when research completes
  useEffect(() => {
    if ((localStatus === 'done' || localStatus === 'error') && localReport && !hasSavedToHistory.current) {
      hasSavedToHistory.current = true
      const historyRun = createHistoryRunFromState({
        runId: storeRunId,
        query: storeQuery,
        email: storeEmail,
        reportMarkdown: localReport,
        evidence: localEvidence,
        logs: localLogs,
        startedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
        status: localStatus,
        error: localError,
      })
      if (historyRun) {
        addRun(historyRun)
        console.log('[History] Saved run to history:', historyRun.runId)
      }
    }
  }, [localStatus, localReport, storeRunId, storeQuery, storeEmail, localEvidence, localLogs, localError, addRun])

  // Redirect to home if no query and not resuming
  useEffect(() => {
    if (!effectiveQuery && !isInitializing) {
      router.push('/')
    }
  }, [effectiveQuery, isInitializing, router])

  // Initialize and start streaming
  useEffect(() => {
    // Wait for client-side hydration
    if (!isMounted) {
      console.log('[Live] Waiting for mount...')
      return
    }

    console.log('[Live] Effect running with:', { 
      effectiveRunId, 
      effectiveQuery, 
      localStatus, 
      isNewRun, 
      storeRunId,
      hasStarted: hasStartedStreaming.current 
    })

    // Case 1: New run - always start fresh streaming
    if (isNewRun && effectiveRunId && effectiveQuery) {
      // Skip if we already started streaming for this exact run
      if (hasStartedStreaming.current && effectiveRunId === storeRunId) {
        console.log('[Live] Already streaming this run, skipping')
        setIsInitializing(false)
        return
      }

      hasStartedStreaming.current = true
      hasSavedToHistory.current = false

      // Reset local state
      setLocalStep('planning')
      setLocalProgress({ ...initialProgress })
      setLocalLogs([])
      setLocalEvidence([])
      setLocalReport(undefined)
      setLocalStatus('running')
      setLocalError(undefined)
      setLocalActiveChannel('planner')

      // Reset store for persistence
      console.log('[Live] Starting NEW research run:', { runId: effectiveRunId, query: effectiveQuery })
      storeReset(effectiveRunId, effectiveQuery, effectiveEmail)
      setIsInitializing(false)

      // Start streaming
      const cleanup = startSSE({
        runId: effectiveRunId,
        query: effectiveQuery,
        email: effectiveEmail,
        onEvent: applyEventLocally,
        onClose: () => {
          console.log('[Stream] Connection closed')
        },
        onError: (err) => {
          console.error('[Stream] Error:', err)
          setLocalError(err.message)
          setLocalStatus('error')
          setConnectionError(err.message)
        },
      })

      return () => {
        cleanup()
      }
    }

    // Case 2: Resuming a completed/errored run - just display from store
    if (effectiveRunId === storeRunId && (storeStatus === 'done' || storeStatus === 'error')) {
      console.log('[Live] Showing completed/errored run')
      setIsInitializing(false)
      return
    }

    // Case 3: Resuming a running state - continue displaying from store
    if (effectiveRunId === storeRunId && storeStatus === 'running' && storeLogs.length > 0) {
      console.log('[Live] Resuming running state')
      setIsInitializing(false)
      return
    }

    // Case 4: No valid run data - go back home
    if (!effectiveRunId || !effectiveQuery) {
      console.log('[Live] Missing runId or query, cannot start')
      setIsInitializing(false)
      return
    }

    // Default: Nothing matched, just stop initializing
    console.log('[Live] No matching condition, stopping initialization')
    setIsInitializing(false)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMounted, effectiveRunId, effectiveQuery, effectiveEmail, isNewRun, storeReset, applyEventLocally])

  // Show loading state
  if (isInitializing) {
    return (
      <div className="mx-auto max-w-[1200px] px-6 py-8">
        <PageHeaderSkeleton />
        <div className="grid gap-6 xl:grid-cols-[280px_1fr_340px]">
          <ProgressPanelSkeleton />
          <AgentConsoleSkeleton />
          <EvidencePanelSkeleton />
        </div>
      </div>
    )
  }

  // Show error if no query
  if (!effectiveQuery) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No research query found. Please start a new research from the home page.
          </AlertDescription>
        </Alert>
        <div className="mt-4 text-center">
          <Button onClick={() => router.push('/')}>Return to Home</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-[1200px] px-6 py-8">
      {/* Streaming progress indicator */}
      {localStatus === 'running' && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed left-0 right-0 top-16 z-50 md:top-0"
        >
          <Progress value={undefined} className="h-1 rounded-none" />
        </motion.div>
      )}

      {/* Page Header */}
      <PageHeader query={effectiveQuery} email={effectiveEmail} />

      {/* Connection Error */}
      {connectionError && localStatus === 'error' && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>{connectionError}</span>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setConnectionError(null)
                  window.location.reload()
                }}
              >
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* 3-Column Grid Layout */}
      <div className="grid gap-6 md:grid-cols-1 xl:grid-cols-[280px_1fr_340px]">
        {/* Left: Progress Panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          <ProgressPanel progress={localProgress} step={localStep} status={localStatus} />
        </motion.div>

        {/* Center: Agent Console */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <AgentConsole
            activeChannel={localActiveChannel}
            logs={localLogs}
            onChange={setLocalActiveChannel}
          />
        </motion.div>

        {/* Right: Evidence Panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <EvidencePanel evidence={localEvidence} />
        </motion.div>
      </div>

      {/* Success State - Show Report Button */}
      {localStatus === 'done' && localReport && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <Alert className="border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950/20">
            <FileText className="h-4 w-4 text-green-600 dark:text-green-500" />
            <AlertDescription className="flex items-center justify-between">
              <span className="font-medium text-green-900 dark:text-green-100">
                Research complete! Your report is ready.
              </span>
              <Link href="/report">
                <Button size="sm" className="ml-4">
                  Open Report
                </Button>
              </Link>
            </AlertDescription>
          </Alert>
        </motion.div>
      )}
    </div>
  )
}

export default function LiveResearchPage() {
  return (
    <Suspense fallback={
      <div className="mx-auto max-w-[1200px] px-6 py-8">
        <PageHeaderSkeleton />
        <div className="grid gap-6 xl:grid-cols-[280px_1fr_340px]">
          <ProgressPanelSkeleton />
          <AgentConsoleSkeleton />
          <EvidencePanelSkeleton />
        </div>
      </div>
    }>
      <LiveResearchContent />
    </Suspense>
  )
}
