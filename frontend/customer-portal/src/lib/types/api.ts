// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: ApiError;
  message?: string;
}

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

// Pagination
export interface PaginationParams {
  page?: number;
  limit?: number;
}

// Filters
export interface TransactionFilters {
  status?: string;
  classification?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
}
