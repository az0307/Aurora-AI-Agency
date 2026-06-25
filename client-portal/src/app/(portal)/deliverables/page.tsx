import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { db } from '@/lib/db'
import { formatDate } from '@/lib/utils'
import { ExternalLink, FileText, Image, Video, Link2, BarChart2 } from 'lucide-react'

const ICON_MAP: Record<string, React.ElementType> = {
  DOCUMENT: FileText,
  IMAGE: Image,
  VIDEO: Video,
  LINK: Link2,
  REPORT: BarChart2,
  WORKFLOW: FileText,
  OTHER: FileText,
}

export default async function DeliverablesPage() {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')

  const clientUser = await db.clientUser.findUnique({
    where: { clerkId: userId },
    include: {
      client: {
        include: {
          jobs: {
            include: { deliverables: { orderBy: { createdAt: 'desc' } } },
            orderBy: { updatedAt: 'desc' },
          },
        },
      },
    },
  })

  if (!clientUser) redirect('/sign-in')

  const allDeliverables = clientUser.client.jobs.flatMap((job) =>
    job.deliverables.map((d) => ({ ...d, jobTitle: job.title }))
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Deliverables</h1>
        <p className="text-slate-400 text-sm mt-1">Everything Aurora has produced for you.</p>
      </div>

      {allDeliverables.length === 0 && (
        <div className="text-center py-20 text-slate-500">
          <FileText className="w-8 h-8 mx-auto mb-3 opacity-40" />
          <p>No deliverables yet — they'll appear here as jobs complete.</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {allDeliverables.map((d) => {
          const Icon = ICON_MAP[d.type] ?? FileText
          return (
            <a
              key={d.id}
              href={d.url}
              target="_blank"
              rel="noreferrer"
              className="group bg-slate-900 border border-slate-800 hover:border-purple-700 rounded-xl p-4 flex items-start gap-3 transition-colors"
            >
              <div className="shrink-0 w-9 h-9 bg-purple-900/40 rounded-lg flex items-center justify-center">
                <Icon className="w-4 h-4 text-purple-400" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium group-hover:text-purple-300 transition-colors flex items-center gap-1.5">
                  {d.name}
                  <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                </p>
                <p className="text-xs text-slate-500 mt-0.5">{d.jobTitle}</p>
                {d.description && <p className="text-xs text-slate-400 mt-1">{d.description}</p>}
                <p className="text-xs text-slate-600 mt-1">{formatDate(d.createdAt)}</p>
              </div>
            </a>
          )
        })}
      </div>
    </div>
  )
}
