'use client';

import { Button } from '@/components/ui';
import { useAuth } from '@/lib/context/AuthContext';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const handleNewTransaction = () => {
    router.push('/dashboard/transactions/new');
  };

  const handleTransactionHistory = () => {
    router.push('/dashboard/transactions');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 px-4">
        {/* Welcome Section */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome, {user?.full_name || user?.username}!
          </h1>
          <p className="mt-3 text-gray-600">
            Fraud Detection System
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-4">
          <Button
            variant="primary"
            fullWidth
            size="lg"
            onClick={handleNewTransaction}
          >
            New Transaction
          </Button>

          <Button
            variant="secondary"
            fullWidth
            size="lg"
            onClick={handleTransactionHistory}
          >
            Transaction History
          </Button>

          <Button
            variant="secondary"
            fullWidth
            size="lg"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </div>

        {/* Info Section */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800 text-center">
            Submit new transactions or view your complete transaction history with search and filters
          </p>
        </div>
      </div>
    </div>
  );
}

