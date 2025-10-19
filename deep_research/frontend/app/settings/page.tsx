'use client'

import { motion } from 'framer-motion'
import { Settings as SettingsIcon } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="border-b border-border/40 bg-background/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="mt-2 text-muted-foreground">
            Configure your Deep Research Agent preferences
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center text-center"
          >
            <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-muted">
              <SettingsIcon className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">Settings Coming Soon</h3>
            <p className="text-sm text-muted-foreground max-w-md">
              Configure API keys, email preferences, and research settings in the next update
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
