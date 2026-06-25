import { redirect } from 'next/navigation'
import { auth } from '@clerk/nextjs/server'

export default function RootPage() {
  const { userId } = auth()
  if (userId) redirect('/dashboard')
  redirect('/sign-in')
}
