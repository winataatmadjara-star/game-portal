from flask import Blueprint, jsonify, request, session
from app.database import SessionLocal
from app.models import User, Game, GameScore
from sqlalchemy import func
import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================================
# STATISTIK
# ============================================================
@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Statistik umum portal game."""
    db = SessionLocal()
    try:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_games = db.query(func.count(Game.id)).filter(Game.is_active == 1).scalar() or 0
        total_plays = db.query(func.count(GameScore.id)).scalar() or 0

        return jsonify({
            "status": "success",
            "total_users": total_users,
            "total_games": total_games,
            "total_plays": total_plays,
            "active_players": 142,  # dummy, bisa diisi real-time nanti
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    finally:
        db.close()


# ============================================================
# GAME
# ============================================================
@api_bp.route('/games', methods=['GET'])
def list_games():
    """Daftar semua game aktif, opsional filter kategori."""
    db = SessionLocal()
    try:
        category = request.args.get('category')
        q = db.query(Game).filter(Game.is_active == 1)
        if category:
            q = q.filter(Game.category == category)

        games = q.order_by(Game.views.desc()).all()
        return jsonify({
            "status": "success",
            "count": len(games),
            "data": [{
                "id": g.id,
                "title": g.title,
                "slug": g.slug,
                "category": g.category,
                "description": g.description,
                "thumbnail": g.thumbnail,
                "views": g.views,
            } for g in games]
        })
    finally:
        db.close()


@api_bp.route('/games/<slug>', methods=['GET'])
def get_game(slug):
    """Detail satu game + tambah views."""
    db = SessionLocal()
    try:
        game = db.query(Game).filter_by(slug=slug, is_active=1).first()
        if not game:
            return jsonify({"status": "error", "message": "Game tidak ditemukan"}), 404

        game.views = (game.views or 0) + 1
        db.commit()

        return jsonify({
            "status": "success",
            "data": {
                "id": game.id,
                "title": game.title,
                "slug": game.slug,
                "category": game.category,
                "description": game.description,
                "embed_url": game.embed_url,
                "views": game.views,
            }
        })
    finally:
        db.close()


# ============================================================
# SKOR / LEADERBOARD
# ============================================================
@api_bp.route('/scores', methods=['POST'])
def save_score():
    """
    Simpan skor dari game HTML5.
    - User login  : skor DISIMPAN ke database + cek achievement
    - Guest       : skor TIDAK DISIMPAN (hanya konfirmasi)
    """
    data = request.get_json() or {}
    slug = data.get('slug')
    score_raw = data.get('score', 0)

    # Validasi slug
    if not slug:
        return jsonify({"status": "error", "message": "slug wajib diisi"}), 400

    # Validasi score
    try:
        score = int(score_raw)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "score harus angka"}), 400

    if score < 0 or score > 1_000_000:
        return jsonify({"status": "error", "message": "score tidak valid"}), 400

    # ===== CEK LOGIN STATUS =====
    user_id = session.get('user_id')

    # GUEST — skor TIDAK disimpan
    if user_id is None:
        return jsonify({
            "status": "guest",
            "saved": False,
            "message": "Login untuk menyimpan skor & masuk leaderboard!",
            "score": score
        }), 200

    # ===== USER LOGIN — simpan ke database =====
    db = SessionLocal()
    try:
        game = db.query(Game).filter_by(slug=slug).first()
        if not game:
            return jsonify({"status": "error", "message": "Game tidak ditemukan"}), 404

        new_score = GameScore(
            game_id=game.id,
            user_id=user_id,
            score=score
        )
        db.add(new_score)
        db.commit()
        db.refresh(new_score)

        # ===== CEK & UNLOCK ACHIEVEMENT =====
        # Fungsi ini return list of dict (bukan objek SQLAlchemy)
        newly_unlocked = []
        try:
            from app.achievements import check_and_unlock_achievements
            newly_unlocked = check_and_unlock_achievements(user_id)
        except Exception as e:
            # Jangan gagalkan save score kalau achievement error
            print(f"⚠️ Achievement error: {e}")

        return jsonify({
            "status": "success",
            "saved": True,
            "id": new_score.id,
            "score": new_score.score,
            "message": "Skor berhasil disimpan!",
            "achievements": newly_unlocked  # sudah berupa list of dict
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/leaderboard/<slug>', methods=['GET'])
def leaderboard(slug):
    """Top skor untuk game tertentu. Default 10, bisa sampai 50."""
    db = SessionLocal()
    try:
        game = db.query(Game).filter_by(slug=slug).first()
        if not game:
            return jsonify({"status": "error", "message": "Game tidak ditemukan"}), 404

        try:
            limit = min(int(request.args.get('limit', 10)), 50)
        except (ValueError, TypeError):
            limit = 10

        rows = (
            db.query(GameScore, User.username)
            .outerjoin(User, GameScore.user_id == User.id)
            .filter(GameScore.game_id == game.id)
            .order_by(GameScore.score.desc())
            .limit(limit)
            .all()
        )

        return jsonify({
            "status": "success",
            "game": game.title,
            "count": len(rows),
            "data": [{
                "rank": i + 1,
                "username": username or "Guest",
                "score": s.score,
                "date": s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else '-'
            } for i, (s, username) in enumerate(rows)]
        })
    finally:
        db.close()


# ============================================================
# USER
# ============================================================
@api_bp.route('/me', methods=['GET'])
def me():
    """Info user yang sedang login."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Belum login"}), 401

    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        return jsonify({
            "status": "success",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        })
    finally:
        db.close()


# ============================================================
# PLAYER STATS (opsional)
# ============================================================
@api_bp.route('/my-scores', methods=['GET'])
def my_scores():
    """Skor user yang sedang login (untuk halaman profil)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Belum login"}), 401

    db = SessionLocal()
    try:
        rows = (
            db.query(GameScore, Game.title, Game.slug)
            .join(Game, GameScore.game_id == Game.id)
            .filter(GameScore.user_id == user_id)
            .order_by(GameScore.created_at.desc())
            .limit(50)
            .all()
        )

        return jsonify({
            "status": "success",
            "count": len(rows),
            "data": [{
                "game_title": title,
                "game_slug": slug,
                "score": s.score,
                "date": s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else '-'
            } for s, title, slug in rows]
        })
    finally:
        db.close()


# ============================================================
# ACHIEVEMENT API
# ============================================================
@api_bp.route('/achievements', methods=['GET'])
def get_achievements():
    """Daftar achievement user yang sedang login."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Belum login"}), 401

    db = SessionLocal()
    try:
        from app.models import Achievement, UserAchievement

        all_achievements = db.query(Achievement).filter(
            Achievement.is_active == 1
        ).order_by(Achievement.category, Achievement.points).all()

        unlocked_ids = set(
            row.achievement_id
            for row in db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id
            ).all()
        )

        return jsonify({
            "status": "success",
            "total": len(all_achievements),
            "unlocked": len(unlocked_ids),
            "data": [{
                "slug": a.slug,
                "title": a.title,
                "description": a.description,
                "icon": a.icon,
                "category": a.category,
                "points": a.points,
                "unlocked": a.id in unlocked_ids
            } for a in all_achievements]
        })
    finally:
        db.close()