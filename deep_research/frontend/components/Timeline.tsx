'use client'

import { motion } from 'framer-motion'
import { Brain, Search, FileText, Mail, CheckCircle2, Loader2 } from 'lucide-react'
import { ResearchStep } from '@/lib/types'
import { cn } from '@/lib/utils'

interface TimelineStep {
  id: ResearchStep
  label: string
  icon: any
}

const timelineSteps: TimelineStep[] = [
  { id: 'planning', label: 'Planning', icon: Brain },
  { id: 'searching', label: 'Research', icon: Search },
  { id: 'writing', label: 'Writing', icon: FileText },
  { id: 'sending_email', label: 'Email', icon: Mail }
]

interface TimelineProps {
  currentStep: ResearchStep | null
  progress: number
  className?: string
}

export function Timeline({ currentStep, progress, className }: TimelineProps) {
  const getCurrentStepIndex = () => {
    if (!currentStep) return -1
    return timelineSteps.findIndex(step => step.id === currentStep)
  }

  const currentStepIndex = getCurrentStepIndex()

  return (
    <div className={cn('space-y-6', className)}>
      <div className="space-y-1">
        <h3 className="text-sm font-semibold text-foreground">Research Progress</h3>
        <p className="text-xs text-muted-foreground">
          {progress}% complete
        </p>
      </div>

      <div className="relative space-y-4">
        {/* Vertical line */}
        <div className="absolute left-5 top-4 bottom-4 w-0.5 bg-border" />

        {timelineSteps.map((step, index) => {
          const Icon = step.icon
          const isActive = index === currentStepIndex
          const isCompleted = index < currentStepIndex
          const stepProgress = index === currentStepIndex ? progress : (index < currentStepIndex ? 100 : 0)

          return (
            <div key={step.id} className="relative flex items-start gap-3">
              {/* Icon container */}
              <div className="relative z-10 flex-shrink-0">
                <motion.div
                  className={cn(
                    'flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors',
                    isCompleted
                      ? 'border-green-500 bg-green-500'
                      : isActive
                      ? 'border-primary bg-primary'
                      : 'border-border bg-background'
                  )}
                  animate={isActive ? {
                    boxShadow: [
                      '0 0 0 0 hsl(var(--primary) / 0.4)',
                      '0 0 0 8px hsl(var(--primary) / 0)',
                    ]
                  } : {}}
                  transition={isActive ? {
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeOut'
                  } : {}}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="h-5 w-5 text-white" />
                  ) : isActive ? (
                    <Loader2 className="h-5 w-5 text-primary-foreground animate-spin" />
                  ) : (
                    <Icon className={cn(
                      'h-5 w-5',
                      isActive || isCompleted ? 'text-primary-foreground' : 'text-muted-foreground'
                    )} />
                  )}
                </motion.div>
              </div>

              {/* Step content */}
              <div className="flex-1 pb-6">
                <div className="flex items-center justify-between mb-2">
                  <h4 className={cn(
                    'text-sm font-medium',
                    isActive || isCompleted ? 'text-foreground' : 'text-muted-foreground'
                  )}>
                    {step.label}
                  </h4>
                  {(isActive || isCompleted) && (
                    <span className="text-xs font-medium text-muted-foreground">
                      {stepProgress}%
                    </span>
                  )}
                </div>

                {/* Progress bar for active/completed steps */}
                {(isActive || isCompleted) && (
                  <div className="h-1 w-full overflow-hidden rounded-full bg-secondary">
                    <motion.div
                      className={cn(
                        'h-full',
                        isCompleted ? 'bg-green-500' : 'bg-primary'
                      )}
                      initial={{ width: 0 }}
                      animate={{ width: `${stepProgress}%` }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                    />
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
