import os, re, shutil
from pathlib import Path

GAMES_DIR = Path("app/static/games")
BACKUP = True

NEW_SAVE_SCORE = r"""async function saveScore(finalScore) {
    if (finalScore <= 0) return;
    try {
        const res = await fetch('/api/scores', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slug: '__SLUG__', score: finalScore })
        });
        const data = await res.json();
        if (data.status === 'guest') {
            showGuestScoreNotice(finalScore);
        } else if (data.status === 'success') {
            console.log('OK Skor tersimpan:', data);
        }
    } catch (e) {
        console.warn('Gagal simpan skor:', e);
    }
}

function showGuestScoreNotice(score) {
    var existing = document.getElementById('guest-score-notice');
    if (existing) existing.remove();
    var notice = document.createElement('div');
    notice.id = 'guest-score-notice';
    notice.style.cssText = 'position:fixed; top:20px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg,#f59e0b,#ef4444); color:#fff; padding:14px 24px; border-radius:12px; font-size:14px; font-weight:600; z-index:10000; box-shadow:0 8px 24px rgba(245,158,11,0.4); font-family:Segoe UI,sans-serif; max-width:90vw; text-align:center; display:flex; align-items:center; gap:10px; flex-wrap:wrap; justify-content:center;';
    notice.innerHTML = 'Login untuk simpan skor <strong>' + score + '</strong> ke leaderboard! <a href="/login" style="color:#fff; text-decoration:underline; font-weight:700;">Login</a>';
    document.body.appendChild(notice);
    setTimeout(function() {
        notice.style.transition = 'opacity 0.5s, transform 0.5s';
        notice.style.opacity = '0';
        notice.style.transform = 'translateX(-50%) translateY(-10px)';
        setTimeout(function() { notice.remove(); }, 500);
    }, 6000);
}"""

PATTERN = re.compile(r'async\s+function\s+saveScore\s*\([^)]*\)\s*\{', re.MULTILINE)

def find_end(text, start):
    depth = 0
    i = start
    in_str = False
    sc = None
    in_lc = False
    in_bc = False
    while i < len(text):
        ch = text[i]
        nc = text[i+1] if i+1 < len(text) else ''
        if in_lc:
            if ch == '\n': in_lc = False
            i += 1; continue
        if in_bc:
            if ch == '*' and nc == '/': in_bc = False; i += 2; continue
            i += 1; continue
        if in_str:
            if ch == '\\': i += 2; continue
            if ch == sc: in_str = False
            i += 1; continue
        if ch == '/' and nc == '/': in_lc = True; i += 2; continue
        if ch == '/' and nc == '*': in_bc = True; i += 2; continue
        if ch in ('"', "'", '`'): in_str = True; sc = ch; i += 1; continue
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    return -1

def update_file(fp, slug):
    content = fp.read_text(encoding='utf-8')
    if 'showGuestScoreNotice' in content:
        return 'skip', 'sudah versi baru'
    m = PATTERN.search(content)
    if not m:
        return 'skip', 'tidak ada saveScore'
    end = find_end(content, m.end() - 1)
    if end == -1:
        return 'err', 'tidak bisa cari akhir fungsi'
    if BACKUP:
        bak = str(fp) + '.bak'
        if not os.path.exists(bak): shutil.copy2(fp, bak)
    new_func = NEW_SAVE_SCORE.replace('__SLUG__', slug)
    fp.write_text(content[:m.start()] + new_func + content[end:], encoding='utf-8')
    return 'ok', 'berhasil'

def main():
    if not GAMES_DIR.exists():
        print("Folder tidak ditemukan:", GAMES_DIR); return
    files = sorted(GAMES_DIR.rglob("*.html"))
    print("=" * 60)
    print("UPDATE saveScore() DI SEMUA GAME")
    print("=" * 60)
    print("Ditemukan", len(files), "file HTML\n")
    s = {'ok': 0, 'skip': 0, 'err': 0}
    for fp in files:
        slug = fp.parent.name
        st, msg = update_file(fp, slug)
        icon = {'ok': '[OK]', 'skip': '[--]', 'err': '[XX]'}.get(st, '[??]')
        print(icon, "[" + slug + "]", fp.relative_to(GAMES_DIR.parent))
        print("     ->", msg)
        s[st] = s.get(st, 0) + 1
    print()
    print("=" * 60)
    print("RINGKASAN")
    print("=" * 60)
    print("Update  :", s.get('ok', 0))
    print("Dilewati:", s.get('skip', 0))
    print("Error   :", s.get('err', 0))
    print("Total   :", len(files))
    print()
    if BACKUP and s.get('ok', 0) > 0:
        print("Backup .bak tersimpan di setiap file yang diubah.")
    print()

if __name__ == '__main__':
    main()
