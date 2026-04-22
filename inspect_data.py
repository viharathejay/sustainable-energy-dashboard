"""Quick data inspection — run once to verify the loader works."""
from src.data_loader import load_se4all

df = load_se4all()

print(f"Total rows: {len(df):,}")
print(f"Countries + aggregates: {df['country'].nunique()}")
print(f"Year range: {df['year'].min()}-{df['year'].max()}")
print(f"Regional aggregates flagged: {df['is_aggregate'].sum():,} rows")
print(f"Actual country rows: {(~df['is_aggregate']).sum():,} rows")
print()
print("=== Missing values per indicator ===")
for col in df.columns:
    if col.endswith("_pct") or col.endswith("_gwh") or col == "energy_intensity":
        missing = df[col].isna().sum()
        pct = missing / len(df) * 100
        print(f"  {col:30s}: {missing:4,} missing ({pct:4.1f}%)")
print()
print("=== Sample (United Kingdom, 2015) ===")
print(df[(df["country"] == "United Kingdom") & (df["year"] == 2015)].T)