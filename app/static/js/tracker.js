// tracker.js
console.log("Professional Python + Rust Traffic Tracking Initialized.");

(function() {
    const TRACKING_ENDPOINT = "https://api.domainanda.com/track/click"; // Sesuaikan dengan endpoint backend Rust/Python Anda

    document.addEventListener("click", function(event) {
        const link = event.target.closest("a");
        if (!link) return;

        const href = link.getAttribute("href");
        if (!href) return;

        // Cek jika tautan mengarah keluar atau ke target tertentu (misal: Instagram)
        if (href.includes("instagram.com") || href.startsWith("http")) {
            const trackingData = JSON.stringify({
                url: href,
                timestamp: new Date().toISOString(),
                referrer: document.referrer || window.location.href,
                userAgent: navigator.userAgent
            });

            // Menggunakan sendBeacon agar data tetap terkirim meskipun halaman berpindah
            if (navigator.sendBeacon) {
                navigator.sendBeacon(TRACKING_ENDPOINT, trackingData);
            } else {
                fetch(TRACKING_ENDPOINT, {
                    method: "POST",
                    body: trackingData,
                    headers: { "Content-Type": "application/json" },
                    keepalive: true
                }).catch(() => {});
            }
        }
    });
})();