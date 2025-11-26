'use client';

import { validateCVV, validationMessages } from '@/lib/utils/validation';
import { ChangeEvent, useState } from 'react';

interface CVVInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  label?: string;
  placeholder?: string;
  required?: boolean;
  showTooltip?: boolean;
}

export default function CVVInput({
  value,
  onChange,
  error,
  label = 'CVV',
  placeholder = '123',
  required = true,
  showTooltip = true
}: CVVInputProps) {
  const [touched, setTouched] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showInfo, setShowInfo] = useState(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    // Only allow digits
    const digits = e.target.value.replace(/\D/g, '');
    
    // Limit to 4 digits
    const limited = digits.slice(0, 4);
    
    onChange(limited);
  };

  const handleBlur = () => {
    setTouched(true);
    setShowPassword(false);
  };

  const handleFocus = () => {
    setShowPassword(true);
  };

  // Display masked value unless focused
  const displayValue = showPassword ? value : '•'.repeat(value.length);

  // Validation error
  const validationError = touched && value.length > 0 && !validateCVV(value)
    ? validationMessages.cvv.invalid
    : '';

  const finalError = error || validationError;

  return (
    <div className="w-full relative">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
          
          {/* Info icon */}
          {showTooltip && (
            <button
              type="button"
              onMouseEnter={() => setShowInfo(true)}
              onMouseLeave={() => setShowInfo(false)}
              onClick={() => setShowInfo(!showInfo)}
              className="ml-1.5 inline-block text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          )}
        </label>
      )}

      {/* CVV Info Tooltip */}
      {showInfo && showTooltip && (
        <div className="absolute top-full left-0 mt-1 z-10 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg">
          <p className="font-medium mb-1">Card Verification Value (CVV)</p>
          <p className="text-gray-300">
            The 3-digit security code on the back of your card (or 4 digits on the front for American Express).
          </p>
          <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 transform rotate-45"></div>
        </div>
      )}

      <div className="relative">
        <input
          type="text"
          inputMode="numeric"
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          placeholder={placeholder}
          maxLength={4}
          className={`
            w-full px-4 py-2.5 border rounded-lg
            font-mono text-base
            transition-all duration-200
            focus:outline-none focus:ring-2
            ${finalError
              ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
              : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200'
            }
            ${!showPassword ? 'tracking-widest text-xl' : ''}
          `}
          aria-invalid={!!finalError}
          aria-describedby={finalError ? 'cvv-error' : undefined}
        />

        {/* Lock icon */}
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </div>

      {/* Error message */}
      {finalError && (
        <p id="cvv-error" className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
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
      {!finalError && validateCVV(value) && (
        <p className="mt-1.5 text-sm text-green-600 flex items-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          Valid CVV
        </p>
      )}
    </div>
  );
}
