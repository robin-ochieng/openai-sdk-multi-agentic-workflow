'use client'

import { ResearchSyncProvider } from '@/lib/useResearchSync'
import { AuthProvider } from '@/components/auth/AuthProvider'

interface ProvidersProps {
  children: React.ReactNode
}

/**
 * Client-side providers that need to wrap the app
 * - AuthProvider: Handles Supabase authentication state
 * - ResearchSyncProvider: Handles syncing research data with Supabase
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
      <ResearchSyncProvider>
        {children}
      </ResearchSyncProvider>
    </AuthProvider>
  )
}
