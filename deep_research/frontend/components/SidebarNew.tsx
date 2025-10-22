'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Activity, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  collapsed?: boolean
}

const navItems = [
  {
    title: 'Home',
    href: '/',
    icon: Home,
  },
  {
    title: 'Live Research',
    href: '/live',
    icon: Activity,
  },
  {
    title: 'Report',
    href: '/report',
    icon: FileText,
  },
]

export function Sidebar({ collapsed = false }: SidebarProps) {
  const pathname = usePathname()

  return (
    <aside
      className={cn(
        "flex h-screen flex-col border-r border-slate-200/60 bg-white dark:border-slate-800 dark:bg-slate-950",
        collapsed ? "w-16" : "w-64"
      )}
      aria-label="Sidebar"
    >
      {/* Brand */}
      <div className="flex h-16 items-center border-b border-slate-200/60 px-6 dark:border-slate-800">
        {!collapsed && (
          <div>
            <h2 className="text-lg font-bold tracking-tight">Deep Research</h2>
            <p className="text-xs text-muted-foreground">AI Agent</p>
          </div>
        )}
        {collapsed && (
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-lg font-bold">DR</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4" aria-label="Main navigation">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive ? 'page' : undefined}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-slate-100 dark:hover:bg-slate-900",
                isActive 
                  ? "bg-slate-100 text-slate-900 dark:bg-slate-900 dark:text-slate-50" 
                  : "text-slate-600 dark:text-slate-400"
              )}
            >
              <Icon className={cn(
                "h-5 w-5 shrink-0",
                isActive && "text-primary"
              )} />
              {!collapsed && <span>{item.title}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-200/60 p-4 dark:border-slate-800">
        <div className={cn(
          "rounded-lg bg-slate-50 p-3 dark:bg-slate-900",
          collapsed && "px-2"
        )}>
          {!collapsed ? (
            <>
              <p className="text-xs font-medium text-slate-900 dark:text-slate-50">
                Deep Research Agent
              </p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                v1.0.0 • Build 2025.10
              </p>
            </>
          ) : (
            <p className="text-center text-xs text-slate-500">v1.0</p>
          )}
        </div>
      </div>
    </aside>
  )
}
