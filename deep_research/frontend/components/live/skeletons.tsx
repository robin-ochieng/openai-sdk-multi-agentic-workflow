import { Card } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

export function ProgressPanelSkeleton() {
  return (
    <Card className="p-6">
      <div className="space-y-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="h-4 w-24 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
              <div className="h-4 w-12 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
            </div>
            <div className="h-2 w-full animate-pulse rounded-full bg-slate-200 dark:bg-slate-800" />
          </div>
        ))}
      </div>
    </Card>
  )
}

export function AgentConsoleSkeleton() {
  return (
    <Card className="flex h-[600px] flex-col">
      <div className="flex gap-2 border-b border-slate-200/60 p-4 dark:border-slate-800">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-9 w-24 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800"
          />
        ))}
      </div>
      <div className="flex-1 space-y-3 p-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="h-4 animate-pulse rounded bg-slate-200 dark:bg-slate-800"
            style={{ width: `${60 + Math.random() * 30}%` }}
          />
        ))}
      </div>
    </Card>
  )
}

export function EvidencePanelSkeleton() {
  return (
    <Card className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="h-5 w-20 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
        <div className="h-8 w-16 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
      </div>
      <Separator className="mb-4" />
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
            <div className="h-3 w-1/2 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
            <div className="h-3 w-full animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
            <div className="h-3 w-5/6 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
          </div>
        ))}
      </div>
    </Card>
  )
}

export function PageHeaderSkeleton() {
  return (
    <div className="mb-8 space-y-2">
      <div className="h-8 w-40 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
      <div className="h-4 w-96 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
    </div>
  )
}
