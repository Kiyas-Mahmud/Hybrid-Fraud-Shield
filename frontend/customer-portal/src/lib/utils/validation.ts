/**
 * Validation utilities for transaction form
 */

/**
 * Luhn Algorithm for credit card validation
 * Returns true if card number is valid
 */
export function validateCardNumber(cardNumber: string): boolean {
  // Remove all non-digit characters
  const digits = cardNumber.replace(/\D/g, '');
  
  // Card must be 13-19 digits
  if (digits.length < 13 || digits.length > 19) {
    return false;
  }
  
  // Luhn algorithm
  let sum = 0;
  let isEven = false;
  
  // Loop through values starting from the rightmost digit
  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10);
    
    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    
    sum += digit;
    isEven = !isEven;
  }
  
  return sum % 10 === 0;
}

/**
 * Validate expiry date (MM/YY format)
 * Returns true if date is valid and in the future
 */
export function validateExpiryDate(expiry: string): boolean {
  // Remove slash and spaces
  const cleaned = expiry.replace(/[\/\s]/g, '');
  
  if (cleaned.length !== 4) {
    return false;
  }
  
  const month = parseInt(cleaned.substring(0, 2), 10);
  const year = parseInt(cleaned.substring(2, 4), 10);
  
  // Validate month
  if (month < 1 || month > 12) {
    return false;
  }
  
  // Get current date
  const now = new Date();
  const currentYear = now.getFullYear() % 100; // Get last 2 digits
  const currentMonth = now.getMonth() + 1; // 0-indexed
  
  // Check if date is in the future
  if (year < currentYear) {
    return false;
  }
  
  if (year === currentYear && month < currentMonth) {
    return false;
  }
  
  return true;
}

/**
 * Validate CVV (3-4 digits)
 */
export function validateCVV(cvv: string): boolean {
  const digits = cvv.replace(/\D/g, '');
  return digits.length === 3 || digits.length === 4;
}

/**
 * Validate amount (must be positive number)
 */
export function validateAmount(amount: string | number): boolean {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return !isNaN(num) && num > 0 && num < 1000000; // Max $1M
}

/**
 * Validate merchant name (not empty, reasonable length)
 */
export function validateMerchantName(name: string): boolean {
  const trimmed = name.trim();
  return trimmed.length >= 2 && trimmed.length <= 100;
}

/**
 * Validate cardholder name (not empty, contains letters)
 */
export function validateCardholderName(name: string): boolean {
  const trimmed = name.trim();
  // Must be at least 2 characters and contain at least one letter
  return trimmed.length >= 2 && /[a-zA-Z]/.test(trimmed);
}

/**
 * Validate billing address (not empty)
 */
export function validateBillingAddress(address: string): boolean {
  const trimmed = address.trim();
  return trimmed.length >= 5 && trimmed.length <= 200;
}

/**
 * Get card type from card number
 */
export function getCardType(cardNumber: string): string {
  const digits = cardNumber.replace(/\D/g, '');
  
  if (/^4/.test(digits)) return 'Visa';
  if (/^5[1-5]/.test(digits)) return 'Mastercard';
  if (/^3[47]/.test(digits)) return 'American Express';
  if (/^6(?:011|5)/.test(digits)) return 'Discover';
  
  return 'Unknown';
}

/**
 * Validation error messages
 */
export const validationMessages = {
  cardNumber: {
    required: 'Card number is required',
    invalid: 'Please enter a valid card number',
    tooShort: 'Card number is too short',
    tooLong: 'Card number is too long'
  },
  expiry: {
    required: 'Expiry date is required',
    invalid: 'Please enter a valid expiry date (MM/YY)',
    expired: 'This card has expired',
    invalidMonth: 'Month must be between 01 and 12'
  },
  cvv: {
    required: 'CVV is required',
    invalid: 'CVV must be 3 or 4 digits'
  },
  amount: {
    required: 'Amount is required',
    invalid: 'Please enter a valid amount',
    tooSmall: 'Amount must be greater than $0',
    tooLarge: 'Amount cannot exceed $1,000,000'
  },
  merchantName: {
    required: 'Merchant name is required',
    tooShort: 'Merchant name must be at least 2 characters',
    tooLong: 'Merchant name cannot exceed 100 characters'
  },
  cardholderName: {
    required: 'Cardholder name is required',
    invalid: 'Please enter a valid name',
    tooShort: 'Name must be at least 2 characters'
  },
  billingAddress: {
    required: 'Billing address is required',
    tooShort: 'Address must be at least 5 characters',
    tooLong: 'Address cannot exceed 200 characters'
  }
};
