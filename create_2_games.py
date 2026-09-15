import os
from pathlib import Path

BASE = Path("app/static/games")
os.makedirs(BASE / "space-shooter", exist_ok=True)
os.makedirs(BASE / "ninja-runner", exist_ok=True)

SPACE_SHOOTER = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Space Shooter</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
html, body { width:100%; height:100%; overflow:hidden; position:fixed; background:#000; color:#fff; touch-action:none; }
body { display:flex; justify-content:center; align-items:center; }
.bg-stars { position:fixed; inset:0; z-index:0; background:radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%); }
.game-container { position:relative; z-index:1; display:flex; flex-direction:column; align-items:center; gap:8px; padding:8px; width:100%; height:100%; }
.title { font-size:1.5rem; font-weight:800; background:linear-gradient(135deg,#22d3ee,#a78bfa); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:2px; text-transform:uppercase; filter:drop-shadow(0 0 12px rgba(34,211,238,0.5)); }
.hud { display:flex; justify-content:space-between; align-items:center; width:100%; max-width:520px; background:rgba(15,23,42,0.85); backdrop-filter:blur(10px); padding:10px 16px; border-radius:12px; border:1px solid rgba(34,211,238,0.25); }
.hud-item { display:flex; flex-direction:column; align-items:center; gap:2px; }
.hud-label { font-size:10px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; }
.hud-value { font-size:16px; font-weight:700; font-family:'Courier New',monospace; }
.hud .score .hud-value { color:#22d3ee; }
.hud .lives .hud-value { color:#ef4444; }
.hud .wave .hud-value { color:#a78bfa; }
.hud .hp .hud-value { color:#fbbf24; }
.level-progress { width:100%; max-width:520px; height:6px; background:rgba(15,23,42,0.85); border-radius:3px; overflow:hidden; border:1px solid rgba(167,139,250,0.2); }
.level-progress-fill { height:100%; width:0%; background:linear-gradient(90deg,#a78bfa,#22d3ee); transition:width 0.3s ease; }
.canvas-wrapper { position:relative; display:inline-block; border:3px solid rgba(34,211,238,0.4); border-radius:14px; overflow:hidden; box-shadow:0 0 40px rgba(34,211,238,0.3); }
canvas { display:block; background:#000; touch-action:none; }
.overlay { position:absolute; inset:0; background:rgba(0,0,0,0.9); display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:20px; z-index:10; }
.overlay.hidden { display:none; }
.overlay h1 { font-size:1.8rem; margin-bottom:12px; background:linear-gradient(135deg,#22d3ee,#a78bfa); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay h1.dead { background:linear-gradient(135deg,#ef4444,#f97316); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay h1.win { background:linear-gradient(135deg,#fbbf24,#22c55e); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay p { margin-bottom:6px; font-size:13px; color:#cbd5e1; line-height:1.5; max-width:340px; }
.overlay .final-score { font-size:2.2rem; font-weight:800; color:#fbbf24; margin:12px 0; font-family:'Courier New',monospace; }
.overlay button { padding:12px 32px; background:linear-gradient(135deg,#22d3ee,#a78bfa); color:#fff; border:none; border-radius:10px; font-size:15px; font-weight:700; cursor:pointer; margin-top:10px; box-shadow:0 4px 15px rgba(34,211,238,0.4); }
.level-badge { display:inline-block; padding:4px 14px; background:rgba(167,139,250,0.2); border:1px solid #a78bfa; border-radius:20px; font-size:11px; color:#a78bfa; font-weight:700; margin-bottom:10px; text-transform:uppercase; }
.toast { position:fixed; top:18%; left:50%; transform:translateX(-50%) scale(0); background:linear-gradient(135deg,#a78bfa,#22d3ee); color:#fff; padding:14px 28px; border-radius:14px; font-size:16px; font-weight:800; z-index:100; box-shadow:0 10px 40px rgba(34,211,238,0.6); pointer-events:none; text-align:center; }
.toast.show { animation:toastPop 2s ease forwards; }
@keyframes toastPop { 0%{transform:translateX(-50%) scale(0);opacity:0;} 15%{transform:translateX(-50%) scale(1.1);opacity:1;} 25%{transform:translateX(-50%) scale(1);opacity:1;} 85%{transform:translateX(-50%) scale(1);opacity:1;} 100%{transform:translateX(-50%) scale(0.9);opacity:0;} }
.controls-mobile { display:none; gap:8px; margin-top:4px; }
.controls-mobile button { padding:10px 18px; background:rgba(22,33,62,0.9); color:#22d3ee; border:2px solid #22d3ee; border-radius:12px; font-size:14px; font-weight:700; cursor:pointer; user-select:none; }
@media (max-width:600px) { .title{font-size:1.1rem;} .hud{max-width:96vw;font-size:11px;padding:6px 10px;} .hud-value{font-size:13px;} .controls-mobile{display:flex;} }
</style>
</head>
<body>
<div class="bg-stars"></div>
<div class="game-container">
    <div class="title">🚀 Space Shooter</div>
    <div class="hud">
        <div class="hud-item score"><span class="hud-label">Score</span><span class="hud-value" id="score">0</span></div>
        <div class="hud-item hp"><span class="hud-label">HP</span><span class="hud-value" id="hp">100</span></div>
        <div class="hud-item wave"><span class="hud-label">Wave</span><span class="hud-value" id="wave">1/10</span></div>
        <div class="hud-item lives"><span class="hud-label">Lives</span><span class="hud-value" id="lives">❤❤❤</span></div>
    </div>
    <div class="level-progress"><div class="level-progress-fill" id="progress"></div></div>
    <div class="canvas-wrapper">
        <canvas id="canvas" width="560" height="700"></canvas>
        <div id="overlay" class="overlay">
            <div class="level-badge" id="badge">WAVE 1</div>
            <h1>🚀 SPACE SHOOTER</h1>
            <p><strong>10 Wave</strong> dengan boss di setiap akhir!</p>
            <p>← → untuk gerak · SPACE untuk tembak</p>
            <p>atau swipe di mobile</p>
            <button id="startBtn" type="button">▶ MULAI</button>
        </div>
    </div>
    <div class="controls-mobile">
        <button type="button" id="btnLeft">◀</button>
        <button type="button" id="btnFire">🔥</button>
        <button type="button" id="btnRight">▶</button>
    </div>
</div>
<div id="toast" class="toast"></div>
<script>
var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');
var scoreEl = document.getElementById('score');
var hpEl = document.getElementById('hp');
var waveEl = document.getElementById('wave');
var livesEl = document.getElementById('lives');
var progressEl = document.getElementById('progress');
var overlay = document.getElementById('overlay');
var badge = document.getElementById('badge');
var startBtn = document.getElementById('startBtn');
var toast = document.getElementById('toast');
var W = canvas.width, H = canvas.height;
var player, bullets, enemies, enemyBullets, particles, stars;
var score=0, hp=100, lives=3, wave=1, killsInWave=0, killsNeeded=5;
var isRunning=false, isPaused=false, waveTransitioning=false;
var gameLoop, frameCount=0;
var keys = { left:false, right:false, fire:false };
var audioCtx=null;
function initAudio(){ if(!audioCtx){ try{ audioCtx=new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} } }
function playSound(f,d,t,v){ t=t||'sine'; v=v||0.06; if(!audioCtx) return; try{ var o=audioCtx.createOscillator(); var g=audioCtx.createGain(); o.type=t; o.frequency.value=f; g.gain.value=v; g.gain.exponentialRampToValueAtTime(0.0001,audioCtx.currentTime+d); o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime+d); }catch(e){} }
var SFX = {
    shoot:function(){ playSound(880,0.05,'square',0.04); },
    hit:function(){ playSound(220,0.08,'sawtooth',0.05); },
    explode:function(){ playSound(120,0.2,'sawtooth',0.08); },
    powerup:function(){ [523,659,784].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.1); },i*60); }); },
    levelUp:function(){ [523,659,784,1047].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.15); },i*100); }); },
    gameOver:function(){ [400,300,200,150].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.2,'sawtooth',0.1); },i*120); }); },
    win:function(){ [523,659,784,1047,1319].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.2); },i*130); }); }
};
function fitCanvas(){ var maxW=Math.min(window.innerWidth-30,560); var maxH=Math.min(window.innerHeight-200,700); var ratio=W/H; var cw=maxW,ch=cw/ratio; if(ch>maxH){ch=maxH;cw=ch*ratio;} canvas.style.width=cw+'px'; canvas.style.height=ch+'px'; }
window.addEventListener('resize',fitCanvas);
function showToast(t){ toast.textContent=t; toast.classList.remove('show'); void toast.offsetWidth; toast.classList.add('show'); }
function spawnParticles(x,y,color,n){ n=n||12; for(var i=0;i<n;i++){ var a=(Math.PI*2*i)/n+Math.random()*0.5; var sp=1+Math.random()*4; particles.push({ x:x, y:y, vx:Math.cos(a)*sp, vy:Math.sin(a)*sp, life:1, color:color, size:2+Math.random()*3 }); } }
function updateParticles(){ particles=particles.filter(function(p){return p.life>0;}); particles.forEach(function(p){ p.x+=p.vx; p.y+=p.vy; p.vx*=0.96; p.vy*=0.96; p.life-=0.025; }); }
function drawParticles(){ particles.forEach(function(p){ ctx.globalAlpha=p.life; ctx.fillStyle=p.color; ctx.beginPath(); ctx.arc(p.x,p.y,p.size,0,Math.PI*2); ctx.fill(); }); ctx.globalAlpha=1; }
function initStars(){ stars=[]; for(var i=0;i<80;i++){ stars.push({ x:Math.random()*W, y:Math.random()*H, size:Math.random()*2+0.5, speed:Math.random()*2+0.5 }); } }
function updateStars(){ stars.forEach(function(s){ s.y+=s.speed; if(s.y>H){ s.y=0; s.x=Math.random()*W; } }); }
function drawStars(){ stars.forEach(function(s){ ctx.fillStyle='rgba(255,255,255,'+(0.3+s.size/3)+')'; ctx.fillRect(s.x,s.y,s.size,s.size); }); }
function initGame(){ initAudio(); wave=1; score=0; hp=100; lives=3; killsInWave=0; initStars(); resetWave(); overlay.classList.add('hidden'); isRunning=true; isPaused=false; waveTransitioning=false; clearInterval(gameLoop); gameLoop=setInterval(update,1000/60); }
function resetWave(){ killsNeeded = 5 + (wave-1)*2; killsInWave=0; player={ x:W/2, y:H-60, w:36, h:36, speed:6, cooldown:0, invuln:60 }; bullets=[]; enemies=[]; enemyBullets=[]; particles=[]; waveEl.textContent=wave+'/10'; badge.textContent='WAVE '+wave; hpEl.textContent=hp; scoreEl.textContent=score; livesEl.textContent='❤'.repeat(Math.max(0,lives)); spawnEnemies(); updateProgress(); }
function updateProgress(){ var pct=(killsInWave/killsNeeded)*100; progressEl.style.width=Math.min(100,pct)+'%'; }
function spawnEnemies(){ var count=killsNeeded; for(var i=0;i<count;i++){ var type=Math.random(); var enemy; if(type<0.6){ enemy={ x:60+Math.random()*(W-120), y:-40-Math.random()*300, w:32, h:32, speed:1+wave*0.15, hp:1+(wave>=5?1:0), type:'basic', color:'#ef4444' }; } else if(type<0.85){ enemy={ x:60+Math.random()*(W-120), y:-40-Math.random()*300, w:40, h:40, speed:0.8+wave*0.1, hp:2+Math.floor(wave/3), type:'tank', color:'#f97316' }; } else { enemy={ x:60+Math.random()*(W-120), y:-40-Math.random()*300, w:28, h:28, speed:2+wave*0.2, hp:1, type:'fast', color:'#a78bfa' }; } enemy.maxHp=enemy.hp; enemies.push(enemy); } }
function spawnBoss(){ enemies=[]; var bossHp = 20 + wave*10; enemies.push({ x:W/2, y:-80, w:120, h:80, speed:0.5, hp:bossHp, maxHp:bossHp, type:'boss', color:'#dc2626', shootTimer:0, moveDir:1 }); badge.textContent='BOSS WAVE '+wave; showToast('👹 BOSS WAVE '+wave+'!'); }
function update(){ if(!isRunning||isPaused||waveTransitioning) return; frameCount++; updateStars(); if(keys.left) player.x-=player.speed; if(keys.right) player.x+=player.speed; player.x=Math.max(30,Math.min(W-30,player.x)); if(player.invuln>0) player.invuln--; player.cooldown--; if(keys.fire && player.cooldown<=0){ bullets.push({ x:player.x-8, y:player.y-20, vy:-9, w:4, h:12, dmg:1 }); bullets.push({ x:player.x+8, y:player.y-20, vy:-9, w:4, h:12, dmg:1 }); player.cooldown=10; SFX.shoot(); } bullets.forEach(function(b){ b.y+=b.vy; }); bullets=bullets.filter(function(b){ return b.y>-20; }); enemies.forEach(function(e){ if(e.type==='boss'){ e.y+=e.speed; if(e.y>60) e.y=60; e.x+=e.moveDir*1.5; if(e.x<80||e.x>W-80) e.moveDir*=-1; e.shootTimer--; if(e.shootTimer<=0){ e.shootTimer=60-wave*3; if(e.shootTimer<20) e.shootTimer=20; for(var i=-1;i<=1;i++){ enemyBullets.push({ x:e.x, y:e.y+e.h/2, vx:i*2, vy:4, r:6 }); } } } else { e.y+=e.speed; } }); enemies=enemies.filter(function(e){ return e.y<H+80; }); enemyBullets.forEach(function(b){ b.x+=b.vx; b.y+=b.vy; }); enemyBullets=enemyBullets.filter(function(b){ return b.y<H+20 && b.x>-20 && b.x<W+20; }); enemies.forEach(function(e){ bullets.forEach(function(b){ if(!b.dead && b.x>e.x-e.w/2 && b.x<e.x+e.w/2 && b.y>e.y-e.h/2 && b.y<e.y+e.h/2){ b.dead=true; e.hp-=b.dmg; SFX.hit(); spawnParticles(b.x,b.y,'#fbbf24',4); if(e.hp<=0){ e.dead=true; var pts = e.type==='boss'? 500 : e.type==='tank'? 30 : e.type==='fast'? 20 : 10; score+=pts; scoreEl.textContent=score; killsInWave++; SFX.explode(); spawnParticles(e.x,e.y,e.color,15); updateProgress(); } } }); }); bullets=bullets.filter(function(b){ return !b.dead; }); enemies=enemies.filter(function(e){ return !e.dead; }); if(!(enemies[0]&&enemies[0].type==='boss') && killsInWave>=killsNeeded && enemies.length===0){ spawnBoss(); } enemies.forEach(function(e){ if(player.invuln>0) return; var dx=Math.abs(player.x-e.x), dy=Math.abs(player.y-e.y); if(dx<e.w/2+18 && dy<e.h/2+18){ hitPlayer(e.type==='boss'?40:20); } }); enemyBullets.forEach(function(b){ if(player.invuln>0) return; var dx=player.x-b.x, dy=player.y-b.y; if(Math.sqrt(dx*dx+dy*dy)<20){ b.dead=true; hitPlayer(10); } }); enemyBullets=enemyBullets.filter(function(b){return !b.dead;}); if(enemies.length===0 && killsInWave>=killsNeeded && !(enemies[0]&&enemies[0].type==='boss') && frameCount>60){ } updateParticles(); draw(); }
function hitPlayer(dmg){ hp-=dmg; hpEl.textContent=Math.max(0,hp); player.invuln=60; SFX.explode(); spawnParticles(player.x,player.y,'#ef4444',20); if(hp<=0){ lives--; livesEl.textContent='❤'.repeat(Math.max(0,lives)); if(lives<=0){ gameOver('Kehabisan nyawa!'); } else { hp=100; hpEl.textContent=100; player.invuln=120; } } }
function draw(){ ctx.fillStyle='#000'; ctx.fillRect(0,0,W,H); drawStars(); ctx.save(); if(player.invuln>0 && Math.floor(frameCount/6)%2===0){ ctx.globalAlpha=0.4; } drawPlayer(); ctx.restore(); bullets.forEach(function(b){ ctx.fillStyle='#22d3ee'; ctx.shadowColor='#22d3ee'; ctx.shadowBlur=10; ctx.fillRect(b.x-b.w/2,b.y-b.h/2,b.w,b.h); ctx.shadowBlur=0; }); enemies.forEach(function(e){ drawEnemy(e); }); enemyBullets.forEach(function(b){ ctx.fillStyle='#ef4444'; ctx.shadowColor='#ef4444'; ctx.shadowBlur=10; ctx.beginPath(); ctx.arc(b.x,b.y,b.r,0,Math.PI*2); ctx.fill(); ctx.shadowBlur=0; }); drawParticles(); }
function drawPlayer(){ ctx.save(); ctx.translate(player.x,player.y); ctx.fillStyle='#22d3ee'; ctx.shadowColor='#22d3ee'; ctx.shadowBlur=15; ctx.beginPath(); ctx.moveTo(0,-20); ctx.lineTo(-18,15); ctx.lineTo(-8,10); ctx.lineTo(0,18); ctx.lineTo(8,10); ctx.lineTo(18,15); ctx.closePath(); ctx.fill(); ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(0,-5,4,0,Math.PI*2); ctx.fill(); ctx.restore(); }
function drawEnemy(e){ ctx.save(); ctx.translate(e.x,e.y); ctx.fillStyle=e.color; ctx.shadowColor=e.color; ctx.shadowBlur=12; if(e.type==='boss'){ ctx.beginPath(); ctx.moveTo(-e.w/2,-e.h/2); ctx.lineTo(e.w/2,-e.h/2); ctx.lineTo(e.w/2-10,e.h/2); ctx.lineTo(0,e.h/2-10); ctx.lineTo(-e.w/2+10,e.h/2); ctx.closePath(); ctx.fill(); ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(-25,0,7,0,Math.PI*2); ctx.arc(25,0,7,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#000'; ctx.beginPath(); ctx.arc(-25,2,3,0,Math.PI*2); ctx.arc(25,2,3,0,Math.PI*2); ctx.fill(); } else if(e.type==='tank'){ ctx.fillRect(-e.w/2,-e.h/2,e.w,e.h); ctx.fillStyle='rgba(255,255,255,0.3)'; ctx.fillRect(-e.w/2,-e.h/2,e.w,4); } else if(e.type==='fast'){ ctx.beginPath(); ctx.moveTo(0,e.h/2); ctx.lineTo(-e.w/2,-e.h/2); ctx.lineTo(e.w/2,-e.h/2); ctx.closePath(); ctx.fill(); } else { ctx.beginPath(); ctx.arc(0,0,e.w/2,0,Math.PI*2); ctx.fill(); } ctx.restore(); }
function nextWave(){ if(wave>=10){ return winGame(); } waveTransitioning=true; isPaused=true; SFX.levelUp(); var next=wave+1; showToast('🌊 WAVE '+next+'!'); setTimeout(function(){ wave=next; if(wave<=10){ resetWave(); isPaused=false; waveTransitioning=false; } },2000); }
function checkWaveComplete(){ if(enemies.length===0 && killsInWave>=killsNeeded){ nextWave(); } }
var origUpdate = update;
update = function(){ origUpdate(); if(!isPaused && !waveTransitioning && enemies.length===0 && killsInWave>=killsNeeded){ checkWaveComplete(); } };
function gameOver(reason){ isRunning=false; clearInterval(gameLoop); SFX.gameOver(); overlay.classList.remove('hidden'); overlay.innerHTML='<div class="level-badge">WAVE '+wave+'</div><h1 class="dead">💀 GAME OVER</h1><p>'+(reason||'Coba lagi!')+'</p><p>Skor kamu:</p><div class="final-score">'+score+'</div><button id="restartBtn" type="button">🔄 MAIN LAGI</button>'; document.getElementById('restartBtn').addEventListener('click',initGame); saveScore(score); }
function winGame(){ isRunning=false; clearInterval(gameLoop); SFX.win(); overlay.classList.remove('hidden'); overlay.innerHTML='<div class="level-badge">🏆 SEMUA WAVE SELESAI</div><h1 class="win">🏆 YOU WIN!</h1><p>Kamu menaklukkan 10 wave!</p><div class="final-score">'+score+'</div><button id="restartBtn" type="button">🔄 MAIN LAGI</button>'; document.getElementById('restartBtn').addEventListener('click',initGame); saveScore(score); }
function saveScore(s){ if(s<=0) return; fetch('/api/scores',{ method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({slug:'space-shooter',score:s}) }).then(function(r){return r.json();}).then(function(data){ if(data.status==='guest'){ showGuestNotice(s); } }).catch(function(){}); }
function showGuestNotice(s){ var n=document.createElement('div'); n.style.cssText='position:fixed; top:20px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg,#f59e0b,#ef4444); color:#fff; padding:14px 24px; border-radius:12px; font-size:14px; font-weight:600; z-index:10000; box-shadow:0 8px 24px rgba(245,158,11,0.4);'; n.innerHTML='Login untuk simpan skor <strong>'+s+'</strong>! <a href="/login" style="color:#fff; text-decoration:underline;">Login</a>'; document.body.appendChild(n); setTimeout(function(){ n.remove(); },6000); }
document.addEventListener('keydown',function(e){ var k=e.key.toLowerCase(); if(k===' '||k==='spacebar'){ e.preventDefault(); if(!isRunning) initGame(); else keys.fire=true; } if(k==='arrowleft'||k==='a') keys.left=true; if(k==='arrowright'||k==='d') keys.right=true; if(k==='p'&&isRunning){ isPaused=!isPaused; } });
document.addEventListener('keyup',function(e){ var k=e.key.toLowerCase(); if(k===' '||k==='spacebar') keys.fire=false; if(k==='arrowleft'||k==='a') keys.left=false; if(k==='arrowright'||k==='d') keys.right=false; });
document.getElementById('btnLeft').addEventListener('touchstart',function(e){ e.preventDefault(); keys.left=true; });
document.getElementById('btnLeft').addEventListener('touchend',function(e){ e.preventDefault(); keys.left=false; });
document.getElementById('btnRight').addEventListener('touchstart',function(e){ e.preventDefault(); keys.right=true; });
document.getElementById('btnRight').addEventListener('touchend',function(e){ e.preventDefault(); keys.right=false; });
document.getElementById('btnFire').addEventListener('touchstart',function(e){ e.preventDefault(); keys.fire=true; });
document.getElementById('btnFire').addEventListener('touchend',function(e){ e.preventDefault(); keys.fire=false; });
startBtn.addEventListener('click',initGame);
fitCanvas();
</script>
</body>
</html>
"""

NINJA_RUNNER = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Ninja Runner</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
html, body { width:100%; height:100%; overflow:hidden; position:fixed; background:#0a0e27; color:#fff; touch-action:none; }
body { display:flex; justify-content:center; align-items:center; }
.bg-gradient { position:fixed; inset:0; z-index:0; background:linear-gradient(180deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%); animation:bgShift 20s ease-in-out infinite alternate; }
@keyframes bgShift { 0%{filter:hue-rotate(0deg);} 100%{filter:hue-rotate(20deg);} }
.game-container { position:relative; z-index:1; display:flex; flex-direction:column; align-items:center; gap:8px; padding:8px; width:100%; height:100%; }
.title { font-size:1.5rem; font-weight:800; background:linear-gradient(135deg,#ef4444,#fbbf24); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:2px; text-transform:uppercase; filter:drop-shadow(0 0 12px rgba(239,68,68,0.5)); }
.hud { display:flex; justify-content:space-between; align-items:center; width:100%; max-width:720px; background:rgba(15,23,42,0.85); backdrop-filter:blur(10px); padding:10px 16px; border-radius:12px; border:1px solid rgba(239,68,68,0.25); }
.hud-item { display:flex; flex-direction:column; align-items:center; gap:2px; }
.hud-label { font-size:10px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; }
.hud-value { font-size:16px; font-weight:700; font-family:'Courier New',monospace; }
.hud .score .hud-value { color:#fbbf24; }
.hud .dist .hud-value { color:#22d3ee; }
.hud .level .hud-value { color:#a78bfa; }
.hud .lives .hud-value { color:#ef4444; }
.level-progress { width:100%; max-width:720px; height:6px; background:rgba(15,23,42,0.85); border-radius:3px; overflow:hidden; border:1px solid rgba(239,68,68,0.2); }
.level-progress-fill { height:100%; width:0%; background:linear-gradient(90deg,#ef4444,#fbbf24); transition:width 0.3s ease; }
.canvas-wrapper { position:relative; display:inline-block; border:3px solid rgba(239,68,68,0.4); border-radius:14px; overflow:hidden; box-shadow:0 0 40px rgba(239,68,68,0.3); }
canvas { display:block; background:transparent; touch-action:none; }
.overlay { position:absolute; inset:0; background:rgba(10,14,39,0.95); display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:20px; z-index:10; }
.overlay.hidden { display:none; }
.overlay h1 { font-size:1.8rem; margin-bottom:12px; background:linear-gradient(135deg,#ef4444,#fbbf24); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay h1.dead { background:linear-gradient(135deg,#ef4444,#f97316); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay h1.win { background:linear-gradient(135deg,#fbbf24,#22c55e); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.overlay p { margin-bottom:6px; font-size:13px; color:#cbd5e1; line-height:1.5; max-width:340px; }
.overlay .final-score { font-size:2.2rem; font-weight:800; color:#fbbf24; margin:12px 0; font-family:'Courier New',monospace; }
.overlay button { padding:12px 32px; background:linear-gradient(135deg,#ef4444,#fbbf24); color:#fff; border:none; border-radius:10px; font-size:15px; font-weight:700; cursor:pointer; margin-top:10px; box-shadow:0 4px 15px rgba(239,68,68,0.4); }
.level-badge { display:inline-block; padding:4px 14px; background:rgba(239,68,68,0.2); border:1px solid #ef4444; border-radius:20px; font-size:11px; color:#ef4444; font-weight:700; margin-bottom:10px; text-transform:uppercase; }
.toast { position:fixed; top:18%; left:50%; transform:translateX(-50%) scale(0); background:linear-gradient(135deg,#ef4444,#fbbf24); color:#fff; padding:14px 28px; border-radius:14px; font-size:16px; font-weight:800; z-index:100; box-shadow:0 10px 40px rgba(239,68,68,0.6); pointer-events:none; text-align:center; }
.toast.show { animation:toastPop 2s ease forwards; }
@keyframes toastPop { 0%{transform:translateX(-50%) scale(0);opacity:0;} 15%{transform:translateX(-50%) scale(1.1);opacity:1;} 25%{transform:translateX(-50%) scale(1);opacity:1;} 85%{transform:translateX(-50%) scale(1);opacity:1;} 100%{transform:translateX(-50%) scale(0.9);opacity:0;} }
.controls-mobile { display:none; gap:8px; margin-top:4px; }
.controls-mobile button { padding:12px 24px; background:rgba(22,33,62,0.9); color:#ef4444; border:2px solid #ef4444; border-radius:12px; font-size:16px; font-weight:700; cursor:pointer; user-select:none; }
@media (max-width:600px) { .title{font-size:1.1rem;} .hud{max-width:96vw;font-size:11px;padding:6px 10px;} .hud-value{font-size:13px;} .controls-mobile{display:flex;} }
</style>
</head>
<body>
<div class="bg-gradient"></div>
<div class="game-container">
    <div class="title">🥷 Ninja Runner</div>
    <div class="hud">
        <div class="hud-item score"><span class="hud-label">Score</span><span class="hud-value" id="score">0</span></div>
        <div class="hud-item dist"><span class="hud-label">Jarak</span><span class="hud-value" id="dist">0m</span></div>
        <div class="hud-item level"><span class="hud-label">Level</span><span class="hud-value" id="level">1/10</span></div>
        <div class="hud-item lives"><span class="hud-label">Lives</span><span class="hud-value" id="lives">❤❤❤</span></div>
    </div>
    <div class="level-progress"><div class="level-progress-fill" id="progress"></div></div>
    <div class="canvas-wrapper">
        <canvas id="canvas" width="800" height="400"></canvas>
        <div id="overlay" class="overlay">
            <div class="level-badge" id="badge">LEVEL 1</div>
            <h1>🥷 NINJA RUNNER</h1>
            <p><strong>10 Level</strong> dengan rintangan berbeda!</p>
            <p>SPACE / Tap untuk lompat · Double jump tersedia</p>
            <button id="startBtn" type="button">▶ MULAI</button>
        </div>
    </div>
    <div class="controls-mobile">
        <button type="button" id="btnJump">⬆ LOMPAT</button>
    </div>
</div>
<div id="toast" class="toast"></div>
<script>
var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');
var scoreEl = document.getElementById('score');
var distEl = document.getElementById('dist');
var levelEl = document.getElementById('level');
var livesEl = document.getElementById('lives');
var progressEl = document.getElementById('progress');
var overlay = document.getElementById('overlay');
var badge = document.getElementById('badge');
var startBtn = document.getElementById('startBtn');
var toast = document.getElementById('toast');
var W = canvas.width, H = canvas.height;
var GROUND_Y = H - 60;
var player, obstacles, particles, stars, coins;
var score=0, distance=0, lives=3, level=1, levelDistance=0, levelTarget=500;
var isRunning=false, isPaused=false, levelTransitioning=false;
var gameLoop, frameCount=0, speed=6;
var audioCtx=null;
function initAudio(){ if(!audioCtx){ try{ audioCtx=new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} } }
function playSound(f,d,t,v){ t=t||'sine'; v=v||0.06; if(!audioCtx) return; try{ var o=audioCtx.createOscillator(); var g=audioCtx.createGain(); o.type=t; o.frequency.value=f; g.gain.value=v; g.gain.exponentialRampToValueAtTime(0.0001,audioCtx.currentTime+d); o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime+d); }catch(e){} }
var SFX = {
    jump:function(){ playSound(500,0.08,'sine',0.05); },
    doubleJump:function(){ playSound(700,0.08,'sine',0.05); },
    coin:function(){ playSound(880,0.06,'square',0.05); },
    hit:function(){ playSound(150,0.15,'sawtooth',0.08); },
    levelUp:function(){ [523,659,784,1047].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.15); },i*100); }); },
    gameOver:function(){ [400,300,200,150].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.2,'sawtooth',0.1); },i*120); }); },
    win:function(){ [523,659,784,1047,1319].forEach(function(f,i){ setTimeout(function(){ playSound(f,0.2); },i*130); }); }
};
function fitCanvas(){ var maxW=Math.min(window.innerWidth-30,800); var maxH=Math.min(window.innerHeight-200,400); var ratio=W/H; var cw=maxW,ch=cw/ratio; if(ch>maxH){ch=maxH;cw=ch*ratio;} canvas.style.width=cw+'px'; canvas.style.height=ch+'px'; }
window.addEventListener('resize',fitCanvas);
function showToast(t){ toast.textContent=t; toast.classList.remove('show'); void toast.offsetWidth; toast.classList.add('show'); }
function spawnParticles(x,y,color,n){ n=n||12; for(var i=0;i<n;i++){ var a=(Math.PI*2*i)/n+Math.random()*0.5; var sp=1+Math.random()*4; particles.push({ x:x, y:y, vx:Math.cos(a)*sp, vy:Math.sin(a)*sp-2, life:1, color:color, size:2+Math.random()*3 }); } }
function updateParticles(){ particles=particles.filter(function(p){return p.life>0;}); particles.forEach(function(p){ p.x+=p.vx; p.y+=p.vy; p.vy+=0.2; p.vx*=0.97; p.life-=0.025; }); }
function drawParticles(){ particles.forEach(function(p){ ctx.globalAlpha=p.life; ctx.fillStyle=p.color; ctx.beginPath(); ctx.arc(p.x,p.y,p.size,0,Math.PI*2); ctx.fill(); }); ctx.globalAlpha=1; }
function initGame(){ initAudio(); level=1; score=0; distance=0; levelDistance=0; lives=3; speed=6; levelTarget=500; particles=[]; initStars(); resetLevel(); overlay.classList.add('hidden'); isRunning=true; isPaused=false; levelTransitioning=false; clearInterval(gameLoop); gameLoop=setInterval(update,1000/60); }
function initStars(){ stars=[]; for(var i=0;i<50;i++){ stars.push({ x:Math.random()*W, y:Math.random()*GROUND_Y, size:Math.random()*2+0.5, speed:Math.random()*2+1 }); } }
function updateStars(){ stars.forEach(function(s){ s.x-=s.speed*(speed/6); if(s.x<-5){ s.x=W+5; s.y=Math.random()*GROUND_Y; } }); }
function drawStars(){ stars.forEach(function(s){ ctx.fillStyle='rgba(255,255,255,'+(0.3+s.size/3)+')'; ctx.fillRect(s.x,s.y,s.size,s.size); }); }
function resetLevel(){ player={ x:100, y:GROUND_Y-40, w:36, h:56, vy:0, jumps:0, maxJumps:2, onGround:true, runPhase:0 }; obstacles=[]; coins=[]; particles=[]; levelDistance=0; levelEl.textContent=level+'/10'; badge.textContent='LEVEL '+level; scoreEl.textContent=score; distEl.textContent=Math.floor(distance)+'m'; livesEl.textContent='❤'.repeat(Math.max(0,lives)); updateProgress(); spawnInitialObstacles(); }
function updateProgress(){ var pct=(levelDistance/levelTarget)*100; progressEl.style.width=Math.min(100,pct)+'%'; }
function spawnInitialObstacles(){ for(var i=0;i<5;i++){ spawnObstacle(W+200+i*250); } for(var j=0;j<3;j++){ spawnCoin(W+150+j*220); } }
function spawnObstacle(x){ var type=Math.random(); var obs; var typeName; if(type<0.5){ obs={ x:x, y:GROUND_Y-30, w:30, h:30, type:'spike' }; typeName='spike'; } else if(type<0.75){ obs={ x:x, y:GROUND_Y-50, w:40, h:50, type:'box' }; } else { obs={ x:x, y:GROUND_Y-70, w:50, h:70, type:'tall' }; } obs.w=obs.w||30; obstacles.push(obs); }
function spawnCoin(x){ coins.push({ x:x, y:GROUND_Y-80-Math.random()*60, r:10, collected:false }); }
function update(){ if(!isRunning||isPaused||levelTransitioning) return; frameCount++; updateStars(); player.vy+=0.9; player.y+=player.vy; if(player.y>=GROUND_Y-player.h){ player.y=GROUND_Y-player.h; player.vy=0; player.jumps=0; player.onGround=true; } else { player.onGround=false; } player.runPhase+=0.3; obstacles.forEach(function(o){ o.x-=speed; }); obstacles=obstacles.filter(function(o){ return o.x+o.w>-20; }); coins.forEach(function(c){ c.x-=speed; }); coins=coins.filter(function(c){ return c.x+c.r>-20 && !c.collected; }); var last=obstacles[obstacles.length-1]; if(!last || last.x < W-200){ spawnObstacle(W+50); if(Math.random()<0.6) spawnCoin(W+150+Math.random()*150); } coins.forEach(function(c){ var dx=player.x-c.x, dy=(player.y+player.h/2)-c.y; if(Math.sqrt(dx*dx+dy*dy)<player.w/2+c.r+5){ c.collected=true; score+=50; scoreEl.textContent=score; SFX.coin(); spawnParticles(c.x,c.y,'#fbbf24',10); } }); obstacles.forEach(function(o){ var px1=player.x-player.w/2+5, px2=player.x+player.w/2-5; var py1=player.y, py2=player.y+player.h; if(px2>o.x && px1<o.x+o.w && py2>o.y && py1<o.y+o.h){ hitPlayer(); } }); distance+=speed*0.1; levelDistance+=speed*0.1; distEl.textContent=Math.floor(distance)+'m'; updateProgress(); if(levelDistance>=levelTarget){ nextLevel(); } updateParticles(); draw(); }
function hitPlayer(){ SFX.hit(); spawnParticles(player.x,player.y+player.h/2,'#ef4444',20); lives--; livesEl.textContent='❤'.repeat(Math.max(0,lives)); if(lives<=0){ gameOver('Kehabisan nyawa!'); } else { player.y=GROUND_Y-player.h; player.vy=-12; player.jumps=1; } }
function draw(){ ctx.clearRect(0,0,W,H); drawStars(); ctx.fillStyle='#16213e'; ctx.fillRect(0,GROUND_Y,W,H-GROUND_Y); ctx.fillStyle='#1e293b'; ctx.fillRect(0,GROUND_Y,W,4); ctx.fillStyle='#0f3460'; for(var i=0;i<W;i+=40){ var offset=(frameCount*speed)%40; ctx.fillRect(i-offset,GROUND_Y+4,20,2); } drawPlayer(); obstacles.forEach(function(o){ drawObstacle(o); }); coins.forEach(function(c){ if(!c.collected) drawCoin(c); }); drawParticles(); }
function drawPlayer(){ ctx.save(); ctx.translate(player.x,player.y); var bob=player.onGround?Math.sin(player.runPhase)*3:0; if(player.onGround){ ctx.fillStyle='#ef4444'; ctx.beginPath(); ctx.arc(0,player.h/2+bob,8,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#1e293b'; ctx.fillRect(-12,player.h/2-4,24,8); } ctx.fillStyle='#0f172a'; ctx.fillRect(-10,player.h/2-20,20,30); ctx.fillStyle='#fbbf24'; ctx.fillRect(-8,player.h/2-18,16,4); ctx.fillStyle='#ef4444'; ctx.beginPath(); ctx.arc(0,-player.h/2+8,12,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#fff'; ctx.fillRect(-4,-player.h/2+6,3,3); ctx.fillRect(2,-player.h/2+6,3,3); ctx.fillStyle='#fbbf24'; ctx.beginPath(); ctx.moveTo(-10,-player.h/2+4); ctx.lineTo(-18,-player.h/2+2); ctx.lineTo(-10,-player.h/2-2); ctx.closePath(); ctx.fill(); ctx.restore(); }
function drawObstacle(o){ ctx.save(); ctx.shadowColor='#ef4444'; ctx.shadowBlur=10; if(o.type==='spike'){ ctx.fillStyle='#94a3b8'; ctx.beginPath(); ctx.moveTo(o.x,o.y+o.h); ctx.lineTo(o.x+o.w/2,o.y); ctx.lineTo(o.x+o.w,o.y+o.h); ctx.closePath(); ctx.fill(); } else if(o.type==='box'){ ctx.fillStyle='#78350f'; ctx.fillRect(o.x,o.y,o.w,o.h); ctx.fillStyle='#f59e0b'; ctx.fillRect(o.x,o.y,o.w,6); } else { ctx.fillStyle='#1e293b'; ctx.fillRect(o.x,o.y,o.w,o.h); ctx.fillStyle='#ef4444'; ctx.fillRect(o.x+4,o.y+4,o.w-8,8); } ctx.restore(); }
function drawCoin(c){ ctx.save(); ctx.shadowColor='#fbbf24'; ctx.shadowBlur=15; ctx.fillStyle='#fbbf24'; ctx.beginPath(); ctx.arc(c.x,c.y,c.r,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#f59e0b'; ctx.beginPath(); ctx.arc(c.x,c.y,c.r-2,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#fbbf24'; ctx.font='bold 12px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText('$',c.x,c.y+1); ctx.restore(); }
function nextLevel(){ if(level>=10){ return winGame(); } levelTransitioning=true; isPaused=true; SFX.levelUp(); var next=level+1; showToast('🏁 LEVEL '+next+'!'); setTimeout(function(){ level=next; speed+=0.7; levelTarget+=300; resetLevel(); isPaused=false; levelTransitioning=false; },1800); }
function gameOver(reason){ isRunning=false; clearInterval(gameLoop); SFX.gameOver(); overlay.classList.remove('hidden'); overlay.innerHTML='<div class="level-badge">LEVEL '+level+'</div><h1 class="dead">💀 GAME OVER</h1><p>'+(reason||'Coba lagi!')+'</p><p>Skor:</p><div class="final-score">'+score+'</div><p style="font-size:12px;color:#94a3b8;">Jarak: '+Math.floor(distance)+'m</p><button id="restartBtn" type="button">🔄 MAIN LAGI</button>'; document.getElementById('restartBtn').addEventListener('click',initGame); saveScore(score); }
function winGame(){ isRunning=false; clearInterval(gameLoop); SFX.win(); overlay.classList.remove('hidden'); overlay.innerHTML='<div class="level-badge">🏆 SEMUA LEVEL SELESAI</div><h1 class="win">🏆 YOU WIN!</h1><p>Kamu menyelesaikan 10 level!</p><div class="final-score">'+score+'</div><p style="font-size:12px;color:#94a3b8;">Jarak: '+Math.floor(distance)+'m</p><button id="restartBtn" type="button">🔄 MAIN LAGI</button>'; document.getElementById('restartBtn').addEventListener('click',initGame); saveScore(score); }
function saveScore(s){ if(s<=0) return; fetch('/api/scores',{ method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({slug:'ninja-runner',score:s}) }).then(function(r){return r.json();}).then(function(data){ if(data.status==='guest'){ showGuestNotice(s); } }).catch(function(){}); }
function showGuestNotice(s){ var n=document.createElement('div'); n.style.cssText='position:fixed; top:20px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg,#f59e0b,#ef4444); color:#fff; padding:14px 24px; border-radius:12px; font-size:14px; font-weight:600; z-index:10000;'; n.innerHTML='Login untuk simpan skor <strong>'+s+'</strong>! <a href="/login" style="color:#fff; text-decoration:underline;">Login</a>'; document.body.appendChild(n); setTimeout(function(){ n.remove(); },6000); }
function jump(){ if(!isRunning||isPaused||levelTransitioning) return; if(player.jumps<player.maxJumps){ player.vy=-14; player.jumps++; player.onGround=false; if(player.jumps===1) SFX.jump(); else SFX.doubleJump(); spawnParticles(player.x,player.y+player.h,'#22d3ee',8); } }
document.addEventListener('keydown',function(e){ var k=e.key.toLowerCase(); if(k===' '||k==='spacebar'||k==='arrowup'||k==='w'){ e.preventDefault(); if(!isRunning) initGame(); else jump(); } if(k==='p'&&isRunning){ isPaused=!isPaused; } });
canvas.addEventListener('touchstart',function(e){ e.preventDefault(); if(!isRunning) initGame(); else jump(); },{passive:false});
canvas.addEventListener('click',function(e){ if(!isRunning) initGame(); else jump(); });
document.getElementById('btnJump').addEventListener('click',function(e){ e.preventDefault(); jump(); });
startBtn.addEventListener('click',initGame);
fitCanvas();
</script>
</body>
</html>
"""

# Tulis file
(BASE / "space-shooter" / "space-shooter.html").write_text(SPACE_SHOOTER, encoding='utf-8')
(BASE / "ninja-runner" / "ninja-runner.html").write_text(NINJA_RUNNER, encoding='utf-8')
print("File game berhasil ditulis!")
