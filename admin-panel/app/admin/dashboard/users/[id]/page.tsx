"use client";

import Header from "@/components/Header";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  MdArrowBack,
  MdAttachMoney,
  MdBarChart,
  MdCalendarToday,
  MdCheckCircle,
  MdCreditCard,
  MdDevices,
  MdNetworkCheck,
  MdPerson,
  MdShield,
  MdShowChart,
  MdWarning,
} from "react-icons/md";

interface UserAnalytics {
  user_info: {
    id: number;
    username: string;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
    is_blocked: boolean;
    created_at: string;
  };
  transaction_stats: {
    total_transactions: number;
    total_amount: number;
    avg_transaction_amount: number;
    fraud_count: number;
    suspicious_count: number;
    safe_count: number;
  };
  ip_addresses: Array<{
    ip: string;
    count: number;
    last_used: string;
  }>;
  devices: Array<{
    device_id: string;
    count: number;
    last_used: string;
  }>;
  spending_pattern: {
    avg_daily_transactions: number;
    avg_weekly_transactions: number;
    most_active_hour: number;
    merchant_diversity: number;
  };
  monthly_spending: Array<{
    month: string;
    total_amount: number;
    transaction_count: number;
  }>;
  recent_transactions: Array<{
    id: number;
    amount: number;
    merchant: string;
    classification: string;
    risk_score: number;
    created_at: string;
  }>;
}

export default function UserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const userId = params.id;

  const [data, setData] = useState<UserAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState<string>("all");
  const [selectedMonth, setSelectedMonth] = useState<string>("all");

  useEffect(() => {
    fetchUserAnalytics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const fetchUserAnalytics = async () => {
    try {
      const token = localStorage.getItem("admin_token");
      const response = await fetch(
        `http://localhost:8000/api/v1/admin/users/${userId}/analytics`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log("User analytics:", result);
        setData(result);
      } else {
        console.error("Failed to fetch:", response.status);
      }
    } catch (error) {
      console.error("Failed to fetch user analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-admin-bg min-h-screen">
        <Header title="User Analytics" />
        <div className="p-8 text-center text-admin-text">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-orange"></div>
          <p className="mt-4">Loading user analytics...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-admin-bg min-h-screen">
        <Header title="User Analytics" />
        <div className="p-8 text-center">
          <div className="bg-white rounded-lg shadow-md p-8">
            <MdPerson className="text-6xl text-gray-300 mx-auto mb-4" />
            <p className="text-admin-text-light text-lg">User not found</p>
          </div>
        </div>
      </div>
    );
  }

  const fraudRate =
    data.transaction_stats.total_transactions > 0
      ? (data.transaction_stats.fraud_count /
          data.transaction_stats.total_transactions) *
        100
      : 0;

  const suspiciousRate =
    data.transaction_stats.total_transactions > 0
      ? (data.transaction_stats.suspicious_count /
          data.transaction_stats.total_transactions) *
        100
      : 0;

  const safeRate =
    data.transaction_stats.total_transactions > 0
      ? (data.transaction_stats.safe_count /
          data.transaction_stats.total_transactions) *
        100
      : 0;

  return (
    <div className="bg-admin-bg min-h-screen">
      <Header title="User Analytics" />

      <div className="p-8">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-primary-orange hover:text-yellow-600 mb-6 font-semibold transition-colors"
        >
          <MdArrowBack />
          Back to Users
        </button>

        {/* User Info Card */}
        <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-xl shadow-lg p-6 mb-6 border-2 border-orange-200">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-orange to-yellow-500 rounded-full flex items-center justify-center shadow-lg">
                <MdPerson className="text-white text-4xl" />
              </div>
              <div>
                <h2 className="text-3xl font-bold text-admin-text">
                  {data.user_info.username}
                </h2>
                <p className="text-lg text-admin-text-light">
                  {data.user_info.full_name}
                </p>
                <p className="text-sm text-admin-text-light mt-1">
                  <span className="inline-flex items-center gap-1">
                    📧 {data.user_info.email}
                  </span>
                </p>
                <p className="text-xs text-admin-text-light mt-2">
                  <span className="font-semibold">Role:</span>{" "}
                  {data.user_info.role.toUpperCase()}
                </p>
              </div>
            </div>

            <div className="text-right">
              <span
                className={`px-4 py-2 rounded-full text-sm font-bold shadow-md ${
                  data.user_info.is_blocked
                    ? "bg-red-500 text-white"
                    : data.user_info.is_active
                    ? "bg-green-500 text-white"
                    : "bg-gray-500 text-white"
                }`}
              >
                {data.user_info.is_blocked
                  ? "🚫 BLOCKED"
                  : data.user_info.is_active
                  ? "✅ ACTIVE"
                  : "⏸️ INACTIVE"}
              </span>
              <p className="text-sm text-admin-text-light mt-3">
                <MdCalendarToday className="inline mr-1" />
                Member since{" "}
                {new Date(data.user_info.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-2">
              <MdCreditCard className="text-3xl text-blue-500" />
              <span className="text-2xl font-bold text-admin-text">
                {data.transaction_stats.total_transactions}
              </span>
            </div>
            <p className="text-sm text-admin-text-light">Total Transactions</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between mb-2">
              <MdAttachMoney className="text-3xl text-green-500" />
              <span className="text-2xl font-bold text-admin-text">
                ${data.transaction_stats.total_amount.toFixed(0)}
              </span>
            </div>
            <p className="text-sm text-admin-text-light">Total Spent</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-emerald-500">
            <div className="flex items-center justify-between mb-2">
              <MdCheckCircle className="text-3xl text-emerald-500" />
              <span className="text-2xl font-bold text-admin-text">
                {data.transaction_stats.safe_count}
              </span>
            </div>
            <p className="text-sm text-admin-text-light">
              Safe ({safeRate.toFixed(1)}%)
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between mb-2">
              <MdWarning className="text-3xl text-yellow-500" />
              <span className="text-2xl font-bold text-admin-text">
                {data.transaction_stats.suspicious_count}
              </span>
            </div>
            <p className="text-sm text-admin-text-light">
              Suspicious ({suspiciousRate.toFixed(1)}%)
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between mb-2">
              <MdShield className="text-3xl text-red-500" />
              <span className="text-2xl font-bold text-admin-text">
                {data.transaction_stats.fraud_count}
              </span>
            </div>
            <p className="text-sm text-admin-text-light">
              Fraud ({fraudRate.toFixed(1)}%)
            </p>
          </div>
        </div>

        {/* Activity Patterns */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <MdShowChart className="text-2xl text-primary-orange" />
            <h3 className="text-xl font-bold text-admin-text">
              Activity Patterns
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-3xl font-bold text-admin-text">
                {data.spending_pattern.avg_daily_transactions.toFixed(1)}
              </p>
              <p className="text-sm text-admin-text-light mt-1">
                Avg Daily Transactions
              </p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-3xl font-bold text-admin-text">
                {data.spending_pattern.avg_weekly_transactions.toFixed(1)}
              </p>
              <p className="text-sm text-admin-text-light mt-1">
                Avg Weekly Transactions
              </p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-3xl font-bold text-admin-text">
                {data.spending_pattern.most_active_hour}:00
              </p>
              <p className="text-sm text-admin-text-light mt-1">
                Most Active Hour
              </p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-3xl font-bold text-admin-text">
                {data.spending_pattern.merchant_diversity}
              </p>
              <p className="text-sm text-admin-text-light mt-1">
                Unique Merchants
              </p>
            </div>
          </div>
        </div>

        {/* Monthly Spending with Calendar Filter */}
        {data.monthly_spending &&
          data.monthly_spending.length > 0 &&
          (() => {
            // Get unique years and months
            const years = Array.from(
              new Set(data.monthly_spending.map((m) => m.month.split("-")[0]))
            )
              .sort()
              .reverse();
            const months = [
              { value: "01", label: "January" },
              { value: "02", label: "February" },
              { value: "03", label: "March" },
              { value: "04", label: "April" },
              { value: "05", label: "May" },
              { value: "06", label: "June" },
              { value: "07", label: "July" },
              { value: "08", label: "August" },
              { value: "09", label: "September" },
              { value: "10", label: "October" },
              { value: "11", label: "November" },
              { value: "12", label: "December" },
            ];

            // Filter monthly spending based on selected year and month
            const filteredSpending = data.monthly_spending.filter((month) => {
              if (selectedYear === "all" && selectedMonth === "all")
                return true;
              const [year, monthNum] = month.month.split("-");
              if (selectedYear !== "all" && year !== selectedYear) return false;
              if (selectedMonth !== "all" && monthNum !== selectedMonth)
                return false;
              return true;
            });

            return (
              <div className="bg-white rounded-xl shadow-md p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <MdBarChart className="text-2xl text-primary-orange" />
                    <h3 className="text-xl font-bold text-admin-text">
                      Monthly Spending
                    </h3>
                  </div>

                  {/* Calendar Filter */}
                  <div className="flex items-center gap-3">
                    <MdCalendarToday className="text-xl text-primary-orange" />
                    <select
                      value={selectedYear}
                      onChange={(e) => setSelectedYear(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-admin-text bg-white hover:border-primary-orange focus:outline-none focus:ring-2 focus:ring-primary-orange"
                    >
                      <option value="all">All Years</option>
                      {years.map((year) => (
                        <option key={year} value={year}>
                          {year}
                        </option>
                      ))}
                    </select>

                    <select
                      value={selectedMonth}
                      onChange={(e) => setSelectedMonth(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-admin-text bg-white hover:border-primary-orange focus:outline-none focus:ring-2 focus:ring-primary-orange"
                    >
                      <option value="all">All Months</option>
                      {months.map((month) => (
                        <option key={month.value} value={month.value}>
                          {month.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {filteredSpending.length > 0 ? (
                  <div className="space-y-3">
                    {filteredSpending.map((month, index) => {
                      const maxAmount = Math.max(
                        ...filteredSpending.map((m) => m.total_amount)
                      );
                      const widthPercentage =
                        (month.total_amount / maxAmount) * 100;

                      return (
                        <div key={index} className="flex items-center gap-4">
                          <div className="w-24 text-sm font-semibold text-admin-text">
                            {new Date(month.month + "-01").toLocaleDateString(
                              "en-US",
                              { month: "short", year: "numeric" }
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="relative h-10 bg-gray-100 rounded-lg overflow-hidden">
                              <div
                                className="absolute h-full bg-gradient-to-r from-primary-orange to-yellow-500 rounded-lg flex items-center justify-end px-3"
                                style={{ width: `${widthPercentage}%` }}
                              >
                                <span className="text-sm font-bold text-white">
                                  ${month.total_amount.toFixed(0)}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="w-20 text-right">
                            <p className="text-xs font-semibold text-admin-text">
                              {month.transaction_count} txns
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <MdCalendarToday className="text-5xl text-gray-300 mx-auto mb-3" />
                    <p className="text-admin-text-light">
                      No transactions found for the selected period
                    </p>
                  </div>
                )}
              </div>
            );
          })()}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Top 3 IP Addresses */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-4">
              <MdNetworkCheck className="text-2xl text-primary-orange" />
              <h3 className="text-xl font-bold text-admin-text">
                Top 3 IP Addresses
              </h3>
            </div>
            <div className="space-y-3">
              {data.ip_addresses && data.ip_addresses.length > 0 ? (
                data.ip_addresses.map((ip, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-mono text-sm font-bold text-admin-text">
                          {ip.ip}
                        </p>
                        <p className="text-xs text-admin-text-light">
                          Last: {new Date(ip.last_used).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-blue-500 text-white text-sm font-bold rounded-full">
                      {ip.count}×
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-admin-text-light text-center py-4">
                  No IP data
                </p>
              )}
            </div>
          </div>
          {/* Devices */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-4">
              <MdDevices className="text-2xl text-primary-orange" />
              <h3 className="text-xl font-bold text-admin-text">Devices</h3>
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {data.devices && data.devices.length > 0 ? (
                data.devices.slice(0, 5).map((device, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 bg-purple-50 rounded-lg border border-purple-200"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-bold text-admin-text truncate">
                        {device.device_id}
                      </p>
                      <p className="text-xs text-admin-text-light">
                        Last: {new Date(device.last_used).toLocaleString()}
                      </p>
                    </div>
                    <span className="px-3 py-1 bg-purple-500 text-white text-sm font-bold rounded-full ml-2">
                      {device.count}×
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-admin-text-light text-center py-4">
                  No device data
                </p>
              )}
            </div>
          </div>
        </div>

        {/* All Transactions */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <MdCreditCard className="text-2xl text-primary-orange" />
            <h3 className="text-xl font-bold text-admin-text">
              Recent Transactions
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">
                    ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">
                    Merchant
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">
                    Amount
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">
                    Risk
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.recent_transactions &&
                data.recent_transactions.length > 0 ? (
                  data.recent_transactions.map((txn) => (
                    <tr
                      key={txn.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() =>
                        router.push(`/admin/dashboard/transactions/${txn.id}`)
                      }
                    >
                      <td className="px-4 py-4 text-sm font-semibold text-admin-text">
                        #{txn.id}
                      </td>
                      <td className="px-4 py-4 text-sm text-admin-text max-w-xs truncate">
                        {txn.merchant}
                      </td>
                      <td className="px-4 py-4 text-sm font-bold text-green-600">
                        ${txn.amount.toFixed(2)}
                      </td>
                      <td className="px-4 py-4 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[80px]">
                            <div
                              className={`h-2 rounded-full ${
                                txn.risk_score > 0.7
                                  ? "bg-red-500"
                                  : txn.risk_score > 0.4
                                  ? "bg-yellow-500"
                                  : "bg-green-500"
                              }`}
                              style={{ width: `${txn.risk_score * 100}%` }}
                            />
                          </div>
                          <span className="text-xs font-semibold">
                            {(txn.risk_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold ${
                            txn.classification === "FRAUD"
                              ? "bg-red-500 text-white"
                              : txn.classification === "SUSPICIOUS"
                              ? "bg-yellow-500 text-white"
                              : "bg-green-500 text-white"
                          }`}
                        >
                          {txn.classification}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm text-admin-text-light">
                        {new Date(txn.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={6}
                      className="px-4 py-8 text-center text-admin-text-light"
                    >
                      No transactions found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
