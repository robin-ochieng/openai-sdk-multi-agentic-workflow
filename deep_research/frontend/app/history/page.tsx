'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { format, formatDistanceToNow } from 'date-fns'
import { 
  Search, 
  Clock, 
  FileText, 
  Trash2, 
  CheckCircle2,
  XCircle,
  History as HistoryIcon,
  Sparkles,
  ArrowRight,
  BookOpen,
  Calendar,
  Link2
} from 'lucide-react'

import { useHistoryStore, type HistoryRun } from '@/lib/historyStore'
import { useRunStore } from '@/lib/runStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

export default function HistoryPage() {
  const router = useRouter()
  const { runs, removeRun, clearHistory } = useHistoryStore()
  const { restoreRun } = useRunStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  // Filter runs based on search query
  const filteredRuns = runs.filter(run =>
    run.query.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleViewReport = (run: HistoryRun) => {
    // Restore the run to the store so the report page can display it
    restoreRun({
      runId: run.runId,
      query: run.query,
      email: run.email,
      reportMarkdown: run.reportMarkdown,
      evidence: run.evidence,
      logs: run.logs,
      status: run.status,
      error: run.error,
      startedAt: run.startedAt,
      completedAt: run.completedAt,
    })
    router.push('/report')
  }

  if (!isMounted) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      {/* Header with gradient background */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative mb-8 overflow-hidden rounded-2xl bg-gradient-to-r from-slate-50 via-white to-slate-50 border border-slate-200 p-8 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dark:border-slate-800"
      >
        <div className="absolute -right-20 -top-20 h-60 w-60 rounded-full bg-gradient-to-br from-blue-500/10 to-cyan-500/5 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 h-60 w-60 rounded-full bg-gradient-to-br from-violet-500/10 to-purple-500/5 blur-3xl" />
        
        <div className="relative flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/25">
            <HistoryIcon className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Research History</h1>
            <p className="mt-1 text-slate-500 dark:text-slate-400">
              View and manage your past research sessions
            </p>
          </div>
        </div>
        
        {/* Stats */}
        {runs.length > 0 && (
          <div className="relative mt-6 flex gap-6 border-t border-slate-200 dark:border-slate-700/50 pt-6">
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-blue-500" />
              <span className="text-sm text-slate-600 dark:text-slate-300">
                <span className="font-bold text-slate-900 dark:text-white">{runs.length}</span> research sessions
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Link2 className="h-4 w-4 text-cyan-500" />
              <span className="text-sm text-slate-600 dark:text-slate-300">
                <span className="font-bold text-slate-900 dark:text-white">
                  {runs.reduce((acc, run) => acc + run.evidence.length, 0)}
                </span> sources collected
              </span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-emerald-500" />
              <span className="text-sm text-slate-600 dark:text-slate-300">
                <span className="font-bold text-slate-900 dark:text-white">
                  {runs.reduce((acc, run) => acc + run.wordCount, 0).toLocaleString()}
                </span> words written
              </span>
            </div>
          </div>
        )}
      </motion.div>

      {/* Search and Actions */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search research history..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 border-slate-200 dark:border-slate-800"
          />
        </div>
        
        {runs.length > 0 && (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" size="sm" className="text-destructive hover:bg-destructive/10">
                <Trash2 className="mr-2 h-4 w-4" />
                Clear All
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear all history?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete all {runs.length} research sessions from your history.
                  This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => clearHistory()}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  Delete All
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
      </motion.div>

      {/* History List */}
      {filteredRuns.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-dashed border-2 bg-gradient-to-b from-white to-slate-50/50 dark:from-slate-900 dark:to-slate-950">
            <CardContent className="flex flex-col items-center justify-center py-20">
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-100 to-slate-50 shadow-inner dark:from-slate-800 dark:to-slate-900">
                <HistoryIcon className="h-10 w-10 text-slate-300 dark:text-slate-600" />
              </div>
              <h3 className="mt-6 text-xl font-semibold">No research history</h3>
              <p className="mt-2 max-w-sm text-center text-muted-foreground">
                {searchQuery 
                  ? "No results match your search query."
                  : "Your completed research sessions will appear here. Start your first research to see it here."}
              </p>
              {!searchQuery && (
                <Link href="/" className="mt-6">
                  <Button className="gap-2 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600">
                    <Sparkles className="h-4 w-4" />
                    Start New Research
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <div className="space-y-4">
          <AnimatePresence mode="popLayout">
            {filteredRuns.map((run, index) => (
              <motion.div
                key={run.runId}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className={cn(
                  "group overflow-hidden border-0 bg-gradient-to-b from-white to-slate-50/50 shadow-lg transition-all duration-300 hover:shadow-xl dark:from-slate-900 dark:to-slate-950",
                  run.status === 'done' && "hover:shadow-green-500/10",
                  run.status === 'error' && "hover:shadow-red-500/10"
                )}>
                  <div className={cn(
                    "absolute left-0 top-0 h-full w-1",
                    run.status === 'done' && "bg-gradient-to-b from-green-500 to-emerald-500",
                    run.status === 'error' && "bg-gradient-to-b from-red-500 to-rose-500"
                  )} />
                  <CardHeader className="pb-3 pl-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start gap-3">
                          <div className={cn(
                            "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                            run.status === 'done' && "bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/25",
                            run.status === 'error' && "bg-gradient-to-br from-red-500 to-rose-600 text-white shadow-lg shadow-red-500/25"
                          )}>
                            {run.status === 'done' ? (
                              <CheckCircle2 className="h-5 w-5" />
                            ) : (
                              <XCircle className="h-5 w-5" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <CardTitle className="text-base font-semibold line-clamp-2 leading-tight">
                              {run.query}
                            </CardTitle>
                            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                {format(new Date(run.completedAt), 'MMM d, yyyy')}
                              </span>
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {formatDistanceToNow(new Date(run.completedAt), { addSuffix: true })}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <Badge 
                        variant="outline"
                        className={cn(
                          "shrink-0 border-0 font-medium",
                          run.status === 'done' && "bg-green-100 text-green-700 dark:bg-green-950/50 dark:text-green-400",
                          run.status === 'error' && "bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400"
                        )}
                      >
                        {run.status === 'done' ? 'Complete' : 'Error'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0 pl-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1.5 rounded-md bg-slate-100 px-2 py-1 dark:bg-slate-800">
                          <FileText className="h-3.5 w-3.5 text-blue-500" />
                          <span className="font-medium">{run.wordCount.toLocaleString()}</span> words
                        </span>
                        <span className="flex items-center gap-1.5 rounded-md bg-slate-100 px-2 py-1 dark:bg-slate-800">
                          <Link2 className="h-3.5 w-3.5 text-cyan-500" />
                          <span className="font-medium">{run.evidence.length}</span> sources
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              className="h-9 w-9 p-0 text-muted-foreground hover:bg-red-100 hover:text-destructive dark:hover:bg-red-950/50"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Delete this research?</AlertDialogTitle>
                              <AlertDialogDescription>
                                This will permanently delete this research session. This action cannot be undone.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={() => removeRun(run.runId)}
                                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                              >
                                Delete
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                        <Button 
                          size="sm"
                          onClick={() => handleViewReport(run)}
                          className="gap-2 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
                        >
                          View Report
                          <ArrowRight className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Summary */}
      {runs.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-8 text-center text-sm text-muted-foreground"
        >
          Showing {filteredRuns.length} of {runs.length} research sessions
        </motion.div>
      )}
    </div>
  )
}
