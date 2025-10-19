import Link from 'next/link'

export default function DashboardHome() {
  const sections = [
    { href: '/dashboard/analytics', label: 'Analytics' },
    { href: '/dashboard/icps', label: 'ICPs' },
    { href: '/dashboard/moves', label: 'Moves' },
    { href: '/dashboard/positioning', label: 'Positioning' },
    { href: '/dashboard/research', label: 'Research' },
    { href: '/dashboard/strategy', label: 'Strategy' },
    { href: '/dashboard/settings', label: 'Settings' }
  ]

  return (
    <main className="p-6">
      <h1 className="text-3xl font-semibold mb-6">Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sections.map((s) => (
          <Link
            key={s.href}
            href={s.href}
            className="block rounded-xl border p-4 hover:bg-gray-50 transition"
          >
            <div className="text-lg font-medium">{s.label}</div>
            <div className="text-sm text-gray-500">{s.href}</div>
          </Link>
        ))}
      </div>
    </main>
  )
}
