from app.database import engine
from sqlalchemy import text

conn = engine.connect()
conn = conn.execution_options(isolation_level="AUTOCOMMIT")

migrations = [
    "ALTER TABLE game_scores ADD COLUMN IF NOT EXISTS max_level INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE game_scores ADD COLUMN IF NOT EXISTS won INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE achievements ADD COLUMN IF NOT EXISTS tier VARCHAR(20) NOT NULL DEFAULT 'rookie'",
    "ALTER TABLE achievements ADD COLUMN IF NOT EXISTS is_secret INTEGER NOT NULL DEFAULT 0",
    "CREATE INDEX IF NOT EXISTS ix_achievements_tier_category ON achievements (tier, category)",
]

for sql in migrations:
    try:
        conn.execute(text(sql))
        print(f"OK: {sql[:60]}...")
    except Exception as e:
        print(f"SKIP: {sql[:60]}... -> {e}")

conn.close()
print("Migrasi selesai.")