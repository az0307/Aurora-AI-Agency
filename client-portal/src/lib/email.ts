// Thin wrapper around Resend's REST API — intentionally no `resend` SDK dependency
// (avoids an install-time dependency in sandboxed environments). Mirrors the raw
// `fetch` pattern already used in the sibling ymiroofing.com.au repo's
// `functions/api/lead.js`.

const RESEND_API_URL = 'https://api.resend.com/emails'

interface SendEmailParams {
  to: string
  subject: string
  html: string
  text?: string
}

/**
 * Send a transactional email via Resend's REST API.
 *
 * Ready to be called from future Stripe billing webhooks or deliverable
 * notification routes once those handlers exist — no changes needed here.
 */
export async function sendEmail({ to, subject, html, text }: SendEmailParams): Promise<void> {
  const apiKey = process.env.RESEND_API_KEY
  const from = process.env.EMAIL_FROM || 'Aurora AI Agency <noreply@aurora-agency.example>'

  if (!apiKey) {
    console.warn('[email] RESEND_API_KEY not set — skipping send', { to, subject })
    return
  }

  const res = await fetch(RESEND_API_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from,
      to,
      subject,
      html,
      ...(text ? { text } : {}),
    }),
  })

  if (!res.ok) {
    const body = await res.text().catch(() => '')
    console.error('[email] Resend send failed', { status: res.status, body })
  }
}
