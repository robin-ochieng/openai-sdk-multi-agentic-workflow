'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { ResearchState } from '@/lib/types'
import { startResearch } from '@/lib/api'
import { Mail, AlertCircle } from 'lucide-react'
import { StartButton } from './StartButton'
import { ExamplesPopover } from './ExamplesPopover'
import { cn } from '@/lib/utils'

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

  const buttonState = researchState.isResearching 
    ? 'loading' 
    : researchState.report 
    ? 'success' 
    : 'idle'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="overflow-hidden border-2 border-border/50 glass-effect shadow-premium-lg">
        <form onSubmit={handleSubmit} className="p-6 md:p-8">
          <div className="space-y-6">
            {/* Header with Examples */}
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">New Research</h2>
              {!researchState.isResearching && (
                <ExamplesPopover
                  onSelectExample={(exampleQuery: string) => {
                    setQuery(exampleQuery)
                    setErrors({})
                  }}
                />
              )}
            </div>

            {/* Query Input with Floating Label */}
            <div className="relative">
              <Textarea
                id="query"
                name="query"
                placeholder=" "
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value)
                  if (errors.query) setErrors({ ...errors, query: undefined })
                }}
                disabled={researchState.isResearching}
                className={cn(
                  'min-h-[120px] resize-none text-base peer pt-6 rounded-xl focus-ring-premium',
                  errors.query && 'border-destructive'
                )}
                aria-invalid={!!errors.query}
                aria-describedby={errors.query ? 'query-error' : 'query-helper'}
              />
              <label
                htmlFor="query"
                className="absolute left-3 top-2 text-xs font-medium text-muted-foreground transition-all peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-focus:top-2 peer-focus:text-xs"
              >
                Research Query <span className="text-destructive">*</span>
              </label>
              {errors.query && (
                <div id="query-error" className="mt-2 flex items-center gap-1.5 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  <span>{errors.query}</span>
                </div>
              )}
              {!errors.query && (
                <p id="query-helper" className="mt-2 text-xs text-muted-foreground">
                  Minimum 12 characters. Be specific for better research results.
                </p>
              )}
            </div>

            {/* Email Input with Floating Label */}
            <div className="relative">
              <div className="relative">
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder=" "
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (errors.email) setErrors({ ...errors, email: undefined })
                  }}
                  disabled={researchState.isResearching}
                  className={cn(
                    'peer pl-10 pt-6 pb-2 rounded-xl focus-ring-premium',
                    errors.email && 'border-destructive'
                  )}
                  aria-invalid={!!errors.email}
                  aria-describedby={errors.email ? 'email-error' : 'email-helper'}
                />
                <Mail className="absolute left-3 top-4 h-5 w-5 text-muted-foreground pointer-events-none" />
                <label
                  htmlFor="email"
                  className="absolute left-10 top-2 text-xs font-medium text-muted-foreground transition-all peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-focus:top-2 peer-focus:text-xs"
                >
                  Email Address (Optional)
                </label>
              </div>
              {errors.email && (
                <div id="email-error" className="mt-2 flex items-center gap-1.5 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  <span>{errors.email}</span>
                </div>
              )}
              {!errors.email && (
                <p id="email-helper" className="mt-2 text-xs text-muted-foreground">
                  Get the report delivered to your inbox when complete
                </p>
              )}
            </div>

            {/* Submit Button */}
            <StartButton
              onClick={() => handleSubmit(new Event('submit') as any)}
              disabled={researchState.isResearching}
              state={buttonState}
              queryLength={query.trim().length}
            />
          </div>
        </form>
      </Card>
    </motion.div>
  )
}
