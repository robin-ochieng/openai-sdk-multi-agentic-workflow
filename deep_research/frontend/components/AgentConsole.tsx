'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Copy, Quote, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react'
import { LogEntry } from '@/lib/types'
import { formatTimestamp, copyToClipboard } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface AgentConsoleProps {
  logs: LogEntry[]
  className?: string
}

interface GroupedLogs {
  planner: LogEntry[]
  web: LogEntry[]
  synthesizer: LogEntry[]
  editor: LogEntry[]
}

export function AgentConsole({ logs, className }: AgentConsoleProps) {
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set())
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const groupLogsByAgent = (): GroupedLogs => {
    const grouped: GroupedLogs = {
      planner: [],
      web: [],
      synthesizer: [],
      editor: []
    }

    logs.forEach(log => {
      const message = log.message.toLowerCase()
      if (message.includes('plan') || log.step === 'planning') {
        grouped.planner.push(log)
      } else if (message.includes('search') || message.includes('web') || log.step === 'searching') {
        grouped.web.push(log)
      } else if (message.includes('writ') || message.includes('report') || log.step === 'writing') {
        grouped.synthesizer.push(log)
      } else if (message.includes('email') || log.step === 'sending_email') {
        grouped.editor.push(log)
      } else {
        // Default to web for uncategorized
        grouped.web.push(log)
      }
    })

    return grouped
  }

  const groupedLogs = groupLogsByAgent()

  const toggleChunk = (id: string) => {
    const newExpanded = new Set(expandedChunks)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedChunks(newExpanded)
  }

  const handleCopy = async (text: string, id: string) => {
    const success = await copyToClipboard(text)
    if (success) {
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    }
  }

  const renderLogEntry = (log: LogEntry, index: number) => {
    const isLong = log.message.length > 200
    const isExpanded = expandedChunks.has(log.id)
    const displayMessage = isLong && !isExpanded 
      ? log.message.slice(0, 200) + '...' 
      : log.message

    return (
      <motion.div
        key={log.id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.02 }}
        className="group relative rounded-lg border border-border/50 bg-card/50 p-4 hover:border-border transition-colors"
      >
        {/* Timestamp chip */}
        <div className="flex items-start justify-between mb-2">
          <div className="inline-flex items-center gap-2 text-xs">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-muted/50 text-muted-foreground font-mono">
              {formatTimestamp(log.timestamp)}
            </span>
            {log.emoji && <span className="text-base">{log.emoji}</span>}
            <span className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium',
              log.type === 'error' && 'bg-destructive/10 text-destructive',
              log.type === 'success' && 'bg-green-500/10 text-green-700 dark:text-green-400',
              log.type === 'warning' && 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400',
              log.type === 'info' && 'bg-blue-500/10 text-blue-700 dark:text-blue-400'
            )}>
              {log.type}
            </span>
          </div>
          
          {/* Action buttons - visible on hover */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              onClick={() => handleCopy(log.message, log.id)}
              title="Copy to clipboard"
            >
              {copiedId === log.id ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              title="Quote to report"
            >
              <Quote className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        {/* Log message */}
        <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap font-mono">
          {displayMessage}
        </p>

        {/* Expand/collapse button for long messages */}
        {isLong && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleChunk(log.id)}
            className="mt-2 h-auto py-1 px-2 text-xs font-medium text-muted-foreground hover:text-foreground"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-3 w-3 mr-1" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3 mr-1" />
                Show more
              </>
            )}
          </Button>
        )}
      </motion.div>
    )
  }

  const renderTabContent = (logs: LogEntry[], emptyMessage: string) => {
    if (logs.length === 0) {
      return (
        <div className="flex items-center justify-center h-40 text-sm text-muted-foreground">
          {emptyMessage}
        </div>
      )
    }

    return (
      <div className="space-y-3">
        {logs.map((log, index) => renderLogEntry(log, index))}
      </div>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="space-y-1">
        <h3 className="text-sm font-semibold text-foreground">Agent Console</h3>
        <p className="text-xs text-muted-foreground">
          Live streaming output from research agents
        </p>
      </div>

      <Tabs defaultValue="web" className="w-full">
        <TabsList className="grid w-full grid-cols-4 h-auto p-1">
          <TabsTrigger value="planner" className="text-xs">
            Planner
            {groupedLogs.planner.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-primary/20 text-[10px] font-medium">
                {groupedLogs.planner.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="web" className="text-xs">
            Web
            {groupedLogs.web.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-primary/20 text-[10px] font-medium">
                {groupedLogs.web.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="synthesizer" className="text-xs">
            Synthesizer
            {groupedLogs.synthesizer.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-primary/20 text-[10px] font-medium">
                {groupedLogs.synthesizer.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="editor" className="text-xs">
            Editor
            {groupedLogs.editor.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-primary/20 text-[10px] font-medium">
                {groupedLogs.editor.length}
              </span>
            )}
          </TabsTrigger>
        </TabsList>

        <div className="mt-4 max-h-[600px] overflow-y-auto pr-2 scrollbar-thin">
          <TabsContent value="planner" className="mt-0">
            {renderTabContent(groupedLogs.planner, 'No planning logs yet...')}
          </TabsContent>

          <TabsContent value="web" className="mt-0">
            {renderTabContent(groupedLogs.web, 'No web search logs yet...')}
          </TabsContent>

          <TabsContent value="synthesizer" className="mt-0">
            {renderTabContent(groupedLogs.synthesizer, 'No synthesis logs yet...')}
          </TabsContent>

          <TabsContent value="editor" className="mt-0">
            {renderTabContent(groupedLogs.editor, 'No editor logs yet...')}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  )
}
