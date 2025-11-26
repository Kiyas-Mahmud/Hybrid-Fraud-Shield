'use client';

import { formatExpiryDate } from '@/lib/utils/formatters';
import { validateExpiryDate, validationMessages } from '@/lib/utils/validation';
import { ChangeEvent, useState } from 'react';

interface ExpiryInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  label?: string;
  placeholder?: string;
  required?: boolean;
}

export default function ExpiryInput({
  value,
  onChange,
  error,
  label = 'Expiry Date',
  placeholder = 'MM/YY',
  required = true
}: ExpiryInputProps) {
  const [touched, setTouched] = useState(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    // Remove all non-digit characters
    const digits = e.target.value.replace(/\D/g, '');
    
    // Limit to 4 digits (MMYY)
    const limited = digits.slice(0, 4);
    
    onChange(limited);
  };

  const handleBlur = () => {
    setTouched(true);
  };

  // Display value with formatting
  const displayValue = formatExpiryDate(value);

  // Validation error
  const validationError = touched && value.length > 0 && !validateExpiryDate(value)
    ? validationMessages.expiry.invalid
    : '';

  const finalError = error || validationError;

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder={placeholder}
        maxLength={5} // MM/YY = 5 characters
        className={`
          w-full px-4 py-2.5 border rounded-lg
          font-mono text-base
          transition-all duration-200
          focus:outline-none focus:ring-2
          ${finalError
            ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
            : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200'
          }
        `}
        aria-invalid={!!finalError}
        aria-describedby={finalError ? 'expiry-error' : undefined}
      />

      {/* Error message */}
      {finalError && (
        <p id="expiry-error" className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {finalError}
        </p>
      )}

      {/* Success message */}
      {!finalError && value.length === 4 && validateExpiryDate(value) && (
        <p className="mt-1.5 text-sm text-green-600 flex items-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          Valid expiry date
        </p>
      )}
    </div>
  );
}
