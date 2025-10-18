'use client'

import { motion } from 'framer-motion'
import { ChevronRight, Home } from 'lucide-react'
import { ResearchState } from '@/lib/types'
import { Timeline } from './Timeline'
import { AgentConsole } from './AgentConsole'
import { EvidenceDrawer } from './EvidenceDrawer'
import { cn } from '@/lib/utils'
import { useState } from 'react'

interface RunLayoutProps {
  researchState: ResearchState
  runId?: string
  className?: string
}

export function RunLayout({ researchState, runId = '001', className }: RunLayoutProps) {
  const [showMobileDrawer, setShowMobileDrawer] = useState<'timeline' | 'evidence' | null>(null)

  const progress = typeof researchState.progress === 'number' 
    ? researchState.progress 
    : researchState.progress.percentage

  return (
    <div className={cn('space-y-6', className)}>
      {/* Breadcrumb */}
      <motion.nav
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-2 text-sm"
        aria-label="Breadcrumb"
      >
        <a 
          href="/" 
          className="flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors focus-ring-premium rounded px-2 py-1"
        >
          <Home className="h-3.5 w-3.5" />
          Home
        </a>
        <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="text-muted-foreground">Run #{runId}</span>
        <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="font-medium text-foreground">Live</span>
      </motion.nav>

      {/* Three-pane layout - Desktop */}
      <div className="hidden lg:grid lg:grid-cols-[280px_minmax(0,1fr)_340px] gap-6">
        {/* Left: Timeline (sticky) */}
        <motion.aside
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="sticky top-6 h-fit"
        >
          <div className="rounded-2xl border border-border/50 bg-card p-6 shadow-premium">
            <Timeline
              currentStep={researchState.currentStep || null}
              progress={progress}
            />
          </div>
        </motion.aside>

        {/* Center: Agent Console */}
        <motion.main
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="min-w-0"
        >
          <div className="rounded-2xl border border-border/50 bg-card p-6 shadow-premium">
            <AgentConsole logs={researchState.logs} />
          </div>
        </motion.main>

        {/* Right: Evidence Drawer */}
        <motion.aside
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="sticky top-6 h-fit max-h-[calc(100vh-3rem)] overflow-hidden"
        >
          <div className="rounded-2xl border border-border/50 bg-card p-6 shadow-premium h-full">
            <EvidenceDrawer sources={[]} />
          </div>
        </motion.aside>
      </div>

      {/* Mobile/Tablet Layout */}
      <div className="lg:hidden space-y-4">
        {/* Horizontal Timeline Stepper */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-border/50 bg-card p-4 shadow-premium"
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">Progress</h3>
            <span className="text-xs font-medium text-muted-foreground">{progress}%</span>
          </div>
          <div className="flex items-center gap-2">
            {['Planning', 'Research', 'Writing', 'Email'].map((step, index) => {
              const stepProgress = Math.floor((index + 1) * 25)
              const isActive = progress >= stepProgress - 25 && progress < stepProgress
              const isCompleted = progress >= stepProgress
              
              return (
                <div key={step} className="flex-1">
                  <div className={cn(
                    'h-1.5 rounded-full transition-colors',
                    isCompleted ? 'bg-green-500' : isActive ? 'bg-primary' : 'bg-muted'
                  )} />
                  <p className="text-[10px] mt-1 text-center text-muted-foreground">
                    {step}
                  </p>
                </div>
              )
            })}
          </div>
        </motion.div>

        {/* Agent Console */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl border border-border/50 bg-card p-4 shadow-premium"
        >
          <AgentConsole logs={researchState.logs} />
        </motion.div>

        {/* Collapsible Evidence */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-2xl border border-border/50 bg-card p-4 shadow-premium"
        >
          <EvidenceDrawer sources={[]} />
        </motion.div>
      </div>
    </div>
  )
}
