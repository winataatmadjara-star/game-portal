from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.database import SessionLocal
from app.models import Game, User, GameScore, LoginAttempt
from werkzeug.security import generate_password_hash
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
import sys
import flask
import subprocess
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ============================================================
# HELPER
# ============================================================
def require_admin():
    """Cek apakah user adalah admin. Return redirect atau None."""
    if not session.get('user_id'):
        return redirect(url_for('auth.admin_login', next=request.path))
    if not session.get('is_admin'):
        flash('Akses ditolak. Hanya admin yang bisa masuk.', 'error')
        return redirect('/')
    return None


def get_admin_name():
    return session.get('user', 'Admin')


def run_git_command(command_list, cwd=None):
    """Menjalankan perintah Git secara aman menggunakan subprocess."""
    try:
        if not cwd:
            cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

        result = subprocess.run(
            command_list,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )

        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            return True, output.strip()
        else:
            return False, output.strip()
    except subprocess.TimeoutExpired:
        return False, "❌ Error: Proses Git melebihi batas waktu (timeout 30 detik)."
    except Exception as e:
        return False, f"❌ Terjadi kesalahan sistem: {str(e)}"


# ============================================================
# DASHBOARD
# ============================================================
@admin_bp.route('/dashboard')
def dashboard():
    check = require_admin()
    if check: return check

    chart_mode = request.args.get('chart', 'scores')
    db = SessionLocal()
    try:
        # ===== STATISTIK =====
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_admins = db.query(func.count(User.id)).filter(User.role == 'Admin').scalar() or 0
        total_games = db.query(func.count(Game.id)).scalar() or 0
        active_games = db.query(func.count(Game.id)).filter(Game.is_active == 1).scalar() or 0
        total_scores = db.query(func.count(GameScore.id)).scalar() or 0
        total_views = db.query(func.sum(Game.views)).scalar() or 0

        avg_score_raw = db.query(func.avg(GameScore.score)).scalar()
        avg_score = round(avg_score_raw) if avg_score_raw else 0

        # Login hari ini
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logins = db.query(func.count(LoginAttempt.id)).filter(
            LoginAttempt.created_at >= today_start,
            LoginAttempt.success == 1
        ).scalar() or 0
        today_failed = db.query(func.count(LoginAttempt.id)).filter(
            LoginAttempt.created_at >= today_start,
            LoginAttempt.success == 0
        ).scalar() or 0

        # ===== CHART DATA (7 hari terakhir) =====
        chart_data = []
        counts = []
        for i in range(6, -1, -1):
            day_start = today_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            if chart_mode == 'logins':
                count = db.query(func.count(LoginAttempt.id)).filter(
                    LoginAttempt.created_at >= day_start,
                    LoginAttempt.created_at < day_end
                ).scalar() or 0
            else:  # scores
                count = db.query(func.count(GameScore.id)).filter(
                    GameScore.created_at >= day_start,
                    GameScore.created_at < day_end
                ).scalar() or 0

            counts.append(count)
            chart_data.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'label': day_start.strftime('%a'),
                'count': count,
                'height': 0
            })

        max_count = max(counts) if counts else 1
        if max_count == 0: max_count = 1
        for d in chart_data:
            d['height'] = int((d['count'] / max_count) * 100)

        # ===== RECENT =====
        recent_games = db.query(Game).order_by(Game.created_at.desc()).limit(5).all()
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()

        recent_scores_raw = (
            db.query(GameScore, User.username, Game.title)
            .outerjoin(User, GameScore.user_id == User.id)
            .join(Game, GameScore.game_id == Game.id)
            .order_by(GameScore.created_at.desc())
            .limit(5)
            .all()
        )
        recent_scores = [
            {'username': u, 'game_title': gt, 'score': s.score}
            for s, u, gt in recent_scores_raw
        ]

        recent_logins = db.query(LoginAttempt).order_by(LoginAttempt.created_at.desc()).limit(5).all()

        return render_template('admin/dashboard.html',
            admin_user=get_admin_name(),
            total_users=total_users,
            total_admins=total_admins,
            total_games=total_games,
            active_games=active_games,
            total_scores=total_scores,
            total_views=total_views,
            avg_score=avg_score,
            today_logins=today_logins,
            today_failed=today_failed,
            chart_data=chart_data,
            chart_mode=chart_mode,
            recent_games=recent_games,
            recent_users=recent_users,
            recent_scores=recent_scores,
            recent_logins=recent_logins
        )
    finally:
        db.close()


# ============================================================
# KELOLA GAME
# ============================================================
@admin_bp.route('/games')
def games_management():
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        games = db.query(Game).order_by(Game.created_at.desc()).all()
        return render_template('admin/games.html',
            admin_user=get_admin_name(),
            games=games
        )
    finally:
        db.close()


@admin_bp.route('/games/<slug>/toggle')
def toggle_game(slug):
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        game = db.query(Game).filter_by(slug=slug).first()
        if game:
            game.is_active = 0 if game.is_active else 1
            db.commit()
            flash(f'Game "{game.title}" {"diaktifkan" if game.is_active else "dinonaktifkan"}.', 'success')
    finally:
        db.close()
    return redirect(url_for('admin.games_management'))


@admin_bp.route('/games/<slug>/delete')
def delete_game(slug):
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        game = db.query(Game).filter_by(slug=slug).first()
        if game:
            title = game.title
            db.delete(game)
            db.commit()
            flash(f'Game "{title}" dihapus beserta semua skornya.', 'success')
    finally:
        db.close()
    return redirect(url_for('admin.games_management'))


@admin_bp.route('/games/new', methods=['GET', 'POST'])
def new_game():
    check = require_admin()
    if check: return check

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        embed_url = request.form.get('embed_url', '').strip()
        thumbnail = request.form.get('thumbnail', '').strip() or None

        if not title or not slug or not category or not embed_url:
            flash('Semua field wajib diisi!', 'error')
        else:
            db = SessionLocal()
            try:
                if db.query(Game).filter_by(slug=slug).first():
                    flash(f'Slug "{slug}" sudah digunakan.', 'error')
                else:
                    game = Game(
                        title=title, slug=slug, category=category,
                        description=description, embed_url=embed_url,
                        thumbnail=thumbnail, is_active=1, views=0
                    )
                    db.add(game)
                    db.commit()
                    flash(f'Game "{title}" berhasil ditambahkan!', 'success')
                    return redirect(url_for('admin.games_management'))
            finally:
                db.close()

    return render_template('admin/game_form.html',
        admin_user=get_admin_name(),
        game=None
    )


@admin_bp.route('/games/<slug>/edit', methods=['GET', 'POST'])
def edit_game(slug):
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        game = db.query(Game).filter_by(slug=slug).first()
        if not game:
            flash('Game tidak ditemukan.', 'error')
            return redirect(url_for('admin.games_management'))

        if request.method == 'POST':
            game.title = request.form.get('title', game.title).strip()
            game.category = request.form.get('category', game.category).strip()
            game.description = request.form.get('description', game.description).strip()
            game.embed_url = request.form.get('embed_url', game.embed_url).strip()
            thumbnail = request.form.get('thumbnail', '').strip()
            if thumbnail: game.thumbnail = thumbnail
            game.is_active = 1 if request.form.get('is_active') else 0
            db.commit()
            flash(f'Game "{game.title}" berhasil diupdate!', 'success')
            return redirect(url_for('admin.games_management'))

        return render_template('admin/game_form.html',
            admin_user=get_admin_name(),
            game=game
        )
    finally:
        db.close()


# ============================================================
# KELOLA USER
# ============================================================
@admin_bp.route('/users')
def user_management():
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        rows = (
            db.query(User, func.count(GameScore.id).label('score_count'))
            .outerjoin(GameScore, GameScore.user_id == User.id)
            .group_by(User.id)
            .order_by(User.created_at.desc())
            .all()
        )
        total = db.query(func.count(User.id)).scalar() or 0

        return render_template('admin/users.html',
            admin_user=get_admin_name(),
            users=rows,
            total=total
        )
    finally:
        db.close()


@admin_bp.route('/users/save', methods=['POST'])
def save_user():
    check = require_admin()
    if check: return check

    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', 'member').strip()

    if not username or not email:
        flash('Username dan email wajib diisi!', 'error')
        return redirect(url_for('admin.user_management'))

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if user:
            user.email = email
            user.role = role
            flash(f'User "{username}" berhasil diupdate.', 'success')
        else:
            default_password = generate_password_hash('password123')
            new_user = User(
                username=username, email=email, phone='-',
                password=default_password, role=role
            )
            db.add(new_user)
            flash(f'User "{username}" berhasil ditambahkan. Password default: password123', 'success')
        db.commit()
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('admin.user_management'))


@admin_bp.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user:
            flash('User tidak ditemukan.', 'error')
        elif user.username == 'admin':
            flash('User "admin" tidak bisa dihapus.', 'error')
        elif user.id == session.get('user_id'):
            flash('Tidak bisa menghapus akun sendiri.', 'error')
        else:
            username = user.username
            db.delete(user)
            db.commit()
            flash(f'User "{username}" berhasil dihapus.', 'success')
    finally:
        db.close()

    return redirect(url_for('admin.user_management'))


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user:
            flash('User tidak ditemukan.', 'error')
            return redirect(url_for('admin.user_management'))

        if request.method == 'POST':
            user.email = request.form.get('email', user.email).strip()
            user.phone = request.form.get('phone', user.phone or '-').strip() or '-'
            user.role = request.form.get('role', user.role).strip()

            new_password = request.form.get('new_password', '').strip()
            if new_password and len(new_password) >= 6:
                user.password = generate_password_hash(new_password)

            db.commit()
            flash(f'User "{user.username}" berhasil diupdate.', 'success')
            return redirect(url_for('admin.user_management'))

        return render_template('admin/user_form.html',
            admin_user=get_admin_name(),
            user=user
        )
    finally:
        db.close()


# ============================================================
# LOG LOGIN
# ============================================================
@admin_bp.route('/logins')
def login_logs():
    check = require_admin()
    if check: return check

    filter_status = request.args.get('status', '')
    db = SessionLocal()
    try:
        q = db.query(LoginAttempt)
        if filter_status == 'success':
            q = q.filter(LoginAttempt.success == 1)
        elif filter_status == 'failed':
            q = q.filter(LoginAttempt.success == 0)

        logs = q.order_by(LoginAttempt.created_at.desc()).limit(200).all()

        total = db.query(func.count(LoginAttempt.id)).scalar() or 0
        total_success = db.query(func.count(LoginAttempt.id)).filter(LoginAttempt.success == 1).scalar() or 0
        total_failed = db.query(func.count(LoginAttempt.id)).filter(LoginAttempt.success == 0).scalar() or 0

        return render_template('admin/logins.html',
            admin_user=get_admin_name(),
            logs=logs,
            total=total,
            total_success=total_success,
            total_failed=total_failed,
            filter_status=filter_status
        )
    finally:
        db.close()


# ============================================================
# PENGATURAN & GIT AUTOMATION API
# ============================================================
@admin_bp.route('/settings')
def web_settings():
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_games = db.query(func.count(Game.id)).scalar() or 0
        total_scores = db.query(func.count(GameScore.id)).scalar() or 0
        total_logins = db.query(func.count(LoginAttempt.id)).scalar() or 0

        return render_template('admin/settings.html',
            admin_user=get_admin_name(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            flask_version=flask.__version__,
            server_time=datetime.utcnow().strftime('%d %b %Y, %H:%M:%S UTC'),
            total_users=total_users,
            total_games=total_games,
            total_scores=total_scores,
            total_logins=total_logins
        )
    finally:
        db.close()


@admin_bp.route('/settings/clear-logs', methods=['POST'])
def clear_login_logs():
    check = require_admin()
    if check: return check

    db = SessionLocal()
    try:
        deleted = db.query(LoginAttempt).delete()
        db.commit()
        flash(f'{deleted} log login berhasil dihapus.', 'success')
    finally:
        db.close()
    return redirect(url_for('admin.web_settings'))


@admin_bp.route('/git-pull', methods=['POST'])
def api_git_pull():
    check = require_admin()
    if check: return check

    success, output = run_git_command(['git', 'pull', 'origin', 'main'])
    if success:
        return flask.jsonify({"success": True, "message": "Berhasil melakukan git pull!", "output": output}), 200
    else:
        return flask.jsonify({"success": False, "message": "Gagal git pull.", "output": output}), 500


@admin_bp.route('/git-push', methods=['POST'])
def api_git_push():
    check = require_admin()
    if check: return check

    data = request.get_json() or {}
    commit_message = data.get('commit_message', 'chore: update settings via web panel')
    clean_message = commit_message.replace('"', '\\"')

    success_add, out_add = run_git_command(['git', 'add', '.'])
    if not success_add:
        return flask.jsonify({"success": False, "message": "Gagal git add", "output": out_add}), 500

    success_commit, out_commit = run_git_command(['git', 'commit', '-m', clean_message])
    if not success_commit and "nothing to commit" not in out_commit.lower():
        return flask.jsonify({"success": False, "message": "Gagal git commit", "output": out_commit}), 500

    success_push, out_push = run_git_command(['git', 'push', 'origin', 'main'])
    if not success_push:
        return flask.jsonify({"success": False, "message": "Gagal git push ke remote", "output": out_push}), 500

    full_output = f"{out_add}\n{out_commit}\n{out_push}"
    return flask.jsonify({"success": True, "message": "Berhasil push ke GitHub!", "output": full_output}), 200


# ============================================================
# PRICING (placeholder)
# ============================================================
@admin_bp.route('/pricing')
def pricing_plans():
    check = require_admin()
    if check: return check

    return render_template('admin/pricing.html',
        admin_user=get_admin_name()
    )