'use client'

import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Home, Download, Share2, FileText, ArrowLeft, AlertCircle, Loader2 } from 'lucide-react'
import { ReportPreview } from '@/components/ReportPreview'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useHistoryStore } from '@/lib/historyStore'
import { useRunStore } from '@/lib/runStore'
import { useMemo } from 'react'

export default function SingleReportPage() {
  const params = useParams()
  const router = useRouter()
  const reportId = params.id as string

  // Get run from history store
  const { getRun } = useHistoryStore()
  const historyRun = useMemo(() => getRun(reportId), [getRun, reportId])

  // Also check current run store (for just-completed research)
  const currentRun = useRunStore()
  const isCurrentRun = currentRun.runId === reportId

  // Determine which data to use
  const report = useMemo(() => {
    if (isCurrentRun && currentRun.reportMarkdown) {
      return {
        markdown_report: currentRun.reportMarkdown,
        short_summary: currentRun.query,
        word_count: currentRun.reportMarkdown.split(/\s+/).length,
        title: currentRun.query,
        sources: currentRun.evidence.map(e => e.url),
      }
    }
    
    if (historyRun) {
      return {
        markdown_report: historyRun.reportMarkdown,
        short_summary: historyRun.query,
        word_count: historyRun.wordCount,
        title: historyRun.query,
        sources: historyRun.evidence.map(e => e.url),
      }
    }

    return null
  }, [isCurrentRun, currentRun, historyRun])

  // Handle download as markdown
  const handleDownloadMarkdown = () => {
    if (!report) return
    
    const blob = new Blob([report.markdown_report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `research-report-${reportId}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Handle share
  const handleShare = async () => {
    if (!report) return
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: report.title,
          text: report.short_summary,
          url: window.location.href,
        })
      } catch (err) {
        // User cancelled or error
        console.log('Share cancelled or failed:', err)
      }
    } else {
      // Fallback: copy to clipboard
      await navigator.clipboard.writeText(window.location.href)
      alert('Link copied to clipboard!')
    }
  }

  // Not found state
  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Report not found. It may have been deleted or hasn't been synced yet.
            </AlertDescription>
          </Alert>
          <Button onClick={() => router.push('/reports')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Reports
          </Button>
        </div>
      </div>
    )
  }

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
              <span className="text-foreground font-medium line-clamp-1 max-w-[200px]">
                {report.title}
              </span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
                onClick={handleDownloadMarkdown}
              >
                <FileText className="h-4 w-4" />
                <span className="hidden sm:inline">Markdown</span>
              </button>

              <button
                className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
                onClick={handleShare}
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
              report={report}
              isResearching={false}
            />
          </motion.div>
        </div>
      </div>
    </div>
  )
}
