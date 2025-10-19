'use client'

import { usePathname } from 'next/navigation'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { MobileSidebar } from './MobileSidebar'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

const routeTitles: Record<string, string> = {
  '/': 'Home',
  '/live': 'Live Research',
  '/report': 'Report',
}

export function Topbar() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  const pageTitle = routeTitles[pathname] || 'Deep Research Agent'

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-slate-200/60 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:border-slate-800 dark:bg-slate-950/95 dark:supports-[backdrop-filter]:bg-slate-950/60 px-6">
      {/* Mobile menu */}
      <MobileSidebar />

      {/* Page title */}
      <div className="flex-1">
        <h1 className="text-lg font-semibold tracking-tight">{pageTitle}</h1>
      </div>

      {/* Theme toggle */}
      {mounted && (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>
      )}
    </header>
  )
}
