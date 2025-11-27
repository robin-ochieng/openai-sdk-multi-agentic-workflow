'use client'

import { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, FileText, Calendar, Download, Trash2, RefreshCw, Loader2, AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useHistoryStore, type HistoryRun } from '@/lib/historyStore'
import { formatDistanceToNow } from 'date-fns'

interface ReportDisplay {
  runId: string
  query: string
  completedAt: string
  wordCount: number
  evidenceCount: number
  status: 'done' | 'error'
  readTime: string
  source: 'local' | 'remote'
}

export default function ReportsPage() {
  const { runs: localRuns, removeRun } = useHistoryStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Convert local runs to display format
  const reports: ReportDisplay[] = useMemo(() => {
    return localRuns.map(run => ({
      runId: run.runId,
      query: run.query,
      completedAt: run.completedAt,
      wordCount: run.wordCount,
      evidenceCount: run.evidence.length,
      status: run.status,
      readTime: `${Math.ceil(run.wordCount / 200)} min`,
      source: 'local' as const,
    }))
  }, [localRuns])

  // Filter reports based on search query
  const filteredReports = useMemo(() => {
    if (!searchQuery.trim()) return reports
    const query = searchQuery.toLowerCase()
    return reports.filter(report => 
      report.query.toLowerCase().includes(query)
    )
  }, [reports, searchQuery])

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    } catch {
      return 'Unknown date'
    }
  }

  // Format relative time
  const formatRelativeTime = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true })
    } catch {
      return ''
    }
  }

  // Handle delete
  const handleDelete = async (runId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (confirm('Are you sure you want to delete this report?')) {
      removeRun(runId)
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="border-b border-border/40 bg-background/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold">Research Reports</h1>
              <p className="mt-2 text-muted-foreground">
                Browse and manage your completed research reports
                {reports.length > 0 && (
                  <span className="ml-2 text-sm">
                    ({reports.length} report{reports.length !== 1 ? 's' : ''})
                  </span>
                )}
              </p>
            </div>
            
            {/* Search and Actions */}
            <div className="flex gap-3">
              <div className="relative max-w-md flex-1 md:max-w-sm">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search reports..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="container mx-auto px-4 py-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}

      {/* Reports Grid */}
      <div className="py-8">
        <div className="container mx-auto px-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : filteredReports.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredReports.map((report, index) => (
                <motion.div
                  key={report.runId}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link href={`/reports/${report.runId}`}>
                    <Card className="group cursor-pointer overflow-hidden border border-border/40 bg-card/50 backdrop-blur-sm transition-all hover:shadow-premium hover:border-primary/20">
                      <div className="p-6">
                        {/* Header */}
                        <div className="mb-4 flex items-start justify-between">
                          <div className={`flex h-12 w-12 items-center justify-center rounded-lg transition-colors ${
                            report.status === 'error' 
                              ? 'bg-destructive/10 group-hover:bg-destructive/20' 
                              : 'bg-primary/10 group-hover:bg-primary/20'
                          }`}>
                            <FileText className={`h-6 w-6 ${
                              report.status === 'error' ? 'text-destructive' : 'text-primary'
                            }`} />
                          </div>
                          <div className="flex items-center gap-2">
                            {report.status === 'error' && (
                              <span className="rounded-full bg-destructive/10 px-2 py-0.5 text-xs font-medium text-destructive">
                                Error
                              </span>
                            )}
                            <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                              {report.source === 'local' ? 'Local' : 'Synced'}
                            </span>
                          </div>
                        </div>

                        {/* Title */}
                        <h3 className="mb-3 line-clamp-2 text-lg font-semibold group-hover:text-primary transition-colors">
                          {report.query}
                        </h3>

                        {/* Meta */}
                        <div className="mb-4 flex flex-wrap gap-3 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1" title={formatDate(report.completedAt)}>
                            <Calendar className="h-3.5 w-3.5" />
                            <span>{formatRelativeTime(report.completedAt)}</span>
                          </div>
                          <span>•</span>
                          <span>{report.wordCount.toLocaleString()} words</span>
                          <span>•</span>
                          <span>{report.readTime} read</span>
                        </div>

                        {/* Stats */}
                        <div className="mb-4 flex items-center gap-4 text-sm">
                          <div className="flex items-center gap-1.5 text-muted-foreground">
                            <span className="text-lg">📚</span>
                            <span>{report.evidenceCount} sources</span>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2 border-t border-border/40 pt-4">
                          <button
                            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-primary/10 px-4 py-2 text-sm font-medium text-primary hover:bg-primary/20 transition-colors"
                            onClick={(e) => {
                              e.preventDefault()
                              // Navigate to report
                            }}
                          >
                            <FileText className="h-4 w-4" />
                            <span>View Report</span>
                          </button>
                          <button
                            className="flex items-center justify-center rounded-lg border border-border/40 px-3 py-2 text-sm text-muted-foreground hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-colors"
                            onClick={(e) => handleDelete(report.runId, e)}
                            title="Delete report"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </Card>
                  </Link>
                </motion.div>
              ))}
            </div>
          ) : (
            /* Empty State */
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-20 text-center"
            >
              <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-muted">
                <FileText className="h-10 w-10 text-muted-foreground" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                {searchQuery ? 'No matching reports' : 'No reports yet'}
              </h3>
              <p className="mb-6 text-sm text-muted-foreground max-w-md">
                {searchQuery 
                  ? 'Try adjusting your search query'
                  : 'Start a new research query to generate your first comprehensive report'
                }
              </p>
              {!searchQuery && (
                <Link
                  href="/"
                  className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                  Start Research
                </Link>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
