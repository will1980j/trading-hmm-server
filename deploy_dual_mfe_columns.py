import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    exit(1)

print("Connecting to Railway database...")
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

print("\n1. Adding be_mfe and no_be_mfe columns...")
cursor.execute("""
    ALTER TABLE automated_signals 
    ADD COLUMN IF NOT EXISTS be_mfe FLOAT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS no_be_mfe FLOAT DEFAULT NULL;
""")

print("2. Migrating existing mfe data to no_be_mfe...")
cursor.execute("""
    UPDATE automated_signals 
    SET no_be_mfe = mfe 
    WHERE no_be_mfe IS NULL AND mfe IS NOT NULL;
""")

rows_updated = cursor.rowcount
print(f"   ✅ Migrated {rows_updated} existing MFE values to no_be_mfe column")

conn.commit()

print("\n3. Verifying schema...")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'automated_signals' 
    AND column_name IN ('mfe', 'be_mfe', 'no_be_mfe')
    ORDER BY column_name;
""")

columns = cursor.fetchall()
print("   MFE columns in database:")
for col_name, col_type in columns:
    print(f"     - {col_name}: {col_type}")

cursor.close()
conn.close()

print("\n✅ Dual MFE columns added successfully!")
print("\nNext steps:")
print("1. Update webhook handler to store be_mfe and no_be_mfe from TradingView")
print("2. Update API to return both MFE values")
print("3. Dashboard will automatically display both columns")
