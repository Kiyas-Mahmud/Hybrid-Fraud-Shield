'use client';

import { Badge, Button } from '@/components/ui';
import { formatCurrency } from '@/lib/utils/formatters';
import Link from 'next/link';

interface RiskFactor {
  factor: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  explanation?: string;
}

interface TransactionResultProps {
  /**
   * Transaction classification
   */
  classification: 'SAFE' | 'SUSPICIOUS' | 'FRAUD';
  
  /**
   * Transaction status
   */
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'BLOCKED';
  
  /**
   * Transaction amount
   */
  amount: number;
  
  /**
   * Merchant name
   */
  merchant: string;
  
  /**
   * AI-generated explanation
   */
  explanation: string;
  
  /**
   * List of risk factors detected
   */
  riskFactors?: RiskFactor[];
  
  /**
   * Transaction ID for viewing details
   */
  transactionId?: number;
  
  /**
   * Whether to show action buttons
   * @default true
   */
  showActions?: boolean;
}

/**
 * Reusable transaction result display component
 * 
 * Features:
 * - Dynamic color themes based on classification
 * - Explanation text from AI
 * - Risk factors list with severity indicators
 * - Action buttons for next steps
 * - NO RISK SCORE displayed (as requested)
 * 
 * @example
 * <TransactionResult
 *   classification="SAFE"
 *   status="APPROVED"
 *   amount={45.00}
 *   merchant="Starbucks"
 *   explanation="Transaction appears normal..."
 *   riskFactors={[...]}
 * />
 */
export default function TransactionResult({
  classification,
  status,
  amount,
  merchant,
  explanation,
  riskFactors = [],
  transactionId,
  showActions = true,
}: TransactionResultProps) {
  // Determine theme colors based on classification
  const getTheme = () => {
    switch (classification) {
      case 'SAFE':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: 'text-green-600',
          iconBg: 'bg-green-100',
          title: 'text-green-900',
          badge: 'success' as const,
          icon: (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ),
        };
      case 'SUSPICIOUS':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: 'text-yellow-600',
          iconBg: 'bg-yellow-100',
          title: 'text-yellow-900',
          badge: 'warning' as const,
          icon: (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          ),
        };
      case 'FRAUD':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          iconBg: 'bg-red-100',
          title: 'text-red-900',
          badge: 'error' as const,
          icon: (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ),
        };
    }
  };

  const theme = getTheme();

  // Get status message
  const getStatusMessage = () => {
    if (classification === 'SAFE') {
      return '✅ Transaction Approved';
    }
    if (classification === 'FRAUD') {
      return '🚨 Transaction Blocked';
    }
    if (status === 'PENDING') {
      return '⏳ Awaiting Confirmation';
    }
    if (status === 'APPROVED') {
      return '✅ Transaction Approved';
    }
    if (status === 'REJECTED' || status === 'BLOCKED') {
      return '🚫 Transaction Blocked';
    }
    return 'Transaction Processed';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'text-green-700 bg-green-100';
      case 'medium':
        return 'text-yellow-700 bg-yellow-100';
      case 'high':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 p-6">
      {/* Header Card */}
      <div className={`${theme.bg} border ${theme.border} rounded-lg p-6 space-y-4`}>
        {/* Icon */}
        <div className="flex justify-center">
          <div className={`w-16 h-16 rounded-full ${theme.iconBg} flex items-center justify-center ${theme.icon}`}>
            {theme.icon}
          </div>
        </div>

        {/* Status */}
        <div className="text-center space-y-2">
          <h2 className={`text-2xl font-bold ${theme.title}`}>
            {getStatusMessage()}
          </h2>
          
          <div className="flex justify-center gap-2">
            <Badge variant={theme.badge}>{classification}</Badge>
            <Badge variant={status === 'APPROVED' ? 'success' : status === 'PENDING' ? 'warning' : 'error'}>
              {status}
            </Badge>
          </div>
        </div>

        {/* Transaction Details */}
        <div className="text-center pt-4 border-t border-gray-200">
          <p className="text-3xl font-bold text-gray-900">
            {formatCurrency(amount)}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            at <span className="font-semibold">{merchant}</span>
          </p>
        </div>
      </div>

      {/* Explanation */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Analysis Details
        </h3>
        <p className="text-gray-700 leading-relaxed">
          {explanation}
        </p>
      </div>

      {/* Risk Factors */}
      {riskFactors && riskFactors.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Risk Factors Detected
          </h3>
          <div className="space-y-3">
            {riskFactors.map((factor, index) => (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 space-y-2"
              >
                <div className="flex items-start justify-between">
                  <h4 className="font-semibold text-gray-900">
                    {factor.factor}
                  </h4>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getSeverityColor(factor.severity)}`}>
                    {factor.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {factor.description}
                </p>
                {factor.explanation && (
                  <p className="text-sm text-gray-500 italic">
                    {factor.explanation}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {showActions && (
        <div className="flex gap-4">
          <Link href="/dashboard" className="flex-1">
            <Button variant="secondary" fullWidth>
              Back to Dashboard
            </Button>
          </Link>
          
          <Link href="/dashboard/transactions/new" className="flex-1">
            <Button variant="primary" fullWidth>
              New Transaction
            </Button>
          </Link>
        </div>
      )}

      {/* Transaction ID */}
      {transactionId && (
        <p className="text-center text-xs text-gray-500">
          Transaction ID: #{transactionId}
        </p>
      )}
    </div>
  );
}
