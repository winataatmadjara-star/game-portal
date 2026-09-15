from flask import Blueprint, render_template, abort, session, redirect, url_for, request
from app.database import SessionLocal
from app.models import Game, GameScore, User, Achievement, UserAchievement
from sqlalchemy import func, distinct
import time

web_bp = Blueprint('web', __name__)

# Batas waktu main untuk guest (detik)
GUEST_TIME_LIMIT = 120


def get_current_user():
    return session.get("user")


def is_logged_in():
    return session.get("user_id") is not None


# ============================================================
# HALAMAN DEPAN — bebas akses
# ============================================================
@web_bp.route('/')
def home_page():
    db = SessionLocal()
    try:
        category = request.args.get('category')
        q = db.query(Game).filter(Game.is_active == 1)
        if category:
            q = q.filter(Game.category == category)

        games = q.order_by(Game.views.desc()).all()

        categories = db.query(Game.category).filter(Game.is_active == 1).distinct().all()
        categories = [c[0] for c in categories]

        return render_template("index.html",
            games=games,
            categories=categories,
            current_category=category,
            user=get_current_user(),
            is_admin=session.get("is_admin", False)
        )
    finally:
        db.close()


# ============================================================
# HALAMAN SEARCH — bebas akses
# ============================================================
@web_bp.route('/search')
def search_page():
    q = request.args.get('q', '').strip()
    db = SessionLocal()
    try:
        if q:
            games = db.query(Game).filter(
                Game.is_active == 1,
                (Game.title.ilike(f'%{q}%')) | (Game.description.ilike(f'%{q}%'))
            ).order_by(Game.views.desc()).all()
        else:
            games = []

        return render_template("search.html",
            games=games,
            query=q,
            user=get_current_user(),
            is_admin=session.get("is_admin", False)
        )
    finally:
        db.close()


# ============================================================
# HALAMAN LEADERBOARD — bebas akses
# ============================================================
@web_bp.route('/leaderboard')
def leaderboard_page():
    """Halaman leaderboard — top 10 skor per game."""
    db = SessionLocal()
    try:
        games = db.query(Game).filter(Game.is_active == 1).order_by(Game.views.desc()).all()

        leaderboards = {}
        for g in games:
            rows = (
                db.query(GameScore, User.username)
                .outerjoin(User, GameScore.user_id == User.id)
                .filter(GameScore.game_id == g.id)
                .order_by(GameScore.score.desc())
                .limit(10)
                .all()
            )
            leaderboards[g.slug] = {
                'title': g.title,
                'rows': rows
            }

        return render_template('leaderboard.html',
            leaderboards=leaderboards,
            user=get_current_user(),
            is_admin=session.get("is_admin", False)
        )
    finally:
        db.close()


# ============================================================
# HALAMAN PROFIL — wajib login
# ============================================================
@web_bp.route('/profile')
def profile_page():
    """Halaman profil user yang sedang login."""
    if not is_logged_in():
        return redirect('/login?next=/profile')

    user_id = session.get('user_id')
    db = SessionLocal()
    try:
        user_obj = db.query(User).get(user_id)
        if not user_obj:
            session.clear()
            return redirect('/login')

        # Riwayat 20 skor terakhir user
        scores = (
            db.query(GameScore, Game.title, Game.slug)
            .join(Game, GameScore.game_id == Game.id)
            .filter(GameScore.user_id == user_id)
            .order_by(GameScore.created_at.desc())
            .limit(20)
            .all()
        )

        # Statistik user
        total_plays = db.query(func.count(GameScore.id)).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        # Total skor (semua game)
        total_score = db.query(func.sum(GameScore.score)).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        high_score = db.query(func.max(GameScore.score)).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        unique_games = db.query(func.count(distinct(GameScore.game_id))).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        # Jumlah achievement unlocked
        achievement_count = db.query(func.count(UserAchievement.id)).filter(
            UserAchievement.user_id == user_id
        ).scalar() or 0

        return render_template('profile.html',
            user=get_current_user(),
            is_admin=session.get("is_admin", False),
            profile=user_obj,
            scores=scores,
            total_plays=total_plays,
            total_score=total_score,
            high_score=high_score,
            unique_games=unique_games,
            achievement_count=achievement_count
        )
    finally:
        db.close()


# ============================================================
# HALAMAN SKOR SAYA — wajib login
# ============================================================
@web_bp.route('/my-scores')
def my_scores_page():
    """Halaman riwayat lengkap skor user yang sedang login."""
    if not is_logged_in():
        return redirect('/login?next=/my-scores')

    user_id = session.get('user_id')
    db = SessionLocal()
    try:
        user_obj = db.query(User).get(user_id)
        if not user_obj:
            session.clear()
            return redirect('/login')

        # Semua skor user (max 100)
        scores = (
            db.query(GameScore, Game.title, Game.slug, Game.category)
            .join(Game, GameScore.game_id == Game.id)
            .filter(GameScore.user_id == user_id)
            .order_by(GameScore.created_at.desc())
            .limit(100)
            .all()
        )

        # ===== STATISTIK =====
        total_plays = db.query(func.count(GameScore.id)).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        # Total skor dari semua game
        total_score = db.query(func.sum(GameScore.score)).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        high_score = db.query(func.max(GameScore.score)).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        unique_games = db.query(func.count(distinct(GameScore.game_id))).filter(
            GameScore.user_id == user_id
        ).scalar() or 0

        avg_score = db.query(func.avg(GameScore.score)).filter(
            GameScore.user_id == user_id
        ).scalar()
        avg_score = round(avg_score or 0)

        # ===== SKOR PER KATEGORI =====
        category_stats = (
            db.query(
                Game.category,
                func.count(GameScore.id).label('plays'),
                func.sum(GameScore.score).label('total'),
                func.max(GameScore.score).label('best')
            )
            .join(GameScore, GameScore.game_id == Game.id)
            .filter(GameScore.user_id == user_id)
            .group_by(Game.category)
            .order_by(func.sum(GameScore.score).desc())
            .all()
        )

        return render_template('my_scores.html',
            user=get_current_user(),
            is_admin=session.get("is_admin", False),
            profile=user_obj,
            scores=scores,
            total_plays=total_plays,
            total_score=total_score,
            high_score=high_score,
            unique_games=unique_games,
            avg_score=avg_score,
            category_stats=category_stats
        )
    finally:
        db.close()


# ============================================================
# HALAMAN ACHIEVEMENT — wajib login
# ============================================================
@web_bp.route('/achievements')
def achievements_page():
    """Halaman daftar achievement user."""
    if not is_logged_in():
        return redirect('/login?next=/achievements')

    user_id = session.get('user_id')
    db = SessionLocal()
    try:
        user_obj = db.query(User).get(user_id)
        if not user_obj:
            session.clear()
            return redirect('/login')

        # Semua achievement aktif
        all_achievements = db.query(Achievement).filter(
            Achievement.is_active == 1
        ).order_by(Achievement.category, Achievement.points).all()

        # Achievement yang sudah di-unlock user
        unlocked_ids = set(
            row.achievement_id
            for row in db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id
            ).all()
        )

        # Pisahkan unlocked vs locked
        unlocked = [a for a in all_achievements if a.id in unlocked_ids]
        locked = [a for a in all_achievements if a.id not in unlocked_ids]

        # Statistik poin
        total_points = sum(a.points for a in unlocked)
        max_points = sum(a.points for a in all_achievements)

        return render_template('achievements.html',
            user=get_current_user(),
            is_admin=session.get("is_admin", False),
            profile=user_obj,
            unlocked=unlocked,
            locked=locked,
            total_points=total_points,
            max_points=max_points,
            total_unlocked=len(unlocked),
            total_achievements=len(all_achievements)
        )
    finally:
        db.close()


# ============================================================
# DETAIL GAME — bebas akses
# ============================================================
@web_bp.route('/game/<game_slug>')
def game_detail_page(game_slug):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.slug == game_slug).first()
        if not game:
            abort(404, description="Game tidak ditemukan")

        logged_in = is_logged_in()

        game.views = (game.views or 0) + 1
        db.commit()
        db.refresh(game)

        related = db.query(Game).filter(
            Game.category == game.category,
            Game.id != game.id,
            Game.is_active == 1
        ).order_by(Game.views.desc()).limit(6).all()

        return render_template("game_detail.html",
            game=game,
            related=related,
            user=get_current_user(),
            is_admin=session.get("is_admin", False),
            logged_in=logged_in
        )
    finally:
        db.close()


# ============================================================
# HALAMAN PLAY — Guest Time Limit 120 detik
# ============================================================
@web_bp.route('/play/<game_slug>')
def play_game(game_slug):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.slug == game_slug, Game.is_active == 1).first()
        if not game:
            abort(404, description="Game tidak ditemukan")

        game.views = (game.views or 0) + 1
        db.commit()
        db.refresh(game)

        # ===== USER LOGIN — main tanpa batas =====
        if is_logged_in():
            return render_template("play.html",
                game=game,
                user=get_current_user(),
                is_admin=session.get("is_admin", False),
                logged_in=True,
                guest_mode=False,
                time_left=None,
                total_time=None
            )

        # ===== GUEST — cek timer =====
        now = time.time()
        guest_start = session.get('guest_start_time')
        guest_game = session.get('guest_game')

        if guest_game != game_slug:
            session['guest_start_time'] = now
            session['guest_game'] = game_slug
            guest_start = now

        if guest_start is None:
            session['guest_start_time'] = now
            session['guest_game'] = game_slug
            guest_start = now

        elapsed = now - guest_start
        time_left = max(0, GUEST_TIME_LIMIT - elapsed)

        return render_template("play.html",
            game=game,
            user=None,
            is_admin=False,
            logged_in=False,
            guest_mode=True,
            time_left=int(time_left),
            total_time=GUEST_TIME_LIMIT
        )
    finally:
        db.close()


# ============================================================
# RESET GUEST TIMER
# ============================================================
@web_bp.route('/guest/reset')
def reset_guest_timer():
    session.pop('guest_start_time', None)
    session.pop('guest_game', None)
    return redirect('/')


# ============================================================
# HALAMAN STATIS
# ============================================================
@web_bp.route('/tos')
def tos_page():
    return render_template("tos.html",
        user=get_current_user(),
        is_admin=session.get("is_admin", False)
    )


@web_bp.route('/privacy')
def privacy_page():
    return render_template("privacy.html",
        user=get_current_user(),
        is_admin=session.get("is_admin", False)
    )


@web_bp.route('/contact')
def contact_page():
    return render_template("contact.html",
        user=get_current_user(),
        is_admin=session.get("is_admin", False)
    )