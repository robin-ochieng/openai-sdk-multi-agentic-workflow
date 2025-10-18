'use client'

import { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ResearchState } from '@/lib/types'
import { formatTimestamp } from '@/lib/utils'
import {
  Brain,
  Search,
  FileText,
  Mail,
  CheckCircle2,
  Loader2,
  AlertCircle,
} from 'lucide-react'

interface LiveProgressProps {
  researchState: ResearchState
}

const stepIcons = {
  planning: Brain,
  searching: Search,
  writing: FileText,
  sending_email: Mail,
}

const stepLabels = {
  planning: 'Planning Research',
  searching: 'Searching Web',
  writing: 'Writing Report',
  sending_email: 'Sending Email',
}

export function LiveProgress({ researchState }: LiveProgressProps) {
  const logsEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to latest log
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [researchState.logs])

  const currentStep = researchState.currentStep || 'planning'
  const CurrentIcon = stepIcons[currentStep as keyof typeof stepIcons] || Loader2

  return (
    <Card className="overflow-hidden border-2 border-primary/20 bg-gradient-to-br from-card to-card/80">
      <div className="border-b border-border/50 bg-gradient-to-r from-primary/10 to-primary/5 p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
            <CurrentIcon className="h-6 w-6 animate-pulse text-primary" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">
              {stepLabels[currentStep as keyof typeof stepLabels] || 'Processing'}
            </h2>
            <p className="text-sm text-muted-foreground">
              Real-time progress updates from AI agents
            </p>
          </div>
          <Badge variant="secondary" className="h-fit">
            {typeof researchState.progress === 'number' 
              ? researchState.progress 
              : researchState.progress.percentage}%
          </Badge>
        </div>
      </div>

      {/* Logs Container */}
      <div className="max-h-[500px] overflow-y-auto p-6">
        <div className="space-y-2 font-mono text-sm">
          {researchState.logs.length === 0 ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Initializing research agents...</span>
            </div>
          ) : (
            researchState.logs.map((log, index) => (
              <div
                key={index}
                className="group flex items-start gap-3 rounded-lg border border-transparent px-3 py-2 transition-colors hover:border-border/50 hover:bg-muted/30"
              >
                {/* Icon */}
                <div className="mt-0.5 flex-shrink-0">
                  {log.type === 'error' ? (
                    <AlertCircle className="h-4 w-4 text-destructive" />
                  ) : log.type === 'success' ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2 border-primary/30 bg-primary/10" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 overflow-hidden">
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs text-muted-foreground">
                      {formatTimestamp(log.timestamp)}
                    </span>
                    {log.step && (
                      <Badge variant="outline" className="h-5 text-xs">
                        {log.step}
                      </Badge>
                    )}
                  </div>
                  <p
                    className={`mt-1 break-words ${
                      log.type === 'error'
                        ? 'text-destructive'
                        : log.type === 'success'
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-foreground'
                    }`}
                  >
                    {log.message}
                  </p>
                </div>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>

      {/* Step Progress Bar */}
      <div className="border-t border-border/50 bg-muted/30 p-4">
        <div className="flex items-center justify-between gap-2">
          {Object.entries(stepLabels).map(([step, label], index) => {
            const Icon = stepIcons[step as keyof typeof stepIcons]
            const progressValue = typeof researchState.progress === 'number' 
              ? researchState.progress 
              : researchState.progress.percentage
            const isComplete =
              progressValue > (index + 1) * 25 ||
              (step === 'planning' && researchState.searchPlan) ||
              (step === 'searching' && researchState.searchResults) ||
              (step === 'writing' && researchState.report) ||
              (step === 'sending_email' && researchState.emailSent)
            const isCurrent = currentStep === step
            const isPending = !isComplete && !isCurrent

            return (
              <div key={step} className="flex flex-1 flex-col items-center gap-2">
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all ${
                    isComplete
                      ? 'border-green-500 bg-green-500/20 text-green-600 dark:text-green-400'
                      : isCurrent
                      ? 'border-primary bg-primary/20 text-primary'
                      : 'border-border bg-muted text-muted-foreground'
                  }`}
                >
                  {isComplete ? (
                    <CheckCircle2 className="h-5 w-5" />
                  ) : (
                    <Icon className={`h-5 w-5 ${isCurrent ? 'animate-pulse' : ''}`} />
                  )}
                </div>
                <span
                  className={`text-xs font-medium ${
                    isComplete || isCurrent ? 'text-foreground' : 'text-muted-foreground'
                  }`}
                >
                  {label.split(' ')[0]}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </Card>
  )
}
