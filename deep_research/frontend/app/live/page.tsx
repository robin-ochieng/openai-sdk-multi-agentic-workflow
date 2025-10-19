'use client'

import { Suspense, useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { AlertCircle, FileText } from 'lucide-react'
import Link from 'next/link'

import { useRunStore } from '@/lib/runStore'
import { startSSE, startMockSSE } from '@/lib/streamClient'
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

function LiveResearchContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [isInitializing, setIsInitializing] = useState(true)
  const [connectionError, setConnectionError] = useState<string | null>(null)

  const {
    runId,
    query,
    email,
    step,
    progress,
    activeChannel,
    logs,
    evidence,
    reportMarkdown,
    status,
    error,
    reset,
    applyEvent,
    setActiveChannel,
    setStatus,
    setError,
  } = useRunStore()

  // Get runId from URL or store
  const urlRunId = searchParams.get('runId')
  const isDemoMode = searchParams.get('demo') === '1'
  const effectiveRunId = urlRunId || runId

  // Redirect to home if no query
  useEffect(() => {
    if (!query && !isInitializing) {
      router.push('/')
    }
  }, [query, isInitializing, router])

  // Initialize and start streaming
  useEffect(() => {
    if (!effectiveRunId || !query) {
      setIsInitializing(false)
      return
    }

    // Reset state for new run
    reset(effectiveRunId, query, email)
    setIsInitializing(false)

    // Start streaming (mock or real)
    const cleanup = isDemoMode
      ? startMockSSE({
          onEvent: (event) => {
            applyEvent(event)
          },
          onClose: () => {
            console.log('[Stream] Connection closed')
          },
        })
      : startSSE({
          runId: effectiveRunId,
          query,
          email,
          onEvent: (event) => {
            applyEvent(event)
          },
          onClose: () => {
            console.log('[Stream] Connection closed')
          },
          onError: (err) => {
            console.error('[Stream] Error:', err)
            setError(err.message)
            setConnectionError(err.message)
          },
        })

    return () => {
      cleanup()
    }
  }, [effectiveRunId, query, email, isDemoMode])

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
  if (!query) {
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
      {status === 'running' && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed left-0 right-0 top-16 z-50 md:top-0"
        >
          <Progress value={undefined} className="h-1 rounded-none" />
        </motion.div>
      )}

      {/* Page Header */}
      <PageHeader query={query} email={email} />

      {/* Connection Error */}
      {connectionError && status === 'error' && (
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
          <ProgressPanel progress={progress} step={step} status={status} />
        </motion.div>

        {/* Center: Agent Console */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <AgentConsole
            activeChannel={activeChannel}
            logs={logs}
            onChange={setActiveChannel}
          />
        </motion.div>

        {/* Right: Evidence Panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <EvidencePanel evidence={evidence} />
        </motion.div>
      </div>

      {/* Success State - Show Report Button */}
      {status === 'done' && reportMarkdown && (
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

      {/* Demo Mode Indicator */}
      {isDemoMode && (
        <div className="mt-6 text-center">
          <p className="text-xs text-muted-foreground">
            🎭 Demo Mode - Simulated streaming data
          </p>
        </div>
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
