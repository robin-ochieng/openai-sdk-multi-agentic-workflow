import { Button } from '@/components/ui/button'
import { Loader2, Rocket } from 'lucide-react'

interface StartButtonProps {
  onClick?: () => void | Promise<void>
  disabled?: boolean
  state?: 'idle' | 'loading' | 'success'
  queryLength?: number
}

export function StartButton({ onClick, disabled, state = 'idle', queryLength }: StartButtonProps) {
  const isBusy = state === 'loading'
  const isQueryTooShort = typeof queryLength === 'number' && queryLength < 10
  const isDisabled = disabled || isBusy || isQueryTooShort

  const label =
    state === 'success'
      ? 'Research Complete'
      : state === 'loading'
      ? 'Researching...'
      : 'Start Research'

  return (
    <Button
      type="submit"
      onClick={onClick}
      disabled={isDisabled}
      className="w-full"
    >
      {isBusy ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : (
        <Rocket className="mr-2 h-4 w-4" />
      )}
      {label}
    </Button>
  )
}
