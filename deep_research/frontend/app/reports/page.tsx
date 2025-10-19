'use client'

import { motion } from 'framer-motion'
import { Search, FileText, Calendar, Download } from 'lucide-react'
import Link from 'next/link'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

// Mock data - will be replaced with real data
const mockReports = [
  {
    id: '001',
    title: 'Comparison of the Eastern and Western NBA Conferences: 2022-23 Season and Expectations for 2025-26 Season',
    date: '2025-10-18',
    wordCount: 658,
    linesRead: 86,
    readTime: '4 min',
    keyFindings: [
      'Eastern Conference Highlights',
      'Western Conference Highlights',
      'Team Performances'
    ]
  }
]

export default function ReportsPage() {
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
              </p>
            </div>
            
            {/* Search */}
            <div className="relative max-w-md flex-1 md:max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search reports..."
                className="pl-10"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="py-8">
        <div className="container mx-auto px-4">
          {mockReports.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {mockReports.map((report, index) => (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Link href={`/reports/${report.id}`}>
                    <Card className="group cursor-pointer overflow-hidden border border-border/40 bg-card/50 backdrop-blur-sm transition-all hover:shadow-premium hover:border-primary/20">
                      <div className="p-6">
                        {/* Header */}
                        <div className="mb-4 flex items-start justify-between">
                          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                            <FileText className="h-6 w-6 text-primary" />
                          </div>
                          <span className="rounded-full bg-muted px-3 py-1 text-xs font-medium">
                            #{report.id}
                          </span>
                        </div>

                        {/* Title */}
                        <h3 className="mb-3 line-clamp-2 text-lg font-semibold group-hover:text-primary transition-colors">
                          {report.title}
                        </h3>

                        {/* Meta */}
                        <div className="mb-4 flex flex-wrap gap-3 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3.5 w-3.5" />
                            <span>{report.date}</span>
                          </div>
                          <span>•</span>
                          <span>{report.wordCount} words</span>
                          <span>•</span>
                          <span>{report.readTime} read</span>
                        </div>

                        {/* Key Findings */}
                        <div className="space-y-1">
                          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                            Key Findings
                          </p>
                          <ul className="space-y-1">
                            {report.keyFindings.slice(0, 3).map((finding, i) => (
                              <li key={i} className="text-sm text-muted-foreground line-clamp-1">
                                • {finding}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Actions */}
                        <div className="mt-4 flex gap-2 border-t border-border/40 pt-4">
                          <button
                            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-primary/10 px-4 py-2 text-sm font-medium text-primary hover:bg-primary/20 transition-colors"
                            onClick={(e) => {
                              e.preventDefault()
                              // Handle download
                            }}
                          >
                            <Download className="h-4 w-4" />
                            <span>Download</span>
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
              <h3 className="mb-2 text-lg font-semibold">No reports yet</h3>
              <p className="mb-6 text-sm text-muted-foreground max-w-md">
                Start a new research query to generate your first comprehensive report
              </p>
              <Link
                href="/home"
                className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                Start Research
              </Link>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
