#!/usr/bin/env python3
import os, psycopg2, hashlib
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

cursor.execute("""
    SELECT id, vendor, dataset, file_sha256
    FROM data_ingest_runs
    WHERE dataset_version_id IS NULL AND file_sha256 IS NOT NULL
    ORDER BY id
""")

runs = cursor.fetchall()

for run_id, vendor, dataset, file_sha in runs:
    components = f"{vendor}|{dataset}|{file_sha}"
    version_id = hashlib.sha256(components.encode()).hexdigest()[:16]
    
    cursor.execute("""
        UPDATE data_ingest_runs SET dataset_version_id = %s
        WHERE id = %s AND dataset_version_id IS NULL
    """, (version_id, run_id))
    print(f"✅ Run {run_id}: {version_id}")

conn.commit()
cursor.close()
conn.close()

print(f"\n✅ Backfilled {len(runs)} dataset version IDs")
