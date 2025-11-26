'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { MdDashboard, MdCreditCard, MdPeople, MdLogout } from 'react-icons/md';

const navigation = [
  { name: 'Dashboard', href: '/admin/dashboard', icon: MdDashboard },
  { name: 'Transactions', href: '/admin/dashboard/transactions', icon: MdCreditCard },
  { name: 'Users', href: '/admin/dashboard/users', icon: MdPeople },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [adminUser, setAdminUser] = useState<{username: string; role: string} | null>(null);

  useEffect(() => {
    const user = localStorage.getItem('admin_user');
    if (user) {
      setAdminUser(JSON.parse(user));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    router.push('/admin/login');
  };

  return (
    <div className="w-64 bg-gray-50 h-screen fixed left-0 top-0 flex flex-col border-r border-gray-200">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-orange rounded-lg flex items-center justify-center">
            <span className="text-white text-xl font-bold">FS</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-primary-navy">Fraud Shield</h1>
            <p className="text-xs text-gray-500">Admin Dashboard</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigation.map((item) => {
          // Fix: Only dashboard should match exactly, others match with children
          const isActive = item.href === '/admin/dashboard' 
            ? pathname === item.href
            : pathname === item.href || pathname?.startsWith(item.href + '/');
          const IconComponent = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-primary-orange bg-opacity-10 text-primary-navy border-l-4 border-primary-orange'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <IconComponent className="text-lg" />
              <span className="font-medium text-sm">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-gray-200">
        {adminUser && (
          <div className="mb-3 px-3 py-2 bg-gray-100 rounded-lg">
            <p className="text-xs text-gray-500">Signed in as</p>
            <p className="text-primary-navy font-semibold text-sm mt-1">{adminUser.username}</p>
            <p className="text-xs text-primary-orange mt-0.5">{adminUser.role}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 font-medium text-sm"
        >
          <MdLogout className="text-base" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}
