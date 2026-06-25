import type {
  Agency,
  Client,
  ClientUser,
  Job,
  Deliverable,
  JobActivity,
  Invoice,
} from '@prisma/client'

export type ClientWithDetails = Client & {
  users: ClientUser[]
  jobs: (Job & { deliverables: Deliverable[] })[]
  invoices: Invoice[]
}

export type JobWithDetails = Job & {
  deliverables: Deliverable[]
  activities: JobActivity[]
  client: Client
}

export type InvoiceWithClient = Invoice & { client: Client }

export const JOB_STATUS_LABELS: Record<string, string> = {
  INBOX: 'Inbox',
  IN_PROGRESS: 'In Progress',
  REVIEW: 'Under Review',
  DONE: 'Done',
  CANCELLED: 'Cancelled',
}

export const JOB_STATUS_COLORS: Record<string, string> = {
  INBOX: 'bg-slate-100 text-slate-700',
  IN_PROGRESS: 'bg-blue-100 text-blue-700',
  REVIEW: 'bg-amber-100 text-amber-700',
  DONE: 'bg-green-100 text-green-700',
  CANCELLED: 'bg-red-100 text-red-700',
}

export const INVOICE_STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-slate-100 text-slate-700',
  SENT: 'bg-blue-100 text-blue-700',
  PAID: 'bg-green-100 text-green-700',
  OVERDUE: 'bg-red-100 text-red-700',
  CANCELLED: 'bg-slate-100 text-slate-500',
}
