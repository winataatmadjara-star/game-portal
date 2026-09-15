"""
Achievement System — Auto-unlock based on user activity.
50 achievements across 7 categories.
"""
from app.database import SessionLocal
from app.models import Achievement, UserAchievement, GameScore, User, Game
from sqlalchemy import func, distinct
from datetime import datetime, timedelta


# ============================================================
# MAIN FUNCTION — CHECK & UNLOCK
# ============================================================
def check_and_unlock_achievements(user_id):
    """
    Cek semua achievement untuk user, unlock yang memenuhi syarat.
    Return: list of dict (plain data, aman diakses setelah session ditutup).
    """
    if not user_id:
        return []

    db = SessionLocal()
    newly_unlocked_data = []
    try:
        achievements = db.query(Achievement).filter(Achievement.is_active == 1).all()

        unlocked_ids = set(
            row.achievement_id
            for row in db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id
            ).all()
        )

        stats = get_user_stats(db, user_id)

        for ach in achievements:
            if ach.id in unlocked_ids:
                continue

            if check_condition(ach, stats):
                ua = UserAchievement(user_id=user_id, achievement_id=ach.id)
                db.add(ua)
                newly_unlocked_data.append({
                    'slug': ach.slug,
                    'title': ach.title,
                    'description': ach.description,
                    'icon': ach.icon,
                    'category': ach.category,
                    'points': ach.points,
                })

        if newly_unlocked_data:
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"⚠️ Error unlocking achievements: {e}")
    finally:
        db.close()

    return newly_unlocked_data


# ============================================================
# USER STATISTIK
# ============================================================
def get_user_stats(db, user_id):
    """Kumpulkan semua statistik user sekali query."""
    total_plays = db.query(func.count(GameScore.id)).filter(
        GameScore.user_id == user_id
    ).scalar() or 0

    total_score = db.query(func.sum(GameScore.score)).filter(
        GameScore.user_id == user_id
    ).scalar() or 0

    high_score = db.query(func.max(GameScore.score)).filter(
        GameScore.user_id == user_id
    ).scalar() or 0

    unique_games = db.query(func.count(distinct(GameScore.game_id))).filter(
        GameScore.user_id == user_id
    ).scalar() or 0

    # Skor per game
    game_scores = {}
    rows = (
        db.query(
            GameScore.game_id,
            func.count(GameScore.id),
            func.max(GameScore.score)
        )
        .filter(GameScore.user_id == user_id)
        .group_by(GameScore.game_id)
        .all()
    )
    for game_id, count, best in rows:
        game = db.query(Game).get(game_id)
        if game:
            game_scores[game.slug] = {'plays': count, 'best': best or 0}

    # Main hari ini
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_plays = db.query(func.count(GameScore.id)).filter(
        GameScore.user_id == user_id,
        GameScore.created_at >= today_start
    ).scalar() or 0

    return {
        'total_plays': total_plays,
        'total_score': total_score,
        'high_score': high_score,
        'unique_games': unique_games,
        'game_scores': game_scores,
        'today_plays': today_plays
    }


# ============================================================
# CEK KONDISI ACHIEVEMENT
# ============================================================
def check_condition(ach, stats):
    """Cek apakah kondisi achievement terpenuhi."""
    ct = ach.condition_type
    cv = ach.condition_value
    slug = ach.condition_slug

    if ct == 'total_plays':
        return stats['total_plays'] >= cv

    elif ct == 'total_score':
        return stats['total_score'] >= cv

    elif ct == 'high_score':
        return stats['high_score'] >= cv

    elif ct == 'unique_games':
        return stats['unique_games'] >= cv

    elif ct == 'game_plays':
        if not slug or slug not in stats['game_scores']:
            return False
        return stats['game_scores'][slug]['plays'] >= cv

    elif ct == 'game_score':
        if not slug or slug not in stats['game_scores']:
            return False
        return stats['game_scores'][slug]['best'] >= cv

    elif ct == 'daily_plays':
        return stats['today_plays'] >= cv

    return False


# ============================================================
# SEED 50 ACHIEVEMENT
# ============================================================
def seed_achievements():
    """Isi tabel achievements dengan 50 default achievements."""
    DEFAULT_ACHIEVEMENTS = [
        # =====================================================
        # KATEGORI 1: MILESTONE — Total Main (8)
        # =====================================================
        {'slug': 'play_1', 'title': 'Langkah Pertama', 'description': 'Mainkan game pertamamu', 'icon': '🎮', 'category': 'milestone', 'points': 10, 'condition_type': 'total_plays', 'condition_value': 1},
        {'slug': 'play_5', 'title': 'Pemanasan', 'description': 'Mainkan 5 game', 'icon': '🎯', 'category': 'milestone', 'points': 15, 'condition_type': 'total_plays', 'condition_value': 5},
        {'slug': 'play_10', 'title': 'Pemain Aktif', 'description': 'Mainkan 10 game', 'icon': '🔥', 'category': 'milestone', 'points': 20, 'condition_type': 'total_plays', 'condition_value': 10},
        {'slug': 'play_25', 'title': 'Pemain Setia', 'description': 'Mainkan 25 game', 'icon': '⚡', 'category': 'milestone', 'points': 30, 'condition_type': 'total_plays', 'condition_value': 25},
        {'slug': 'play_50', 'title': 'Gamer Sejati', 'description': 'Mainkan 50 game', 'icon': '💪', 'category': 'milestone', 'points': 50, 'condition_type': 'total_plays', 'condition_value': 50},
        {'slug': 'play_100', 'title': 'Veteran', 'description': 'Mainkan 100 game', 'icon': '🎖️', 'category': 'milestone', 'points': 100, 'condition_type': 'total_plays', 'condition_value': 100},
        {'slug': 'play_250', 'title': 'Legenda', 'description': 'Mainkan 250 game', 'icon': '🏅', 'category': 'milestone', 'points': 200, 'condition_type': 'total_plays', 'condition_value': 250},
        {'slug': 'play_500', 'title': 'Grand Master', 'description': 'Mainkan 500 game', 'icon': '👑', 'category': 'milestone', 'points': 500, 'condition_type': 'total_plays', 'condition_value': 500},

        # =====================================================
        # KATEGORI 2: SKOR TOTAL (6)
        # =====================================================
        {'slug': 'total_500', 'title': 'Skor 500', 'description': 'Total skor 500', 'icon': '⭐', 'category': 'score', 'points': 10, 'condition_type': 'total_score', 'condition_value': 500},
        {'slug': 'total_1k', 'title': 'Skor 1K', 'description': 'Total skor 1.000', 'icon': '🌟', 'category': 'score', 'points': 20, 'condition_type': 'total_score', 'condition_value': 1000},
        {'slug': 'total_5k', 'title': 'Skor 5K', 'description': 'Total skor 5.000', 'icon': '✨', 'category': 'score', 'points': 40, 'condition_type': 'total_score', 'condition_value': 5000},
        {'slug': 'total_10k', 'title': 'Skor 10K', 'description': 'Total skor 10.000', 'icon': '💫', 'category': 'score', 'points': 60, 'condition_type': 'total_score', 'condition_value': 10000},
        {'slug': 'total_50k', 'title': 'Skor 50K', 'description': 'Total skor 50.000', 'icon': '🌠', 'category': 'score', 'points': 150, 'condition_type': 'total_score', 'condition_value': 50000},
        {'slug': 'total_100k', 'title': 'Skor 100K', 'description': 'Total skor 100.000', 'icon': '🌈', 'category': 'score', 'points': 300, 'condition_type': 'total_score', 'condition_value': 100000},

        # =====================================================
        # KATEGORI 3: SKOR TUNGGAL (6)
        # =====================================================
        {'slug': 'high_100', 'title': 'Skor Tunggal 100', 'description': 'Dapat skor 100 dalam 1 game', 'icon': '🥉', 'category': 'high_score', 'points': 10, 'condition_type': 'high_score', 'condition_value': 100},
        {'slug': 'high_500', 'title': 'Skor Tunggal 500', 'description': 'Dapat skor 500 dalam 1 game', 'icon': '🥈', 'category': 'high_score', 'points': 25, 'condition_type': 'high_score', 'condition_value': 500},
        {'slug': 'high_1k', 'title': 'Skor Tunggal 1K', 'description': 'Dapat skor 1.000 dalam 1 game', 'icon': '🥇', 'category': 'high_score', 'points': 50, 'condition_type': 'high_score', 'condition_value': 1000},
        {'slug': 'high_2k', 'title': 'Skor Tunggal 2K', 'description': 'Dapat skor 2.000 dalam 1 game', 'icon': '🏆', 'category': 'high_score', 'points': 80, 'condition_type': 'high_score', 'condition_value': 2000},
        {'slug': 'high_5k', 'title': 'Skor Tunggal 5K', 'description': 'Dapat skor 5.000 dalam 1 game', 'icon': '💎', 'category': 'high_score', 'points': 150, 'condition_type': 'high_score', 'condition_value': 5000},
        {'slug': 'high_10k', 'title': 'Skor Tunggal 10K', 'description': 'Dapat skor 10.000 dalam 1 game', 'icon': '🔮', 'category': 'high_score', 'points': 300, 'condition_type': 'high_score', 'condition_value': 10000},

        # =====================================================
        # KATEGORI 4: EKSPLORASI — Game Unik (6)
        # =====================================================
        {'slug': 'explore_2', 'title': 'Mulai Menjelajah', 'description': 'Coba 2 game berbeda', 'icon': '🧭', 'category': 'explore', 'points': 10, 'condition_type': 'unique_games', 'condition_value': 2},
        {'slug': 'explore_3', 'title': 'Penjelajah', 'description': 'Coba 3 game berbeda', 'icon': '🗺️', 'category': 'explore', 'points': 20, 'condition_type': 'unique_games', 'condition_value': 3},
        {'slug': 'explore_5', 'title': 'Kolektor Game', 'description': 'Coba 5 game berbeda', 'icon': '🎒', 'category': 'explore', 'points': 40, 'condition_type': 'unique_games', 'condition_value': 5},
        {'slug': 'explore_8', 'title': 'Penakluk Katalog', 'description': 'Coba 8 game berbeda', 'icon': '🏰', 'category': 'explore', 'points': 70, 'condition_type': 'unique_games', 'condition_value': 8},
        {'slug': 'explore_10', 'title': 'Master Katalog', 'description': 'Coba 10 game berbeda', 'icon': '👑', 'category': 'explore', 'points': 100, 'condition_type': 'unique_games', 'condition_value': 10},
        {'slug': 'explore_all', 'title': 'Sang Penjelajah', 'description': 'Coba 15 game berbeda', 'icon': '🌌', 'category': 'explore', 'points': 200, 'condition_type': 'unique_games', 'condition_value': 15},

        # =====================================================
        # KATEGORI 5: GAME SPESIFIK (10)
        # =====================================================
        {'slug': 'snake_100', 'title': 'Ular Kecil', 'description': 'Skor 100 di Snake', 'icon': '🐍', 'category': 'game', 'points': 15, 'condition_type': 'game_score', 'condition_slug': 'snake', 'condition_value': 100},
        {'slug': 'snake_500', 'title': 'Master Ular', 'description': 'Skor 500 di Snake', 'icon': '🐍', 'category': 'game', 'points': 40, 'condition_type': 'game_score', 'condition_slug': 'snake', 'condition_value': 500},
        {'slug': 'tetris_500', 'title': 'Master Tetris', 'description': 'Skor 500 di Tetris', 'icon': '🧱', 'category': 'game', 'points': 40, 'condition_type': 'game_score', 'condition_slug': 'tetris', 'condition_value': 500},
        {'slug': 'breakout_500', 'title': 'Penghancur Bata', 'description': 'Skor 500 di Breakout', 'icon': '💥', 'category': 'game', 'points': 40, 'condition_type': 'game_score', 'condition_slug': 'breakout', 'condition_value': 500},
        {'slug': 'flappy_300', 'title': 'Burung Terbang', 'description': 'Skor 300 di Flappy Bird', 'icon': '🐦', 'category': 'game', 'points': 40, 'condition_type': 'game_score', 'condition_slug': 'flappy-bird', 'condition_value': 300},
        {'slug': '2048_500', 'title': 'Master 2048', 'description': 'Skor 500 di 2048', 'icon': '🔢', 'category': 'game', 'points': 40, 'condition_type': 'game_score', 'condition_slug': '2048', 'condition_value': 500},
        {'slug': 'pacman_500', 'title': 'Penguasa Labirin', 'description': 'Skor 500 di Pac-Man', 'icon': '👻', 'category': 'game', 'points': 40, 'condition_type': 'game_score', 'condition_slug': 'pacman', 'condition_value': 500},
        {'slug': 'shooter_1k', 'title': 'Ace Pilot', 'description': 'Skor 1.000 di Space Shooter', 'icon': '🚀', 'category': 'game', 'points': 60, 'condition_type': 'game_score', 'condition_slug': 'space-shooter', 'condition_value': 1000},
        {'slug': 'ninja_500', 'title': 'Ninja Legendaris', 'description': 'Skor 500 di Ninja Runner', 'icon': '🥷', 'category': 'game', 'points': 40, 'condition_type': 'game_score', 'condition_slug': 'ninja-runner', 'condition_value': 500},
        {'slug': 'geo_800', 'title': 'Cendekiawan Geo', 'description': 'Skor 800 di Geo Explorer', 'icon': '🌍', 'category': 'game', 'points': 60, 'condition_type': 'game_score', 'condition_slug': 'geo-explorer', 'condition_value': 800},

        # =====================================================
        # KATEGORI 6: GAME PLAYS — Main Game Spesifik (6)
        # =====================================================
        {'slug': 'snake_10x', 'title': 'Pecinta Snake', 'description': 'Main Snake 10×', 'icon': '🐍', 'category': 'game_plays', 'points': 25, 'condition_type': 'game_plays', 'condition_slug': 'snake', 'condition_value': 10},
        {'slug': 'tetris_10x', 'title': 'Pecinta Tetris', 'description': 'Main Tetris 10×', 'icon': '🧱', 'category': 'game_plays', 'points': 25, 'condition_type': 'game_plays', 'condition_slug': 'tetris', 'condition_value': 10},
        {'slug': 'shooter_10x', 'title': 'Pecinta Shooter', 'description': 'Main Space Shooter 10×', 'icon': '🚀', 'category': 'game_plays', 'points': 25, 'condition_type': 'game_plays', 'condition_slug': 'space-shooter', 'condition_value': 10},
        {'slug': 'ninja_10x', 'title': 'Pecinta Ninja', 'description': 'Main Ninja Runner 10×', 'icon': '🥷', 'category': 'game_plays', 'points': 25, 'condition_type': 'game_plays', 'condition_slug': 'ninja-runner', 'condition_value': 10},
        {'slug': 'geo_10x', 'title': 'Pecinta Geo', 'description': 'Main Geo Explorer 10×', 'icon': '🌍', 'category': 'game_plays', 'points': 25, 'condition_type': 'game_plays', 'condition_slug': 'geo-explorer', 'condition_value': 10},
        {'slug': 'snake_50x', 'title': 'Master Snake 50', 'description': 'Main Snake 50×', 'icon': '🐍', 'category': 'game_plays', 'points': 100, 'condition_type': 'game_plays', 'condition_slug': 'snake', 'condition_value': 50},

        # =====================================================
        # KATEGORI 7: HARIAN (4)
        # =====================================================
        {'slug': 'daily_3', 'title': 'Semangat Pagi', 'description': 'Main 3 game hari ini', 'icon': '🌅', 'category': 'daily', 'points': 15, 'condition_type': 'daily_plays', 'condition_value': 3},
        {'slug': 'daily_5', 'title': 'Rajin Main', 'description': 'Main 5 game hari ini', 'icon': '📅', 'category': 'daily', 'points': 25, 'condition_type': 'daily_plays', 'condition_value': 5},
        {'slug': 'daily_10', 'title': 'Produktif', 'description': 'Main 10 game hari ini', 'icon': '⚡', 'category': 'daily', 'points': 50, 'condition_type': 'daily_plays', 'condition_value': 10},
        {'slug': 'daily_20', 'title': 'Gila Main', 'description': 'Main 20 game hari ini', 'icon': '🔥', 'category': 'daily', 'points': 100, 'condition_type': 'daily_plays', 'condition_value': 20},
    ]

    db = SessionLocal()
    added = 0
    try:
        for data in DEFAULT_ACHIEVEMENTS:
            existing = db.query(Achievement).filter_by(slug=data['slug']).first()
            if not existing:
                db.add(Achievement(**data))
                added += 1
        db.commit()
        total = db.query(Achievement).count()
        print(f"OK: {added} achievement ditambahkan (total: {total})")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Error seed: {e}")
    finally:
        db.close()