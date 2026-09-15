from app import create_app
from app.database import SessionLocal
from app.models import Game

app = create_app()

DESCRIPTIONS = {
    'snake': """🐍 Snake Adventure — Kendalikan ular yang terus memanjang setiap kali memakan buah. Tantangannya: jangan menabrak dinding, rintangan, atau tubuhmu sendiri!

🎮 Cara Bermain:
• Gunakan Arrow Keys atau WASD untuk menggerakkan ular
• Tekan Space untuk pause / lanjut
• Makan buah untuk menambah skor dan panjang ular

🏆 5 Level Menantang:
• Level 1 (Pemula) — 5 buah, tanpa rintangan
• Level 2 (Mudah) — 6 buah, 2 rintangan horizontal
• Level 3 (Menengah) — 7 buah, kotak tengah + 4 sudut
• Level 4 (Sulit) — 8 buah, pola silang
• Level 5 (MASTER) — 10 buah, rintangan penuh

⭐ Fitur:
• Warna berubah tiap level
• Kecepatan meningkat setiap 50 poin
• Efek partikel dan sound effect
• Leaderboard otomatis tersimpan

💡 Tips: Rencanakan jalur 2-3 langkah ke depan, jangan hanya mengejar buah!""",

    'breakout': """🧱 Breakout Pro — Hancurkan semua bata dengan bola pantul. 10 level dengan pola dan tingkat kesulitan berbeda menantimu!

🎮 Cara Bermain:
• Gerakkan paddle dengan mouse, ← →, atau A/D
• Klik atau tekan Space untuk melempar bola
• Tekan Space untuk pause

🏆 10 Level:
• Level 1-3: Pemula, Zigzag, Pyramida
• Level 4-6: Bata Kuat, Catur, Berlian
• Level 7-9: Bercelah, Bunker, Labirin
• Level 10: MASTER — pola chaos!

⭐ Fitur:
• Sistem combo x9 untuk skor berlipat
• Bata dengan 2-3 HP di level tinggi
• Efek 3D dan partikel ledakan
• 3 nyawa per permainan

💡 Tips: Fokus ke bata paling atas dulu untuk memberi ruang gerak bola!""",

    'tetris': """🎮 Tetris Arcade Pro — Susun balok jatuh agar membentuk baris penuh. Baris penuh akan hilang dan memberi skor!

🎮 Cara Bermain:
• ← → untuk geser balok
• ↑ untuk putar balok
• ↓ untuk jatuh cepat
• Space untuk hard drop (jatuh seketika)
• P untuk pause

🏆 5 Tingkat Kesulitan:
• Level 1 (Santai) — 1.0 detik per baris
• Level 2 (Normal) — 0.8 detik
• Level 3 (Menengah) — 0.6 detik
• Level 4 (Cepat) — 0.4 detik
• Level 5 (Ekstrem) — 0.2 detik

⭐ Fitur:
• Preview balok berikutnya
• Sistem skor berlipat untuk multi-bar
• Efek 3D blok dan suara
• Kontrol mobile

💡 Tips: Selalu sisakan satu kolom kosong untuk balok I panjang!""",

    'flappy-bird': """🐦 Flappy Bird — Terbang melewati celah pipa hijau tanpa menabrak. Semakin jauh terbang, semakin tinggi skor!

🎮 Cara Bermain:
• Klik atau tekan Space untuk mengepakkan sayap
• Hindari pipa atas dan bawah
• Setiap pipa yang dilewati = 1 poin

⭐ Fitur:
• Kontrol sederhana, sulit dikuasai
• Efek parallax background
• High score tersimpan
• Cocok untuk main cepat

💡 Tips: Terbang di tengah celah, jangan terlalu dekat ke pipa!""",

    '2048': """🔢 2048 — Gabungkan angka yang sama dengan menggeser papan. Target: mencapai angka 2048!

🎮 Cara Bermain:
• Arrow Keys atau swipe untuk menggeser semua angka
• Angka sama yang bertemu akan digabung (2+2=4)
• Setiap gabungan menambah skor
• Game over jika papan penuh dan tidak ada gabungan

⭐ Fitur:
• Animasi halus
• Warna berbeda tiap angka
• Undo dan restart
• High score tersimpan

💡 Tips: Jaga angka terbesar di satu sudut, jangan digeser dari sana!""",

    'pacman': """👻 Pac-Man — Makan semua titik di labirin sambil menghindari hantu. Klasik arcade legendaris!

🎮 Cara Bermain:
• Arrow Keys atau WASD untuk bergerak
• Makan titik kecil = 10 poin
• Makan power pellet = hantu bisa dimakan
• Hindari hantu saat tidak ada power pellet

⭐ Fitur:
• Labirin klasik
• 4 hantu dengan AI berbeda
• Power pellet untuk balas serang
• Sound effect khas arcade

💡 Tips: Gunakan power pellet saat hantu berkumpul untuk skor maksimal!""",

    'minesweeper': """💣 Minesweeper — Temukan semua ranjau tanpa meledakkannya. Gunakan angka petunjuk untuk menandai posisi ranjau!

🎮 Cara Bermain:
• Klik kiri untuk membuka kotak
• Klik kanan untuk menandai ranjau 🚩
• Angka menunjukkan jumlah ranjau di sekitar
• Menang jika semua kotak aman terbuka

⭐ Fitur:
• 3 tingkat kesulitan
• Timer dan counter ranjau
• Klik pertama selalu aman
• Kontrol mobile friendly

💡 Tips: Mulai dari pojok, lalu gunakan logika angka untuk menyebar!""",

    'memory-card': """🃏 Memory Card — Cocokkan pasangan kartu yang sama. Latih daya ingat dan konsentrasi!

🎮 Cara Bermain:
• Klik kartu untuk membuka
• Klik kartu kedua, jika sama akan tetap terbuka
• Jika beda, kartu akan tertutup kembali
• Selesaikan semua pasangan secepat mungkin

⭐ Fitur:
• Beberapa tingkat kesulitan
• Timer dan jumlah langkah
• Animasi flip kartu
• High score tersimpan

💡 Tips: Hafalkan posisi kartu, jangan asal klik!""",
}

with app.app_context():
    db = SessionLocal()
    try:
        updated = 0
        for slug, desc in DESCRIPTIONS.items():
            g = db.query(Game).filter_by(slug=slug).first()
            if g:
                g.description = desc
                updated += 1
                print(f"OK {slug}")
            else:
                print(f"SKIP {slug} - tidak ada di database")
        db.commit()
        print(f"\nSELESAI: {updated} deskripsi game diupdate!")
    finally:
        db.close()
