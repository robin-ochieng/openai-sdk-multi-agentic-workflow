'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ReportData } from '@/lib/types'
import { downloadFile, copyToClipboard } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import {
  FileText,
  Download,
  Copy,
  CheckCircle2,
  Eye,
  Code,
  Loader2,
  Share2,
  List,
  Lightbulb,
  BookOpen,
} from 'lucide-react'

interface ReportPreviewProps {
  report: ReportData | null
  isResearching: boolean
}

export function ReportPreview({ report, isResearching }: ReportPreviewProps) {
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('preview')
  const [viewMode, setViewMode] = useState<'report' | 'outline'>('report')

  if (!report && isResearching) {
    return (
      <Card className="border-2 border-purple-500/20 bg-gradient-to-br from-card to-card/80 p-8">
        <div className="flex flex-col items-center gap-4 text-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-600 dark:text-purple-400" />
          <p className="text-lg font-medium">Generating comprehensive report...</p>
          <p className="text-sm text-muted-foreground">
            Analyzing research data and creating structured content
          </p>
        </div>
      </Card>
    )
  }

  if (!report) return null

  const handleCopy = async () => {
    const content = report.content || report.markdown_report
    const success = await copyToClipboard(content)
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    const content = report.content || report.markdown_report
    downloadFile(content, `research-report-${Date.now()}.md`, 'text/markdown')
  }

  const handleDownloadPDF = () => {
    // Placeholder for PDF download - would require PDF generation library
    alert('PDF download coming soon!')
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Research Report',
          text: report.short_summary || 'Check out this research report',
        })
      } catch (err) {
        console.log('Share canceled')
      }
    } else {
      // Fallback: copy link to clipboard
      await copyToClipboard(window.location.href)
      alert('Link copied to clipboard!')
    }
  }

  // Extract key findings from report (simple approach)
  const extractKeyFindings = (content: string): string[] => {
    const lines = content.split('\n')
    const findings: string[] = []
    let inKeyFindingsSection = false

    for (const line of lines) {
      if (line.toLowerCase().includes('key findings') || line.toLowerCase().includes('summary')) {
        inKeyFindingsSection = true
        continue
      }
      if (inKeyFindingsSection && line.trim().startsWith('- ')) {
        findings.push(line.trim().substring(2))
        if (findings.length >= 5) break
      }
      if (inKeyFindingsSection && line.startsWith('## ') && findings.length > 0) {
        break
      }
    }

    // If no findings found, extract first few bullet points
    if (findings.length === 0) {
      for (const line of lines) {
        if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
          findings.push(line.trim().substring(2))
          if (findings.length >= 5) break
        }
      }
    }

    return findings
  }

  const keyFindings = extractKeyFindings(report.content || report.markdown_report)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="overflow-hidden border-2 border-purple-500/20 bg-gradient-to-br from-card to-card/80 shadow-premium-lg">
        {/* Header */}
        <div className="border-b border-border/50 bg-gradient-to-r from-purple-500/10 to-purple-500/5 p-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-500/20">
                  <FileText className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">Research Report Complete</h2>
                  <p className="text-sm text-muted-foreground">
                    {(report.content || report.markdown_report).split('\n').length} lines •{' '}
                    {Math.ceil((report.content || report.markdown_report).split(' ').length / 200)} min read
                    {report.word_count && ` • ${report.word_count} words`}
                  </p>
                </div>
              </div>

              {/* View mode toggle */}
              <div className="flex gap-2">
                <Button
                  variant={viewMode === 'outline' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('outline')}
                  className="h-8"
                >
                  <List className="h-4 w-4 mr-1.5" />
                  Outline
                </Button>
                <Button
                  variant={viewMode === 'report' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('report')}
                  className="h-8"
                >
                  <BookOpen className="h-4 w-4 mr-1.5" />
                  Report
                </Button>
              </div>
            </div>

            {/* CTA Row */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDownloadPDF}
                className="h-9"
              >
                <Download className="mr-2 h-4 w-4" />
                PDF
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                disabled={copied}
                className="h-9"
              >
                {copied ? (
                  <>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="mr-2 h-4 w-4" />
                    Markdown
                  </>
                )}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleShare}
                className="h-9"
              >
                <Share2 className="mr-2 h-4 w-4" />
                Share
              </Button>
            </div>
          </div>
        </div>

        {/* Key Findings Section (if outline mode or at top) */}
        {keyFindings.length > 0 && (
          <div className="border-b border-border/50 bg-muted/30 p-6">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              <h3 className="font-semibold">Key Findings</h3>
            </div>
            <ul className="space-y-2">
              {keyFindings.map((finding, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-2 text-sm"
                >
                  <span className="flex-shrink-0 mt-1.5 h-1.5 w-1.5 rounded-full bg-purple-500" />
                  <span>{finding}</span>
                </motion.li>
              ))}
            </ul>
          </div>
        )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="border-b border-border/50 px-6">
          <TabsList className="grid w-full max-w-[400px] grid-cols-2">
            <TabsTrigger value="preview">
              <Eye className="mr-2 h-4 w-4" />
              Preview
            </TabsTrigger>
            <TabsTrigger value="markdown">
              <Code className="mr-2 h-4 w-4" />
              Markdown
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="preview" className="m-0 p-6">
          <div className="prose prose-slate dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight as any]}
              components={{
                h1: ({ children }) => (
                  <h1 className="mb-6 border-b border-border pb-2 text-4xl font-bold">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="mb-4 mt-8 text-2xl font-bold">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="mb-3 mt-6 text-xl font-semibold">{children}</h3>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary underline-offset-4 hover:underline"
                  >
                    {children}
                  </a>
                ),
                code: ({ className, children }) => {
                  const isInline = !className
                  return isInline ? (
                    <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm">
                      {children}
                    </code>
                  ) : (
                    <code className={className}>{children}</code>
                  )
                },
              }}
            >
              {report.content || report.markdown_report}
            </ReactMarkdown>
          </div>
        </TabsContent>

        <TabsContent value="markdown" className="m-0 p-6">
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="absolute right-2 top-2"
            >
              {copied ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
            <pre className="overflow-x-auto rounded-lg border border-border bg-muted p-4 text-sm">
              <code>{report.content || report.markdown_report}</code>
            </pre>
          </div>
        </TabsContent>
      </Tabs>

      {/* Citations Section */}
      {report.sources && report.sources.length > 0 && (
        <div className="border-t border-border/50 bg-muted/30 p-6">
          <h3 className="mb-3 font-semibold flex items-center gap-2">
            <span>Citations</span>
            <Badge variant="secondary" className="text-xs">
              {report.sources.length}
            </Badge>
          </h3>
          <div className="grid gap-2 md:grid-cols-2">
            {report.sources.map((source, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-start gap-2 p-3 rounded-lg border border-border/50 bg-card hover:border-border transition-colors"
              >
                <span className="flex-shrink-0 flex items-center justify-center h-5 w-5 rounded-full bg-primary/10 text-primary text-xs font-medium">
                  {index + 1}
                </span>
                <a
                  href={source}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm hover:underline text-foreground/90 line-clamp-2 flex-1"
                >
                  {new URL(source).hostname}
                </a>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </Card>
    </motion.div>
  )
}
