'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Github } from 'lucide-react'
import { ThemeToggle } from '@/components/theme-toggle'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function Navbar() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center px-8">
        <div className="mr-8 flex">
          <Link href="/" className="mr-8 flex items-center space-x-2">
            <span className="text-lg font-bold">systtechbot</span>
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link
              href="/dashboard"
              className={cn(
                'transition-colors hover:text-foreground/80',
                pathname === '/dashboard'
                  ? 'text-foreground font-medium'
                  : 'text-foreground/60'
              )}
            >
              Dashboard
            </Link>
            <Link
              href="/chat"
              className={cn(
                'transition-colors hover:text-foreground/80',
                pathname === '/chat'
                  ? 'text-foreground font-medium'
                  : 'text-foreground/60'
              )}
            >
              Chat
            </Link>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          <nav className="flex items-center space-x-1">
            <Button variant="ghost" size="icon" asChild>
              <a
                href="https://github.com/hanafubuuki/systtechbot"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Github className="h-[1.2rem] w-[1.2rem]" />
                <span className="sr-only">GitHub</span>
              </a>
            </Button>
            <ThemeToggle />
          </nav>
        </div>
      </div>
    </header>
  )
}

