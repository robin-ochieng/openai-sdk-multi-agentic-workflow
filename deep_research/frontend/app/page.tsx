'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ResearchForm } from '@/components/ResearchForm'
import { RunLayout } from '@/components/RunLayout'
import { ReportPreview } from '@/components/ReportPreview'
import { EmailPreview } from '@/components/EmailPreview'
import { ResearchState } from '@/lib/types'
import { Shield, Lock, CheckCircle2 } from 'lucide-react'

export default function HomePage() {
  const [researchState, setResearchState] = useState<ResearchState>({
    isResearching: false,
    currentStep: null,
    progress: 0,
    logs: [],
    searchPlan: null,
    searchResults: null,
    report: null,
    emailSent: false,
    error: null,
  })

  return (
    <main className="min-h-screen">
      {/* Hero Section - Premium & Minimal */}
      <section className="relative overflow-hidden border-b border-border/40">
        {/* Background layers */}
        <div className="absolute inset-0 hero-gradient"></div>
        <div className="absolute inset-0 grid-pattern opacity-[0.03]"></div>
        <div className="absolute inset-0 noise-texture"></div>
        
        <div className="container relative mx-auto px-4 py-20 md:py-28">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-4xl text-center"
          >
            <h1 className="mb-6 bg-gradient-to-br from-foreground via-foreground to-foreground/70 bg-clip-text text-5xl font-bold tracking-tight text-transparent md:text-7xl">
              Deep Research Agent
            </h1>
            <p className="mb-8 text-xl text-muted-foreground md:text-2xl">
              Transform any query into comprehensive research reports with AI-powered
              multi-agent collaboration
            </p>
            
            {/* Trust indicators */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.4 }}
              className="flex flex-wrap items-center justify-center gap-4 text-sm text-muted-foreground"
            >
              <div className="flex items-center gap-2">
                <Lock className="h-4 w-4" />
                <span>Private</span>
              </div>
              <span className="text-border">•</span>
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                <span>Secure</span>
              </div>
              <span className="text-border">•</span>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                <span>Source-backed</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Research Interface */}
      <section className="py-16 bg-muted/20">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-6xl space-y-8">
            {/* Research Form - Only show if not researching */}
            {!researchState.isResearching && !researchState.report && (
              <ResearchForm
                researchState={researchState}
                setResearchState={setResearchState}
              />
            )}

            {/* Run Layout - Show during research */}
            {researchState.isResearching && (
              <RunLayout researchState={researchState} />
            )}

            {/* Report Preview */}
            {researchState.report && (
              <ReportPreview
                report={researchState.report}
                isResearching={researchState.isResearching}
              />
            )}

            {/* Email Preview */}
            {researchState.emailSent && (
              <EmailPreview report={researchState.report} />
            )}

            {/* Error Display */}
            {researchState.error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-xl border border-destructive/50 bg-destructive/10 p-6 shadow-premium"
              >
                <h3 className="mb-2 font-semibold text-destructive">Error</h3>
                <p className="text-sm text-destructive/90">{researchState.error}</p>
              </motion.div>
            )}

            {/* Empty State */}
            {!researchState.isResearching && !researchState.report && !researchState.error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center py-12"
              >
                <p className="text-muted-foreground text-sm">
                  Enter a research query above to get started
                </p>
              </motion.div>
            )}
          </div>
        </div>
      </section>
    </main>
  )
}
