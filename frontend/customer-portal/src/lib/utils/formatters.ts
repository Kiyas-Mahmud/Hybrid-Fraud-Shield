import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format currency amount
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

/**
 * Format date to readable string
 */
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

/**
 * Format date to relative time (e.g., "2 minutes ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const then = new Date(date);
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
  
  return formatDate(date);
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Format card number with spaces (e.g., "1234 5678 9012 3456")
 */
export function formatCardNumber(cardNumber: string): string {
  // Remove all non-digit characters
  const digits = cardNumber.replace(/\D/g, '');
  
  // Add space every 4 digits
  const formatted = digits.match(/.{1,4}/g)?.join(' ') || digits;
  
  return formatted;
}

/**
 * Mask card number showing only last 4 digits (e.g., "•••• •••• •••• 1234")
 */
export function maskCardNumber(cardNumber: string): string {
  const digits = cardNumber.replace(/\D/g, '');
  
  if (digits.length < 4) {
    return '•'.repeat(digits.length);
  }
  
  const lastFour = digits.slice(-4);
  const maskedLength = Math.max(0, digits.length - 4);
  const masked = '•'.repeat(maskedLength);
  
  // Format with spaces
  const combined = masked + lastFour;
  return combined.match(/.{1,4}/g)?.join(' ') || combined;
}

/**
 * Format expiry date with slash (e.g., "12/26")
 */
export function formatExpiryDate(expiry: string): string {
  // Remove all non-digit characters
  const digits = expiry.replace(/\D/g, '');
  
  if (digits.length === 0) {
    return '';
  }
  
  if (digits.length <= 2) {
    return digits;
  }
  
  // Add slash after month
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}`;
}

/**
 * Format risk score as percentage (e.g., "12.5%")
 */
export function formatRiskScore(score: number): string {
  const percentage = score * 100;
  return `${percentage.toFixed(1)}%`;
}

/**
 * Mask CVV (e.g., "•••")
 */
export function maskCVV(cvv: string): string {
  return '•'.repeat(cvv.length);
}

/**
 * Get risk score color class based on score value
 */
export function getRiskScoreColor(score: number): string {
  if (score < 0.3) {
    return 'text-green-600'; // SAFE
  } else if (score < 0.7) {
    return 'text-yellow-600'; // SUSPICIOUS
  } else {
    return 'text-red-600'; // FRAUD
  }
}

/**
 * Get classification badge color
 */
export function getClassificationColor(classification: string): {
  bg: string;
  text: string;
  border: string;
} {
  switch (classification.toUpperCase()) {
    case 'SAFE':
      return {
        bg: 'bg-green-50',
        text: 'text-green-700',
        border: 'border-green-200'
      };
    case 'SUSPICIOUS':
      return {
        bg: 'bg-yellow-50',
        text: 'text-yellow-700',
        border: 'border-yellow-200'
      };
    case 'FRAUD':
      return {
        bg: 'bg-red-50',
        text: 'text-red-700',
        border: 'border-red-200'
      };
    default:
      return {
        bg: 'bg-gray-50',
        text: 'text-gray-700',
        border: 'border-gray-200'
      };
  }
}

/**
 * Get status badge color
 */
export function getStatusColor(status: string): {
  bg: string;
  text: string;
  border: string;
} {
  switch (status.toUpperCase()) {
    case 'APPROVED':
      return {
        bg: 'bg-green-50',
        text: 'text-green-700',
        border: 'border-green-200'
      };
    case 'PENDING':
      return {
        bg: 'bg-blue-50',
        text: 'text-blue-700',
        border: 'border-blue-200'
      };
    case 'REJECTED':
      return {
        bg: 'bg-orange-50',
        text: 'text-orange-700',
        border: 'border-orange-200'
      };
    case 'BLOCKED':
      return {
        bg: 'bg-red-50',
        text: 'text-red-700',
        border: 'border-red-200'
      };
    default:
      return {
        bg: 'bg-gray-50',
        text: 'text-gray-700',
        border: 'border-gray-200'
      };
  }
}
