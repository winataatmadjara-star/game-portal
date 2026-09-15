import os
from pathlib import Path

BASE = Path("app/static/games")
os.makedirs(BASE / "geo-explorer", exist_ok=True)

GEO = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Geo Explorer</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
html, body { width:100%; height:100%; overflow:hidden; position:fixed; background:#0a0e27; color:#fff; touch-action:none; }
body { display:flex; justify-content:center; align-items:center; }
.bg-map { position:fixed; inset:0; z-index:0; background:radial-gradient(ellipse at center, #1a3a5c 0%, #0a0e27 100%); }
.game-container { position:relative; z-index:1; display:flex; flex-direction:column; align-items:center; gap:8px; padding:8px; width:100%; height:100%; }
.title { font-size:1.5rem; font-weight:800; background:linear-gradient(135deg,#22d3ee,#4ade80); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:2px; text-transform:uppercase; filter:drop-shadow(0 0 12px rgba(34,211,238,0.5)); }
.hud { display:flex; justify-content:space-between; align-items:center; width:100%; max-width:640px; background:rgba(15,23,42,0.9); backdrop-filter:blur(10px); padding:10px 16px; border-radius:12px; border:1px solid rgba(34,211,238,0.3); }
.hud-item { display:flex; flex-direction:column; align-items:center; gap:2px; }
.hud-label { font-size:10px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; }
.hud-value { font-size:16px; font-weight:700; font-family:'Courier New',monospace; }
.hud .score .hud-value { color:#22d3ee; }
.hud .lives .hud-value { color:#ef4444; }
.hud .level .hud-value { color:#4ade80; }
.hud .streak .hud-value { color:#fbbf24; }
.level-progress { width:100%; max-width:640px; height:6px; background:rgba(15,23,42,0.9); border-radius:3px; overflow:hidden; border:1px solid rgba(74,222,128,0.3); }
.level-progress-fill { height:100%; width:0%; background:linear-gradient(90deg,#22d3ee,#4ade80); transition:width 0.4s ease; }
.canvas-wrapper { position:relative; display:inline-block; border:3px solid rgba(34,211,238,0.4); border-radius:14px; overflow:hidden; box-shadow:0 0 40px rgba(34,211,238,0.3); }
canvas { display:block; background:#0a0e27; touch-action:none; }
.overlay { position:absolute; inset:0; background:rgba(10,14,39,0.95); display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:24px; z-index:10; }
.overlay.hidden { display:none; }
.overlay h1 { font-size:1.8rem; margin-bottom:12px; background:linear-gradient(135deg,#22d3ee,#4ade80); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay h1.dead { background:linear-gradient(135deg,#ef4444,#f97316); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay h1.win { background:linear-gradient(135deg,#fbbf24,#22c55e); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay p { margin-bottom:6px; font-size:13px; color:#cbd5e1; line-height:1.5; max-width:380px; }
.overlay .final-score { font-size:2.2rem; font-weight:800; color:#fbbf24; margin:12px 0; font-family:'Courier New',monospace; }
.overlay button { padding:12px 32px; background:linear-gradient(135deg,#22d3ee,#4ade80); color:#0a0e27; border:none; border-radius:10px; font-size:15px; font-weight:700; cursor:pointer; margin-top:10px; box-shadow:0 4px 15px rgba(34,211,238,0.4); }
.level-badge { display:inline-block; padding:4px 14px; background:rgba(74,222,128,0.2); border:1px solid #4ade80; border-radius:20px; font-size:11px; color:#4ade80; font-weight:700; margin-bottom:10px; text-transform:uppercase; }
.toast { position:fixed; top:18%; left:50%; transform:translateX(-50%) scale(0); background:linear-gradient(135deg,#22d3ee,#4ade80); color:#0a0e27; padding:14px 28px; border-radius:14px; font-size:16px; font-weight:800; z-index:100; box-shadow:0 10px 40px rgba(34,211,238,0.6); pointer-events:none; text-align:center; }
.toast.show { animation:toastPop 2s ease forwards; }
@keyframes toastPop { 0%{transform:translateX(-50%) scale(0);opacity:0;} 15%{transform:translateX(-50%) scale(1.1);opacity:1;} 25%{transform:translateX(-50%) scale(1);opacity:1;} 85%{transform:translateX(-50%) scale(1);opacity:1;} 100%{transform:translateX(-50%) scale(0.9);opacity:0;} }
.controls-mobile { display:none; gap:8px; margin-top:4px; }
@media (max-width:700px) { .title{font-size:1.1rem;} .hud{max-width:96vw;font-size:11px;padding:6px 10px;} .hud-value{font-size:13px;} }
</style>
</head>
<body>
<div class="bg-map"></div>
<div class="game-container">
    <div class="title">🌍 Geo Explorer</div>
    <div class="hud">
        <div class="hud-item score"><span class="hud-label">Skor</span><span class="hud-value" id="score">0</span></div>
        <div class="hud-item lives"><span class="hud-label">Nyawa</span><span class="hud-value" id="lives">❤❤❤</span></div>
        <div class="hud-item level"><span class="hud-label">Level</span><span class="hud-value" id="levelDisplay">1/10</span></div>
        <div class="hud-item streak"><span class="hud-label">Streak</span><span class="hud-value" id="streak">x1</span></div>
    </div>
    <div class="level-progress"><div class="level-progress-fill" id="progress"></div></div>
    <div class="canvas-wrapper">
        <canvas id="canvas" width="640" height="500"></canvas>
        <div id="overlay" class="overlay">
            <div class="level-badge" id="badge">LEVEL 1</div>
            <h1>🌍 GEO EXPLORER</h1>
            <p><strong>10 Level</strong> petualangan geografi!</p>
            <p>Tebak ibu kota, negara, benua, dan landmark dunia</p>
            <p>Jawab cepat untuk skor lebih tinggi</p>
            <button id="startBtn" type="button">▶ MULAI PETUALANGAN</button>
        </div>
    </div>
</div>
<div id="toast" class="toast"></div>
<script>
var canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d');
var scoreEl=document.getElementById('score'),livesEl=document.getElementById('lives'),levelDisplayEl=document.getElementById('levelDisplay'),streakEl=document.getElementById('streak');
var progressEl=document.getElementById('progress'),overlay=document.getElementById('overlay'),badge=document.getElementById('badge'),startBtn=document.getElementById('startBtn'),toast=document.getElementById('toast');
var W=canvas.width,H=canvas.height;

var score=0,lives=3,level=1,streak=1,questionsAnswered=0,correctInLevel=0,questionsNeeded=5;
var currentQuestion=null,shuffledAnswers=[],answerRects=[],timeLeft=0,timeMax=0;
var isRunning=false,isPaused=false,levelTransitioning=false,showingFeedback=false,feedbackType='',feedbackText='';
var gameLoop,frameCount=0,particles=[],stars=[];

/* ============================================================
   BANK SOAL — 10 level, masing-masing 10+ soal
   ============================================================ */
var QUESTIONS = [
    /* LEVEL 1 — Ibu kota ASEAN */
    [
        {q:"Apa ibu kota Indonesia?",a:["Jakarta","Bandung","Surabaya","Medan"],c:0},
        {q:"Apa ibu kota Malaysia?",a:["Kuala Lumpur","Singapore","Bangkok","Manila"],c:0},
        {q:"Apa ibu kota Thailand?",a:["Bangkok","Hanoi","Phnom Penh","Vientiane"],c:0},
        {q:"Apa ibu kota Vietnam?",a:["Hanoi","Ho Chi Minh","Da Nang","Hue"],c:0},
        {q:"Apa ibu kota Filipina?",a:["Manila","Cebu","Davao","Quezon"],c:0},
        {q:"Apa ibu kota Singapura?",a:["Singapore","Johor","Batam","Kuala Lumpur"],c:0},
        {q:"Apa ibu kota Kamboja?",a:["Phnom Penh","Siem Reap","Battambang","Sihanoukville"],c:0},
        {q:"Apa ibu kota Laos?",a:["Vientiane","Luang Prabang","Pakse","Savannakhet"],c:0},
        {q:"Apa ibu kota Myanmar?",a:["Naypyidaw","Yangon","Mandalay","Bago"],c:0},
        {q:"Apa ibu kota Brunei?",a:["Bandar Seri Begawan","Kuala Belait","Seria","Tutong"],c:0}
    ],
    /* LEVEL 2 — Negara di Asia Tenggara */
    [
        {q:"Negara mana yang berbatasan langsung dengan Indonesia?",a:["Malaysia","Thailand","Vietnam","Filipina"],c:0},
        {q:"Negara ASEAN yang tidak memiliki laut?",a:["Laos","Kamboja","Vietnam","Myanmar"],c:0},
        {q:"Negara mana yang berbentuk kepulauan terbesar di dunia?",a:["Indonesia","Filipina","Malaysia","Brunei"],c:0},
        {q:"Negara mana yang pernah dijajah Prancis?",a:["Vietnam","Malaysia","Indonesia","Thailand"],c:0},
        {q:"Negara mana yang tidak pernah dijajah?",a:["Thailand","Vietnam","Myanmar","Kamboja"],c:0},
        {q:"Negara mana yang ibu kotanya Kuala Lumpur?",a:["Malaysia","Singapore","Brunei","Indonesia"],c:0},
        {q:"Negara mana yang terkenal dengan kuil Angkor Wat?",a:["Kamboja","Thailand","Vietnam","Laos"],c:0},
        {q:"Negara mana yang memiliki mata uang Baht?",a:["Thailand","Myanmar","Laos","Kamboja"],c:0},
        {q:"Negara mana yang berbentuk kerajaan?",a:["Brunei","Vietnam","Laos","Filipina"],c:0},
        {q:"Negara mana yang paling banyak penduduknya di ASEAN?",a:["Indonesia","Filipina","Vietnam","Thailand"],c:0}
    ],
    /* LEVEL 3 — Asia */
    [
        {q:"Apa negara terbesar di dunia berdasarkan luas?",a:["Rusia","Kanada","China","USA"],c:0},
        {q:"Apa negara dengan penduduk terbanyak di dunia?",a:["India","China","USA","Indonesia"],c:0},
        {q:"Apa ibu kota Jepang?",a:["Tokyo","Osaka","Kyoto","Nagoya"],c:0},
        {q:"Apa ibu kota China?",a:["Beijing","Shanghai","Hong Kong","Guangzhou"],c:0},
        {q:"Apa ibu kota India?",a:["New Delhi","Mumbai","Kolkata","Chennai"],c:0},
        {q:"Apa ibu kota Korea Selatan?",a:["Seoul","Busan","Incheon","Daegu"],c:0},
        {q:"Gunung tertinggi di dunia ada di negara?",a:["Nepal","China","India","Bhutan"],c:0},
        {q:"Apa negara dengan ekonomi terbesar di Asia?",a:["China","Jepang","India","Korea Selatan"],c:0},
        {q:"Apa ibu kota Arab Saudi?",a:["Riyadh","Jeddah","Mecca","Medina"],c:0},
        {q:"Apa ibu kota Turki?",a:["Ankara","Istanbul","Izmir","Bursa"],c:0}
    ],
    /* LEVEL 4 — Eropa */
    [
        {q:"Apa ibu kota Prancis?",a:["Paris","Lyon","Marseille","Nice"],c:0},
        {q:"Apa ibu kota Jerman?",a:["Berlin","Munich","Hamburg","Frankfurt"],c:0},
        {q:"Apa ibu kota Italia?",a:["Roma","Milan","Napoli","Venesia"],c:0},
        {q:"Apa ibu kota Spanyol?",a:["Madrid","Barcelona","Valencia","Sevilla"],c:0},
        {q:"Apa ibu kota Inggris?",a:["London","Manchester","Birmingham","Liverpool"],c:0},
        {q:"Apa ibu kota Belanda?",a:["Amsterdam","Rotterdam","Den Haag","Utrecht"],c:0},
        {q:"Apa ibu kota Portugal?",a:["Lisbon","Porto","Coimbra","Braga"],c:0},
        {q:"Apa ibu kota Rusia?",a:["Moscow","St Petersburg","Kazan","Sochi"],c:0},
        {q:"Apa ibu kota Yunani?",a:["Athena","Thessaloniki","Patras","Heraklion"],c:0},
        {q:"Apa ibu kota Swiss?",a:["Bern","Zurich","Geneva","Basel"],c:0}
    ],
    /* LEVEL 5 — Amerika */
    [
        {q:"Apa ibu kota Amerika Serikat?",a:["Washington DC","New York","Los Angeles","Chicago"],c:0},
        {q:"Apa ibu kota Kanada?",a:["Ottawa","Toronto","Vancouver","Montreal"],c:0},
        {q:"Apa ibu kota Meksiko?",a:["Mexico City","Guadalajara","Monterrey","Cancun"],c:0},
        {q:"Apa ibu kota Brasil?",a:["Brasilia","Rio de Janeiro","Sao Paulo","Salvador"],c:0},
        {q:"Apa ibu kota Argentina?",a:["Buenos Aires","Cordoba","Rosario","Mendoza"],c:0},
        {q:"Apa negara terbesar di Amerika Selatan?",a:["Brasil","Argentina","Peru","Kolombia"],c:0},
        {q:"Apa ibu kota Peru?",a:["Lima","Cusco","Arequipa","Trujillo"],c:0},
        {q:"Apa ibu kota Chili?",a:["Santiago","Valparaiso","Concepcion","Antofagasta"],c:0},
        {q:"Apa ibu kota Kuba?",a:["Havana","Santiago","Camaguey","Holguin"],c:0},
        {q:"Air terjun tertinggi di dunia ada di?",a:["Venezuela","Brasil","Argentina","Guyana"],c:0}
    ],
    /* LEVEL 6 — Afrika */
    [
        {q:"Apa ibu kota Mesir?",a:["Kairo","Alexandria","Luxor","Aswan"],c:0},
        {q:"Apa ibu kota Afrika Selatan?",a:["Pretoria","Cape Town","Johannesburg","Durban"],c:0},
        {q:"Apa negara terbesar di Afrika?",a:["Aljazair","Libya","Sudan","Congo"],c:0},
        {q:"Apa ibu kota Kenya?",a:["Nairobi","Mombasa","Kisumu","Nakuru"],c:0},
        {q:"Apa ibu kota Nigeria?",a:["Abuja","Lagos","Kano","Ibadan"],c:0},
        {q:"Apa ibu kota Maroko?",a:["Rabat","Casablanca","Marrakech","Fes"],c:0},
        {q:"Apa gurun terbesar di Afrika?",a:["Sahara","Kalahari","Namib","Danakil"],c:0},
        {q:"Sungai terpanjang di Afrika?",a:["Nil","Congo","Niger","Zambezi"],c:0},
        {q:"Apa ibu kota Ethiopia?",a:["Addis Ababa","Dire Dawa","Mekelle","Gondar"],c:0},
        {q:"Apa ibu kota Ghana?",a:["Accra","Kumasi","Tamale","Cape Coast"],c:0}
    ],
    /* LEVEL 7 — Australia & Oceania */
    [
        {q:"Apa ibu kota Australia?",a:["Canberra","Sydney","Melbourne","Brisbane"],c:0},
        {q:"Apa ibu kota Selandia Baru?",a:["Wellington","Auckland","Christchurch","Hamilton"],c:0},
        {q:"Apa negara terbesar di Oceania?",a:["Australia","Selandia Baru","Papua Nugini","Fiji"],c:0},
        {q:"Hewan khas Australia?",a:["Kanguru","Panda","Beruang","Harimau"],c:0},
        {q:"Apa ibu kota Fiji?",a:["Suva","Nadi","Lautoka","Labasa"],c:0},
        {q:"Terumbu karang terbesar di dunia?",a:["Great Barrier Reef","Red Sea Reef","Maldives","Palau"],c:0},
        {q:"Pulau terbesar di dunia?",a:["Greenland","Kalimantan","Sumatera","Papua"],c:0},
        {q:"Apa ibu kota Papua Nugini?",a:["Port Moresby","Lae","Mount Hagen","Madang"],c:0},
        {q:"Apa ibu kota Samoa?",a:["Apia","Pago Pago","Nuku alofa","Suva"],c:0},
        {q:"Apa ibu kota Tonga?",a:["Nuku alofa","Apia","Neiafu","Haveluloto"],c:0}
    ],
    /* LEVEL 8 — Bendera & Simbol */
    [
        {q:"Bendera apa yang berlambang daun maple?",a:["Kanada","USA","Inggris","Jepang"],c:0},
        {q:"Negara dengan bendera matahari terbit?",a:["Jepang","Korea","China","Vietnam"],c:0},
        {q:"Bendera apa yang berlambang bulan bintang?",a:["Turki","Pakistan","Aljazair","Malaysia"],c:0},
        {q:"Bendera apa yang berlambang bintang kuning?",a:["Vietnam","China","Korea","Singapura"],c:0},
        {q:"Bendera Israel berlambang apa?",a:["Bintang Daud","Bulan","Matahari","Salib"],c:0},
        {q:"Bendera apa yang memiliki warna merah putih biru horizontal?",a:["Belanda","Prancis","Rusia","Thailand"],c:0},
        {q:"Bendera apa yang memiliki 50 bintang?",a:["USA","China","Brazil","Australia"],c:0},
        {q:"Bendera apa yang berlambang singa?",a:["Singapura","Malaysia","Sri Lanka","India"],c:0},
        {q:"Bendera apa yang berlambang salib putih di merah?",a:["Swiss","Denmark","Swedia","Norwegia"],c:0},
        {q:"Bendera apa yang berlambang elang?",a:["Indonesia","Albania","Meksiko","Mesir"],c:0}
    ],
    /* LEVEL 9 — Landmark Dunia */
    [
        {q:"Menara Eiffel ada di negara?",a:["Prancis","Italia","Inggris","Belgia"],c:0},
        {q:"Colosseum ada di kota?",a:["Roma","Athena","Madrid","Paris"],c:0},
        {q:"Taj Mahal ada di negara?",a:["India","Pakistan","Bangladesh","Nepal"],c:0},
        {q:"Piramida Giza ada di?",a:["Mesir","Sudan","Libya","Yaman"],c:0},
        {q:"Tembok Besar ada di?",a:["China","Mongolia","Korea","Jepang"],c:0},
        {q:"Machu Picchu ada di?",a:["Peru","Chili","Bolivia","Argentina"],c:0},
        {q:"Angkor Wat ada di?",a:["Kamboja","Thailand","Vietnam","Laos"],c:0},
        {q:"Stonehenge ada di?",a:["Inggris","Irlandia","Skotlandia","Prancis"],c:0},
        {q:"Petra ada di?",a:["Yordania","Mesir","Israel","Arab Saudi"],c:0},
        {q:"Christ the Redeemer ada di?",a:["Brasil","Argentina","Portugal","Spanyol"],c:0}
    ],
    /* LEVEL 10 — Campuran */
    [
        {q:"Berapa jumlah benua di dunia?",a:["7","5","6","8"],c:0},
        {q:"Samudra terbesar di dunia?",a:["Pasifik","Atlantik","Hindia","Arktik"],c:0},
        {q:"Danau terbesar di dunia?",a:["Kaspia","Superior","Victoria","Baikal"],c:0},
        {q:"Negara dengan garis pantai terpanjang?",a:["Kanada","Indonesia","Rusia","Australia"],c:0},
        {q:"Pulau paling padat penduduknya?",a:["Jawa","Honshu","Sumatera","Luzon"],c:0},
        {q:"Negara terkecil di dunia?",a:["Vatikan","Monaco","San Marino","Nauru"],c:0},
        {q:"Kota terpadat di dunia?",a:["Tokyo","Delhi","Shanghai","Sao Paulo"],c:0},
        {q:"Gunung tertinggi di Asia Tenggara?",a:["Hkakabo Razi","Kinabalu","Semeru","Fansipan"],c:0},
        {q:"Laut terdalam di dunia?",a:["Laut Filipina","Laut Jawa","Laut Kaspia","Laut Merah"],c:0},
        {q:"Negara dengan zona waktu terbanyak?",a:["Prancis","Rusia","USA","China"],c:0}
    ]
];

/* ============================================================
   AUDIO
   ============================================================ */
var audioCtx=null;
function initAudio(){ if(!audioCtx){ try{ audioCtx=new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} } }
function playSound(f,d,t,v){ t=t||'sine'; v=v||0.06; if(!audioCtx) return; try{ var o=audioCtx.createOscillator(),g=audioCtx.createGain(); o.type=t; o.frequency.value=f; g.gain.value=v; g.gain.exponentialRampToValueAtTime(0.0001,audioCtx.currentTime+d); o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime+d); }catch(e){} }
var SFX = {
    correct:function(){ [523,659,784].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.1,'sine',0.08); },i*70); }); },
    wrong:function(){ playSound(180,0.25,'sawtooth',0.08); },
    tick:function(){ playSound(1000,0.03,'square',0.03); },
    levelUp:function(){ [523,659,784,1047].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.15,'sine',0.09); },i*100); }); },
    gameOver:function(){ [400,300,200,150].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.2,'sawtooth',0.1); },i*120); }); },
    win:function(){ [523,659,784,1047,1319].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.2,'sine',0.09); },i*130); }); }
};

/* ============================================================
   FIT CANVAS
   ============================================================ */
function fitCanvas(){
    var maxW = Math.min(window.innerWidth - 30, 640);
    var maxH = Math.min(window.innerHeight - 220, 500);
    var ratio = W / H;
    var cw = maxW, ch = cw / ratio;
    if(ch > maxH){ ch = maxH; cw = ch * ratio; }
    canvas.style.width = cw + 'px';
    canvas.style.height = ch + 'px';
    draw();
}
window.addEventListener('resize', fitCanvas);

/* ============================================================
   PARTICLES
   ============================================================ */
function spawnParticles(x,y,color,n){
    n = n || 12;
    for(var i=0;i<n;i++){
        var a = (Math.PI*2*i)/n + Math.random()*0.5;
        var sp = 2 + Math.random()*4;
        particles.push({x:x,y:y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,life:1,color:color,size:2+Math.random()*4});
    }
}
function updateParticles(){
    particles = particles.filter(function(p){return p.life>0;});
    particles.forEach(function(p){
        p.x += p.vx; p.y += p.vy;
        p.vy += 0.15;
        p.vx *= 0.97; p.vy *= 0.97;
        p.life -= 0.02;
    });
}
function drawParticles(){
    particles.forEach(function(p){
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
        ctx.fill();
    });
    ctx.globalAlpha = 1;
}

/* ============================================================
   INIT GAME
   ============================================================ */
function initGame(){
    initAudio();
    score = 0; lives = 3; level = 1; streak = 1;
    questionsAnswered = 0; correctInLevel = 0;
    particles = [];
    frameCount = 0;
    overlay.classList.add('hidden');
    isRunning = true; isPaused = false; levelTransitioning = false;
    showingFeedback = false;
    updateHUD();
    updateProgress();
    nextQuestion();
    clearInterval(gameLoop);
    gameLoop = setInterval(update, 1000/60);
    fitCanvas();
}

function updateHUD(){
    scoreEl.textContent = score;
    livesEl.textContent = '❤'.repeat(Math.max(0,lives));
    levelDisplayEl.textContent = level + '/10';
    streakEl.textContent = 'x' + streak;
}

function updateProgress(){
    questionsNeeded = 5 + (level-1) * 1;
    var pct = (correctInLevel / questionsNeeded) * 100;
    progressEl.style.width = Math.min(100, pct) + '%';
    badge.textContent = 'LEVEL ' + level;
}

/* ============================================================
   QUESTION
   ============================================================ */
function nextQuestion(){
    var bank = QUESTIONS[Math.min(level-1, QUESTIONS.length-1)];
    currentQuestion = bank[Math.floor(Math.random()*bank.length)];
    shuffledAnswers = currentQuestion.a.slice();
    for(var i = shuffledAnswers.length - 1; i > 0; i--){
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = shuffledAnswers[i]; shuffledAnswers[i] = shuffledAnswers[j]; shuffledAnswers[j] = tmp;
    }
    // Durasi waktu per level
    timeMax = Math.max(8, 20 - level);
    timeLeft = timeMax;
    showingFeedback = false;
    feedbackType = '';
    feedbackText = '';
    computeAnswerRects();
    draw();
}

function computeAnswerRects(){
    answerRects = [];
    var marginX = 40;
    var marginY = H - 260;
    var gap = 14;
    var colW = (W - marginX*2 - gap) / 2;
    var rowH = 50;
    for(var i=0;i<shuffledAnswers.length;i++){
        var col = i % 2;
        var row = Math.floor(i / 2);
        answerRects.push({
            x: marginX + col * (colW + gap),
            y: marginY + row * (rowH + gap),
            w: colW,
            h: rowH,
            text: shuffledAnswers[i]
        });
    }
}

/* ============================================================
   ANSWER
   ============================================================ */
function answerClick(idx){
    if(!isRunning || isPaused || levelTransitioning || showingFeedback) return;
    var chosen = shuffledAnswers[idx];
    var correct = currentQuestion.c;
    var correctAnswer = currentQuestion.a[correct];
    var isCorrect = (chosen === correctAnswer);

    if(isCorrect){
        var timeBonus = Math.round(timeLeft * 5);
        var pts = 100 * streak + timeBonus;
        score += pts;
        correctInLevel++;
        streak = Math.min(streak + 1, 9);
        showingFeedback = true;
        feedbackType = 'correct';
        feedbackText = '+' + pts + (timeBonus > 0 ? ' (bonus ' + timeBonus + ')' : '');
        SFX.correct();
        spawnParticles(W/2, H/2 - 40, '#4ade80', 20);
        updateHUD();
        updateProgress();

        setTimeout(function(){
            if(correctInLevel >= questionsNeeded){
                nextLevel();
            } else {
                nextQuestion();
            }
        }, 900);
    } else {
        lives--;
        streak = 1;
        showingFeedback = true;
        feedbackType = 'wrong';
        feedbackText = 'Salah! Jawaban: ' + correctAnswer;
        SFX.wrong();
        spawnParticles(W/2, H/2 - 40, '#ef4444', 18);
        updateHUD();

        if(lives <= 0){
            setTimeout(function(){ gameOver('Kehabisan nyawa!'); }, 1200);
            return;
        }
        setTimeout(function(){
            nextQuestion();
        }, 1400);
    }
}

/* ============================================================
   LEVEL TRANSITION
   ============================================================ */
function nextLevel(){
    if(level >= 10){ winGame(); return; }
    levelTransitioning = true;
    isPaused = true;
    SFX.levelUp();
    var next = level + 1;
    showToast('🎉 LEVEL ' + next + '!');
    setTimeout(function(){
        level = next;
        correctInLevel = 0;
        updateHUD();
        updateProgress();
        isPaused = false;
        levelTransitioning = false;
        nextQuestion();
    }, 1800);
}

/* ============================================================
   UPDATE
   ============================================================ */
var lastTick = 0;
function update(){
    if(!isRunning || isPaused || levelTransitioning) return;
    frameCount++;

    // Timer countdown
    timeLeft -= 1/60;
    // Tick sound per detik
    var secNow = Math.ceil(timeLeft);
    if(secNow !== lastTick && secNow <= 5 && secNow > 0){
        lastTick = secNow;
        SFX.tick();
    }
    if(timeLeft <= 0 && !showingFeedback){
        // Waktu habis = salah
        lives--;
        streak = 1;
        showingFeedback = true;
        feedbackType = 'wrong';
        var correctAnswer = currentQuestion.a[currentQuestion.c];
        feedbackText = 'Waktu habis! Jawaban: ' + correctAnswer;
        SFX.wrong();
        updateHUD();
        if(lives <= 0){
            setTimeout(function(){ gameOver('Kehabisan waktu!'); }, 1200);
            return;
        }
        setTimeout(function(){ nextQuestion(); }, 1400);
    }

    updateParticles();
    draw();
}

/* ============================================================
   DRAW
   ============================================================ */
function draw(){
    // Background
    var grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, '#0d1f3c');
    grad.addColorStop(1, '#0a0e27');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Grid samar
    ctx.strokeStyle = 'rgba(34,211,238,0.05)';
    ctx.lineWidth = 1;
    for(var i=0;i<W;i+=40){ ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,H); ctx.stroke(); }
    for(var j=0;j<H;j+=40){ ctx.beginPath(); ctx.moveTo(0,j); ctx.lineTo(W,j); ctx.stroke(); }

    if(!currentQuestion) return;

    // ===== JUDUL LEVEL =====
    ctx.fillStyle = 'rgba(74,222,128,0.9)';
    ctx.font = 'bold 12px "Segoe UI",sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('LEVEL ' + level + ' — SOAL ' + (correctInLevel+1) + '/' + questionsNeeded, W/2, 30);

    // ===== PERTANYAAN =====
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 22px "Segoe UI",sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    var q = currentQuestion.q;
    var qLines = wrapText(q, W - 80, 'bold 22px "Segoe UI",sans-serif');
    var qStartY = 80;
    qLines.forEach(function(line, i){
        ctx.fillText(line, W/2, qStartY + i * 32);
    });

    // ===== TIMER BAR =====
    var timerY = qStartY + qLines.length * 32 + 20;
    var timerW = W - 80;
    var timerPct = Math.max(0, timeLeft / timeMax);
    var timerColor = timerPct > 0.5 ? '#4ade80' : timerPct > 0.25 ? '#fbbf24' : '#ef4444';

    ctx.fillStyle = 'rgba(15,23,42,0.8)';
    roundRect(40, timerY, timerW, 16, 8);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.lineWidth = 2;
    roundRect(40, timerY, timerW, 16, 8);
    ctx.stroke();

    ctx.fillStyle = timerColor;
    roundRect(40, timerY, timerW * timerPct, 16, 8);
    ctx.fill();

    // Angka timer
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px "Courier New",monospace';
    ctx.textAlign = 'center';
    ctx.fillText(Math.ceil(Math.max(0, timeLeft)) + 's', W/2, timerY + 8);

    // ===== FEEDBACK OVERLAY =====
    if(showingFeedback){
        var overlayColor = feedbackType === 'correct' ? 'rgba(74,222,128,0.9)' : 'rgba(239,68,68,0.9)';
        ctx.fillStyle = overlayColor;
        roundRect(W/2 - 200, H/2 - 30, 400, 60, 14);
        ctx.fill();
        ctx.fillStyle = '#0a0e27';
        ctx.font = 'bold 18px "Segoe UI",sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(feedbackText, W/2, H/2);
        drawParticles();
        return;
    }

    // ===== JAWABAN =====
    answerRects.forEach(function(r, i){
        // Shadow
        ctx.fillStyle = 'rgba(0,0,0,0.3)';
        roundRect(r.x + 2, r.y + 3, r.w, r.h, 12);
        ctx.fill();

        // Body gradient
        var bodyGrad = ctx.createLinearGradient(r.x, r.y, r.x, r.y + r.h);
        bodyGrad.addColorStop(0, '#1e3a5f');
        bodyGrad.addColorStop(1, '#0f2442');
        ctx.fillStyle = bodyGrad;
        roundRect(r.x, r.y, r.w, r.h, 12);
        ctx.fill();

        // Border
        ctx.strokeStyle = 'rgba(34,211,238,0.4)';
        ctx.lineWidth = 2;
        roundRect(r.x, r.y, r.w, r.h, 12);
        ctx.stroke();

        // Highlight atas
        ctx.fillStyle = 'rgba(255,255,255,0.08)';
        roundRect(r.x, r.y, r.w, 8, 12);
        ctx.fill();

        // Text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px "Segoe UI",sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(r.text, r.x + r.w/2, r.y + r.h/2);
    });

    drawParticles();
}

/* Helper wrap text */
function wrapText(text, maxWidth, font){
    ctx.font = font;
    var words = text.split(' ');
    var lines = [];
    var currentLine = '';
    words.forEach(function(word){
        var testLine = currentLine ? currentLine + ' ' + word : word;
        if(ctx.measureText(testLine).width > maxWidth && currentLine){
            lines.push(currentLine);
            currentLine = word;
        } else {
            currentLine = testLine;
        }
    });
    if(currentLine) lines.push(currentLine);
    return lines;
}

/* Helper rounded rect */
function roundRect(x, y, w, h, r){
    if(w < 2*r) r = w/2;
    if(h < 2*r) r = h/2;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
}

/* ============================================================
   TOAST
   ============================================================ */
function showToast(t){
    toast.textContent = t;
    toast.classList.remove('show');
    void toast.offsetWidth;
    toast.classList.add('show');
}

/* ============================================================
   GAME OVER / WIN
   ============================================================ */
function gameOver(reason){
    isRunning = false;
    clearInterval(gameLoop);
    SFX.gameOver();
    overlay.classList.remove('hidden');
    overlay.innerHTML = '<div class="level-badge">LEVEL ' + level + '</div>'
        + '<h1 class="dead">💀 GAME OVER</h1>'
        + '<p>' + (reason || 'Coba lagi!') + '</p>'
        + '<p>Skor kamu:</p>'
        + '<div class="final-score">' + score + '</div>'
        + '<button id="restartBtn" type="button">🔄 MAIN LAGI</button>';
    document.getElementById('restartBtn').addEventListener('click', initGame);
    saveScore(score);
}

function winGame(){
    isRunning = false;
    clearInterval(gameLoop);
    SFX.win();
    overlay.classList.remove('hidden');
    overlay.innerHTML = '<div class="level-badge">🏆 SEMUA LEVEL SELESAI</div>'
        + '<h1 class="win">🏆 YOU WIN!</h1>'
        + '<p>Kamu menaklukkan 10 level Geo Explorer!</p>'
        + '<div class="final-score">' + score + '</div>'
        + '<button id="restartBtn" type="button">🔄 MAIN LAGI</button>';
    document.getElementById('restartBtn').addEventListener('click', initGame);
    saveScore(score);
}

/* ============================================================
   SAVE SCORE
   ============================================================ */
function saveScore(s){
    if(s <= 0) return;
    fetch('/api/scores', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({slug: 'geo-explorer', score: s})
    })
    .then(function(r){ return r.json(); })
    .then(function(data){
        if(data.status === 'guest'){
            showGuestNotice(s);
        }
    })
    .catch(function(){});
}

function showGuestNotice(s){
    var n = document.createElement('div');
    n.style.cssText = 'position:fixed; top:20px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg,#f59e0b,#ef4444); color:#fff; padding:14px 24px; border-radius:12px; font-size:14px; font-weight:600; z-index:10000; box-shadow:0 8px 24px rgba(245,158,11,0.4);';
    n.innerHTML = 'Login untuk simpan skor <strong>' + s + '</strong>! <a href="/login" style="color:#fff; text-decoration:underline;">Login</a>';
    document.body.appendChild(n);
    setTimeout(function(){ n.remove(); }, 6000);
}

/* ============================================================
   INPUT — MOUSE / TOUCH
   ============================================================ */
function getCanvasPos(clientX, clientY){
    var rect = canvas.getBoundingClientRect();
    var scaleX = canvas.width / rect.width;
    var scaleY = canvas.height / rect.height;
    return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY
    };
}

function handleClick(clientX, clientY){
    if(!isRunning || isPaused || levelTransitioning || showingFeedback) return;
    var pos = getCanvasPos(clientX, clientY);
    for(var i=0;i<answerRects.length;i++){
        var r = answerRects[i];
        if(pos.x >= r.x && pos.x <= r.x + r.w && pos.y >= r.y && pos.y <= r.y + r.h){
            answerClick(i);
            return;
        }
    }
}

canvas.addEventListener('click', function(e){
    handleClick(e.clientX, e.clientY);
});

canvas.addEventListener('touchstart', function(e){
    if(e.touches.length !== 1) return;
    e.preventDefault();
    handleClick(e.touches[0].clientX, e.touches[0].clientY);
}, {passive:false});

/* Keyboard shortcut: 1, 2, 3, 4 untuk jawab */
document.addEventListener('keydown', function(e){
    if(!isRunning || isPaused || levelTransitioning || showingFeedback) return;
    var k = e.key;
    if(k >= '1' && k <= '4'){
        var idx = parseInt(k) - 1;
        if(idx < answerRects.length) answerClick(idx);
    }
});

/* ============================================================
   START
   ============================================================ */
startBtn.addEventListener('click', initGame);
fitCanvas();
draw();
</script>
</body>
</html>
"""

(BASE / "geo-explorer" / "geo-explorer.html").write_text(GEO, encoding='utf-8')
print("OK: file geo-explorer.html berhasil ditulis")
