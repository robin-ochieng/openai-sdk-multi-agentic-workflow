'use client'

import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, Globe, TrendingUp, Lightbulb, Sparkles, BookOpen } from 'lucide-react'

interface ExampleQueriesProps {
  onSelectExample: (query: string) => void
}

const examples = [
  {
    query: 'Latest breakthroughs in quantum computing and their practical applications',
    category: 'Technology',
    icon: Brain,
    color: 'blue',
  },
  {
    query: 'Impact of artificial intelligence on healthcare diagnostics and patient care',
    category: 'Healthcare',
    icon: TrendingUp,
    color: 'green',
  },
  {
    query: 'Current state of renewable energy adoption and future trends',
    category: 'Environment',
    icon: Globe,
    color: 'emerald',
  },
  {
    query: 'Emerging trends in remote work technology and collaboration tools',
    category: 'Business',
    icon: Lightbulb,
    color: 'purple',
  },
  {
    query: 'Recent developments in space exploration and commercial spaceflight',
    category: 'Science',
    icon: Sparkles,
    color: 'indigo',
  },
  {
    query: 'Evolution of large language models and their applications in 2024-2025',
    category: 'AI/ML',
    icon: BookOpen,
    color: 'pink',
  },
]

const colorClasses = {
  blue: 'border-blue-500/20 bg-blue-500/5 hover:border-blue-500/40',
  green: 'border-green-500/20 bg-green-500/5 hover:border-green-500/40',
  emerald: 'border-emerald-500/20 bg-emerald-500/5 hover:border-emerald-500/40',
  purple: 'border-purple-500/20 bg-purple-500/5 hover:border-purple-500/40',
  indigo: 'border-indigo-500/20 bg-indigo-500/5 hover:border-indigo-500/40',
  pink: 'border-pink-500/20 bg-pink-500/5 hover:border-pink-500/40',
}

const iconColorClasses = {
  blue: 'text-blue-600 dark:text-blue-400',
  green: 'text-green-600 dark:text-green-400',
  emerald: 'text-emerald-600 dark:text-emerald-400',
  purple: 'text-purple-600 dark:text-purple-400',
  indigo: 'text-indigo-600 dark:text-indigo-400',
  pink: 'text-pink-600 dark:text-pink-400',
}

export function ExampleQueries({ onSelectExample }: ExampleQueriesProps) {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Try an Example</h2>
        <p className="mt-2 text-muted-foreground">
          Click on any example below to see the research agent in action
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {examples.map((example, index) => {
          const Icon = example.icon
          const colorClass = colorClasses[example.color as keyof typeof colorClasses]
          const iconColorClass = iconColorClasses[example.color as keyof typeof iconColorClasses]

          return (
            <Card
              key={index}
              className={`group cursor-pointer overflow-hidden border-2 transition-all duration-300 hover:shadow-lg ${colorClass}`}
              onClick={() => onSelectExample(example.query)}
            >
              <div className="p-5">
                <div className="mb-3 flex items-center justify-between">
                  <Badge variant="secondary" className="h-fit">
                    {example.category}
                  </Badge>
                  <div className={`transition-transform duration-300 group-hover:scale-110 ${iconColorClass}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
                <p className="text-sm leading-relaxed group-hover:text-foreground">
                  {example.query}
                </p>
              </div>
            </Card>
          )
        })}
      </div>

      <p className="text-center text-xs text-muted-foreground">
        Or write your own query in the form above
      </p>
    </div>
  )
}
