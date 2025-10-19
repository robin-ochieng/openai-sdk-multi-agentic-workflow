'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Home, ArrowLeft } from 'lucide-react'
import { RunLayout } from '@/components/RunLayout'
import { useState } from 'react'
import { ResearchState } from '@/lib/types'

export default function LiveResearchPage() {
  const params = useParams()
  const sessionId = params.id as string

  // This will be replaced with global state management
  const [researchState] = useState<ResearchState>({
    isResearching: true,
    currentStep: 'searching',
    progress: 50,
    logs: [
      { id: '1', timestamp: new Date(), type: 'info', message: 'Starting research...', emoji: '🔍' }
    ],
    searchPlan: null,
    searchResults: null,
    report: null,
    emailSent: false,
    error: null,
  })

  return (
    <div className="min-h-screen">
      {/* Breadcrumb Header */}
      <div className="border-b border-border/40 bg-background/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Link href="/home" className="flex items-center gap-1 hover:text-foreground transition-colors">
              <Home className="h-4 w-4" />
              <span>Home</span>
            </Link>
            <span>•</span>
            <span>Run #{sessionId}</span>
            <span>•</span>
            <span className="text-foreground font-medium">Live</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="py-8">
        <div className="container mx-auto px-4">
          <RunLayout researchState={researchState} />
        </div>
      </div>
    </div>
  )
}
