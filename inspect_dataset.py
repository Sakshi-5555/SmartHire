
import pandas as pd

# Load the resume dataset
df = pd.read_csv("dataset/Resume.csv")

# Display basic information
print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values in each column:")
print(df.isnull().sum())

print("\nJob categories:")
print(df["Category"].value_counts())
