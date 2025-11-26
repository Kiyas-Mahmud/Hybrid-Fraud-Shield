'use client';

import { formatCardNumber, maskCardNumber } from '@/lib/utils/formatters';
import { validateCardNumber, validationMessages } from '@/lib/utils/validation';
import { ChangeEvent, useState } from 'react';

interface CardInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  label?: string;
  placeholder?: string;
  required?: boolean;
  showMasked?: boolean;
}

export default function CardInput({
  value,
  onChange,
  error,
  label = 'Card Number',
  placeholder = '1234 5678 9012 3456',
  required = true,
  showMasked = false
}: CardInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [touched, setTouched] = useState(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    // Remove all non-digit characters
    const digits = e.target.value.replace(/\D/g, '');
    
    // Limit to 19 digits (max card length)
    const limited = digits.slice(0, 19);
    
    onChange(limited);
  };

  const handleBlur = () => {
    setIsFocused(false);
    setTouched(true);
  };

  const handleFocus = () => {
    setIsFocused(true);
  };

  // Display value (formatted or masked based on focus/showMasked)
  const displayValue = isFocused || !showMasked
    ? formatCardNumber(value)
    : value.length >= 4
    ? maskCardNumber(value)
    : formatCardNumber(value);

  // Validation error
  const validationError = touched && value && !validateCardNumber(value)
    ? validationMessages.cardNumber.invalid
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

      <div className="relative">
        <input
          type="text"
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          placeholder={placeholder}
          className={`
            w-full px-4 py-2.5 border rounded-lg
            font-mono text-base
            transition-all duration-200
            focus:outline-none focus:ring-2
            ${finalError
              ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
              : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200'
            }
            ${!isFocused && showMasked && value.length >= 4 ? 'tracking-wider' : ''}
          `}
          aria-invalid={!!finalError}
          aria-describedby={finalError ? 'card-error' : undefined}
        />

        {/* Card type icon (optional enhancement) */}
        {value.length >= 1 && !finalError && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <svg
              className="w-8 h-5 text-gray-400"
              fill="currentColor"
              viewBox="0 0 48 32"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect width="48" height="32" rx="4" fill="currentColor" opacity="0.1" />
              <rect x="4" y="10" width="40" height="4" rx="1" fill="currentColor" opacity="0.5" />
            </svg>
          </div>
        )}
      </div>

      {/* Error message */}
      {finalError && (
        <p id="card-error" className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
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

      {/* Helper text */}
      {!finalError && value.length > 0 && validateCardNumber(value) && (
        <p className="mt-1.5 text-sm text-green-600 flex items-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          Valid card number
        </p>
      )}
    </div>
  );
}
