'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';
import { MdSearch, MdPerson, MdBlock, MdCheckCircle, MdVisibility } from 'react-icons/md';
import toast from 'react-hot-toast';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_blocked: boolean;
  created_at: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('http://localhost:8000/api/v1/admin/users?limit=100', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleBlockUser = async (userId: number, currentlyBlocked: boolean) => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(
        `http://localhost:8000/api/v1/admin/users/${userId}/block`,
        {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ block: !currentlyBlocked }),
        }
      );

      if (response.ok) {
        toast.success(currentlyBlocked ? 'User unblocked' : 'User blocked');
        fetchUsers(); // Refresh list
      } else {
        toast.error('Failed to update user status');
      }
    } catch (error) {
      console.error('Failed to block/unblock user:', error);
      toast.error('An error occurred');
    }
  };

  const filteredUsers = users.filter(user => 
    !searchTerm || 
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Pagination
  const totalPages = Math.ceil(filteredUsers.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedUsers = filteredUsers.slice(startIndex, endIndex);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'SUPER_ADMIN':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'ADMIN':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="bg-admin-bg min-h-screen">
      <Header title="User Management" />
      
      <div className="p-8">
        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <MdSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 text-xl" />
              <input
                type="text"
                placeholder="Search by username, email, or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-primary-orange transition-all text-gray-900 placeholder-gray-500 font-medium"
              />
            </div>
            <div className="flex items-center justify-center bg-gray-50 rounded-lg px-4 py-2">
              <span className="text-admin-text font-semibold">
                {filteredUsers.length} Users
              </span>
            </div>
          </div>
        </div>

        {/* Users Grid */}
        {loading ? (
          <div className="text-center text-admin-text py-8">Loading users...</div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center text-admin-text-light py-8">No users found</div>
        ) : (
          <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {paginatedUsers.map((user) => (
              <div key={user.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                  <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary-orange to-yellow-500 rounded-full flex items-center justify-center shadow-md">
                      <MdPerson className="text-white text-2xl" />
                    </div>
                    <div>
                      <h3 className="font-bold text-admin-text">{user.username}</h3>
                      <p className="text-sm text-admin-text-light">{user.full_name}</p>
                    </div>
                  </div>
                  
                  {user.is_blocked && (
                    <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">
                      BLOCKED
                    </span>
                  )}
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-admin-text-light">Email:</span>
                    <span className="text-admin-text">{user.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-admin-text-light">Role:</span>
                    <span className={`px-2 py-0.5 text-xs font-semibold rounded border ${getRoleBadge(user.role)}`}>
                      {user.role}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-admin-text-light">Status:</span>
                    <span className={`flex items-center gap-1 ${user.is_active ? 'text-green-600' : 'text-gray-500'}`}>
                      {user.is_active ? <MdCheckCircle /> : <MdBlock />}
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-admin-text-light">Joined:</span>
                    <span className="text-admin-text">
                      {new Date(user.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-gray-200">
                  <Link
                    href={`/admin/dashboard/users/${user.id}`}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-primary-orange hover:bg-yellow-500 text-white rounded-lg transition-all text-sm font-medium shadow-md"
                  >
                    <MdVisibility />
                    View Details
                  </Link>
                  
                  {user.role === 'CUSTOMER' && (
                    <button
                      onClick={() => handleBlockUser(user.id, user.is_blocked)}
                      className={`flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg transition text-sm font-medium ${
                        user.is_blocked
                          ? 'bg-green-500 text-white hover:bg-green-600'
                          : 'bg-red-500 text-white hover:bg-red-600'
                      }`}
                    >
                      <MdBlock />
                      {user.is_blocked ? 'Unblock' : 'Block'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {filteredUsers.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-4 mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing {startIndex + 1} to {Math.min(endIndex, filteredUsers.length)} of {filteredUsers.length} users
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition"
                >
                  Previous
                </button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1)
                    .filter(page => 
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
                              ? 'bg-primary-orange text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {page}
                        </button>
                      </div>
                    ))
                  }
                </div>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition"
                >
                  Next
                </button>
              </div>
            </div>
          )}
          </>
        )}
      </div>
    </div>
  );
}
