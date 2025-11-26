"""
Database Migration: Add Card Payment Fields
Run this to add encrypted card payment fields to transactions table
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add card payment fields to transactions table"""
    
    # Database connection
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fraude_shield")
    )
    
    cursor = connection.cursor()
    
    try:
        print("Adding card payment fields to transactions table...")
        
        # Add card payment columns
        migration_sql = """
        ALTER TABLE transactions
        ADD COLUMN card_number_encrypted VARCHAR(500) NULL COMMENT 'Encrypted card number',
        ADD COLUMN cardholder_name VARCHAR(200) NULL COMMENT 'Cardholder name',
        ADD COLUMN cvv_encrypted VARCHAR(500) NULL COMMENT 'Encrypted CVV',
        ADD COLUMN expiry_date VARCHAR(10) NULL COMMENT 'Card expiry date (MM/YY)',
        ADD COLUMN billing_address TEXT NULL COMMENT 'Billing address';
        """
        
        cursor.execute(migration_sql)
        connection.commit()
        
        print("✅ Migration completed successfully!")
        print("Added columns:")
        print("  - card_number_encrypted (VARCHAR 500)")
        print("  - cardholder_name (VARCHAR 200)")
        print("  - cvv_encrypted (VARCHAR 500)")
        print("  - expiry_date (VARCHAR 10)")
        print("  - billing_address (TEXT)")
        
    except mysql.connector.Error as err:
        if err.errno == 1060:  # Duplicate column error
            print("⚠️  Columns already exist. Migration skipped.")
        else:
            print(f"❌ Error: {err}")
            connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Card Payment Fields Migration")
    print("=" * 60)
    run_migration()
    print("=" * 60)
