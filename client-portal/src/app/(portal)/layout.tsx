import { redirect } from 'next/navigation'
import { auth, currentUser } from '@clerk/nextjs/server'
import { UserButton } from '@clerk/nextjs'
import Link from 'next/link'
import { LayoutDashboard, Briefcase, FileText, Receipt, Zap } from 'lucide-react'
import { db } from '@/lib/db'

const navItems = [
  { href: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { href: '/jobs', label: 'Jobs', icon: Briefcase },
  { href: '/deliverables', label: 'Deliverables', icon: FileText },
  { href: '/invoices', label: 'Invoices', icon: Receipt },
]

export default async function PortalLayout({ children }: { children: React.ReactNode }) {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')

  const user = await currentUser()
  const clientUser = await db.clientUser.findUnique({
    where: { clerkId: userId },
    include: { client: true },
  })

  if (!clientUser) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        <div className="text-center space-y-3">
          <Zap className="w-10 h-10 text-purple-400 mx-auto" />
          <h2 className="text-xl font-semibold">Portal access pending</h2>
          <p className="text-slate-400 text-sm max-w-xs">
            Your Aurora account is being set up. You'll receive an email when ready.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex bg-slate-950 text-white">
      {/* Sidebar */}
      <aside className="w-60 border-r border-slate-800 flex flex-col p-4 gap-1">
        <div className="flex items-center gap-2 px-2 py-3 mb-4">
          <Zap className="w-5 h-5 text-purple-400" />
          <span className="font-semibold text-sm">Aurora Portal</span>
        </div>

        <p className="text-xs text-slate-500 px-2 mb-1 uppercase tracking-wider">
          {clientUser.client.business || clientUser.client.name}
        </p>

        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
          >
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}

        <div className="mt-auto pt-4 border-t border-slate-800 flex items-center gap-3 px-2">
          <UserButton afterSignOutUrl="/sign-in" />
          <div className="text-xs truncate">
            <p className="text-white font-medium truncate">{user?.firstName ?? clientUser.name}</p>
            <p className="text-slate-500 truncate">{clientUser.email}</p>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  )
}
