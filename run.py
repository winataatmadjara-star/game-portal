import os
from app import create_app
from app.database import engine
from app.models import Base, User, Game, GameScore, LoginAttempt, Achievement, UserAchievement  # noqa: F401
from sqlalchemy import text

app = create_app()


def run_migrations():
    """Migrasi ringan: pastikan kolom & tabel baru ada tanpa merusak data lama."""
    with engine.connect() as conn:
        # ===== Migrasi kolom di tabel users =====
        try:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(30) DEFAULT 'Free';"
            ))
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(30) DEFAULT '-';"
            ))
            conn.commit()
            print("✅ Kolom 'role' & 'phone' dipastikan ada.")
        except Exception as e:
            conn.rollback()
            print(f"⚠️ Migrasi kolom users dilewati: {e}")

        # ===== Migrasi kolom tambahan di tabel games =====
        try:
            conn.execute(text(
                "ALTER TABLE games ADD COLUMN IF NOT EXISTS thumbnail VARCHAR(255);"
            ))
            conn.execute(text(
                "ALTER TABLE games ADD COLUMN IF NOT EXISTS is_active INTEGER DEFAULT 1 NOT NULL;"
            ))
            conn.commit()
            print("✅ Kolom 'thumbnail' & 'is_active' dipastikan ada di tabel games.")
        except Exception as e:
            conn.rollback()
            print(f"⚠️ Migrasi kolom games dilewati (tabel mungkin belum ada): {e}")

        # ===== Migrasi kolom tambahan di tabel login_attempts =====
        try:
            conn.execute(text(
                "ALTER TABLE login_attempts ADD COLUMN IF NOT EXISTS user_agent VARCHAR(255);"
            ))
            conn.commit()
            print("✅ Kolom 'user_agent' dipastikan ada di tabel login_attempts.")
        except Exception as e:
            conn.rollback()
            print(f"⚠️ Migrasi kolom login_attempts dilewati: {e}")

        # ===== Migrasi kolom tambahan di tabel achievements =====
        try:
            conn.execute(text(
                "ALTER TABLE achievements ADD COLUMN IF NOT EXISTS condition_slug VARCHAR(50);"
            ))
            conn.execute(text(
                "ALTER TABLE achievements ADD COLUMN IF NOT EXISTS is_active INTEGER DEFAULT 1 NOT NULL;"
            ))
            conn.commit()
            print("✅ Kolom 'condition_slug' & 'is_active' dipastikan ada di tabel achievements.")
        except Exception as e:
            conn.rollback()
            print(f"⚠️ Migrasi kolom achievements dilewati: {e}")


def init_database():
    """Buat semua tabel yang belum ada berdasarkan metadata SQLAlchemy."""
    Base.metadata.create_all(bind=engine)
    print("🗄️ Database PostgreSQL & tabel berhasil disinkronkan.")


if __name__ == '__main__':
    with app.app_context():
        init_database()      # Buat tabel dulu
        run_migrations()     # Baru migrasi kolom opsional

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    app.run(host="0.0.0.0", port=port, debug=debug)