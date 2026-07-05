import pandas as pd

# Read dataset
df = pd.read_csv("data/raw/government_schemes.csv")

print(df.head())
print(df.info())