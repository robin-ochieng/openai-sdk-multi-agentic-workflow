'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle2, Circle, Loader2, Sparkles, Brain, Search, PenTool, Mail } from 'lucide-react'
import { Card } from '@/components/ui/card'
import type { ResearchStep, RunState } from '@/lib/runStore'
import { cn } from '@/lib/utils'

interface ProgressPanelProps {
  progress: RunState['progress']
  step: ResearchStep
  status: RunState['status']
}

const steps: { key: ResearchStep; label: string; description: string; icon: typeof Circle; color: string }[] = [
  { key: 'planning', label: 'Planning', description: 'Creating research strategy', icon: Brain, color: 'from-violet-500 to-purple-600' },
  { key: 'research', label: 'Research', description: 'Searching & gathering data', icon: Search, color: 'from-blue-500 to-cyan-500' },
  { key: 'writing', label: 'Writing', description: 'Synthesizing report', icon: PenTool, color: 'from-emerald-500 to-teal-500' },
  { key: 'email', label: 'Email', description: 'Sending report', icon: Mail, color: 'from-orange-500 to-amber-500' },
]

export function ProgressPanel({ progress, step, status }: ProgressPanelProps) {
  const getStepStatus = (stepKey: ResearchStep) => {
    const value = progress[stepKey]
    if (value === 100) return 'complete'
    if (stepKey === step && status === 'running') return 'active'
    const stepIndex = steps.findIndex(s => s.key === stepKey)
    const currentIndex = steps.findIndex(s => s.key === step)
    if (stepIndex < currentIndex) return 'complete'
    return 'pending'
  }

  const overallProgress = Object.values(progress).reduce((a, b) => a + b, 0) / 4

  return (
    <Card className="overflow-hidden border-0 bg-gradient-to-b from-white to-slate-50/50 shadow-lg dark:from-slate-900 dark:to-slate-950">
      {/* Header with gradient */}
      <div className="relative overflow-hidden border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white p-5 dark:border-slate-800 dark:from-slate-900 dark:to-slate-800/50">
        <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br from-primary/10 to-primary/5 blur-2xl" />
        <div className="relative flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold tracking-tight">Research Progress</h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {status === 'done' ? 'Completed' : status === 'error' ? 'Failed' : 'In progress...'}
            </p>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-primary/20 to-primary/5">
            <span className="text-lg font-bold text-primary">{Math.round(overallProgress)}%</span>
          </div>
        </div>
      </div>

      {/* Steps */}
      <div className="p-5">
        <div className="space-y-4">
          {steps.map((s, index) => {
            const value = progress[s.key]
            const stepStatus = getStepStatus(s.key)
            const isActive = stepStatus === 'active'
            const isComplete = stepStatus === 'complete'
            const isPending = stepStatus === 'pending'
            const Icon = s.icon

            return (
              <motion.div
                key={s.key}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={cn(
                  'relative rounded-xl border p-4 transition-all duration-300',
                  isActive && 'border-primary/30 bg-primary/5 shadow-sm shadow-primary/10',
                  isComplete && 'border-green-200 bg-green-50/50 dark:border-green-900/50 dark:bg-green-950/20',
                  isPending && 'border-slate-100 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-900/50'
                )}
              >
                {/* Active glow effect */}
                {isActive && (
                  <div className="absolute inset-0 -z-10 animate-pulse rounded-xl bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5" />
                )}

                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div
                    className={cn(
                      'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg transition-all',
                      isComplete && 'bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/25',
                      isActive && `bg-gradient-to-br ${s.color} text-white shadow-lg`,
                      isPending && 'bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-600'
                    )}
                  >
                    {isComplete ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : isActive ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                      >
                        <Icon className="h-5 w-5" />
                      </motion.div>
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <div>
                        <h3
                          className={cn(
                            'font-semibold',
                            isActive && 'text-primary',
                            isComplete && 'text-green-700 dark:text-green-400',
                            isPending && 'text-slate-400 dark:text-slate-600'
                          )}
                        >
                          {s.label}
                        </h3>
                        <p
                          className={cn(
                            'text-xs mt-0.5',
                            isActive && 'text-primary/70',
                            isComplete && 'text-green-600/70 dark:text-green-500/70',
                            isPending && 'text-slate-400 dark:text-slate-600'
                          )}
                        >
                          {s.description}
                        </p>
                      </div>
                      <span
                        className={cn(
                          'text-sm font-mono font-bold tabular-nums',
                          isComplete && 'text-green-600 dark:text-green-500',
                          isActive && 'text-primary',
                          isPending && 'text-slate-300 dark:text-slate-700'
                        )}
                      >
                        {value}%
                      </span>
                    </div>

                    {/* Progress bar */}
                    <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-200/50 dark:bg-slate-800">
                      <motion.div
                        className={cn(
                          'h-full rounded-full',
                          isComplete && 'bg-gradient-to-r from-green-500 to-emerald-500',
                          isActive && `bg-gradient-to-r ${s.color}`,
                          isPending && 'bg-slate-300 dark:bg-slate-700'
                        )}
                        initial={{ width: 0 }}
                        animate={{ width: `${value}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Success State */}
      <AnimatePresence>
        {status === 'done' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mx-5 mb-5"
          >
            <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 p-4 text-white shadow-lg shadow-green-500/25">
              <div className="absolute -right-2 -top-2 opacity-20">
                <Sparkles className="h-16 w-16" />
              </div>
              <div className="relative flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/20 backdrop-blur-sm">
                  <CheckCircle2 className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold">Research Complete!</h3>
                  <p className="text-sm text-white/80">Your report is ready to view</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error State */}
      <AnimatePresence>
        {status === 'error' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mx-5 mb-5"
          >
            <div className="rounded-xl bg-gradient-to-r from-red-500 to-rose-600 p-4 text-white shadow-lg shadow-red-500/25">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/20">
                  <Circle className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold">Research Failed</h3>
                  <p className="text-sm text-white/80">Please try again</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}
