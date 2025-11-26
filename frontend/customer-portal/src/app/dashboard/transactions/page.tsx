'use client';

import ProcessingScreen from '@/components/transactions/ProcessingScreen';
import { Badge, Button } from '@/components/ui';
import { getTransactions } from '@/lib/api/transactions';
import { useToast } from '@/lib/context/ToastContext';
import { Transaction } from '@/lib/types/transaction';
import { formatCurrency, formatDate } from '@/lib/utils/formatters';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function TransactionHistoryPage() {
  const router = useRouter();
  const { showToast } = useToast();
  
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'SAFE' | 'SUSPICIOUS' | 'FRAUD'>('ALL');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'PENDING' | 'APPROVED' | 'BLOCKED'>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Fetch transactions
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const data = await getTransactions();
        setTransactions(data);
      } catch (error) {
        console.error('Error fetching transactions:', error);
        showToast('Failed to load transactions', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [showToast]);

  // Filter transactions
  const filteredTransactions = transactions.filter(transaction => {
    // Classification filter
    if (filter !== 'ALL' && transaction.classification !== filter) {
      return false;
    }
    
    // Status filter
    if (statusFilter !== 'ALL' && transaction.status !== statusFilter) {
      return false;
    }
    
    // Search filter
    if (searchTerm && !transaction.merchant_name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    return true;
  });

  // Pagination calculations
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedTransactions = filteredTransactions.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filter, statusFilter, searchTerm]);

  // Get badge variant for classification
  const getClassificationBadge = (classification: string) => {
    switch (classification) {
      case 'SAFE':
        return <Badge variant="success">SAFE</Badge>;
      case 'SUSPICIOUS':
        return <Badge variant="warning">SUSPICIOUS</Badge>;
      case 'FRAUD':
        return <Badge variant="error">FRAUD</Badge>;
      default:
        return <Badge variant="secondary">{classification}</Badge>;
    }
  };

  // Get badge variant for status
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <Badge variant="success">APPROVED</Badge>;
      case 'PENDING':
        return <Badge variant="warning">PENDING</Badge>;
      case 'BLOCKED':
      case 'REJECTED':
        return <Badge variant="error">BLOCKED</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <ProcessingScreen
        message="Loading transactions..."
        subtitle="Please wait while we fetch your transaction history"
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Transaction History</h1>
          <p className="text-gray-600 mt-2">
            View and manage all your transactions
          </p>
        </div>
        <Link href="/dashboard/transactions/new">
          <Button variant="primary">
            New Transaction
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Merchant
            </label>
            <input
              type="text"
              placeholder="Search by merchant name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Classification Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Classification
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as 'ALL' | 'SAFE' | 'SUSPICIOUS' | 'FRAUD')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Classifications</option>
              <option value="SAFE">Safe</option>
              <option value="SUSPICIOUS">Suspicious</option>
              <option value="FRAUD">Fraud</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'ALL' | 'PENDING' | 'APPROVED' | 'BLOCKED')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="APPROVED">Approved</option>
              <option value="BLOCKED">Blocked</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="flex justify-between items-center text-sm text-gray-600">
        <div>
          Showing {startIndex + 1}-{Math.min(endIndex, filteredTransactions.length)} of {filteredTransactions.length} transactions
        </div>
        {totalPages > 1 && (
          <div className="text-gray-500">
            Page {currentPage} of {totalPages}
          </div>
        )}
      </div>

      {/* Transactions List */}
      {filteredTransactions.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No transactions found
          </h3>
          <p className="text-gray-600 mb-6">
            {searchTerm || filter !== 'ALL' || statusFilter !== 'ALL'
              ? 'Try adjusting your filters'
              : 'You haven\'t made any transactions yet'}
          </p>
          <Link href="/dashboard/transactions/new">
            <Button variant="primary">
              Create Your First Transaction
            </Button>
          </Link>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {paginatedTransactions.map((transaction) => (
              <div
                key={transaction.id}
                onClick={() => router.push(`/dashboard/transactions/${transaction.id}`)}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  {/* Left: Transaction Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {transaction.merchant_name}
                      </h3>
                      <span className="text-2xl font-bold text-gray-900">
                        {formatCurrency(transaction.amount)}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 mb-3">
                      {getClassificationBadge(transaction.classification)}
                      {getStatusBadge(transaction.status)}
                      <Badge variant="secondary">{transaction.transaction_type}</Badge>
                    </div>
                    
                    {transaction.explanation && (
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {transaction.explanation}
                      </p>
                    )}
                  </div>

                  {/* Right: Date & Action */}
                  <div className="text-right ml-4">
                    <p className="text-sm text-gray-500 mb-2">
                      {formatDate(transaction.created_at)}
                    </p>
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View Details →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 mt-8">
              {/* Previous Button */}
              <Button
                variant="secondary"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                ← Previous
              </Button>

              {/* Page Numbers */}
              <div className="flex gap-2">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => {
                  // Show first page, last page, current page, and pages around current
                  if (
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 1 && page <= currentPage + 1)
                  ) {
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                          currentPage === page
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  } else if (
                    page === currentPage - 2 ||
                    page === currentPage + 2
                  ) {
                    return (
                      <span key={page} className="px-2 py-2 text-gray-400">
                        ...
                      </span>
                    );
                  }
                  return null;
                })}
              </div>

              {/* Next Button */}
              <Button
                variant="secondary"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                Next →
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
