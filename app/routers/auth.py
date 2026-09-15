from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.database import SessionLocal
from app.models import User, LoginAttempt
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func
from datetime import datetime, timedelta
import time

# Inisialisasi Blueprint untuk autentikasi
auth_bp = Blueprint('auth', __name__)


# ============================================================
# KONFIGURASI RATE LIMITING
# ============================================================
MAX_ATTEMPTS_SESSION = 5        # Gagal per session sebelum lockout
LOCKOUT_SESSION_MINUTES = 15    # Durasi lockout session (menit)
MAX_ATTEMPTS_IP = 20            # Gagal per IP sebelum diblokir
LOCKOUT_IP_MINUTES = 60         # Durasi blokir IP (menit)
MAX_ATTEMPTS_USERNAME = 10      # Gagal per username sebelum lockout
LOCKOUT_USERNAME_MINUTES = 30   # Durasi lockout username (menit)
PROGRESSIVE_DELAY_MAX = 5       # Delay maksimal (detik)


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_client_ip():
    """Ambil IP client (support proxy/ngrok)."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or '0.0.0.0'


def log_attempt(username, success):
    """Simpan percobaan login ke database."""
    db = SessionLocal()
    try:
        attempt = LoginAttempt(
            username=(username or 'unknown')[:50],
            ip_address=get_client_ip()[:45],
            success=1 if success else 0,
            user_agent=(request.headers.get('User-Agent') or '')[:255]
        )
        db.add(attempt)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"⚠️ Gagal log login attempt: {e}")
    finally:
        db.close()


def count_failed(by='ip', value=None, minutes=15):
    """Hitung percobaan gagal dalam X menit terakhir."""
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        q = db.query(func.count(LoginAttempt.id)).filter(
            LoginAttempt.success == 0,
            LoginAttempt.created_at >= since
        )
        if by == 'ip':
            q = q.filter(LoginAttempt.ip_address == value)
        elif by == 'username':
            q = q.filter(LoginAttempt.username == value)
        return q.scalar() or 0
    finally:
        db.close()


def is_locked_out():
    """
    Cek apakah session/IP saat ini terkunci.
    Return: (is_locked, reason, seconds_remaining)
    """
    now = datetime.utcnow()

    # ===== Session-based lockout =====
    lockout_str = session.get('lockout_until')
    if lockout_str:
        try:
            lockout_until = datetime.fromisoformat(lockout_str)
            if now < lockout_until:
                remaining = int((lockout_until - now).total_seconds())
                return True, 'session', remaining
            else:
                session.pop('lockout_until', None)
                session['login_attempts'] = 0
        except Exception:
            session.pop('lockout_until', None)

    # ===== IP-based lockout =====
    ip = get_client_ip()
    ip_fails = count_failed('ip', ip, LOCKOUT_IP_MINUTES)
    if ip_fails >= MAX_ATTEMPTS_IP:
        return True, 'ip', LOCKOUT_IP_MINUTES * 60

    return False, None, 0


def check_username_lockout(username):
    """Cek apakah username spesifik terkunci."""
    if not username:
        return False
    fails = count_failed('username', username, LOCKOUT_USERNAME_MINUTES)
    return fails >= MAX_ATTEMPTS_USERNAME


def increment_session_attempt():
    """Tambah counter gagal di session."""
    attempts = session.get('login_attempts', 0) + 1
    session['login_attempts'] = attempts
    if attempts >= MAX_ATTEMPTS_SESSION:
        lockout_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_SESSION_MINUTES)
        session['lockout_until'] = lockout_until.isoformat()
        session['login_attempts'] = 0


def reset_session_attempts():
    """Reset counter gagal di session."""
    session.pop('login_attempts', None)
    session.pop('lockout_until', None)


def format_remaining(seconds):
    """Format detik ke 'X menit' atau 'X detik'."""
    if seconds >= 60:
        return f"{seconds // 60} menit"
    return f"{seconds} detik"


# ============================================================
# LOGIN
# ============================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Kalau sudah login, langsung arahkan sesuai role
    if session.get('user_id'):
        if session.get('is_admin'):
            return redirect(url_for('admin.dashboard'))
        return redirect('/')

    next_url = request.args.get('next', '/')
    error_msg = None

    if request.method == 'POST':
        # ===== 1. Cek lockout global (session + IP) =====
        locked, reason, remaining = is_locked_out()
        if locked:
            if reason == 'ip':
                error_msg = f'IP Anda diblokir sementara karena terlalu banyak percobaan gagal. Coba lagi dalam {format_remaining(remaining)}.'
            else:
                error_msg = f'Terlalu banyak percobaan gagal. Coba lagi dalam {format_remaining(remaining)}.'
            return render_template('login.html', error=error_msg, next_url=next_url)

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        next_form = request.form.get('next', next_url)

        # ===== 2. Cek lockout per username =====
        if check_username_lockout(username):
            error_msg = f'Akun "{username}" terkunci sementara karena terlalu banyak percobaan gagal. Coba lagi nanti.'
            return render_template('login.html', error=error_msg, next_url=next_url)

        # ===== 3. Proses login =====
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(username=username).first()

            if not user:
                error_msg = 'Username atau password salah!'
                increment_session_attempt()
                log_attempt(username, False)
                time.sleep(1)  # Delay 1 detik untuk cegah bot cepat
            else:
                # Cek password — hash atau plaintext (fallback)
                password_ok = False
                try:
                    password_ok = check_password_hash(user.password, password)
                except Exception:
                    password_ok = False

                # Fallback: kalau password masih plaintext (data lama)
                if not password_ok and user.password == password:
                    password_ok = True
                    user.password = generate_password_hash(password)
                    db.commit()

                if password_ok:
                    # ===== LOGIN BERHASIL =====
                    reset_session_attempts()
                    log_attempt(username, True)

                    session['user_id'] = user.id
                    session['user'] = user.username
                    session['role'] = getattr(user, 'role', 'Free')
                    session['is_admin'] = (getattr(user, 'role', '') == 'Admin')

                    # Hapus timer guest
                    session.pop('guest_start_time', None)
                    session.pop('guest_game', None)

                    flash('Berhasil masuk!', 'success')

                    # Redirect sesuai role
                    if session['is_admin']:
                        return redirect(url_for('admin.dashboard'))
                    return redirect(next_form)
                else:
                    # ===== LOGIN GAGAL =====
                    error_msg = 'Username atau password salah!'
                    increment_session_attempt()
                    log_attempt(username, False)

                    # Progressive delay (1s, 2s, 3s, ... max 5s)
                    attempts = session.get('login_attempts', 1)
                    delay = min(attempts, PROGRESSIVE_DELAY_MAX)
                    time.sleep(delay)
        finally:
            db.close()

    return render_template('login.html', error=error_msg, next_url=next_url)


# ============================================================
# REGISTER
# ============================================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Kalau sudah login, arahkan ke beranda
    if session.get('user_id'):
        return redirect('/')

    error_msg = None
    success_msg = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        # Validasi
        if not username or not email or not password:
            error_msg = 'Semua field wajib diisi!'
        elif len(username) < 3:
            error_msg = 'Username minimal 3 karakter!'
        elif len(password) < 6:
            error_msg = 'Password minimal 6 karakter!'
        elif '@' not in email or '.' not in email:
            error_msg = 'Format email tidak valid!'
        else:
            db = SessionLocal()
            try:
                # Cek duplikat
                if db.query(User).filter_by(username=username).first():
                    error_msg = 'Username sudah digunakan, silakan pilih yang lain.'
                elif db.query(User).filter_by(email=email).first():
                    error_msg = 'Email sudah terdaftar!'
                else:
                    new_user = User(
                        username=username,
                        email=email,
                        phone=phone or '-',
                        password=generate_password_hash(password),
                        role='Free'   # ← DIUBAH dari 'member' ke 'Free'
                    )
                    db.add(new_user)
                    db.commit()

                    flash('Pendaftaran berhasil! Silakan login.', 'success')
                    return redirect(url_for('auth.admin_login'))
            except Exception as e:
                db.rollback()
                error_msg = f'Terjadi kesalahan: {str(e)}'
            finally:
                db.close()

    return render_template('register.html', error=error_msg, success=success_msg)


# ============================================================
# LOGOUT
# ============================================================
@auth_bp.route('/logout')
def admin_logout():
    session.clear()
    flash('Anda telah keluar dari sistem.', 'info')
    return redirect('/')