import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { db } from '@/lib/db'
import { formatDate } from '@/lib/utils'
import { JOB_STATUS_COLORS, JOB_STATUS_LABELS } from '@/types'
import { FileText } from 'lucide-react'

export default async function JobsPage() {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')

  const clientUser = await db.clientUser.findUnique({
    where: { clerkId: userId },
    include: {
      client: {
        include: {
          jobs: {
            include: { deliverables: true, activities: { orderBy: { createdAt: 'desc' }, take: 3 } },
            orderBy: { updatedAt: 'desc' },
          },
        },
      },
    },
  })

  if (!clientUser) redirect('/sign-in')

  const jobs = clientUser.client.jobs

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Jobs</h1>
        <p className="text-slate-400 text-sm mt-1">All projects Aurora is running for you.</p>
      </div>

      {jobs.length === 0 && (
        <div className="text-center py-20 text-slate-500">
          <FileText className="w-8 h-8 mx-auto mb-3 opacity-40" />
          <p>No jobs yet — check back soon.</p>
        </div>
      )}

      <div className="space-y-3">
        {jobs.map((job) => (
          <div key={job.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-semibold">{job.title}</p>
                {job.skill && <p className="text-xs text-slate-500 mt-0.5">{job.skill}</p>}
                {job.description && (
                  <p className="text-sm text-slate-400 mt-2">{job.description}</p>
                )}
              </div>
              <div className="flex flex-col items-end gap-2 shrink-0">
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${JOB_STATUS_COLORS[job.status]}`}>
                  {JOB_STATUS_LABELS[job.status]}
                </span>
                <span className="text-xs text-slate-600">{formatDate(job.updatedAt)}</span>
              </div>
            </div>

            {/* Deliverables */}
            {job.deliverables.length > 0 && (
              <div className="border-t border-slate-800 pt-3">
                <p className="text-xs text-slate-500 mb-2">Deliverables</p>
                <div className="flex flex-wrap gap-2">
                  {job.deliverables.map((d) => (
                    <a
                      key={d.id}
                      href={d.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs bg-purple-900/40 text-purple-300 border border-purple-800/50 px-2.5 py-1 rounded-full hover:bg-purple-900/70 transition-colors"
                    >
                      {d.name}
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Activity */}
            {job.activities.length > 0 && (
              <div className="border-t border-slate-800 pt-3 space-y-1.5">
                {job.activities.map((a) => (
                  <div key={a.id} className="flex items-start gap-2 text-xs text-slate-400">
                    <span className="text-slate-600 shrink-0 mt-0.5">{formatDate(a.createdAt)}</span>
                    <span>{a.message}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
