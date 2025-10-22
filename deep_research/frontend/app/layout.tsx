import type { Metadata, Viewport } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { Sidebar } from "@/components/SidebarNew"
import { Topbar } from "@/components/Topbar"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Deep Research Agent | AI-Powered Research System",
  description: "Professional AI research system with 4-agent pipeline for comprehensive, traceable research reports",
  keywords: ["AI", "Research", "OpenAI", "Agents", "Deep Research"],
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
    ],
    apple: [
      { url: '/apple-touch-icon.svg', sizes: '180x180', type: 'image/svg+xml' },
    ],
  },
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Deep Research',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#3b82f6' },
    { media: '(prefers-color-scheme: dark)', color: '#1e40af' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
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
        </ThemeProvider>
      </body>
    </html>
  )
}
