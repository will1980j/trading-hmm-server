import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db = os.environ.get("DATABASE_URL")
if not db:
    raise SystemExit("DATABASE_URL not set")

conn = psycopg2.connect(db)
cur = conn.cursor()

cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
print("DB size:", cur.fetchone()[0])

cur.execute("SELECT pg_size_pretty(pg_total_relation_size('market_bars_ohlcv_1m'))")
print("market_bars_ohlcv_1m size:", cur.fetchone()[0])

cur.execute("SELECT pg_size_pretty(pg_total_relation_size('data_ingest_runs'))")
print("data_ingest_runs size:", cur.fetchone()[0])

cur.close()
conn.close()
