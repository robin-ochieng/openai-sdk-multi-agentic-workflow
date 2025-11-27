'use client'

import { useState } from 'react'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { ExternalLink, FileText, Filter, Search, Link2, BookOpen, Globe, ChevronRight } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
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

function getSourceIcon(url: string) {
  const domain = getDomain(url).toLowerCase()
  if (domain.includes('wikipedia')) return BookOpen
  if (domain.includes('github')) return FileText
  return Globe
}

export function EvidencePanel({ evidence }: EvidencePanelProps) {
  const [filterOpen, setFilterOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  
  const filteredEvidence = searchQuery 
    ? evidence.filter(item => 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.snippet?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : evidence

  return (
    <Card className="flex h-[600px] flex-col overflow-hidden border-0 bg-gradient-to-b from-white to-slate-50/50 shadow-lg dark:from-slate-900 dark:to-slate-950">
      {/* Header */}
      <div className="relative overflow-hidden border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white p-5 dark:border-slate-800 dark:from-slate-900 dark:to-slate-800/50">
        <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br from-blue-500/10 to-cyan-500/5 blur-2xl" />
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/25">
              <Link2 className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold tracking-tight">Evidence Sources</h2>
              <p className="mt-0.5 text-xs text-muted-foreground">
                {evidence.length} {evidence.length === 1 ? 'source' : 'sources'} collected
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setFilterOpen(!filterOpen)}
            className={cn(
              "h-9 w-9 rounded-lg p-0 transition-all",
              filterOpen && "bg-primary/10 text-primary"
            )}
          >
            <Filter className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Search Bar - Expandable */}
        <AnimatePresence>
          {filterOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="relative mt-4">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search sources..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-4 text-sm outline-none transition-all placeholder:text-slate-400 focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-slate-900"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          {filteredEvidence.length === 0 ? (
            <div className="flex h-[420px] items-center justify-center">
              <div className="text-center">
                <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-100 to-slate-50 shadow-inner dark:from-slate-800 dark:to-slate-900">
                  <Search className="h-10 w-10 text-slate-300 dark:text-slate-600" />
                </div>
                <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
                  {searchQuery ? 'No matching sources' : 'No sources yet'}
                </h3>
                <p className="mx-auto max-w-xs text-xs text-slate-500 dark:text-slate-400">
                  {searchQuery 
                    ? 'Try adjusting your search query'
                    : 'Evidence will appear here as the research agent discovers relevant sources'
                  }
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {filteredEvidence.map((item, index) => {
                  const SourceIcon = getSourceIcon(item.url)
                  return (
                    <motion.a
                      key={item.id}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      initial={{ opacity: 0, y: 20, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -20, scale: 0.95 }}
                      transition={{ delay: index * 0.03, duration: 0.3 }}
                      className={cn(
                        'group relative block overflow-hidden rounded-xl border border-slate-200/80 bg-white p-4 transition-all duration-300',
                        'hover:border-blue-200 hover:shadow-lg hover:shadow-blue-500/10',
                        'dark:border-slate-800 dark:bg-slate-900/50 dark:hover:border-blue-900/50'
                      )}
                    >
                      {/* Hover gradient overlay */}
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/0 to-cyan-500/0 opacity-0 transition-opacity duration-300 group-hover:opacity-5" />
                      
                      {/* Top row: Icon, Title, Link */}
                      <div className="relative mb-3 flex items-start gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-slate-100 to-slate-50 transition-all group-hover:from-blue-100 group-hover:to-cyan-50 dark:from-slate-800 dark:to-slate-900 dark:group-hover:from-blue-950 dark:group-hover:to-cyan-950">
                          {item.favicon ? (
                            <Image
                              src={item.favicon}
                              alt=""
                              width={20}
                              height={20}
                              className="h-5 w-5 rounded"
                              unoptimized
                              onError={(event) => {
                                event.currentTarget.style.display = 'none'
                                const fallback = event.currentTarget.parentElement?.querySelector('.fallback-icon')
                                if (fallback) (fallback as HTMLElement).style.display = 'block'
                              }}
                            />
                          ) : null}
                          <SourceIcon 
                            className={cn(
                              "h-5 w-5 text-slate-400 dark:text-slate-500 fallback-icon",
                              item.favicon && "hidden"
                            )} 
                          />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="text-sm font-semibold leading-tight text-slate-900 transition-colors group-hover:text-blue-600 dark:text-slate-100 dark:group-hover:text-blue-400 line-clamp-2">
                              {item.title}
                            </h4>
                            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 opacity-0 transition-all group-hover:opacity-100 dark:bg-slate-800">
                              <ExternalLink className="h-3 w-3 text-slate-500" />
                            </div>
                          </div>
                          <div className="mt-1 flex items-center gap-1.5">
                            <Globe className="h-3 w-3 text-slate-400" />
                            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
                              {getDomain(item.url)}
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      {/* Snippet */}
                      {item.snippet && (
                        <div className="relative pl-[52px]">
                          <p className="line-clamp-2 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
                            {item.snippet}
                          </p>
                        </div>
                      )}
                      
                      {/* Bottom action hint */}
                      <div className="relative mt-3 flex items-center gap-1 pl-[52px] text-xs text-blue-600 opacity-0 transition-opacity group-hover:opacity-100 dark:text-blue-400">
                        <span>View source</span>
                        <ChevronRight className="h-3 w-3" />
                      </div>
                    </motion.a>
                  )
                })}
              </AnimatePresence>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      {evidence.length > 0 && (
        <div className="border-t border-slate-100 bg-slate-50/80 px-5 py-3 dark:border-slate-800 dark:bg-slate-900/80">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              <span className="font-bold text-slate-700 dark:text-slate-300">{evidence.length}</span>
              {' '}{evidence.length === 1 ? 'source' : 'sources'} collected
            </p>
            <div className="flex items-center gap-1.5">
              <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
              <span className="text-xs font-medium text-blue-600 dark:text-blue-400">Collecting</span>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}
