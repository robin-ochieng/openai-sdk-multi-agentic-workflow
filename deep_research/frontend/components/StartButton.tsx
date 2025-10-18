'use client'

import { motion } from 'framer-motion'
import { Search, Loader2, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'

type ButtonState = 'idle' | 'loading' | 'success'

interface StartButtonProps {
  onClick: () => void
  disabled?: boolean
  state?: ButtonState
  queryLength: number
  className?: string
}

export function StartButton({ 
  onClick, 
  disabled = false, 
  state = 'idle',
  queryLength,
  className 
}: StartButtonProps) {
  const isDisabled = disabled || queryLength < 12 || state === 'loading'
  
  const buttonContent = {
    idle: {
      icon: <Search className="h-5 w-5" />,
      text: 'Start Research'
    },
    loading: {
      icon: <Loader2 className="h-5 w-5 animate-spin" />,
      text: 'Starting…'
    },
    success: {
      icon: <CheckCircle2 className="h-5 w-5" />,
      text: 'Running'
    }
  }

  const content = buttonContent[state]

  return (
    <div className="space-y-2">
      <motion.button
        onClick={onClick}
        disabled={isDisabled}
        type="button"
        className={cn(
          'group relative w-full h-12 rounded-2xl text-base font-medium',
          'flex items-center justify-center gap-2',
          'transition-all duration-300',
          'focus-ring-premium',
          isDisabled
            ? 'bg-muted text-muted-foreground cursor-not-allowed'
            : 'bg-primary text-primary-foreground hover:shadow-premium-lg btn-shine',
          state === 'success' && 'bg-green-600 hover:bg-green-600',
          className
        )}
        whileHover={!isDisabled ? { scale: 1.01 } : {}}
        whileTap={!isDisabled ? { scale: 0.99 } : {}}
        aria-live="polite"
        aria-busy={state === 'loading'}
        aria-label={`${content.text}${queryLength < 12 ? '. Query must be at least 12 characters.' : ''}`}
      >
        {content.icon}
        <span>{content.text}</span>
      </motion.button>
      
      {queryLength > 0 && queryLength < 12 && (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xs text-muted-foreground text-center"
        >
          {12 - queryLength} more character{12 - queryLength !== 1 ? 's' : ''} required
        </motion.p>
      )}
    </div>
  )
}
