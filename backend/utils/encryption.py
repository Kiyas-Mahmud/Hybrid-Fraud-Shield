"""
Card Data Encryption Utility
Uses AES-256 encryption for PCI-DSS compliance
"""

from cryptography.fernet import Fernet
import os
from typing import Optional

class CardEncryption:
    """
    Handles encryption and decryption of sensitive card data.
    Uses AES-256-GCM encryption via Fernet (symmetric encryption).
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption with a key.
        
        Args:
            encryption_key: Base64-encoded encryption key. If None, uses environment variable.
        """
        if encryption_key is None:
            # Try to import settings first, fallback to os.getenv
            try:
                from config.settings import settings
                encryption_key = settings.ENCRYPTION_KEY
            except:
                encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY must be set in environment variables or passed to constructor")
        
        # Ensure key is bytes
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        # Initialize Fernet cipher
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt sensitive data (card number, CVV).
        
        Args:
            plaintext: The plain text data to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return None
        
        # Convert to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Encrypt
        encrypted_bytes = self.cipher.encrypt(plaintext_bytes)
        
        # Return as base64 string
        return encrypted_bytes.decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plain text string
        """
        if not ciphertext:
            return None
        
        # Convert to bytes
        ciphertext_bytes = ciphertext.encode('utf-8')
        
        # Decrypt
        decrypted_bytes = self.cipher.decrypt(ciphertext_bytes)
        
        # Return as string
        return decrypted_bytes.decode('utf-8')
    
    def encrypt_card_number(self, card_number: str) -> str:
        """
        Encrypt card number.
        
        Args:
            card_number: Card number (with or without dashes)
            
        Returns:
            Encrypted card number
        """
        # Remove dashes/spaces for consistency
        clean_card = card_number.replace('-', '').replace(' ', '')
        return self.encrypt(clean_card)
    
    def encrypt_cvv(self, cvv: str) -> str:
        """
        Encrypt CVV.
        
        Args:
            cvv: 3 or 4 digit CVV code
            
        Returns:
            Encrypted CVV
        """
        return self.encrypt(cvv)
    
    def mask_card_number(self, card_number: str) -> str:
        """
        Mask card number for display (show only last 4 digits).
        
        Args:
            card_number: Full card number
            
        Returns:
            Masked card number (e.g., "**** **** **** 1234")
        """
        # Remove dashes/spaces
        clean_card = card_number.replace('-', '').replace(' ', '')
        
        # Return masked version
        if len(clean_card) >= 4:
            return f"**** **** **** {clean_card[-4:]}"
        else:
            return "****"


# Utility functions for easy access
_card_encryption = None

def get_card_encryption() -> CardEncryption:
    """Get singleton instance of CardEncryption"""
    global _card_encryption
    if _card_encryption is None:
        _card_encryption = CardEncryption()
    return _card_encryption


def encrypt_card_data(card_number: Optional[str], cvv: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """
    Encrypt card number and CVV.
    
    Args:
        card_number: Plain card number
        cvv: Plain CVV
        
    Returns:
        Tuple of (encrypted_card_number, encrypted_cvv)
    """
    encryptor = get_card_encryption()
    
    encrypted_card = encryptor.encrypt_card_number(card_number) if card_number else None
    encrypted_cvv = encryptor.encrypt_cvv(cvv) if cvv else None
    
    return encrypted_card, encrypted_cvv


def mask_card_for_display(card_number: str) -> str:
    """
    Mask card number for safe display.
    
    Args:
        card_number: Full card number
        
    Returns:
        Masked card number
    """
    encryptor = get_card_encryption()
    return encryptor.mask_card_number(card_number)


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this once to generate a key, then store it securely in .env file.
    
    Returns:
        Base64-encoded encryption key
    """
    key = Fernet.generate_key()
    return key.decode('utf-8')


# Example usage (for testing only):
if __name__ == "__main__":
    # Generate a new key
    print("Generated Encryption Key (save this to .env as ENCRYPTION_KEY):")
    print(generate_encryption_key())
    print()
    
    # Test encryption (requires ENCRYPTION_KEY in environment)
    try:
        encryptor = get_card_encryption()
        
        # Test data
        test_card = "1234-5678-9012-3456"
        test_cvv = "123"
        
        # Encrypt
        encrypted_card = encryptor.encrypt_card_number(test_card)
        encrypted_cvv = encryptor.encrypt_cvv(test_cvv)
        
        print("Test Encryption:")
        print(f"Original Card: {test_card}")
        print(f"Encrypted Card: {encrypted_card}")
        print(f"Masked Card: {encryptor.mask_card_number(test_card)}")
        print(f"Original CVV: {test_cvv}")
        print(f"Encrypted CVV: {encrypted_cvv}")
        
        # Decrypt
        decrypted_card = encryptor.decrypt(encrypted_card)
        decrypted_cvv = encryptor.decrypt(encrypted_cvv)
        
        print(f"\nDecrypted Card: {decrypted_card}")
        print(f"Decrypted CVV: {decrypted_cvv}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Set ENCRYPTION_KEY in environment variables to test encryption")
