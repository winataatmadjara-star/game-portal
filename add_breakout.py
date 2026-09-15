from app import create_app
from app.database import SessionLocal
from app.models import Game

app = create_app()

with app.app_context():
    db = SessionLocal()
    try:
        existing = db.query(Game).filter_by(slug='breakout').first()
        if existing:
            print("⚠️  Game 'breakout' sudah ada.")
        else:
            game = Game(
                title="Breakout Pro",
                slug="breakout",
                category="Arcade",
                description="Hancurkan semua bata dengan bola. 10 level dengan pola dan tingkat kesulitan berbeda!",
                embed_url="/static/games/breakout/breakout.html",
                is_active=1,
                views=0
            )
            db.add(game)
            db.commit()
            print("✅ Game 'Breakout Pro' ditambahkan ke database!")
    finally:
        db.close()