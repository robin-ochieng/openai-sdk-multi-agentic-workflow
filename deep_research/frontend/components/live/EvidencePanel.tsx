'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ExternalLink, FileText, Filter } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import type { EvidenceItem } from '@/lib/runStore'
import { cn } from '@/lib/utils'

interface EvidencePanelProps {
  evidence: EvidenceItem[]
}

function getDomain(url: string): string {
  try {
    const domain = new URL(url).hostname
    return domain.replace('www.', '')
  } catch {
    return url
  }
}

export function EvidencePanel({ evidence }: EvidencePanelProps) {
  const [filterOpen, setFilterOpen] = useState(false)

  return (
    <Card className="flex h-[600px] flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200/60 p-4 dark:border-slate-800">
        <h2 className="text-lg font-semibold">Evidence</h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setFilterOpen(!filterOpen)}
          className="h-8"
        >
          <Filter className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          {evidence.length === 0 ? (
            <div className="flex h-[480px] items-center justify-center">
              <div className="text-center">
                <div className="mb-4 flex items-center justify-center">
                  <div className="rounded-full bg-slate-100 p-4 dark:bg-slate-900">
                    <FileText className="h-8 w-8 text-slate-400 dark:text-slate-600" />
                  </div>
                </div>
                <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-300">
                  No sources yet
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Evidence will appear here as the web agent finds sources
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {evidence.map((item, index) => (
                <motion.a
                  key={item.id}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    'group block rounded-lg border border-slate-200/60 p-3 transition-all',
                    'hover:border-primary/50 hover:bg-slate-50/50 hover:shadow-sm',
                    'dark:border-slate-800 dark:hover:border-primary/50 dark:hover:bg-slate-900/50'
                  )}
                >
                  <div className="mb-2 flex items-start gap-2">
                    {item.favicon ? (
                      <img
                        src={item.favicon}
                        alt=""
                        className="h-4 w-4 shrink-0 rounded"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none'
                        }}
                      />
                    ) : (
                      <FileText className="h-4 w-4 shrink-0 text-slate-400" />
                    )}
                    <div className="flex-1 space-y-1">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="text-sm font-medium leading-tight text-slate-900 group-hover:text-primary dark:text-slate-100 dark:group-hover:text-primary">
                          {item.title}
                        </h4>
                        <ExternalLink className="h-3 w-3 shrink-0 text-slate-400 opacity-0 transition-opacity group-hover:opacity-100" />
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {getDomain(item.url)}
                      </p>
                    </div>
                  </div>
                  {item.snippet && (
                    <p className="line-clamp-2 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
                      {item.snippet}
                    </p>
                  )}
                </motion.a>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      {evidence.length > 0 && (
        <>
          <Separator />
          <div className="px-4 py-3">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              <span className="font-medium">{evidence.length}</span>{' '}
              {evidence.length === 1 ? 'source' : 'sources'} found
            </p>
          </div>
        </>
      )}
    </Card>
  )
}
