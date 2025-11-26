// Transaction Types
export interface Transaction {
  id: number;
  amount: number;
  merchant_name: string;
  transaction_type: TransactionType;
  description?: string;
  location?: string;
  device_info?: string;
  ip_address?: string;
  risk_score: number;
  classification: RiskClassification;
  status: TransactionStatus;
  risk_factors?: Record<string, any>;
  model_predictions?: Record<string, number>;
  explanation?: string;
  created_at: string;
  updated_at?: string;
  user_response?: 'YES' | 'NO';
  responded_at?: string;
}

export enum TransactionType {
  ONLINE = 'ONLINE',
  IN_STORE = 'IN_STORE',
  ATM = 'ATM',
  TRANSFER = 'TRANSFER'
}

export enum TransactionStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  BLOCKED = 'BLOCKED'
}

export enum RiskClassification {
  SAFE = 'SAFE',
  SUSPICIOUS = 'SUSPICIOUS',
  FRAUD = 'FRAUD'
}

// Transaction Submit Request
export interface TransactionSubmitRequest {
  amount: number;
  merchant_name: string;
  transaction_type: TransactionType;
  description?: string;
  card_number: string;
  cardholder_name: string;
  cvv: string;
  expiry_date: string;
  billing_address?: string;
  location?: string;
  device_info?: string;
  ip_address?: string;
}

// Transaction Response
export interface TransactionResponse extends Transaction {}

// Transaction List Response
export interface TransactionListResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  limit: number;
}
