import os
import psycopg2
import psycopg2.extras

def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL env variable not set. Please add it before running.")

    print("Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(database_url)

    sql = """
    SELECT trade_id, event_type, be_mfe, no_be_mfe, mfe, mfe_R, mae_R, timestamp
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 10;
    """

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

            print("\n=== LAST 10 MFE_UPDATE ROWS ===")
            if not rows:
                print("No MFE_UPDATE rows found.")
            else:
                for r in rows:
                    print("----------------------------------")
                    print(f"trade_id:   {r.get('trade_id')}")
                    print(f"event_type: {r.get('event_type')}")
                    print(f"be_mfe:     {r.get('be_mfe')}")
                    print(f"no_be_mfe:  {r.get('no_be_mfe')}")
                    print(f"mfe:        {r.get('mfe')}")
                    print(f"mfe_R:      {r.get('mfe_R')}")
                    print(f"mae_R:      {r.get('mae_R')}")
                    print(f"timestamp:  {r.get('timestamp')}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
