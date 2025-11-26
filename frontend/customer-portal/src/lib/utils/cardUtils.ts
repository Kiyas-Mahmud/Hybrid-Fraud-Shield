/**
 * Mask card number for display (e.g., •••• •••• •••• 1234)
 */
export function maskCardNumber(cardNumber: string): string {
  const cleaned = cardNumber.replace(/\s/g, '');
  const lastFour = cleaned.slice(-4);
  return `•••• •••• •••• ${lastFour}`;
}

/**
 * Format card number with spaces (e.g., 1234 5678 9012 3456)
 */
export function formatCardNumber(cardNumber: string): string {
  const cleaned = cardNumber.replace(/\s/g, '');
  const groups = cleaned.match(/.{1,4}/g) || [];
  return groups.join(' ');
}

/**
 * Get card brand from card number
 */
export function getCardBrand(cardNumber: string): string {
  const cleaned = cardNumber.replace(/\s/g, '');
  
  if (/^4/.test(cleaned)) return 'Visa';
  if (/^5[1-5]/.test(cleaned)) return 'Mastercard';
  if (/^3[47]/.test(cleaned)) return 'American Express';
  if (/^6(?:011|5)/.test(cleaned)) return 'Discover';
  
  return 'Unknown';
}

/**
 * Format expiry date as user types
 */
export function formatExpiryDate(value: string): string {
  const cleaned = value.replace(/\D/g, '');
  
  if (cleaned.length >= 2) {
    return `${cleaned.slice(0, 2)}/${cleaned.slice(2, 4)}`;
  }
  
  return cleaned;
}

/**
 * Validate and format CVV as user types
 */
export function formatCVV(value: string): string {
  return value.replace(/\D/g, '').slice(0, 4);
}
