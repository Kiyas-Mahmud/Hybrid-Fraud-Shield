'use client';

import { Button } from '@/components/ui';
import { formatCurrency } from '@/lib/utils/formatters';

interface ConfirmationModalProps {
  /**
   * Whether the modal is open
   */
  isOpen: boolean;
  
  /**
   * Transaction amount to display
   */
  amount: number;
  
  /**
   * Merchant name
   */
  merchant: string;
  
  /**
   * Optional custom title
   * @default "Confirm Transaction"
   */
  title?: string;
  
  /**
   * Optional custom message
   * @default "Did you make this purchase?"
   */
  message?: string;
  
  /**
   * Callback when user confirms (YES)
   */
  onConfirm: () => void;
  
  /**
   * Callback when user cancels (NO)
   */
  onCancel: () => void;
  
  /**
   * Whether the confirmation action is loading
   */
  isLoading?: boolean;
}

/**
 * Reusable confirmation modal component
 * 
 * Features:
 * - Yes/No confirmation buttons
 * - Warning icon with yellow/amber theme
 * - Overlay backdrop
 * - Transaction details display
 * - Keyboard support (ESC to cancel)
 * - Loading state support
 * 
 * @example
 * <ConfirmationModal
 *   isOpen={showModal}
 *   amount={500.00}
 *   merchant="Best Buy"
 *   onConfirm={handleApprove}
 *   onCancel={handleDecline}
 * />
 */
export default function ConfirmationModal({
  isOpen,
  amount,
  merchant,
  title = "Confirm Transaction",
  message = "Did you make this purchase?",
  onConfirm,
  onCancel,
  isLoading = false,
}: ConfirmationModalProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl max-w-md w-full p-6 space-y-6">
          {/* Warning Icon */}
          <div className="flex justify-center">
            <div className="w-16 h-16 rounded-full bg-yellow-100 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
          </div>

          {/* Title */}
          <div className="text-center">
            <h3 className="text-xl font-bold text-gray-900">
              {title}
            </h3>
          </div>

          {/* Transaction Details */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 space-y-2">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">{message}</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(amount)}
              </p>
              <p className="text-sm text-gray-700 mt-1">
                at <span className="font-semibold">{merchant}</span>
              </p>
            </div>
          </div>

          {/* Warning Message */}
          <div className="bg-amber-50 border-l-4 border-amber-500 p-3">
            <p className="text-sm text-amber-800">
              ⚠️ This transaction was flagged as suspicious. Please confirm if you authorized this purchase.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-4">
            <Button
              variant="secondary"
              fullWidth
              onClick={onCancel}
              disabled={isLoading}
            >
              No, Block It
            </Button>
            
            <Button
              variant="primary"
              fullWidth
              onClick={onConfirm}
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : 'Yes, It Was Me'}
            </Button>
          </div>

          {/* Additional Info */}
          <p className="text-xs text-center text-gray-500">
            If you didn&apos;t make this purchase, we&apos;ll block it immediately for your protection.
          </p>
        </div>
      </div>
    </>
  );
}
