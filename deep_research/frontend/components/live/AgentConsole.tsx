'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Activity, Globe, FileText, Mail } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Channel, LogEntry } from '@/lib/runStore'
import { cn } from '@/lib/utils'

interface AgentConsoleProps {
  activeChannel: Channel
  logs: LogEntry[]
  onChange: (channel: Channel) => void
}

const channels: { key: Channel; label: string; icon: typeof Activity }[] = [
  { key: 'planner', label: 'Planner', icon: Activity },
  { key: 'web', label: 'Web', icon: Globe },
  { key: 'synthesizer', label: 'Synthesizer', icon: FileText },
  { key: 'editor', label: 'Editor', icon: Mail },
]

function formatTimestamp(ts: string) {
  try {
    const date = new Date(ts)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
  } catch {
    return '00:00:00'
  }
}

export function AgentConsole({ activeChannel, logs, onChange }: AgentConsoleProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [logs.length])

  const filteredLogs = logs.filter(log => log.channel === activeChannel)

  return (
    <Card className="flex h-[600px] flex-col overflow-hidden">
      {/* Channel Tabs */}
      <div className="flex gap-1 border-b border-slate-200/60 bg-slate-50/50 p-2 dark:border-slate-800 dark:bg-slate-900/50">
        {channels.map((channel) => {
          const Icon = channel.icon
          const channelLogs = logs.filter(l => l.channel === channel.key)
          const hasLogs = channelLogs.length > 0
          const isActive = activeChannel === channel.key

          return (
            <button
              key={channel.key}
              onClick={() => onChange(channel.key)}
              className={cn(
                'relative flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all',
                isActive
                  ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-950 dark:text-slate-100'
                  : 'text-slate-600 hover:bg-white/50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-900/50 dark:hover:text-slate-100'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{channel.label}</span>
              {hasLogs && !isActive && (
                <span className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary/20 text-xs font-semibold text-primary">
                  {channelLogs.length}
                </span>
              )}
              {isActive && hasLogs && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 rounded-lg border-2 border-primary/20"
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Console Output */}
      <ScrollArea className="flex-1">
        <div 
          ref={scrollRef}
          className="p-4"
          aria-live="polite"
          aria-atomic="false"
        >
          {filteredLogs.length === 0 ? (
            <div className="flex h-[500px] items-center justify-center">
              <div className="text-center">
                <Activity className="mx-auto mb-3 h-12 w-12 text-slate-300 dark:text-slate-700" />
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                  Waiting for agent output...
                </p>
                <p className="mt-1 text-xs text-slate-400 dark:text-slate-600">
                  Logs will appear here as the {channels.find(c => c.key === activeChannel)?.label} agent works
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-1 font-mono text-[15px] leading-7">
              {filteredLogs.map((log, index) => (
                <motion.div
                  key={`${log.ts}-${index}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                  className={cn(
                    'flex gap-3 rounded px-2 py-1',
                    log.level === 'error' && 'bg-red-50 dark:bg-red-950/20',
                    log.level === 'warn' && 'bg-yellow-50 dark:bg-yellow-950/20'
                  )}
                >
                  <span className="shrink-0 text-slate-400 dark:text-slate-600">
                    [{formatTimestamp(log.ts)}]
                  </span>
                  <span
                    className={cn(
                      'shrink-0 font-semibold',
                      log.level === 'info' && 'text-blue-600 dark:text-blue-400',
                      log.level === 'warn' && 'text-yellow-600 dark:text-yellow-400',
                      log.level === 'error' && 'text-red-600 dark:text-red-400'
                    )}
                  >
                    ({log.level})
                  </span>
                  <span className="flex-1 text-slate-700 dark:text-slate-300">
                    {log.text}
                  </span>
                </motion.div>
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t border-slate-200/60 bg-slate-50/50 px-4 py-2 dark:border-slate-800 dark:bg-slate-900/50">
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {filteredLogs.length} {filteredLogs.length === 1 ? 'entry' : 'entries'} •{' '}
          <span className="font-medium">{channels.find(c => c.key === activeChannel)?.label}</span>
        </p>
      </div>
    </Card>
  )
}
