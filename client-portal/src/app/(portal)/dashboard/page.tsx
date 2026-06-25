import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { db } from '@/lib/db'
import { formatCents, formatDate } from '@/lib/utils'
import { JOB_STATUS_COLORS, JOB_STATUS_LABELS, INVOICE_STATUS_COLORS } from '@/types'
import { Briefcase, FileText, Receipt, Clock } from 'lucide-react'

export default async function DashboardPage() {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')

  const clientUser = await db.clientUser.findUnique({
    where: { clerkId: userId },
    include: {
      client: {
        include: {
          jobs: {
            include: { deliverables: true },
            orderBy: { updatedAt: 'desc' },
            take: 5,
          },
          invoices: {
            orderBy: { createdAt: 'desc' },
            take: 3,
          },
        },
      },
    },
  })

  if (!clientUser) redirect('/sign-in')

  const { client } = clientUser
  const activeJobs = client.jobs.filter((j) => j.status === 'IN_PROGRESS').length
  const doneJobs = client.jobs.filter((j) => j.status === 'DONE').length
  const totalDeliverables = client.jobs.reduce((a, j) => a + j.deliverables.length, 0)
  const unpaidInvoices = client.invoices.filter((i) => i.status === 'SENT' || i.status === 'OVERDUE')
  const unpaidTotal = unpaidInvoices.reduce((a, i) => a + i.amountCents, 0)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Welcome back, {clientUser.name.split(' ')[0]}</h1>
        <p className="text-slate-400 text-sm mt-1">Here's what's happening with your Aurora projects.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Active Jobs', value: activeJobs, icon: Briefcase, color: 'text-blue-400' },
          { label: 'Completed', value: doneJobs, icon: Clock, color: 'text-green-400' },
          { label: 'Deliverables', value: totalDeliverables, icon: FileText, color: 'text-purple-400' },
          { label: 'Outstanding', value: formatCents(unpaidTotal), icon: Receipt, color: 'text-amber-400' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
              <Icon className={`w-4 h-4 ${color}`} />
            </div>
            <p className="text-2xl font-bold">{value}</p>
          </div>
        ))}
      </div>

      {/* Recent Jobs */}
      <section>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Recent Jobs</h2>
        <div className="space-y-2">
          {client.jobs.length === 0 && (
            <p className="text-slate-500 text-sm">No jobs yet — your Aurora team is getting started.</p>
          )}
          {client.jobs.map((job) => (
            <div key={job.id} className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 flex items-center justify-between gap-4">
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{job.title}</p>
                {job.skill && <p className="text-xs text-slate-500">{job.skill}</p>}
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${JOB_STATUS_COLORS[job.status]}`}>
                  {JOB_STATUS_LABELS[job.status]}
                </span>
                <span className="text-xs text-slate-600">{formatDate(job.updatedAt)}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Recent Invoices */}
      <section>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Recent Invoices</h2>
        <div className="space-y-2">
          {client.invoices.length === 0 && (
            <p className="text-slate-500 text-sm">No invoices yet.</p>
          )}
          {client.invoices.map((inv) => (
            <div key={inv.id} className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium">{inv.invoiceNumber}</p>
                {inv.dueDate && <p className="text-xs text-slate-500">Due {formatDate(inv.dueDate)}</p>}
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold">{formatCents(inv.amountCents)}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${INVOICE_STATUS_COLORS[inv.status]}`}>
                  {inv.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
