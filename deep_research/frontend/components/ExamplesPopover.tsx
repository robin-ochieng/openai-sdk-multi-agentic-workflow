'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Lightbulb, Brain, Globe, TrendingUp, Sparkles, BookOpen } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ExampleQuery {
  label: string
  query: string
  icon: any
  color: string
}

const examples: ExampleQuery[] = [
  {
    label: 'Quantum Computing',
    query: 'Latest breakthroughs in quantum computing and their practical applications in cryptography and drug discovery',
    icon: Brain,
    color: 'blue'
  },
  {
    label: 'AI in Healthcare',
    query: 'Impact of artificial intelligence on healthcare diagnostics, patient care, and medical research in 2024-2025',
    icon: TrendingUp,
    color: 'green'
  },
  {
    label: 'Renewable Energy',
    query: 'Current state of renewable energy adoption, emerging technologies, and future sustainability trends',
    icon: Globe,
    color: 'emerald'
  },
  {
    label: 'Remote Work Tech',
    query: 'Emerging trends in remote work technology, collaboration tools, and hybrid workplace solutions',
    icon: Lightbulb,
    color: 'purple'
  },
  {
    label: 'Space Exploration',
    query: 'Recent developments in space exploration, commercial spaceflight, and Mars colonization efforts',
    icon: Sparkles,
    color: 'indigo'
  },
  {
    label: 'Large Language Models',
    query: 'Evolution of large language models, their applications, and impact on software development in 2024-2025',
    icon: BookOpen,
    color: 'pink'
  }
]

const colorClasses = {
  blue: 'bg-blue-500/10 hover:bg-blue-500/20 border-blue-500/30 hover:border-blue-500/50 text-blue-700 dark:text-blue-400',
  green: 'bg-green-500/10 hover:bg-green-500/20 border-green-500/30 hover:border-green-500/50 text-green-700 dark:text-green-400',
  emerald: 'bg-emerald-500/10 hover:bg-emerald-500/20 border-emerald-500/30 hover:border-emerald-500/50 text-emerald-700 dark:text-emerald-400',
  purple: 'bg-purple-500/10 hover:bg-purple-500/20 border-purple-500/30 hover:border-purple-500/50 text-purple-700 dark:text-purple-400',
  indigo: 'bg-indigo-500/10 hover:bg-indigo-500/20 border-indigo-500/30 hover:border-indigo-500/50 text-indigo-700 dark:text-indigo-400',
  pink: 'bg-pink-500/10 hover:bg-pink-500/20 border-pink-500/30 hover:border-pink-500/50 text-pink-700 dark:text-pink-400'
}

interface ExamplesPopoverProps {
  onSelectExample: (query: string) => void
}

export function ExamplesPopover({ onSelectExample }: ExamplesPopoverProps) {
  const [open, setOpen] = useState(false)
  const popoverRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    if (open) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [open])

  const handleSelect = (query: string) => {
    onSelectExample(query)
    setOpen(false)
  }

  return (
    <div className="relative" ref={popoverRef}>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setOpen(!open)}
        className="text-sm font-medium text-muted-foreground hover:text-foreground focus-ring-premium"
        aria-label="View example research queries"
        aria-expanded={open}
      >
        <Lightbulb className="h-4 w-4 mr-2" />
        Examples
      </Button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="absolute right-0 top-full mt-2 w-[380px] p-4 rounded-2xl glass-effect shadow-premium-lg z-50 border border-border/50"
          >
            <div className="space-y-3">
              <div>
                <h4 className="font-semibold text-sm mb-1">Example Queries</h4>
                <p className="text-xs text-muted-foreground">
                  Click any topic to use as your research query
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                {examples.map((example, index) => {
                  const Icon = example.icon
                  const colorClass = colorClasses[example.color as keyof typeof colorClasses]
                  
                  return (
                    <motion.button
                      key={example.label}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => handleSelect(example.query)}
                      className={cn(
                        'flex items-center gap-2 p-3 rounded-xl border transition-all duration-200',
                        'text-left text-xs font-medium focus-ring-premium',
                        colorClass
                      )}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      type="button"
                    >
                      <Icon className="h-4 w-4 flex-shrink-0" />
                      <span className="line-clamp-2">{example.label}</span>
                    </motion.button>
                  )
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
