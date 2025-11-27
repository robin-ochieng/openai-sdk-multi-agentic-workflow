'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, Globe, FileText, Mail, Terminal, ChevronRight, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Channel, LogEntry } from '@/lib/runStore'
import { cn } from '@/lib/utils'

interface AgentConsoleProps {
  activeChannel: Channel
  logs: LogEntry[]
  onChange: (channel: Channel) => void
}

const channels: { key: Channel; label: string; icon: typeof Activity; gradient: string }[] = [
  { key: 'planner', label: 'Planner', icon: Activity, gradient: 'from-violet-500 to-purple-600' },
  { key: 'web', label: 'Web', icon: Globe, gradient: 'from-blue-500 to-cyan-500' },
  { key: 'synthesizer', label: 'Synthesizer', icon: FileText, gradient: 'from-emerald-500 to-teal-500' },
  { key: 'editor', label: 'Editor', icon: Mail, gradient: 'from-orange-500 to-amber-500' },
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

function LogIcon({ level }: { level: string }) {
  switch (level) {
    case 'error':
      return <AlertCircle className="h-3.5 w-3.5 text-red-500" />
    case 'warn':
      return <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
    default:
      return <Info className="h-3.5 w-3.5 text-blue-500" />
  }
}

export function AgentConsole({ activeChannel, logs, onChange }: AgentConsoleProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const [isExpanded, setIsExpanded] = useState(true)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [logs.length])

  const filteredLogs = logs.filter(log => log.channel === activeChannel)
  const activeChannelConfig = channels.find(c => c.key === activeChannel)

  return (
    <Card className="flex h-[600px] flex-col overflow-hidden border-0 bg-gradient-to-b from-white to-slate-50/80 shadow-lg dark:from-slate-900 dark:to-slate-950">
      {/* Header */}
      <div className="relative overflow-hidden border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white px-4 py-3 dark:border-slate-800 dark:from-slate-900 dark:to-slate-800/50">
        <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br from-violet-500/10 to-purple-500/5 blur-2xl" />
        <div className="relative flex items-center gap-3">
          <div className={cn(
            'flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br shadow-lg',
            activeChannelConfig?.gradient
          )}>
            <Terminal className="h-4 w-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">Agent Console</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Real-time agent activity logs</p>
          </div>
        </div>
      </div>

      {/* Channel Tabs */}
      <div className="flex gap-1 border-b border-slate-100 bg-slate-50/80 p-2 dark:border-slate-800 dark:bg-slate-900/80">
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
                'relative flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-white text-slate-900 shadow-md dark:bg-slate-800 dark:text-white'
                  : 'text-slate-500 hover:bg-white/80 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-200'
              )}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTabBg"
                  className={cn(
                    'absolute inset-0 rounded-lg bg-gradient-to-r opacity-10',
                    channel.gradient
                  )}
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                />
              )}
              <div className={cn(
                'relative flex h-6 w-6 items-center justify-center rounded-md',
                isActive 
                  ? `bg-gradient-to-br ${channel.gradient}` 
                  : 'bg-slate-200 dark:bg-slate-700'
              )}>
                <Icon className={cn('h-3.5 w-3.5', isActive ? 'text-white' : 'text-slate-500 dark:text-white')} />
              </div>
              <span className="relative">{channel.label}</span>
              {hasLogs && (
                <span className={cn(
                  'relative ml-1 flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-bold',
                  isActive 
                    ? 'bg-slate-900/10 text-slate-700 dark:bg-white/20 dark:text-white' 
                    : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                )}>
                  {channelLogs.length}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Console Output */}
      <ScrollArea className="flex-1 bg-slate-50/50 dark:bg-[#0d1117]">
        <div 
          ref={scrollRef}
          className="p-4"
          aria-live="polite"
          aria-atomic="false"
        >
          {filteredLogs.length === 0 ? (
            <div className="flex h-[420px] items-center justify-center">
              <div className="text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-100 to-slate-50 shadow-inner dark:from-slate-800 dark:to-slate-900">
                  <Terminal className="h-8 w-8 text-slate-300 dark:text-slate-600" />
                </div>
                <p className="font-medium text-slate-500 dark:text-slate-400">
                  Awaiting agent activity...
                </p>
                <p className="mt-2 text-sm text-slate-400 dark:text-slate-600">
                  Logs will stream here as the{' '}
                  <span className={cn(
                    'bg-gradient-to-r bg-clip-text font-semibold text-transparent',
                    activeChannelConfig?.gradient
                  )}>
                    {activeChannelConfig?.label}
                  </span>{' '}
                  agent works
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-1">
              <AnimatePresence mode="popLayout">
                {filteredLogs.map((log, index) => (
                  <motion.div
                    key={`${log.ts}-${index}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className={cn(
                      'group flex items-start gap-3 rounded-lg px-3 py-2 font-mono text-sm transition-colors',
                      log.level === 'error' && 'bg-red-50 hover:bg-red-100 dark:bg-red-950/30 dark:hover:bg-red-950/50',
                      log.level === 'warn' && 'bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/20 dark:hover:bg-amber-950/30',
                      log.level === 'info' && 'hover:bg-slate-100 dark:hover:bg-slate-800/50'
                    )}
                  >
                    <ChevronRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400 transition-transform group-hover:translate-x-0.5 dark:text-slate-600" />
                    <span className="shrink-0 text-slate-400 tabular-nums dark:text-slate-500">
                      {formatTimestamp(log.ts)}
                    </span>
                    <div className="flex shrink-0 items-center gap-1.5">
                      <LogIcon level={log.level} />
                      <span
                        className={cn(
                          'rounded px-1.5 py-0.5 text-xs font-medium uppercase tracking-wide',
                          log.level === 'info' && 'bg-blue-100 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400',
                          log.level === 'warn' && 'bg-amber-100 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400',
                          log.level === 'error' && 'bg-red-100 text-red-600 dark:bg-red-950/50 dark:text-red-400'
                        )}
                      >
                        {log.level}
                      </span>
                    </div>
                    <span className="flex-1 text-slate-700 leading-relaxed dark:text-slate-300">
                      {log.text}
                    </span>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50/80 px-4 py-2.5 dark:border-slate-800 dark:bg-slate-900/80">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 animate-pulse rounded-full bg-green-500 shadow-lg shadow-green-500/50" />
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Live</span>
          </div>
          <div className="h-4 w-px bg-slate-200 dark:bg-slate-700" />
          <p className="text-xs text-slate-400 dark:text-slate-500">
            <span className="font-bold text-slate-600 dark:text-slate-400">{filteredLogs.length}</span>
            {' '}{filteredLogs.length === 1 ? 'entry' : 'entries'}
          </p>
        </div>
        <div className={cn(
          'rounded-md bg-gradient-to-r px-2 py-1 text-xs font-medium text-white',
          activeChannelConfig?.gradient
        )}>
          {activeChannelConfig?.label}
        </div>
      </div>
    </Card>
  )
}
