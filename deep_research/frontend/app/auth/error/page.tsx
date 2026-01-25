'use client'

import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { AlertTriangle, ArrowLeft, RefreshCw } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

const ERROR_MESSAGES: Record<string, { title: string; description: string }> = {
  'access_denied': {
    title: 'Access Denied',
    description: 'You do not have permission to access this resource.',
  },
  'invalid_request': {
    title: 'Invalid Request',
    description: 'The authentication request was invalid or malformed.',
  },
  'server_error': {
    title: 'Server Error',
    description: 'An unexpected error occurred. Please try again later.',
  },
  'email_not_confirmed': {
    title: 'Email Not Confirmed',
    description: 'Please check your email and click the confirmation link.',
  },
  'invalid_credentials': {
    title: 'Invalid Credentials',
    description: 'The email or password you entered is incorrect.',
  },
  'session_expired': {
    title: 'Session Expired',
    description: 'Your session has expired. Please sign in again.',
  },
  'default': {
    title: 'Authentication Error',
    description: 'An error occurred during authentication. Please try again.',
  },
}

export default function AuthErrorPage() {
  const searchParams = useSearchParams()
  const errorCode = searchParams.get('error') || 'default'
  const errorDescription = searchParams.get('error_description')
  
  const errorInfo = ERROR_MESSAGES[errorCode] || ERROR_MESSAGES['default']

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
              <AlertTriangle className="h-6 w-6 text-destructive" />
            </div>
            <CardTitle className="text-2xl font-bold">{errorInfo.title}</CardTitle>
            <CardDescription>
              {errorDescription || errorInfo.description}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {errorCode !== 'default' && (
              <div className="rounded-md bg-muted p-3">
                <p className="text-xs text-muted-foreground">
                  Error code: <code className="font-mono">{errorCode}</code>
                </p>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex flex-col gap-3">
            <Button asChild className="w-full">
              <Link href="/auth/login">
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Link>
            </Button>
            <Link
              href="/"
              className="flex items-center justify-center text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to home
            </Link>
          </CardFooter>
        </Card>
      </motion.div>
    </div>
  )
}
