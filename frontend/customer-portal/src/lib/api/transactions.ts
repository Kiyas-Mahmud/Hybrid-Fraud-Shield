import {
    PaginationParams,
    Transaction,
    TransactionFilters,
    TransactionResponse,
    TransactionSubmitRequest,
} from '@/lib/types';
import apiClient from './client';

/**
 * Submit new transaction
 */
export async function submitTransaction(
  data: TransactionSubmitRequest
): Promise<TransactionResponse> {
  const response = await apiClient.post<TransactionResponse>('/transactions/submit', data);
  return response.data;
}

/**
 * Get transaction by ID
 */
export async function getTransaction(id: number): Promise<Transaction> {
  const response = await apiClient.get<Transaction>(`/transactions/${id}`);
  return response.data;
}

/**
 * Get user's transactions
 */
export async function getTransactions(
  filters?: TransactionFilters,
  pagination?: PaginationParams
): Promise<Transaction[]> {
  const params = {
    ...filters,
    ...pagination,
  };
  
  const response = await apiClient.get<Transaction[]>('/transactions/', { params });
  return response.data;
}

/**
 * Respond to pending transaction (YES/NO)
 */
export async function respondToTransaction(
  id: number,
  response: 'YES' | 'NO'
): Promise<{ message: string; transaction_id: number; status: string }> {
  const result = await apiClient.post(`/transactions/${id}/respond`, {
    response,
  });
  return result.data;
}
