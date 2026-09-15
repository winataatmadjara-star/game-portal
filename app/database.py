import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

# Ambil URL dari environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Validasi pengaman: Jika .env tidak terbaca, berikan peringatan jelas
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "FATAL: DATABASE_URL tidak ditemukan di file .env! "
        "Pastikan file .env ada di root project dan variabel DATABASE_URL sudah terisi."
    )

# Buat SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Buat session factory untuk database session di setiap request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk model database Anda
Base = declarative_base()

# Dependency untuk mengambil sesi database di router Flask
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()