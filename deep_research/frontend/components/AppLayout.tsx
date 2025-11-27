'use client'

import { usePathname } from 'next/navigation'
import { Sidebar } from '@/components/SidebarNew'
import { Topbar } from '@/components/Topbar'

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  
  // Auth pages get a minimal layout without sidebar
  const isAuthPage = pathname?.startsWith('/auth')
  
  if (isAuthPage) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-slate-100 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950">
        {children}
      </div>
    )
  }

  // Regular pages get the full layout with sidebar and topbar
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop Sidebar - Fixed on md+ */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Topbar with mobile menu and theme toggle */}
        <Topbar />

        {/* Page Content with gradient background */}
        <main className="flex-1 overflow-auto bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
          {children}
        </main>
      </div>
    </div>
  )
}
