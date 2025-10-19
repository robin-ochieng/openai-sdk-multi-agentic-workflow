'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface PageHeaderProps {
  query: string
  email?: string
}

export function PageHeader({ query, email }: PageHeaderProps) {
  return (
    <div className="mb-8">
      <Link href="/">
        <Button variant="ghost" size="sm" className="mb-4 -ml-2">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Button>
      </Link>
      <h1 className="mb-2 text-3xl font-bold tracking-tight">Live Research</h1>
      <div className="space-y-1 text-sm text-muted-foreground">
        <p>
          <span className="font-medium text-slate-700 dark:text-slate-300">Query:</span> {query}
        </p>
        {email && (
          <p>
            <span className="font-medium text-slate-700 dark:text-slate-300">Email:</span> {email}
          </p>
        )}
      </div>
    </div>
  )
}
