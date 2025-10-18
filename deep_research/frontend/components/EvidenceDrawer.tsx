'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ExternalLink, Filter, X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Source {
  id: string
  title: string
  domain: string
  url: string
  snippet: string
  credibility: 'High' | 'Medium' | 'Low'
  type?: string
  date?: string
}

interface EvidenceDrawerProps {
  sources: Source[]
  className?: string
}

const credibilityColors = {
  High: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/30',
  Medium: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/30',
  Low: 'bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/30'
}

// Mock sources for demonstration (will be replaced with real data)
const mockSources: Source[] = [
  {
    id: '1',
    title: 'Latest Quantum Computing Breakthroughs',
    domain: 'nature.com',
    url: 'https://nature.com/quantum-computing',
    snippet: 'Researchers have achieved a new milestone in quantum error correction, demonstrating stable qubits for over 1000 operations...',
    credibility: 'High',
    type: 'Research Paper',
    date: '2024-10-15'
  },
  {
    id: '2',
    title: 'Practical Applications of Quantum Computing',
    domain: 'sciencedaily.com',
    url: 'https://sciencedaily.com/quantum-apps',
    snippet: 'New quantum algorithms show promise for drug discovery and optimization problems in logistics...',
    credibility: 'High',
    type: 'News Article',
    date: '2024-10-12'
  },
  {
    id: '3',
    title: 'Understanding Quantum Supremacy',
    domain: 'medium.com',
    url: 'https://medium.com/quantum-supremacy',
    snippet: 'An overview of what quantum supremacy means and how it impacts various industries...',
    credibility: 'Medium',
    type: 'Blog Post',
    date: '2024-10-08'
  }
]

export function EvidenceDrawer({ sources = mockSources, className }: EvidenceDrawerProps) {
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [filters, setFilters] = useState({
    credibility: 'All',
    type: 'All',
    domain: 'All'
  })

  const filteredSources = sources.filter(source => {
    if (filters.credibility !== 'All' && source.credibility !== filters.credibility) return false
    if (filters.type !== 'All' && source.type !== filters.type) return false
    if (filters.domain !== 'All' && source.domain !== filters.domain) return false
    return true
  })

  const getFavicon = (domain: string) => {
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground">Evidence</h3>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2 text-xs"
          >
            <Filter className="h-3 w-3 mr-1" />
            Filter
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          {filteredSources.length} source{filteredSources.length !== 1 ? 's' : ''} found
        </p>
      </div>

      {/* Source cards */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 scrollbar-thin">
        {filteredSources.map((source, index) => (
          <motion.div
            key={source.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={cn(
              'group rounded-xl border bg-card p-4 transition-all duration-200 hover:shadow-premium cursor-pointer',
              selectedSource?.id === source.id && 'ring-2 ring-primary'
            )}
            onClick={() => setSelectedSource(selectedSource?.id === source.id ? null : source)}
          >
            {/* Header with favicon and domain */}
            <div className="flex items-start gap-3 mb-3">
              <img
                src={getFavicon(source.domain)}
                alt={`${source.domain} favicon`}
                className="h-5 w-5 rounded flex-shrink-0 mt-0.5"
                onError={(e) => {
                  e.currentTarget.style.display = 'none'
                }}
              />
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-foreground line-clamp-2 mb-1">
                  {source.title}
                </h4>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-muted-foreground">
                    {source.domain}
                  </span>
                  {source.date && (
                    <span className="text-xs text-muted-foreground">
                      • {new Date(source.date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              
              {/* Credibility badge */}
              <Badge 
                variant="outline" 
                className={cn('text-[10px] px-2 py-0.5 font-medium', credibilityColors[source.credibility])}
              >
                {source.credibility}
              </Badge>
            </div>

            {/* Snippet */}
            <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed mb-3">
              {source.snippet}
            </p>

            {/* Footer with type and link */}
            <div className="flex items-center justify-between">
              {source.type && (
                <Badge variant="secondary" className="text-[10px]">
                  {source.type}
                </Badge>
              )}
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs opacity-0 group-hover:opacity-100 transition-opacity ml-auto"
                onClick={(e) => {
                  e.stopPropagation()
                  window.open(source.url, '_blank', 'noopener,noreferrer')
                }}
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                Open
              </Button>
            </div>

            {/* Expanded preview */}
            {selectedSource?.id === source.id && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mt-4 pt-4 border-t border-border"
              >
                <div className="space-y-2">
                  <p className="text-xs text-foreground leading-relaxed">
                    {source.snippet}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs"
                      onClick={(e) => {
                        e.stopPropagation()
                        window.open(source.url, '_blank', 'noopener,noreferrer')
                      }}
                    >
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Visit Source
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}

        {filteredSources.length === 0 && (
          <div className="flex items-center justify-center h-40 text-sm text-muted-foreground">
            No sources match your filters
          </div>
        )}
      </div>
    </div>
  )
}
