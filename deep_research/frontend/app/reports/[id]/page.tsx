'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Home, Download, Share2, FileText } from 'lucide-react'
import { ReportPreview } from '@/components/ReportPreview'

// Mock report data
const mockReport = {
  markdown_report: `# Comparison of the Eastern and Western NBA Conferences

## Introduction
The NBA is divided into two main conferences: the Eastern Conference and the Western Conference...

## Key Findings
- Eastern Conference has shown consistent growth
- Western Conference maintains competitive balance
- Individual player performances drive conference dynamics`,
  short_summary: 'Comprehensive analysis of NBA conferences performance',
  word_count: 658,
  title: 'NBA Conference Analysis 2022-2025',
  sources: []
}

export default function SingleReportPage() {
  const params = useParams()
  const reportId = params.id as string

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="sticky top-0 z-10 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Link href="/" className="flex items-center gap-1 hover:text-foreground transition-colors">
                <Home className="h-4 w-4" />
                <span>Home</span>
              </Link>
              <span>•</span>
              <Link href="/reports" className="hover:text-foreground transition-colors">
                Reports
              </Link>
              <span>•</span>
              <span className="text-foreground font-medium">#{reportId}</span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
                onClick={() => {
                  // Handle download
                }}
              >
                <Download className="h-4 w-4" />
                <span className="hidden sm:inline">PDF</span>
              </button>
              
              <button
                className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
                onClick={() => {
                  // Handle markdown download
                }}
              >
                <FileText className="h-4 w-4" />
                <span className="hidden sm:inline">Markdown</span>
              </button>

              <button
                className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
                onClick={() => {
                  // Handle share
                  if (navigator.share) {
                    navigator.share({
                      title: mockReport.title,
                      text: mockReport.short_summary,
                    })
                  }
                }}
              >
                <Share2 className="h-4 w-4" />
                <span className="hidden sm:inline">Share</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Report Content */}
      <div className="py-8">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <ReportPreview
              report={mockReport}
              isResearching={false}
            />
          </motion.div>
        </div>
      </div>
    </div>
  )
}
