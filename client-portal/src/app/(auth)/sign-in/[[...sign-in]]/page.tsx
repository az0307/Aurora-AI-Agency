import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-purple-950">
      <div className="flex flex-col items-center gap-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">Aurora Client Portal</h1>
          <p className="text-slate-400 mt-1 text-sm">Sign in to view your projects and invoices</p>
        </div>
        <SignIn />
      </div>
    </main>
  )
}
