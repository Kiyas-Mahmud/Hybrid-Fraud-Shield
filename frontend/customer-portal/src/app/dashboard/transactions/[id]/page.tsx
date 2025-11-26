'use client';

import ConfirmationModal from '@/components/transactions/ConfirmationModal';
import ProcessingScreen from '@/components/transactions/ProcessingScreen';
import TransactionResult from '@/components/transactions/TransactionResult';
import { getTransaction, respondToTransaction } from '@/lib/api/transactions';
import { useToast } from '@/lib/context/ToastContext';
import { Transaction } from '@/lib/types/transaction';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function TransactionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { showToast } = useToast();
  
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [responding, setResponding] = useState(false);

  const transactionId = params.id as string;

  // Fetch transaction details
  useEffect(() => {
    const fetchTransaction = async () => {
      try {
        setLoading(true);
        
        // Fetch transaction by ID
        const found = await getTransaction(parseInt(transactionId));
        
        if (!found) {
          showToast('Transaction not found', 'error');
          router.push('/dashboard');
          return;
        }
        
        setTransaction(found);
        
        // Show confirmation modal if status is PENDING and classification is SUSPICIOUS
        if (found.status === 'PENDING' && found.classification === 'SUSPICIOUS') {
          setShowConfirmation(true);
        }
      } catch (error) {
        console.error('Error fetching transaction:', error);
        showToast('Failed to load transaction details', 'error');
        router.push('/dashboard');
      } finally {
        setLoading(false);
      }
    };

    if (transactionId) {
      fetchTransaction();
    }
  }, [transactionId, router, showToast]);

  // Handle YES response (approve)
  const handleApprove = async () => {
    if (!transaction) return;
    
    try {
      setResponding(true);
      await respondToTransaction(transaction.id, 'YES');
      
      // Refresh transaction data
      const updated = await getTransaction(transaction.id);
      
      if (updated) {
        setTransaction(updated);
      }
      
      setShowConfirmation(false);
      showToast('Transaction approved successfully', 'success');
    } catch (error) {
      console.error('Error approving transaction:', error);
      showToast('Failed to approve transaction', 'error');
    } finally {
      setResponding(false);
    }
  };

  // Handle NO response (reject)
  const handleReject = async () => {
    if (!transaction) return;
    
    try {
      setResponding(true);
      await respondToTransaction(transaction.id, 'NO');
      
      // Refresh transaction data
      const updated = await getTransaction(transaction.id);
      
      if (updated) {
        setTransaction(updated);
      }
      
      setShowConfirmation(false);
      showToast('Transaction blocked successfully', 'success');
    } catch (error) {
      console.error('Error rejecting transaction:', error);
      showToast('Failed to block transaction', 'error');
    } finally {
      setResponding(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <ProcessingScreen
        message="Loading transaction details..."
        subtitle="Please wait while we fetch your transaction information"
      />
    );
  }

  // Transaction not found
  if (!transaction) {
    return (
      <div className="max-w-2xl mx-auto text-center p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Transaction Not Found
        </h2>
        <p className="text-gray-600 mb-6">
          The transaction you&apos;re looking for doesn&apos;t exist or you don&apos;t have permission to view it.
        </p>
        <button
          onClick={() => router.push('/dashboard')}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Confirmation Modal for SUSPICIOUS transactions */}
      <ConfirmationModal
        isOpen={showConfirmation}
        amount={transaction.amount}
        merchant={transaction.merchant_name}
        onConfirm={handleApprove}
        onCancel={handleReject}
        isLoading={responding}
      />

      {/* Transaction Result Display */}
      <TransactionResult
        classification={transaction.classification}
        status={transaction.status}
        amount={transaction.amount}
        merchant={transaction.merchant_name}
        explanation={transaction.explanation || 'No explanation available'}
        riskFactors={transaction.risk_factors}
        transactionId={transaction.id}
        showActions={true}
      />
    </div>
  );
}
