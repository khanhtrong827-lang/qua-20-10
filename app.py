from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit
import json
import mimetypes
import socket
import threading
import webbrowser


# ==========================================
# 1. THAY ĐỔI NỘI DUNG TẠI ĐÂY
# ==========================================

TEN_NGUOI_NHAN = "Sùng Thị Thảo "
TEN_NGUOI_GUI = "Và Trọng Khánh"

TIEU_DE = "Một ngày dịu dàng dành cho chị"

LOI_CHUC = (
    "Chúc chị có một ngày 20/10 thật hạnh phúc, "
    "luôn rạng rỡ, bình an và được yêu thương thật nhiều."
)

LOI_NHAN = (
    "Gửi chị một chút dịu dàng giữa cuộc sống bận rộn. "
    "Mong những điều tốt đẹp sẽ luôn tìm đến chị, "
    "những ước mơ sẽ dần thành hiện thực và nụ cười "
    "sẽ luôn ở trên môi. Chúc chị một ngày thật đáng nhớ! 💗"
    "Chúc chị thành công trên con đường mà mình chọn"
    "Mong cuộc sống của chị luôn rực rỡ và suôn sẻ "
     "Mong những áp lực không tìm đến chị và gặp nhiều may mắn hơn"
)

# Các câu chú thích chạy chữ. Chạm màn hình để đi tiếp.
# Dùng {ten} để chèn tên người nhận.
CHU_THICH = [
    ("💌", "Có một điều bất ngờ nhỏ đang chờ {ten}..."),
    ("🌷", "Hôm nay là 20/10, ngày của những người phụ nữ tuyệt vời nhất."),
    ("☁️", "Và em có một bài hát muốn gửi tặng chị : Mây."),
    ("🍀", " Em tặng chị ngọn cỏ 4 lá này nè, chúc chị thật nhiều may mắn!"),
    ("🌸", "Cảm ơn chị vì đã luôn dịu dàng và ở bên em một thời gian."),
    ("💗", "Giờ thì, mời chị bước vào khu vườn nhỏ này nhé!"),
]

# Đặt file nhạc cùng thư mục với file .py này (tự tải bài "Mây - H2K" về).
FILE_NHAC = "Noi nay co anh 2.mp3"

CONG = 8000


# ==========================================
# 2. GIAO DIỆN WEBSITE
# ==========================================

HTML = Template(r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="theme-color" content="#ffe4ef">
    <title>$title</title>

    <style>
        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        html, body {
            touch-action: manipulation;
        }

        body {
            margin: 0;
            min-height: 100vh;
            min-height: 100dvh;
            overflow-x: hidden;
            font-family: "Segoe UI", Arial, sans-serif;
            text-align: center;
            color: #81415e;
            background:
                radial-gradient(ellipse at 15% 10%, white 0%, transparent 38%),
                linear-gradient(145deg, #ffe3ed, #fff2f7 45%, #f9e3ff);
        }

        body.khoa {
            overflow: hidden;
            height: 100dvh;
        }

        header { padding: 35px 18px 10px; }

        .eyebrow {
            font-size: 12px;
            letter-spacing: 3px;
            color: #b95b88;
        }

        h1 {
            max-width: 800px;
            margin: 18px auto;
            font-size: clamp(28px, 5vw, 48px);
            color: #d64f89;
        }

        .intro {
            max-width: 600px;
            margin: auto;
            line-height: 1.8;
        }

        .scene {
            width: min(90%, 400px);
            margin: 30px auto 45px;
            perspective: 1200px;
        }

        .card {
            padding: 18px 18px 26px;
            border: 1px solid white;
            border-radius: 28px;
            background: rgba(255, 255, 255, .88);
            box-shadow: 0 25px 65px #b94f7d25;
            transition: transform .15s ease-out;
        }

        .badge {
            display: inline-block;
            padding: 8px 14px;
            border-radius: 30px;
            background: #ffe3ef;
            font-size: 13px;
        }

        .flowers {
            display: grid;
            place-items: center;
            min-height: 210px;
            margin-top: 18px;
            border-radius: 22px;
            font-size: clamp(60px, 15vw, 88px);
            background: linear-gradient(145deg, #ffe0ed, #fff5fa, #f0dcff);
        }

        h2, h3 { color: #d64f89; }

        p {
            line-height: 1.9;
            overflow-wrap: anywhere;
        }

        button {
            margin: 10px 0;
            padding: 14px 22px;
            border: 0;
            border-radius: 30px;
            color: white;
            font-size: 15px;
            cursor: pointer;
            background: linear-gradient(135deg, #f58bb6, #ce66b8);
            box-shadow: 0 8px 22px #d55a9640;
        }

        button:focus-visible {
            outline: 3px solid #bd477b;
            outline-offset: 4px;
        }

        .letter {
            margin-top: 18px;
            padding: 18px;
            border: 1px solid #ffd5e7;
            border-radius: 20px;
            background: #fff0f6;
        }

        .signature {
            font-style: italic;
            color: #c34e81;
        }

        .gallery {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 20px;
            width: min(92%, 950px);
            margin: 25px auto 45px;
        }

        .photo-card {
            padding: 25px 15px;
            border-radius: 22px;
            background: #ffffffcc;
            box-shadow: 0 15px 35px #b94f7d20;
        }

        .flower-icon { font-size: 70px; }

        footer { padding: 20px 15px 35px; }

        .heart {
            position: fixed;
            bottom: -50px;
            z-index: 55;
            pointer-events: none;
            user-select: none;
            animation: float-up 7s linear forwards;
        }

        @keyframes float-up {
            0%   { transform: translateY(0); opacity: 0; }
            10%  { opacity: .9; }
            100% { transform: translateY(-115vh) rotate(300deg); opacity: 0; }
        }

        /* ---------- MÀN HÌNH CHÚ THÍCH (chạm để tiếp) ---------- */
        #story {
            position: fixed;
            inset: 0;
            z-index: 50;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
            cursor: pointer;
            user-select: none;
            -webkit-user-select: none;
            transition: opacity .8s ease;
            background:
                radial-gradient(ellipse at 20% 10%, white 0%, transparent 40%),
                linear-gradient(145deg, #ffe0ec, #fff1f7 50%, #f3dcff);
        }

        #story.an {
            opacity: 0;
            pointer-events: none;
        }

        .big {
            font-size: clamp(76px, 24vw, 120px);
            line-height: 1;
        }

        .big.pop { animation: pop .6s ease; }

        @keyframes pop {
            0%   { transform: scale(.3) rotate(-15deg); opacity: 0; }
            70%  { transform: scale(1.15) rotate(4deg); opacity: 1; }
            100% { transform: scale(1) rotate(0); }
        }

        .bubble {
            width: min(100%, 420px);
            min-height: 150px;
            margin-top: 26px;
            padding: 22px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 24px;
            font-size: 18px;
            line-height: 1.8;
            background: rgba(255, 255, 255, .92);
            box-shadow: 0 20px 50px #b94f7d28;
        }

        .hint {
            margin-top: 20px;
            font-size: 14px;
            color: #b95b88;
            animation: blink 1.4s ease-in-out infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: .4; }
            50%      { opacity: 1; }
        }

        .dots {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }

        .dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #f3bcd3;
            transition: .3s;
        }

        .dots span.on {
            width: 22px;
            border-radius: 8px;
            background: #d64f89;
        }

        /* ---------- HIỆU ỨNG LẤP LÁNH ---------- */
        .sparkle {
            position: absolute;
            pointer-events: none;
            color: #e58ab4;
            animation: twinkle 2.5s ease-in-out infinite;
        }

        @keyframes twinkle {
            0%, 100% { opacity: .15; transform: scale(.6); }
            50%      { opacity: 1; transform: scale(1.2) rotate(20deg); }
        }

        .pt {
            position: fixed;
            z-index: 70;
            pointer-events: none;
            font-size: 20px;
            animation: burst 1s ease-out forwards;
        }

        @keyframes burst {
            0%   { transform: translate(0, 0) scale(.4); opacity: 1; }
            100% { transform: translate(var(--dx), var(--dy)) scale(1.1) rotate(180deg); opacity: 0; }
        }

        .confetti {
            position: fixed;
            top: -40px;
            z-index: 70;
            pointer-events: none;
            animation: fall linear forwards;
        }

        @keyframes fall {
            to { transform: translateY(115vh) rotate(720deg); }
        }

        .big.glow { filter: drop-shadow(0 0 18px #6fcf7f); }

        /* ---------- NÚT NHẠC ---------- */
        #musicBtn {
            position: fixed;
            top: max(14px, env(safe-area-inset-top));
            right: 14px;
            z-index: 60;
            width: 46px;
            height: 46px;
            margin: 0;
            padding: 0;
            font-size: 20px;
            display: none;
        }

        #musicBtn.hien { display: block; }

        @media (max-width: 650px) {
            .gallery {
                grid-template-columns: 1fr;
                max-width: 380px;
            }
            .eyebrow { letter-spacing: 1px; }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation: none !important;
                transition: none !important;
            }
        }
    </style>
</head>

<body class="khoa">
    <audio id="bgm" src="/nhac" loop preload="auto" playsinline></audio>

    <button id="musicBtn" type="button" aria-label="Bật hoặc tắt nhạc">🔇</button>

    <!-- Màn hình chú thích: chạm bất kỳ đâu để đi tiếp -->
    <div id="story" role="button" tabindex="0"
         aria-label="Chạm để đi tiếp">
        <div id="sparkles" aria-hidden="true"></div>
        <div class="big" id="big">💌</div>
        <div class="bubble" id="bubble">Có một món quà nhỏ dành cho bạn</div>
        <div class="hint" id="hint">Chạm để mở quà 🎵</div>
        <div class="dots" id="dots" aria-hidden="true"></div>
    </div>

    <header>
        <p class="eyebrow">✿ 20 THÁNG 10 · NGÀY ĐẶC BIỆT ✿</p>
        <h1>$title</h1>
        <p class="intro">
            Một khu vườn nhỏ và một lời chúc chân thành
            dành riêng cho em. 🌷
        </p>
    </header>

    <main>
        <div class="scene">
            <section class="card" id="mainCard">
                <span class="badge">💌 Một món quà nhỏ</span>

                <div class="flowers" role="img"
                     aria-label="Những bông hoa dành tặng em">
                    🌷 💐 🌸
                </div>

                <h2>Gửi $receiver 💗</h2>

                <p>$wish</p>

                <button id="letterButton" type="button"
                        aria-expanded="false" aria-controls="letter">
                    🌸 Mở bức thư bí mật
                </button>

                <div class="letter" id="letter" hidden>
                    <h3>Gửi em bằng tất cả sự dịu dàng 💕</h3>
                    <p>$note</p>
                    <p class="signature">Thân gửi: $sender</p>
                    <div style="font-size:30px">🌷 💗 🌸 💖 🌷</div>
                </div>
            </section>
        </div>

        <h2>🌷 Khu vườn hoa mộng mơ</h2>

        <section class="gallery">
            <article class="photo-card">
                <div class="flower-icon" aria-hidden="true">🌹</div>
                <h3>Lời chúc</h3>
                <p>Một lời chúc chân thành dành cho em.</p>
            </article>

            <article class="photo-card">
                <div class="flower-icon" aria-hidden="true">🌻</div>
                <h3>Nắng và hoa</h3>
                <p>Mong mỗi ngày đều có niềm vui nhỏ.</p>
            </article>

            <article class="photo-card">
                <div class="flower-icon" aria-hidden="true">🌸</div>
                <h3>Dịu dàng</h3>
                <p>Mong điều tốt đẹp luôn ở bên em.</p>
            </article>
        </section>
    </main>

    <footer>
        <p>Được làm bằng Python và một chút yêu thương 💗</p>
        <strong>Chúc mừng ngày Phụ nữ Việt Nam 20/10!</strong>
    </footer>

    <script>
        const steps = $steps;

        const story  = document.getElementById("story");
        const big    = document.getElementById("big");
        const bubble = document.getElementById("bubble");
        const hint   = document.getElementById("hint");
        const dotsEl = document.getElementById("dots");
        const audio  = document.getElementById("bgm");
        const mbtn   = document.getElementById("musicBtn");
        const letter = document.getElementById("letter");
        const button = document.getElementById("letterButton");
        const card   = document.getElementById("mainCard");

        const motion = window.matchMedia("(prefers-reduced-motion: reduce)");

        /* ---------- Âm thanh hiệu ứng (tự tạo, không cần file) ---------- */
        let ac = null, sfxOn = true;

        function getAC() {
            if (!ac) {
                const AC = window.AudioContext || window.webkitAudioContext;
                if (AC) ac = new AC();
            }
            if (ac && ac.state === "suspended") ac.resume();
            return ac;
        }

        function tone(freq, start, dur, vol, type, force) {
            const c = getAC();
            if (!c || (!sfxOn && !force)) return;
            const o = c.createOscillator();
            const g = c.createGain();
            const t = c.currentTime + (start || 0);
            o.type = type || "sine";
            o.frequency.setValueAtTime(freq, t);
            g.gain.setValueAtTime(0.0001, t);
            g.gain.exponentialRampToValueAtTime(vol || 0.12, t + 0.01);
            g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
            o.connect(g);
            g.connect(c.destination);
            o.start(t);
            o.stop(t + dur + 0.05);
        }

        function sfxTap()    { tone(660, 0, .12, .12); tone(990, .06, .14, .10); }
        function sfxTick()   { tone(1200 + Math.random() * 400, 0, .04, .04, "triangle"); }
        function sfxMagic()  { [784, 988, 1175, 1568].forEach(function (f, k) { tone(f, k * .09, .35, .10); }); }
        function sfxFinish() { [523, 659, 784, 1047, 1319].forEach(function (f, k) { tone(f, k * .10, .5, .10); }); }

        /* ---------- Hiệu ứng hình ảnh ---------- */
        const sparkles = document.getElementById("sparkles");

        function makeSparkles() {
            const sym = ["✧", "✦", "✨", "♪", "♫", "❀"];
            for (let k = 0; k < 22; k++) {
                const s = document.createElement("span");
                s.className = "sparkle";
                s.textContent = sym[k % sym.length];
                s.style.left = Math.random() * 100 + "%";
                s.style.top = Math.random() * 100 + "%";
                s.style.fontSize = (12 + Math.random() * 18) + "px";
                s.style.animationDelay = (Math.random() * 2.5) + "s";
                sparkles.appendChild(s);
            }
        }

        function burst(x, y, icons, n) {
            if (motion.matches) return;
            for (let k = 0; k < n; k++) {
                const p = document.createElement("span");
                const a = Math.random() * Math.PI * 2;
                const d = 50 + Math.random() * 80;
                p.className = "pt";
                p.setAttribute("aria-hidden", "true");
                p.textContent = icons[Math.floor(Math.random() * icons.length)];
                p.style.left = x + "px";
                p.style.top = y + "px";
                p.style.setProperty("--dx", Math.cos(a) * d + "px");
                p.style.setProperty("--dy", Math.sin(a) * d + "px");
                document.body.appendChild(p);
                setTimeout(function () { p.remove(); }, 1000);
            }
        }

        function confetti() {
            if (motion.matches) return;
            const icons = ["🌸", "💗", "✨", "🍀", "🌷", "💖"];
            for (let k = 0; k < 40; k++) {
                const c = document.createElement("span");
                c.className = "confetti";
                c.setAttribute("aria-hidden", "true");
                c.textContent = icons[Math.floor(Math.random() * icons.length)];
                c.style.left = Math.random() * 100 + "vw";
                c.style.fontSize = (16 + Math.random() * 16) + "px";
                c.style.animationDuration = (2.5 + Math.random() * 2.5) + "s";
                c.style.animationDelay = (Math.random() * 0.8) + "s";
                document.body.appendChild(c);
                setTimeout(function () { c.remove(); }, 6500);
            }
        }

        makeSparkles();

        /* ---------- Chú thích chạy chữ ---------- */
        let index = -1, timer = null, typing = false, fullText = "";

        steps.forEach(function () {
            dotsEl.appendChild(document.createElement("span"));
        });

        function updateDots() {
            Array.from(dotsEl.children).forEach(function (d, k) {
                d.className = k === index ? "on" : "";
            });
        }

        function finishTyping() {
            clearInterval(timer);
            typing = false;
            bubble.textContent = fullText;
            hint.style.visibility = "visible";
            hint.textContent = index >= steps.length - 1
                ? "Chạm để vào khu vườn 🌷"
                : "Chạm để tiếp tục ▾";
        }

        function typeText(text) {
            clearInterval(timer);
            const chars = Array.from(text);
            let n = 0;
            fullText = text;
            typing = true;
            bubble.textContent = "";
            hint.style.visibility = "hidden";

            timer = setInterval(function () {
                n++;
                bubble.textContent = chars.slice(0, n).join("");
                if (n % 2 === 0) sfxTick();
                if (n >= chars.length) finishTyping();
            }, 45);
        }

        function showStep(k) {
            index = k;
            big.textContent = steps[k][0];
            big.classList.remove("pop");
            void big.offsetWidth;
            big.classList.add("pop");
            updateDots();
            typeText(steps[k][1]);

            if (steps[k][0] === "🍀") {
                big.classList.add("glow");
                sfxMagic();
                burst(window.innerWidth / 2, window.innerHeight * 0.3,
                      ["✨", "🍀", "💚"], 14);
            } else {
                big.classList.remove("glow");
            }
        }

        function endStory() {
            confetti();
            sfxFinish();
            story.classList.add("an");
            document.body.classList.remove("khoa");
            window.scrollTo(0, 0);
            setTimeout(function () { story.remove(); }, 900);
        }

        function advance() {
            sfxTap();
            if (typing) { finishTyping(); return; }

            if (index === -1) {
                startMusic();          /* lần chạm đầu tiên = cho phép phát nhạc */
                showStep(0);
            } else if (index < steps.length - 1) {
                showStep(index + 1);
            } else {
                endStory();
            }
        }

        story.addEventListener("click", function (e) {
            burst(e.clientX, e.clientY, ["💗", "✨", "🌸"], 8);
            advance();
        });
        story.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                advance();
            }
        });

        /* ---------- Nhạc nền ---------- */
        let wasPlaying = false;
        let useSynth = false;      /* true = dùng nhạc có sẵn trong code */
        let musicWanted = false;
        let synthTimer = null, synthStep = 0;

        /* Giai điệu hộp nhạc dịu nhẹ (tự sáng tác, 32 nhịp, lặp vô hạn) */
        const MEL = [
            659, 784, 880, 784,  659, 587, 523, 0,
            587, 659, 784, 659,  587, 523, 587, 0,
            659, 784, 880, 1047, 880, 784, 659, 0,
            587, 659, 587, 523,  523, 0,   0,   0
        ];
        const BASS = [131, 110, 131, 98];

        function playSynthStep() {
            const m = MEL[synthStep % MEL.length];
            if (m) {
                tone(m, 0.02, 1.0, 0.09, "sine", true);
                tone(m * 2, 0.02, 0.5, 0.025, "triangle", true);
            }
            if (synthStep % 8 === 0) {
                tone(BASS[(synthStep / 8) % 4], 0, 3.2, 0.07, "triangle", true);
            }
            synthStep++;
        }

        function startSynth() {
            useSynth = true;
            if (!getAC()) return;
            if (synthTimer) return;
            playSynthStep();
            synthTimer = setInterval(playSynthStep, 400);
            mbtn.classList.add("hien");
            mbtn.textContent = "🔊";
        }

        function isPlaying() {
            return useSynth ? synthTimer !== null : !audio.paused;
        }

        function startMusic() {
            musicWanted = true;
            if (useSynth) { startSynth(); return; }
            audio.volume = 0.8;
            const p = audio.play();
            if (p && p.catch) {
                p.catch(function (err) {
                    /* Không có file may.mp3 -> dùng nhạc có sẵn */
                    if (!err || err.name !== "NotAllowedError") startSynth();
                });
            }
        }

        function pauseMusic() {
            if (useSynth) {
                clearInterval(synthTimer);
                synthTimer = null;
                mbtn.textContent = "🔇";
            } else {
                audio.pause();
            }
        }

        audio.addEventListener("play", function () {
            mbtn.classList.add("hien");
            mbtn.textContent = "🔊";
        });

        audio.addEventListener("pause", function () {
            mbtn.textContent = "🔇";
        });

        audio.addEventListener("error", function () {
            useSynth = true;                       /* chưa có file nhạc */
            if (musicWanted) startSynth();
        });

        mbtn.addEventListener("click", function (e) {
            e.stopPropagation();
            if (isPlaying()) { sfxOn = false; pauseMusic(); }
            else { sfxOn = true; startMusic(); }
        });

        document.addEventListener("visibilitychange", function () {
            if (document.hidden) {
                wasPlaying = isPlaying();
                if (wasPlaying) pauseMusic();
            } else if (wasPlaying) {
                startMusic();
                wasPlaying = false;
            }
        });

        /* ---------- Thư bí mật ---------- */
        button.addEventListener("click", function () {
            letter.hidden = !letter.hidden;
            const opened = !letter.hidden;

            button.setAttribute("aria-expanded", String(opened));
            button.textContent = opened
                ? "💌 Đóng bức thư"
                : "🌸 Mở bức thư bí mật";

            if (opened) {
                sfxMagic();
                confetti();
                letter.scrollIntoView({
                    behavior: motion.matches ? "auto" : "smooth",
                    block: "nearest"
                });
            }
        });

        /* ---------- Thẻ nghiêng theo chuột (chỉ máy tính) ---------- */
        card.addEventListener("pointermove", function (event) {
            if (event.pointerType !== "mouse" || motion.matches) return;

            const rect = card.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width - 0.5;
            const y = (event.clientY - rect.top) / rect.height - 0.5;

            card.style.transform =
                "rotateY(" + (x * 12) + "deg) rotateX(" + (-y * 10) + "deg)";
        });

        card.addEventListener("pointerleave", function () {
            card.style.transform = "rotateY(0deg) rotateX(0deg)";
        });

        /* ---------- Tim bay ---------- */
        function createHeart() {
            if (motion.matches || document.hidden) return;

            const heart = document.createElement("span");
            const icons = ["💗", "💕", "💖", "🌸", "🌷", "♪", "♫", "✨", "🍀"];

            heart.className = "heart";
            heart.setAttribute("aria-hidden", "true");
            heart.textContent = icons[Math.floor(Math.random() * icons.length)];
            heart.style.left = Math.random() * 100 + "vw";
            heart.style.fontSize = (15 + Math.random() * 19) + "px";

            document.body.appendChild(heart);
            setTimeout(function () { heart.remove(); }, 7500);
        }

        setInterval(createHeart, 900);
    </script>
</body>
</html>
""")

_BUOC = [
    [icon, text.format(ten=TEN_NGUOI_NHAN.strip())]
    for icon, text in CHU_THICH
]

TRANG_WEB = HTML.substitute(
    title=escape(TIEU_DE),
    receiver=escape(TEN_NGUOI_NHAN.strip()),
    sender=escape(TEN_NGUOI_GUI),
    wish=escape(LOI_CHUC),
    note=escape(LOI_NHAN),
    steps=json.dumps(_BUOC, ensure_ascii=False).replace("</", "<\\/"),
).encode("utf-8")


# ==========================================
# 3. XỬ LÝ YÊU CẦU TỪ TRÌNH DUYỆT
# ==========================================

THU_MUC = Path(__file__).resolve().parent
DUONG_DAN_NHAC = THU_MUC / FILE_NHAC


class WebsiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path

        if path in ("/", "/index.html"):
            self.gui_trang()
        elif path == "/nhac":
            self.gui_nhac()
        else:
            self.send_error(404, "Not Found")

    def gui_trang(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(TRANG_WEB)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(TRANG_WEB)

    def gui_nhac(self):
        """Gửi file nhạc, hỗ trợ Range (bắt buộc cho iPhone/Safari)."""
        if not DUONG_DAN_NHAC.is_file():
            self.send_error(404, "Chua co file nhac")
            return

        kich_thuoc = DUONG_DAN_NHAC.stat().st_size
        bat_dau, ket_thuc = 0, kich_thuoc - 1
        ma = 200

        range_header = self.headers.get("Range", "")
        if range_header.startswith("bytes="):
            try:
                a, b = range_header[6:].split(",")[0].split("-", 1)
                if a == "":
                    bat_dau = max(0, kich_thuoc - int(b))
                else:
                    bat_dau = int(a)
                    if b:
                        ket_thuc = min(int(b), kich_thuoc - 1)
                ma = 206
            except ValueError:
                bat_dau, ket_thuc, ma = 0, kich_thuoc - 1, 200

        if bat_dau > ket_thuc or bat_dau >= kich_thuoc:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{kich_thuoc}")
            self.end_headers()
            return

        do_dai = ket_thuc - bat_dau + 1
        loai = mimetypes.guess_type(DUONG_DAN_NHAC.name)[0] or "audio/mpeg"

        self.send_response(ma)
        self.send_header("Content-Type", loai)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(do_dai))
        if ma == 206:
            self.send_header(
                "Content-Range",
                f"bytes {bat_dau}-{ket_thuc}/{kich_thuoc}"
            )
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()

        try:
            with open(DUONG_DAN_NHAC, "rb") as f:
                f.seek(bat_dau)
                con_lai = do_dai
                while con_lai > 0:
                    data = f.read(min(64 * 1024, con_lai))
                    if not data:
                        break
                    self.wfile.write(data)
                    con_lai -= len(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # trình duyệt ngắt kết nối giữa chừng, bình thường

    def log_message(self, format, *args):
        pass  # tắt log cho gọn


def lay_ip_goi_y():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None


# ==========================================
# 4. KHỞI ĐỘNG WEBSITE
# ==========================================

def main():
    try:
        server = ThreadingHTTPServer(("0.0.0.0", CONG), WebsiteHandler)
    except OSError as error:
        print("KHÔNG THỂ KHỞI ĐỘNG WEBSITE.")
        print("Chi tiết:", error)
        print("Nếu cổng đang được dùng, hãy dừng chương trình cũ")
        print("hoặc đổi CONG = 5000 thành CONG = 8000.")
        return

    dia_chi_pc = f"http://127.0.0.1:{CONG}"
    ip = lay_ip_goi_y()

    print("=" * 55)
    print("WEBSITE ĐÃ KHỞI ĐỘNG")
    print("Mở trên PC:", dia_chi_pc)

    if ip:
        print(f"Địa chỉ cho điện thoại: http://{ip}:{CONG}")
        print("Nếu địa chỉ này không đúng, kiểm tra IPv4 bằng ipconfig.")
    else:
        print(f"Điện thoại: http://IP_CUA_PC:{CONG}")

    if DUONG_DAN_NHAC.is_file():
        print("Nhạc: đã tìm thấy", FILE_NHAC)
    else:
        print(f"Không có '{FILE_NHAC}': dùng nhạc hộp nhạc có sẵn trong trang.")
        print(f"(Muốn nghe bài thật, đặt '{FILE_NHAC}' cùng thư mục với file .py)")

    print("PC và điện thoại cần cùng mạng Wi-Fi.")
    print("Nếu điện thoại không vào được, cho phép Python qua Firewall.")
    print("Nhấn Ctrl+C trong Shell để dừng.")
    print("=" * 55)

    timer = threading.Timer(1.0, lambda: webbrowser.open(dia_chi_pc))
    timer.daemon = True
    timer.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng website.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()


