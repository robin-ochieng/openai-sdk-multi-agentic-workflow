'use client'

import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { motion } from 'framer-motion'
import { Search, Sparkles, ArrowRight } from 'lucide-react'

import { useRunStore } from '@/lib/runStore'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'

const formSchema = z.object({
  query: z.string()
    .min(12, {
      message: 'Query must be at least 12 characters for better results.',
    })
    .max(500, {
      message: 'Query must be less than 500 characters.',
    }),
  email: z.string()
    .email({
      message: 'Please enter a valid email address.',
    })
    .optional()
    .or(z.literal('')),
})

type FormValues = z.infer<typeof formSchema>

export default function HomePage() {
  const router = useRouter()
  const { reset } = useRunStore()

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      query: '',
      email: '',
    },
  })

  const onSubmit = async (values: FormValues) => {
    // Generate a unique run ID
    const runId = `run_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // Reset store with new run data
    reset(runId, values.query, values.email || undefined)
    
    // Navigate to live research page - streaming starts automatically
    router.push(`/live?runId=${runId}`)
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        {/* Header */}
        <div className="mb-8 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary"
          >
            <Sparkles className="h-4 w-4" />
            <span>AI-Powered Research</span>
          </motion.div>
          
          <h1 className="mb-3 text-4xl font-bold tracking-tight md:text-5xl">
            Deep Research Agent
          </h1>
          <p className="text-lg text-muted-foreground">
            Enter a research query and let our AI agents find, analyze, and synthesize information for you
          </p>
        </div>

        {/* Form Card */}
        <Card className="border-slate-200 bg-white p-8 shadow-xl dark:border-slate-800 dark:bg-slate-950">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Query Field */}
              <FormField
                control={form.control}
                name="query"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-base font-semibold">
                      Research Query
                    </FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="e.g., What are the latest developments in quantum computing and their potential applications in cryptography?"
                        className="min-h-[120px] resize-none text-base"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Minimum 12 characters. Be specific for better results.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Email Field (Optional) */}
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email (Optional)</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="your@email.com"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Receive the research report via email when complete
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Submit Button */}
              <Button
                type="submit"
                size="lg"
                className="w-full text-base"
                disabled={form.formState.isSubmitting}
              >
                {form.formState.isSubmitting ? (
                  <>
                    <Search className="mr-2 h-5 w-5 animate-spin" />
                    Starting Research...
                  </>
                ) : (
                  <>
                    Start Research
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </>
                )}
              </Button>
            </form>
          </Form>
        </Card>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-8 grid gap-4 sm:grid-cols-3"
        >
          <div className="rounded-lg border border-slate-200/60 bg-white/50 p-4 dark:border-slate-800 dark:bg-slate-950/50">
            <h3 className="mb-1 font-semibold">4-Agent Pipeline</h3>
            <p className="text-sm text-muted-foreground">
              Planner, Searcher, Synthesizer, and Editor work together
            </p>
          </div>
          <div className="rounded-lg border border-slate-200/60 bg-white/50 p-4 dark:border-slate-800 dark:bg-slate-950/50">
            <h3 className="mb-1 font-semibold">Live Progress</h3>
            <p className="text-sm text-muted-foreground">
              Watch each agent work in real-time with detailed logs
            </p>
          </div>
          <div className="rounded-lg border border-slate-200/60 bg-white/50 p-4 dark:border-slate-800 dark:bg-slate-950/50">
            <h3 className="mb-1 font-semibold">Source-Backed</h3>
            <p className="text-sm text-muted-foreground">
              Every claim is traceable to original sources
            </p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}
