import { headers } from 'next/headers'
import { NextResponse } from 'next/server'
import { Webhook } from 'svix'
import { db } from '@/lib/db'

export async function POST(req: Request) {
  const body = await req.text()
  const headerPayload = headers()
  const svixId = headerPayload.get('svix-id')
  const svixTimestamp = headerPayload.get('svix-timestamp')
  const svixSignature = headerPayload.get('svix-signature')

  if (!svixId || !svixTimestamp || !svixSignature) {
    return NextResponse.json({ error: 'Missing svix headers' }, { status: 400 })
  }

  const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!)
  let event: { type: string; data: Record<string, unknown> }

  try {
    event = wh.verify(body, {
      'svix-id': svixId,
      'svix-timestamp': svixTimestamp,
      'svix-signature': svixSignature,
    }) as typeof event
  } catch {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  if (event.type === 'user.created' || event.type === 'user.updated') {
    const data = event.data
    const clerkId = data.id as string
    const email = (data.email_addresses as Array<{ email_address: string; id: string; verification: { status: string } }>)
      .find((e) => e.id === data.primary_email_address_id)?.email_address ?? ''
    const name = `${data.first_name ?? ''} ${data.last_name ?? ''}`.trim() || email
    const avatarUrl = (data.image_url as string) ?? null

    const existing = await db.clientUser.findUnique({ where: { clerkId } })

    if (existing) {
      await db.clientUser.update({
        where: { clerkId },
        data: { name, email, avatarUrl },
      })
    }
    // New users without an existing ClientUser record get one only when Aurora
    // manually links them to a client via the admin API.
  }

  return NextResponse.json({ received: true })
}
