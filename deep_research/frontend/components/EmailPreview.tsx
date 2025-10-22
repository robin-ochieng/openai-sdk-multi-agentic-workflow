'use client'

import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ReportData } from '@/lib/types'
import { Mail, CheckCircle2, AlertCircle } from 'lucide-react'

interface EmailPreviewProps {
  report: ReportData | null
}

export function EmailPreview({ report }: EmailPreviewProps) {
  if (!report) return null

  return (
    <Card className="overflow-hidden border-2 border-green-500/20 bg-gradient-to-br from-card to-card/80">
      <div className="border-b border-border/50 bg-gradient-to-r from-green-500/10 to-green-500/5 p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/20">
            <Mail className="h-6 w-6 text-green-600 dark:text-green-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">Email Sent Successfully</h2>
            <p className="text-sm text-muted-foreground">
              Research report delivered to your inbox
            </p>
          </div>
          <Badge variant="secondary" className="h-fit bg-green-500/20 text-green-700 dark:text-green-300">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Delivered
          </Badge>
        </div>
      </div>

      <div className="p-6">
        <div className="space-y-4">
          <div className="flex items-start gap-3 rounded-lg border border-border/50 bg-muted/30 p-4">
            <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-green-600 dark:text-green-400" />
            <div className="flex-1">
              <p className="font-medium">Report Delivered</p>
              <p className="mt-1 text-sm text-muted-foreground">
                The comprehensive research report has been sent to your email address.
                Check your inbox for the full analysis.
              </p>
            </div>
          </div>

          {report && (
            <div className="space-y-2 rounded-lg border border-border/50 bg-card p-4">
              <h3 className="text-sm font-semibold text-muted-foreground">Email Contents</h3>
              <div className="space-y-1 text-sm">
                <p>
                  <span className="font-medium">Subject:</span> Research Report:{' '}
                  {report.title || 'Deep Research Analysis'}
                </p>
                <p>
                  <span className="font-medium">Summary:</span> {report.short_summary}
                </p>
                <p>
                  <span className="font-medium">Word Count:</span>{' '}
                  {report.word_count.toLocaleString()} words
                </p>
              </div>
            </div>
          )}

          <div className="flex items-start gap-3 rounded-lg border border-blue-500/20 bg-blue-500/5 p-4">
            <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-600 dark:text-blue-400" />
            <div className="flex-1">
              <p className="text-sm text-muted-foreground">
                <strong>Note:</strong> If you don&apos;t see the email in your inbox, please check your
                spam or junk folder. The email was sent from the configured Gmail account.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
