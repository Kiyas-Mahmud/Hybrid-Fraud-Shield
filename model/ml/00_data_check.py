import pandas as pd
import numpy as np

print("="*80)
print("DATA QUALITY CHECK - 72 FEATURES")
print("="*80)

# Load datasets
print("\nLoading datasets...")
train_df = pd.read_csv('../../data/train_72_features.csv')
test_df = pd.read_csv('../../data/test_72_features.csv')

print(f"Train shape: {train_df.shape}")
print(f"Test shape: {test_df.shape}")

# Check for target column
print("\nTarget column check:")
if 'isFraud' in train_df.columns:
    print(f"  isFraud found in train: {train_df['isFraud'].value_counts().to_dict()}")
    print(f"  Fraud rate: {train_df['isFraud'].mean()*100:.2f}%")
else:
    print("  WARNING: isFraud not found in train!")

if 'isFraud' in test_df.columns:
    print(f"  isFraud found in test: {test_df['isFraud'].value_counts().to_dict()}")
    print(f"  Fraud rate: {test_df['isFraud'].mean()*100:.2f}%")
else:
    print("  WARNING: isFraud not found in test!")

# Check nulls
print("\nNull values:")
train_nulls = train_df.isnull().sum().sum()
test_nulls = test_df.isnull().sum().sum()
print(f"  Train nulls: {train_nulls}")
print(f"  Test nulls: {test_nulls}")

if train_nulls > 0:
    print("\nColumns with nulls in train:")
    null_cols = train_df.isnull().sum()[train_df.isnull().sum() > 0]
    for col, count in null_cols.items():
        print(f"  {col}: {count} ({count/len(train_df)*100:.2f}%)")

# Check duplicates
print("\nDuplicate rows:")
train_dupes = train_df.duplicated().sum()
test_dupes = test_df.duplicated().sum()
print(f"  Train duplicates: {train_dupes}")
print(f"  Test duplicates: {test_dupes}")

# Check feature count
print("\nFeature count:")
train_features = train_df.shape[1] - 1 if 'isFraud' in train_df.columns else train_df.shape[1]
test_features = test_df.shape[1] - 1 if 'isFraud' in test_df.columns else test_df.shape[1]
print(f"  Train features: {train_features}")
print(f"  Test features: {test_features}")

# Data types
print("\nData types:")
print(train_df.dtypes.value_counts())

# Basic statistics
print("\nBasic statistics (first 5 numerical columns):")
print(train_df.select_dtypes(include=[np.number]).iloc[:, :5].describe())

print("\n" + "="*80)
print("DATA CHECK COMPLETE")
print("="*80)
