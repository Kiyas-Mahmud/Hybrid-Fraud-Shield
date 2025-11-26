'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import CardInput from '@/components/ui/CardInput';
import ExpiryInput from '@/components/ui/ExpiryInput';
import CVVInput from '@/components/ui/CVVInput';
import Select from '@/components/ui/Select';
import { useToast } from '@/lib/context/ToastContext';
import { submitTransaction } from '@/lib/api/transactions';
import {
  validateCardNumber,
  validateExpiryDate,
  validateCVV,
  validateAmount,
  validateMerchantName,
  validateCardholderName,
  validateBillingAddress,
  validationMessages
} from '@/lib/utils/validation';
import { TransactionType } from '@/lib/types';

interface FormData {
  cardNumber: string;
  cardholderName: string;
  expiryDate: string;
  cvv: string;
  amount: string;
  merchantName: string;
  transactionType: TransactionType | '';
  billingAddress: string;
  description: string;
}

interface FormErrors {
  cardNumber?: string;
  cardholderName?: string;
  expiryDate?: string;
  cvv?: string;
  amount?: string;
  merchantName?: string;
  transactionType?: string;
  billingAddress?: string;
}

const TRANSACTION_TYPES = [
  { value: 'ONLINE', label: 'Online Purchase' },
  { value: 'IN_STORE', label: 'In-Store Purchase' },
  { value: 'ATM', label: 'ATM Withdrawal' }
];

export default function NewTransactionPage() {
  const router = useRouter();
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    cardNumber: '',
    cardholderName: '',
    expiryDate: '',
    cvv: '',
    amount: '',
    merchantName: '',
    transactionType: '',
    billingAddress: '',
    description: ''
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Validate card number
    if (!formData.cardNumber) {
      newErrors.cardNumber = validationMessages.cardNumber.required;
    } else if (!validateCardNumber(formData.cardNumber)) {
      newErrors.cardNumber = validationMessages.cardNumber.invalid;
    }

    // Validate cardholder name
    if (!formData.cardholderName) {
      newErrors.cardholderName = validationMessages.cardholderName.required;
    } else if (!validateCardholderName(formData.cardholderName)) {
      newErrors.cardholderName = validationMessages.cardholderName.invalid;
    }

    // Validate expiry date
    if (!formData.expiryDate) {
      newErrors.expiryDate = validationMessages.expiry.required;
    } else if (!validateExpiryDate(formData.expiryDate)) {
      newErrors.expiryDate = validationMessages.expiry.invalid;
    }

    // Validate CVV
    if (!formData.cvv) {
      newErrors.cvv = validationMessages.cvv.required;
    } else if (!validateCVV(formData.cvv)) {
      newErrors.cvv = validationMessages.cvv.invalid;
    }

    // Validate amount
    if (!formData.amount) {
      newErrors.amount = validationMessages.amount.required;
    } else if (!validateAmount(formData.amount)) {
      newErrors.amount = validationMessages.amount.invalid;
    }

    // Validate merchant name
    if (!formData.merchantName) {
      newErrors.merchantName = validationMessages.merchantName.required;
    } else if (!validateMerchantName(formData.merchantName)) {
      newErrors.merchantName = validationMessages.merchantName.tooShort;
    }

    // Validate transaction type
    if (!formData.transactionType) {
      newErrors.transactionType = 'Please select a transaction type';
    }

    // Validate billing address
    if (!formData.billingAddress) {
      newErrors.billingAddress = validationMessages.billingAddress.required;
    } else if (!validateBillingAddress(formData.billingAddress)) {
      newErrors.billingAddress = validationMessages.billingAddress.tooShort;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }

    try {
      setLoading(true);

      // Format expiry date (MMYY -> MM/YY)
      const expiry = formData.expiryDate.length === 4
        ? `${formData.expiryDate.substring(0, 2)}/${formData.expiryDate.substring(2)}`
        : formData.expiryDate;

      // Submit transaction
      const response = await submitTransaction({
        amount: parseFloat(formData.amount),
        merchant_name: formData.merchantName,
        transaction_type: formData.transactionType as TransactionType,
        card_number: formData.cardNumber,
        cardholder_name: formData.cardholderName,
        cvv: formData.cvv,
        expiry_date: expiry,
        billing_address: formData.billingAddress,
        description: formData.description || undefined
      });

      // Store transaction ID and redirect to processing page
      localStorage.setItem('currentTransactionId', response.id.toString());
      
      toast.success('Transaction submitted successfully!');
      router.push(`/dashboard/transactions/${response.id}`);
      
    } catch (error) {
      console.error('Transaction submission error:', error);
      const errorMsg = error instanceof Error ? error.message : 'Failed to submit transaction';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-blue-600 hover:text-blue-700 flex items-center gap-2 mb-4 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">New Transaction</h1>
          <p className="text-gray-600 mt-2">Submit a transaction for fraud detection analysis</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Card>
            <CardHeader>
              <CardTitle>Payment Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Card Number */}
                <CardInput
                  value={formData.cardNumber}
                  onChange={(value) => setFormData({ ...formData, cardNumber: value })}
                  error={errors.cardNumber}
                  label="Card Number"
                  placeholder="1234 5678 9012 3456"
                  required
                  showMasked={false}
                />

                {/* Cardholder Name */}
                <Input
                  value={formData.cardholderName}
                  onChange={(e) => setFormData({ ...formData, cardholderName: e.target.value })}
                  error={errors.cardholderName}
                  label="Cardholder Name"
                  placeholder="John Doe"
                  required
                />

                {/* Expiry and CVV Row */}
                <div className="grid grid-cols-2 gap-4">
                  <ExpiryInput
                    value={formData.expiryDate}
                    onChange={(value) => setFormData({ ...formData, expiryDate: value })}
                    error={errors.expiryDate}
                    required
                  />

                  <CVVInput
                    value={formData.cvv}
                    onChange={(value) => setFormData({ ...formData, cvv: value })}
                    error={errors.cvv}
                    required
                    showTooltip
                  />
                </div>

                {/* Billing Address */}
                <Input
                  value={formData.billingAddress}
                  onChange={(e) => setFormData({ ...formData, billingAddress: e.target.value })}
                  error={errors.billingAddress}
                  label="Billing Address"
                  placeholder="123 Main St, Los Angeles, CA 90001"
                  required
                />
              </div>
            </CardContent>
          </Card>

          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Transaction Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Amount */}
                <Input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  error={errors.amount}
                  label="Amount"
                  placeholder="0.00"
                  required
                  icon={
                    <span className="text-gray-500">$</span>
                  }
                />

                {/* Merchant Name */}
                <Input
                  value={formData.merchantName}
                  onChange={(e) => setFormData({ ...formData, merchantName: e.target.value })}
                  error={errors.merchantName}
                  label="Merchant Name"
                  placeholder="Amazon, Starbucks, etc."
                  required
                />

                {/* Transaction Type */}
                <Select
                  value={formData.transactionType}
                  onChange={(value) => setFormData({ ...formData, transactionType: value as TransactionType })}
                  options={TRANSACTION_TYPES}
                  error={errors.transactionType}
                  label="Transaction Type"
                  placeholder="Select transaction type"
                  required
                />

                {/* Description (Optional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (Optional)
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Add any additional notes about this transaction..."
                    rows={3}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500 resize-none"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submit Buttons */}
          <div className="mt-6 flex gap-4">
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Processing...' : 'Submit Transaction'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.push('/dashboard')}
              disabled={loading}
            >
              Cancel
            </Button>
          </div>

          {/* Security Notice */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-sm font-medium text-blue-900">Secure Transaction</p>
                <p className="text-sm text-blue-700 mt-1">
                  Your card information is encrypted with AES-256 before transmission. This transaction will be analyzed by our AI fraud detection system.
                </p>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
