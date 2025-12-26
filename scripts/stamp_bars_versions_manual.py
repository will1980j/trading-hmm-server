import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db = os.environ.get("DATABASE_URL")
if not db:
    raise SystemExit("DATABASE_URL not set")

NQ_VER = "d4f77fc8f829782b"
MNQ_VER = "a5f8315acbaed9a1"

conn = psycopg2.connect(db)
cur = conn.cursor()

# Stamp NULL bars to the chosen versions
cur.execute("""
UPDATE market_bars_ohlcv_1m
SET dataset_version_id = %s
WHERE symbol = %s
  AND dataset_version_id IS NULL
""", (NQ_VER, "GLBX.MDP3:NQ"))
nq_updated = cur.rowcount

cur.execute("""
UPDATE market_bars_ohlcv_1m
SET dataset_version_id = %s
WHERE symbol = %s
  AND dataset_version_id IS NULL
""", (MNQ_VER, "GLBX.MDP3:MNQ"))
mnq_updated = cur.rowcount

conn.commit()

print("NQ updated:", nq_updated)
print("MNQ updated:", mnq_updated)

cur.execute("""
SELECT symbol,
       COUNT(1) AS total,
       SUM(CASE WHEN dataset_version_id IS NULL THEN 1 ELSE 0 END) AS nulls
FROM market_bars_ohlcv_1m
WHERE symbol IN (%s, %s)
GROUP BY symbol
ORDER BY symbol
""", ("GLBX.MDP3:MNQ", "GLBX.MDP3:NQ"))

for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
