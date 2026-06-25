import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { db } from '@/lib/db'
import { formatCents, formatDate } from '@/lib/utils'
import { INVOICE_STATUS_COLORS } from '@/types'
import { Receipt } from 'lucide-react'

export default async function InvoicesPage() {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')

  const clientUser = await db.clientUser.findUnique({
    where: { clerkId: userId },
    include: {
      client: {
        include: {
          invoices: { orderBy: { createdAt: 'desc' } },
        },
      },
    },
  })

  if (!clientUser) redirect('/sign-in')

  const invoices = clientUser.client.invoices
  const outstanding = invoices
    .filter((i) => i.status === 'SENT' || i.status === 'OVERDUE')
    .reduce((a, i) => a + i.amountCents, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Invoices</h1>
          <p className="text-slate-400 text-sm mt-1">Your billing history with Aurora.</p>
        </div>
        {outstanding > 0 && (
          <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg px-4 py-2 text-right">
            <p className="text-xs text-amber-400">Outstanding</p>
            <p className="text-lg font-bold text-amber-300">{formatCents(outstanding)}</p>
          </div>
        )}
      </div>

      {invoices.length === 0 && (
        <div className="text-center py-20 text-slate-500">
          <Receipt className="w-8 h-8 mx-auto mb-3 opacity-40" />
          <p>No invoices yet.</p>
        </div>
      )}

      <div className="space-y-2">
        {invoices.map((inv) => (
          <div
            key={inv.id}
            className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-4 flex items-center justify-between gap-4"
          >
            <div>
              <p className="font-medium">{inv.invoiceNumber}</p>
              {inv.description && (
                <p className="text-xs text-slate-500 mt-0.5 max-w-sm truncate">{inv.description}</p>
              )}
              <p className="text-xs text-slate-600 mt-1">
                Issued {formatDate(inv.createdAt)}
                {inv.dueDate && ` · Due ${formatDate(inv.dueDate)}`}
              </p>
            </div>
            <div className="flex items-center gap-4 shrink-0">
              <p className="text-lg font-semibold">{formatCents(inv.amountCents)}</p>
              <span
                className={`text-xs px-2.5 py-1 rounded-full font-medium ${INVOICE_STATUS_COLORS[inv.status]}`}
              >
                {inv.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
