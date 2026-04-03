import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/api/endpoints'
import clsx from 'clsx'

const NAV_ITEMS = [
  { to: '/',             label: 'Overview',    roles: ['system_admin','supervisor','analyst','executive','partner_user'] },
  { to: '/groups',       label: 'Groups',      roles: ['system_admin','supervisor','analyst','field_agent','executive','partner_user'] },
  { to: '/farmers',      label: 'Farmers',     roles: ['system_admin','supervisor','analyst','field_agent','executive'] },
  { to: '/map',          label: 'Map',         roles: ['system_admin','supervisor','analyst','executive','partner_user'] },
  { to: '/analytics',    label: 'Analytics',   roles: ['system_admin','supervisor','analyst','executive'] },
  { to: '/impact',       label: 'Impact',      roles: ['system_admin','analyst','executive','partner_user'] },
  { to: '/reports',      label: 'Reports',     roles: ['system_admin','analyst','executive','partner_user'] },
  { to: '/parameters',   label: 'Parameters',  roles: ['system_admin'] },
  { to: '/agents',       label: 'Agents',      roles: ['system_admin','supervisor','analyst'] },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { user, refreshToken, logout } = useAuthStore()

  const handleLogout = async () => {
    if (refreshToken) {
      try { await authApi.logout(refreshToken) } catch { /* ignore */ }
    }
    logout()
    navigate('/login')
  }

  const visibleNav = NAV_ITEMS.filter(
    (item) => !user || item.roles.includes(user.role)
  )

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-60 bg-primary-900 text-white flex flex-col shrink-0">
        <div className="px-6 py-5 border-b border-primary-700">
          <p className="text-xs text-primary-200 uppercase tracking-widest font-mono">AgriProfile</p>
          <p className="text-sm text-primary-200 mt-0.5">BAHMARK Group</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {visibleNav.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={clsx(
                'flex items-center px-3 py-2 rounded text-sm font-medium transition-colors',
                pathname === item.to
                  ? 'bg-primary-700 text-white'
                  : 'text-primary-200 hover:bg-primary-700 hover:text-white',
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-primary-700">
          <p className="text-xs text-primary-200 truncate">{user?.full_name}</p>
          <p className="text-xs text-primary-500 capitalize">{user?.role?.replace('_', ' ')}</p>
          <button
            onClick={handleLogout}
            className="mt-2 text-xs text-primary-200 hover:text-white transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto bg-neutral-100">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
