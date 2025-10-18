'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { ResearchState } from '@/lib/types'
import { startResearch } from '@/lib/api'
import { Search, Loader2, Mail } from 'lucide-react'

interface ResearchFormProps {
  researchState: ResearchState
  setResearchState: (state: ResearchState | ((prev: ResearchState) => ResearchState)) => void
}

export function ResearchForm({ researchState, setResearchState }: ResearchFormProps) {
  const [query, setQuery] = useState('')
  const [email, setEmail] = useState('')
  const [errors, setErrors] = useState<{ query?: string; email?: string }>({})

  const validateForm = (): boolean => {
    const newErrors: { query?: string; email?: string } = {}

    if (!query.trim()) {
      newErrors.query = 'Please enter a research query'
    } else if (query.trim().length < 10) {
      newErrors.query = 'Query should be at least 10 characters'
    }

    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    // Reset state
    setResearchState({
      isResearching: true,
      currentStep: 'planning',
      progress: 0,
      logs: [],
      searchPlan: null,
      searchResults: null,
      report: null,
      emailSent: false,
      error: null,
    })

    try {
      await startResearch(query, email, (update) => {
        setResearchState((prev) => ({
          ...prev,
          ...update,
        }))
      })
    } catch (error) {
      setResearchState((prev) => ({
        ...prev,
        isResearching: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      }))
    }
  }

  return (
    <Card className="overflow-hidden border-2 border-primary/20 bg-gradient-to-br from-card to-card/80 shadow-xl">
      <form onSubmit={handleSubmit} className="p-6 md:p-8">
        <div className="space-y-6">
          {/* Query Input */}
          <div className="space-y-2">
            <label htmlFor="query" className="text-sm font-medium leading-none">
              Research Query <span className="text-destructive">*</span>
            </label>
            <Textarea
              id="query"
              name="query"
              placeholder="What would you like to research? (e.g., 'Latest developments in quantum computing applications')"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                if (errors.query) setErrors({ ...errors, query: undefined })
              }}
              disabled={researchState.isResearching}
              className="min-h-[120px] resize-none text-base"
              aria-invalid={!!errors.query}
            />
            {errors.query && (
              <p className="text-sm text-destructive">{errors.query}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Be specific for better results. The AI will create a research plan, search the web,
              and generate a comprehensive report.
            </p>
          </div>

          {/* Email Input */}
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium leading-none">
              Email Address (Optional)
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="your.email@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  if (errors.email) setErrors({ ...errors, email: undefined })
                }}
                disabled={researchState.isResearching}
                className="pl-10"
                aria-invalid={!!errors.email}
              />
            </div>
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Receive the research report via email when complete
            </p>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            size="lg"
            disabled={researchState.isResearching || !query.trim()}
            className="w-full text-base font-semibold shadow-lg transition-all duration-300 hover:shadow-xl"
          >
            {researchState.isResearching ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Researching...
              </>
            ) : (
              <>
                <Search className="mr-2 h-5 w-5" />
                Start Research
              </>
            )}
          </Button>

          {/* Progress Indicator */}
          {researchState.isResearching && (
            <div className="space-y-2 rounded-lg border border-primary/20 bg-primary/5 p-4">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium capitalize">
                  {researchState.currentStep?.replace('_', ' ') || 'Initializing'}
                </span>
                <span className="text-muted-foreground">
                  {typeof researchState.progress === 'number' 
                    ? researchState.progress 
                    : researchState.progress.percentage}%
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full bg-gradient-to-r from-primary to-primary/80 transition-all duration-500 ease-out"
                  style={{ 
                    width: `${typeof researchState.progress === 'number' 
                      ? researchState.progress 
                      : researchState.progress.percentage}%` 
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </form>
    </Card>
  )
}
