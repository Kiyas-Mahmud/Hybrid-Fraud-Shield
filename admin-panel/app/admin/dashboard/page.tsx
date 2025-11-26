'use client';

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { MdPeople, MdCreditCard, MdWarning, MdBlock } from 'react-icons/md';

interface Stats {
  total_users: number;
  total_transactions: number;
  fraud_rate: number;
  blocked_transactions: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('http://localhost:8000/api/v1/admin/statistics', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Stats data:', data); // Debug log
        setStats(data);
      } else {
        console.error('Failed to fetch stats:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-admin-bg min-h-screen">
      <Header title="Dashboard Overview" />
      
      <div className="p-8">
        {loading ? (
          <div className="text-admin-text">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Users"
              value={stats?.total_users || 0}
              icon={MdPeople}
              color="blue"
            />
            <StatCard
              title="Total Transactions"
              value={stats?.total_transactions || 0}
              icon={MdCreditCard}
              color="green"
            />
            <StatCard
              title="Fraud Rate"
              value={`${((stats?.fraud_rate || 0) * 100).toFixed(1)}%`}
              icon={MdWarning}
              color="red"
            />
            <StatCard
              title="Blocked"
              value={stats?.blocked_transactions || 0}
              icon={MdBlock}
              color="yellow"
            />
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }: { 
  title: string; 
  value: string | number; 
  icon: React.ComponentType<{ className?: string }>; 
  color: string 
}) {
  const colors = {
    blue: 'bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-accent-blue',
    green: 'bg-gradient-to-br from-teal-50 to-teal-100 border-l-4 border-accent-teal',
    red: 'bg-gradient-to-br from-red-50 to-red-100 border-l-4 border-red-500',
    yellow: 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-l-4 border-accent-yellow',
  };

  const iconColors = {
    blue: 'text-accent-blue',
    green: 'text-accent-teal',
    red: 'text-red-500',
    yellow: 'text-accent-yellow',
  };

  return (
    <div className={`${colors[color as keyof typeof colors]} rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300`}>
      <div className="flex items-center justify-between mb-3">
        <Icon className={`text-4xl ${iconColors[color as keyof typeof iconColors]}`} />
      </div>
      <div className="text-sm text-admin-text-light font-medium mb-1">{title}</div>
      <div className="text-3xl font-bold text-admin-text">{value}</div>
    </div>
  );
}
