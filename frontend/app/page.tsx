import { redirect } from 'next/navigation'

export default function Home() {
  // Редирект на dashboard
  redirect('/dashboard')
}
