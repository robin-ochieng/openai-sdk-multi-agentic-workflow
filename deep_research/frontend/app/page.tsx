'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Sparkles, ArrowRight, Workflow, Activity, Link2, Plus, X, Mail } from 'lucide-react'

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
  emails: z.array(z.string().email({ message: 'Please enter a valid email address.' }).or(z.literal('')))
    .optional(),
})

type FormValues = z.infer<typeof formSchema>

export default function HomePage() {
  const router = useRouter()
  const { reset } = useRunStore()
  const [emailFields, setEmailFields] = useState<string[]>([''])

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      query: '',
      emails: [''],
    },
  })

  const addEmailField = () => {
    if (emailFields.length < 5) {
      setEmailFields([...emailFields, ''])
    }
  }

  const removeEmailField = (index: number) => {
    if (emailFields.length > 1) {
      const newFields = emailFields.filter((_, i) => i !== index)
      setEmailFields(newFields)
      // Update form value
      const currentEmails = form.getValues('emails') || []
      const newEmails = currentEmails.filter((_, i) => i !== index)
      form.setValue('emails', newEmails)
    }
  }

  const updateEmailField = (index: number, value: string) => {
    const newFields = [...emailFields]
    newFields[index] = value
    setEmailFields(newFields)
    // Update form value
    form.setValue('emails', newFields)
  }

  const onSubmit = async (values: FormValues) => {
    // Generate a unique run ID
    const runId = `run_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // Filter out empty emails and join with commas
    const validEmails = emailFields.filter(email => email.trim() !== '' && email.includes('@'))
    const emailString = validEmails.join(',')
    
    // Reset store with new run data
    reset(runId, values.query, emailString || undefined)
    
    // Navigate to live research page with new flag to ensure fresh stream
    // Pass query in URL to avoid hydration timing issues with Zustand store
    const params = new URLSearchParams({
      runId,
      query: values.query,
      new: '1',
    })
    if (emailString) {
      params.set('email', emailString)
    }
    
    router.push(`/live?${params.toString()}`)
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

              {/* Email Field (Optional) - Multiple Recipients */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <FormLabel>Email Recipients (Optional)</FormLabel>
                  {emailFields.length < 5 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={addEmailField}
                      className="h-8 gap-1 text-xs text-primary hover:text-primary"
                    >
                      <Plus className="h-3.5 w-3.5" />
                      Add Recipient
                    </Button>
                  )}
                </div>
                
                <div className="space-y-2">
                  <AnimatePresence mode="popLayout">
                    {emailFields.map((email, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                        className="flex items-center gap-2"
                      >
                        <div className="relative flex-1">
                          <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                          <Input
                            type="email"
                            placeholder={index === 0 ? "primary@email.com" : `recipient${index + 1}@email.com`}
                            value={email}
                            onChange={(e) => updateEmailField(index, e.target.value)}
                            className="pl-9"
                          />
                        </div>
                        {emailFields.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => removeEmailField(index)}
                            className="h-9 w-9 shrink-0 text-muted-foreground hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-950/50"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
                
                <FormDescription>
                  {emailFields.length === 1 
                    ? "Receive the research report via email when complete"
                    : `Send report to ${emailFields.filter(e => e.includes('@')).length || 0} recipient(s)`
                  }
                  {emailFields.length < 5 && " • Max 5 recipients"}
                </FormDescription>
              </div>

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
          {/* 4-Agent Pipeline Card */}
          <motion.div
            whileHover={{ y: -4, scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            className="group relative overflow-hidden rounded-xl border border-slate-200/80 bg-gradient-to-b from-white to-slate-50/80 p-5 shadow-sm transition-shadow hover:shadow-lg dark:border-slate-800 dark:from-slate-900 dark:to-slate-950"
          >
            <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br from-violet-500/10 to-purple-500/5 blur-2xl transition-opacity group-hover:opacity-100" />
            <div className="relative">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/25">
                <Workflow className="h-5 w-5" />
              </div>
              <h3 className="mb-1.5 font-semibold text-slate-900 dark:text-white">4-Agent Pipeline</h3>
              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Planner, Searcher, Synthesizer, and Editor work together seamlessly
              </p>
            </div>
          </motion.div>

          {/* Live Progress Card */}
          <motion.div
            whileHover={{ y: -4, scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            className="group relative overflow-hidden rounded-xl border border-slate-200/80 bg-gradient-to-b from-white to-slate-50/80 p-5 shadow-sm transition-shadow hover:shadow-lg dark:border-slate-800 dark:from-slate-900 dark:to-slate-950"
          >
            <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br from-blue-500/10 to-cyan-500/5 blur-2xl transition-opacity group-hover:opacity-100" />
            <div className="relative">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/25">
                <Activity className="h-5 w-5" />
              </div>
              <h3 className="mb-1.5 font-semibold text-slate-900 dark:text-white">Live Progress</h3>
              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Watch each agent work in real-time with detailed logs
              </p>
            </div>
          </motion.div>

          {/* Source-Backed Card */}
          <motion.div
            whileHover={{ y: -4, scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            className="group relative overflow-hidden rounded-xl border border-slate-200/80 bg-gradient-to-b from-white to-slate-50/80 p-5 shadow-sm transition-shadow hover:shadow-lg dark:border-slate-800 dark:from-slate-900 dark:to-slate-950"
          >
            <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br from-emerald-500/10 to-teal-500/5 blur-2xl transition-opacity group-hover:opacity-100" />
            <div className="relative">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/25">
                <Link2 className="h-5 w-5" />
              </div>
              <h3 className="mb-1.5 font-semibold text-slate-900 dark:text-white">Source-Backed</h3>
              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Every claim is traceable to original sources
              </p>
            </div>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}
