'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, Circle, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import type { ResearchStep, RunState } from '@/lib/runStore'
import { cn } from '@/lib/utils'

interface ProgressPanelProps {
  progress: RunState['progress']
  step: ResearchStep
  status: RunState['status']
}

const steps: { key: ResearchStep; label: string; icon: typeof Circle }[] = [
  { key: 'planning', label: 'Planning', icon: Circle },
  { key: 'research', label: 'Research', icon: Circle },
  { key: 'writing', label: 'Writing', icon: Circle },
  { key: 'email', label: 'Email', icon: Circle },
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

  return (
    <Card className="p-6">
      <h2 className="mb-6 text-lg font-semibold">Research Progress</h2>
      <div className="space-y-6">
        {steps.map((s, index) => {
          const value = progress[s.key]
          const stepStatus = getStepStatus(s.key)
          const isActive = stepStatus === 'active'
          const isComplete = stepStatus === 'complete'

          return (
            <motion.div
              key={s.key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {isComplete ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-500" />
                  ) : isActive ? (
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  ) : (
                    <Circle className="h-5 w-5 text-slate-300 dark:text-slate-700" />
                  )}
                  <span
                    className={cn(
                      'text-sm font-medium',
                      isActive && 'text-primary',
                      isComplete && 'text-slate-700 dark:text-slate-300',
                      !isActive && !isComplete && 'text-slate-400 dark:text-slate-600'
                    )}
                  >
                    {s.label}
                  </span>
                </div>
                <span
                  className={cn(
                    'text-sm font-mono',
                    isActive && 'text-primary font-semibold',
                    isComplete && 'text-green-600 dark:text-green-500',
                    !isActive && !isComplete && 'text-slate-400 dark:text-slate-600'
                  )}
                >
                  {value}%
                </span>
              </div>
              <Progress 
                value={value} 
                className={cn(
                  "h-2",
                  isActive && "animate-pulse"
                )}
              />
              {isActive && value < 100 && (
                <p className="text-xs text-muted-foreground">
                  In progress...
                </p>
              )}
            </motion.div>
          )
        })}
      </div>

      {status === 'done' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 rounded-lg bg-green-50 p-4 dark:bg-green-950/20"
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-500" />
            <span className="text-sm font-medium text-green-900 dark:text-green-100">
              Research Complete!
            </span>
          </div>
        </motion.div>
      )}

      {status === 'error' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 rounded-lg bg-red-50 p-4 dark:bg-red-950/20"
        >
          <span className="text-sm font-medium text-red-900 dark:text-red-100">
            Research failed
          </span>
        </motion.div>
      )}
    </Card>
  )
}
