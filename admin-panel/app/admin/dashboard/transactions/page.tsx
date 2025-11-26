"use client";

import Header from "@/components/Header";
import Link from "next/link";
import { useEffect, useState } from "react";
import { MdFilterList, MdSearch, MdVisibility } from "react-icons/md";

interface Transaction {
  id: number;
  user_id: number;
  amount: number;
  merchant: string;
  classification: string;
  risk_score: number;
  status: string;
  created_at: string;
  username?: string;
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [classificationFilter, setClassificationFilter] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  const fetchTransactions = async () => {
    try {
      const token = localStorage.getItem("admin_token");
      let url = "http://localhost:8000/api/v1/admin/transactions?limit=50";

      if (statusFilter) url += `&status_filter=${statusFilter}`;
      if (classificationFilter)
        url += `&classification_filter=${classificationFilter}`;

      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Transactions data:", data); // Debug log
        setTransactions(data);
      } else {
        console.error("Failed to fetch transactions:", response.status);
      }
    } catch (error) {
      console.error("Failed to fetch transactions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, classificationFilter]);

  const filteredTransactions = transactions.filter(
    (t) =>
      !searchTerm ||
      t.merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.id.toString().includes(searchTerm)
  );

  // Pagination
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedTransactions = filteredTransactions.slice(
    startIndex,
    endIndex
  );

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter, classificationFilter]);

  const getClassificationColor = (classification: string) => {
    switch (classification.toUpperCase()) {
      case "FRAUD":
        return "bg-red-100 text-red-800 border-red-300";
      case "SUSPICIOUS":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "SAFE":
        return "bg-green-100 text-green-800 border-green-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case "APPROVED":
        return "text-green-600";
      case "BLOCKED":
        return "text-red-600";
      case "PENDING":
        return "text-yellow-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <div className="bg-admin-bg min-h-screen">
      <Header title="Transaction Management" />

      <div className="p-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <MdSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 text-xl" />
              <input
                type="text"
                placeholder="Search by merchant, user, or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-primary-orange transition-all text-gray-900 placeholder-gray-500 font-medium"
              />
            </div>

            {/* Status Filter */}
            <div className="relative">
              <MdFilterList className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 text-xl" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-primary-orange appearance-none bg-white text-gray-900 font-medium"
              >
                <option value="">All Status</option>
                <option value="APPROVED">Approved</option>
                <option value="BLOCKED">Blocked</option>
                <option value="PENDING">Pending</option>
              </select>
            </div>

            {/* Classification Filter */}
            <div className="relative">
              <MdFilterList className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 text-xl" />
              <select
                value={classificationFilter}
                onChange={(e) => setClassificationFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-primary-orange appearance-none bg-white text-gray-900 font-medium"
              >
                <option value="">All Classifications</option>
                <option value="SAFE">Safe</option>
                <option value="SUSPICIOUS">Suspicious</option>
                <option value="FRAUD">Fraud</option>
              </select>
            </div>

            {/* Results Count */}
            <div className="flex items-center justify-center bg-gray-50 rounded-lg px-4 py-2">
              <span className="text-admin-text font-semibold">
                {filteredTransactions.length} Results
              </span>
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-admin-text">
              Loading transactions...
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div className="p-8 text-center text-admin-text-light">
              No transactions found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-max">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      User
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      Merchant
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      Amount
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      Risk Score
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      Classification
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedTransactions.map((transaction) => (
                    <tr
                      key={transaction.id}
                      className="hover:bg-gray-50 transition"
                    >
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-admin-text">
                        #{transaction.id}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-admin-text">
                        {transaction.username || `User ${transaction.user_id}`}
                      </td>
                      <td
                        className="px-4 py-4 text-sm text-admin-text max-w-[200px] truncate"
                        title={transaction.merchant}
                      >
                        {transaction.merchant}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-semibold text-admin-text">
                        ${transaction.amount.toFixed(2)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-12 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                transaction.risk_score > 0.7
                                  ? "bg-red-500"
                                  : transaction.risk_score > 0.4
                                  ? "bg-yellow-500"
                                  : "bg-green-500"
                              }`}
                              style={{
                                width: `${transaction.risk_score * 100}%`,
                              }}
                            />
                          </div>
                          <span className="text-admin-text font-medium text-xs">
                            {(transaction.risk_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getClassificationColor(
                            transaction.classification
                          )}`}
                        >
                          {transaction.classification}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-semibold">
                        <span className={getStatusColor(transaction.status)}>
                          {transaction.status}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-admin-text-light">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <Link
                          href={`/admin/dashboard/transactions/${transaction.id}`}
                          className="inline-flex items-center gap-1 text-primary-orange hover:text-yellow-600 font-semibold transition-colors"
                        >
                          <MdVisibility />
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination Controls */}
        {!loading && filteredTransactions.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-4 mt-6 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Showing {startIndex + 1} to{" "}
              {Math.min(endIndex, filteredTransactions.length)} of{" "}
              {filteredTransactions.length} transactions
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition"
              >
                Previous
              </button>
              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter(
                    (page) =>
                      page === 1 ||
                      page === totalPages ||
                      (page >= currentPage - 1 && page <= currentPage + 1)
                  )
                  .map((page, index, array) => (
                    <div key={page} className="flex items-center">
                      {index > 0 && array[index - 1] !== page - 1 && (
                        <span className="px-2 text-gray-500">...</span>
                      )}
                      <button
                        onClick={() => setCurrentPage(page)}
                        className={`px-4 py-2 rounded-lg font-medium transition ${
                          currentPage === page
                            ? "bg-primary-orange text-white"
                            : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                        }`}
                      >
                        {page}
                      </button>
                    </div>
                  ))}
              </div>
              <button
                onClick={() =>
                  setCurrentPage((prev) => Math.min(totalPages, prev + 1))
                }
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
