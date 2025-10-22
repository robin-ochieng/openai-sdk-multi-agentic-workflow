'use client'

import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, FileText, Download, Share2, Clock, Calendar, TrendingUp } from 'lucide-react'
import { useRunStore } from '@/lib/runStore'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useMemo } from 'react'

// Clean duplicate consecutive headings from markdown
function cleanDuplicateHeadings(markdown: string): string {
  const lines = markdown.split('\n')
  const cleaned: string[] = []
  let lastHeading = ''
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // Check if it's a heading (starts with #)
    if (line.match(/^#{1,6}\s+/)) {
      const headingText = line.replace(/^#{1,6}\s+/, '').trim().toLowerCase()
      
      // Skip if same heading appears consecutively (within 3 lines)
      if (headingText === lastHeading && i - cleaned.length < 3) {
        continue
      }
      
      lastHeading = headingText
    } else if (line.length > 0) {
      // Reset if we hit non-empty content
      lastHeading = ''
    }
    
    cleaned.push(lines[i])
  }
  
  return cleaned.join('\n')
}

export default function ReportPage() {
  const router = useRouter()
  const { reportMarkdown, query } = useRunStore()

  // Clean duplicate headings from the markdown
  const cleanedMarkdown = useMemo(() => {
    return reportMarkdown ? cleanDuplicateHeadings(reportMarkdown) : ''
  }, [reportMarkdown])

  // Calculate reading time (average 200 words per minute)
  const wordCount = cleanedMarkdown ? cleanedMarkdown.split(/\s+/).length : 0
  const readingTime = Math.ceil(wordCount / 200)
  const currentDate = new Date().toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })

  // Show empty state if no report
  if (!reportMarkdown) {
    return (
      <div className="container mx-auto max-w-4xl p-6">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => router.push('/')}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Button>
          <h1 className="text-3xl font-bold">Research Report</h1>
        </div>

        <Card className="p-12">
          <div className="text-center">
            <FileText className="mx-auto mb-4 h-16 w-16 text-slate-300 dark:text-slate-700" />
            <h2 className="mb-2 text-xl font-semibold">No Report Yet</h2>
            <p className="mb-6 text-muted-foreground">
              Run a research query first to generate a report.
            </p>
            <Button onClick={() => router.push('/')}>
              Start New Research
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-5xl p-6">
      {/* Header with back button */}
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => router.push('/')}
          className="mb-6 -ml-2"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Button>

        {/* Report Title & Actions */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="secondary" className="text-xs">
                Research Report
              </Badge>
              <Badge variant="outline" className="text-xs">
                <TrendingUp className="mr-1 h-3 w-3" />
                AI Generated
              </Badge>
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3">
              {query || 'Research Report'}
            </h1>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4" />
                <span>{currentDate}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="h-4 w-4" />
                <span>{readingTime} min read</span>
              </div>
              <div className="flex items-center gap-1.5">
                <FileText className="h-4 w-4" />
                <span>{wordCount.toLocaleString()} words</span>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Download
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
          </div>
        </div>
      </div>

      <Separator className="mb-8" />

      {/* Report Content */}
      <Card className="border-none shadow-lg">
        <article className="report-article prose prose-lg prose-slate max-w-none p-8 md:p-12 lg:p-16 dark:prose-invert
          prose-headings:scroll-mt-20
          prose-headings:font-bold
          prose-headings:tracking-tight
          prose-h1:text-4xl
          md:prose-h1:text-5xl
          prose-h1:mb-6
          prose-h1:mt-8
          prose-h1:font-black
          prose-h1:border-b-2
          prose-h1:pb-4
          prose-h1:border-slate-300
          dark:prose-h1:border-slate-700
          prose-h2:text-2xl
          md:prose-h2:text-3xl
          prose-h2:mb-4
          prose-h2:mt-10
          prose-h2:font-bold
          prose-h2:text-slate-900
          dark:prose-h2:text-slate-100
          prose-h3:text-xl
          md:prose-h3:text-2xl
          prose-h3:mb-3
          prose-h3:mt-8
          prose-h3:font-semibold
          prose-h3:text-slate-800
          dark:prose-h3:text-slate-200
          prose-h4:text-lg
          md:prose-h4:text-xl
          prose-h4:mb-2
          prose-h4:mt-6
          prose-h4:font-semibold
          prose-p:text-base
          md:prose-p:text-lg
          prose-p:leading-relaxed
          prose-p:mb-5
          prose-p:text-slate-700
          dark:prose-p:text-slate-300
          prose-a:text-blue-600
          prose-a:no-underline
          prose-a:font-medium
          hover:prose-a:underline
          dark:prose-a:text-blue-400
          prose-strong:font-semibold
          prose-strong:text-slate-900
          dark:prose-strong:text-slate-100
          prose-em:italic
          prose-em:text-slate-700
          dark:prose-em:text-slate-300
          prose-code:rounded
          prose-code:bg-slate-100
          prose-code:px-1.5
          prose-code:py-0.5
          prose-code:text-sm
          prose-code:font-mono
          prose-code:text-slate-900
          prose-code:before:content-none
          prose-code:after:content-none
          dark:prose-code:bg-slate-900
          dark:prose-code:text-slate-100
          prose-pre:bg-slate-900
          prose-pre:text-slate-100
          prose-pre:rounded-lg
          prose-pre:border
          prose-pre:border-slate-800
          dark:prose-pre:bg-slate-950
          dark:prose-pre:border-slate-900
          prose-ul:my-6
          prose-ul:list-disc
          prose-ul:pl-6
          prose-li:my-2
          prose-li:text-slate-700
          dark:prose-li:text-slate-300
          prose-ol:my-6
          prose-ol:list-decimal
          prose-ol:pl-6
          prose-blockquote:border-l-4
          prose-blockquote:border-blue-500
          prose-blockquote:pl-4
          prose-blockquote:italic
          prose-blockquote:text-slate-700
          prose-blockquote:bg-slate-50
          prose-blockquote:py-2
          prose-blockquote:my-6
          dark:prose-blockquote:bg-slate-900
          dark:prose-blockquote:text-slate-300
          prose-hr:border-slate-200
          prose-hr:my-8
          dark:prose-hr:border-slate-800
          prose-table:w-full
          prose-table:border-collapse
          prose-thead:border-b-2
          prose-thead:border-slate-300
          dark:prose-thead:border-slate-700
          prose-th:px-4
          prose-th:py-2
          prose-th:text-left
          prose-th:font-semibold
          prose-td:px-4
          prose-td:py-2
          prose-td:border-t
          prose-td:border-slate-200
          dark:prose-td:border-slate-800
          prose-img:rounded-lg
          prose-img:shadow-md
          prose-img:my-8
        ">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {cleanedMarkdown}
          </ReactMarkdown>
        </article>
      </Card>

      {/* Footer */}
      <div className="mt-8 text-center text-sm text-muted-foreground">
        <p>Generated by Deep Research Agent • Powered by OpenAI GPT-4</p>
        <p className="mt-1">© {new Date().getFullYear()} • All rights reserved</p>
      </div>
    </div>
  )
}
