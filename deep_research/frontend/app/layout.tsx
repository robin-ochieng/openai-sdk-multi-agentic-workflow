import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Deep Research Agent | AI-Powered Research System",
  description: "Professional AI research system with 4-agent pipeline for comprehensive, traceable research reports",
  keywords: ["AI", "Research", "OpenAI", "Agents", "Deep Research"],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-950 dark:via-blue-950 dark:to-purple-950">
          {children}
        </div>
      </body>
    </html>
  )
}
