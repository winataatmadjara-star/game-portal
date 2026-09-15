from app import create_app
from app.database import SessionLocal
from app.models import Game

app = create_app()

GAMES = [
    {
        "title": "Snake",
        "slug": "snake",
        "category": "Arcade",
        "description": "Kendalikan ular, makan buah, jangan tabrak dinding atau diri sendiri!",
        "embed_url": "/static/games/snake/index.html",
    },
    {
        "title": "Tetris",
        "slug": "tetris",
        "category": "Puzzle",
        "description": "Susun balok agar tidak menumpuk ke atas.",
        "embed_url": "/static/games/tetris/index.html",
    },
    {
        "title": "Breakout",
        "slug": "breakout",
        "category": "Arcade",
        "description": "Hancurkan semua bata dengan bola.",
        "embed_url": "/static/games/breakout/index.html",
    },
    {
        "title": "Flappy Bird",
        "slug": "flappy-bird",
        "category": "Arcade",
        "description": "Terbang melewati pipa tanpa menabrak.",
        "embed_url": "/static/games/flappy-bird/index.html",
    },
    {
        "title": "2048",
        "slug": "2048",
        "category": "Puzzle",
        "description": "Gabungkan angka hingga mencapai 2048.",
        "embed_url": "/static/games/2048/index.html",
    },
    {
        "title": "Pac-Man",
        "slug": "pacman",
        "category": "Arcade",
        "description": "Makan semua titik sambil menghindari hantu.",
        "embed_url": "/static/games/pacman/index.html",
    },
    {
        "title": "Minesweeper",
        "slug": "minesweeper",
        "category": "Puzzle",
        "description": "Temukan semua ranjau tanpa meledakkannya.",
        "embed_url": "/static/games/minesweeper/index.html",
    },
    {
        "title": "Memory Card",
        "slug": "memory-card",
        "category": "Puzzle",
        "description": "Cocokkan pasangan kartu yang sama.",
        "embed_url": "/static/games/memory-card/index.html",
    },
]


def seed():
    with app.app_context():
        db = SessionLocal()
        try:
            added = 0
            for data in GAMES:
                existing = db.query(Game).filter_by(slug=data["slug"]).first()
                if not existing:
                    db.add(Game(**data))
                    added += 1
                    print(f"✅ Ditambahkan: {data['title']}")
                else:
                    print(f"⚠️  Sudah ada: {data['title']}")
            db.commit()
            print(f"\n🎉 Selesai. {added} game baru ditambahkan.")
            print(f"📊 Total game di database: {db.query(Game).count()}")
        finally:
            db.close()


if __name__ == "__main__":
    seed()