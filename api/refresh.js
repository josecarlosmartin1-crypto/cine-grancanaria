const TMDB_API_KEY = "f93979c3b2100a4a37b08d7c1228f32c";
const MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
];

function getCanaryToday() {
    const parts = new Intl.DateTimeFormat("en-CA", {
        timeZone: "Atlantic/Canary",
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
    }).formatToParts(new Date());
    const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
    return {
        iso: `${map.year}-${map.month}-${map.day}`,
        day: Number(map.day),
        day2: map.day,
        month: Number(map.month),
        month2: map.month
    };
}

function toTitleCase(str) {
    return (str || "")
        .toLowerCase()
        .replace(/(^|\s|[(-])(\S)/g, (_, p1, p2) => p1 + p2.toUpperCase());
}

async function fetchJson(url, options = {}, timeoutMs = 15000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await fetch(url, { ...options, signal: controller.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } finally {
        clearTimeout(timer);
    }
}

async function createTmdbResolver() {
    let genreMap = {};
    try {
        const gData = await fetchJson(
            `https://api.themoviedb.org/3/genre/movie/list?api_key=${TMDB_API_KEY}&language=es-ES`,
            {},
            8000
        );
        for (const g of gData.genres || []) {
            genreMap[g.id] = g.name;
        }
    } catch {
        // Si falla la carga de géneros, continuamos sin ellos
    }

    const cache = new Map();

    return function resolveMovie(title, fallbackSummary = "") {
        const cleanTitle = title.replace(/\(.*?\)/g, "").replace(/[¡!]/g, "").trim();
        if (cache.has(cleanTitle)) return cache.get(cleanTitle);

        const promise = (async () => {
            try {
                const url = `https://api.themoviedb.org/3/search/movie?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(cleanTitle)}&language=es-ES`;
                const data = await fetchJson(url, {}, 8000);
                const movie = (data.results || [])[0];
                if (movie) {
                    const genres = (movie.genre_ids || [])
                        .map((id) => genreMap[id])
                        .filter(Boolean)
                        .slice(0, 3);
                    return {
                        rating: Math.round((movie.vote_average || 0) * 10) / 10,
                        poster: movie.poster_path ? `https://image.tmdb.org/t/p/w342${movie.poster_path}` : null,
                        summary: movie.overview || fallbackSummary || "",
                        genres
                    };
                }
            } catch {
                // Fallback si falla TMDb
            }
            return { rating: 0, poster: null, summary: fallbackSummary || "", genres: [] };
        })();

        cache.set(cleanTitle, promise);
        return promise;
    };
}

async function scrapeYelmo(today, resolveMovie) {
    const results = {
        "Cine Yelmo Vecindario": [],
        "Cine Yelmo Las Arenas": [],
        "Cine Yelmo Premium Alisios": []
    };
    const baseUrl = "https://yelmocines.es";
    const warmupUrl = `${baseUrl}/cartelera/las-palmas/las-arenas`;
    const todayCandidates = new Set([
        `${today.day2} ${MESES[today.month - 1]}`,
        `${today.day} ${MESES[today.month - 1]}`
    ]);

    try {
        const warmRes = await fetch(warmupUrl, {
            headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" }
        });
        const setCookies = typeof warmRes.headers.getSetCookie === "function"
            ? warmRes.headers.getSetCookie()
            : (warmRes.headers.get("set-cookie") ? [warmRes.headers.get("set-cookie")] : []);
        const cookieHeader = setCookies
            .map((c) => c.split(";")[0].trim())
            .filter(Boolean)
            .join("; ");

        const data = await fetchJson(`${baseUrl}/now-playing.aspx/GetNowPlaying`, {
            method: "POST",
            headers: {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": baseUrl,
                "Referer": warmupUrl,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ...(cookieHeader ? { Cookie: cookieHeader } : {})
            },
            body: JSON.stringify({ cityKey: "las-palmas" })
        });

        for (const c of data?.d?.Cinemas || []) {
            const name = c.Name || "";
            let target = null;
            if (name.includes("Vecindario")) target = "Cine Yelmo Vecindario";
            else if (name.includes("Las Arenas")) target = "Cine Yelmo Las Arenas";
            else if (name.includes("Alisios")) target = "Cine Yelmo Premium Alisios";
            if (!target) continue;

            const dates = c.Dates || [];
            const dateObj = dates.find((d) => todayCandidates.has((d.ShowtimeDate || "").trim().toLowerCase())) || dates[0];
            if (!dateObj) continue;

            const movies = dateObj.Movies || [];
            const resolved = await Promise.all(
                movies.map(async (m) => {
                    const title = toTitleCase((m.Title || "").trim());
                    const info = await resolveMovie(title, m.Synopsis || "");
                    const timeSet = new Set();
                    for (const f of m.Formats || []) {
                        for (const s of f.Showtimes || []) {
                            if (s.Time) timeSet.add(s.Time);
                        }
                    }
                    return { title, info, times: [...timeSet].sort() };
                })
            );

            for (const { title, info, times } of resolved) {
                for (const time of times) {
                    results[target].push({ title, time, ...info });
                }
            }
        }
    } catch {
        // Devolvemos vacío si Yelmo falla; el cliente conserva sus datos previos
    }
    return results;
}

async function scrapeOcine(today, resolveMovie) {
    const results = { "Ocine Premium Siete Palmas": [] };
    const baseApi = "https://tickets.ocinepremium7palmas.es/api/v1";
    const urlWeb = "https://tickets.ocinepremium7palmas.es/?nocap=1";
    const headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://tickets.ocinepremium7palmas.es",
        "Referer": "https://tickets.ocinepremium7palmas.es/"
    };

    try {
        const initData = await fetchJson(`${baseApi}/init`, {
            method: "POST",
            headers,
            body: JSON.stringify({ idioma: "es", plan: "", app: "", cli: "", urlWeb, nomesbar: "N" })
        });
        const token = initData.token || "";

        const sessData = await fetchJson(`${baseApi}/sessions`, {
            method: "POST",
            headers,
            body: JSON.stringify({ token, idioma: "es", urlWeb })
        });

        const pelicules = sessData.pelicules || [];
        const details = await Promise.all(
            pelicules.map(async (p) => {
                if (!p.id) return null;
                try {
                    const det = await fetchJson(`${baseApi}/pelicula/${p.id}?lang=es`, { headers });
                    return { p, det };
                } catch {
                    return null;
                }
            })
        );

        const entries = [];
        const availableDates = new Set();

        for (const item of details) {
            if (!item) continue;
            const { p, det } = item;
            const title = toTitleCase((det.titol || p.titol || "").trim());
            if (!title) continue;
            const synopsis = (det.sinopsis || p.sinopsis || "").trim();
            const rawSessions = [...(det.sessions || [])];
            for (const sub of det.subPelicules || []) {
                rawSessions.push(...(sub.sessions || []));
            }
            for (const s of rawSessions) {
                const sDate = (s.data || "").trim();
                const sTime = (s.hora || "").trim();
                if (sDate && sTime) {
                    availableDates.add(sDate);
                    entries.push({ title, synopsis, sDate, sTime: sTime.split(":").slice(0, 2).join(":") });
                }
            }
        }

        const sortedDates = [...availableDates].sort();
        const targetDate = sortedDates.find((d) => d >= today.iso);
        if (!targetDate) return results;

        const seen = new Set();
        const uniqueToday = [];
        for (const e of entries) {
            if (e.sDate !== targetDate) continue;
            const key = `${e.title}|${e.sTime}`;
            if (seen.has(key)) continue;
            seen.add(key);
            uniqueToday.push(e);
        }

        const resolvedInfos = await Promise.all(
            uniqueToday.map((e) => resolveMovie(e.title, e.synopsis))
        );

        uniqueToday.forEach((e, idx) => {
            results["Ocine Premium Siete Palmas"].push({
                title: e.title,
                time: e.sTime,
                ...resolvedInfos[idx]
            });
        });
    } catch {
        // Devolvemos vacío si Ocine falla
    }
    return results;
}

async function scrapeArtesiete(today, resolveMovie) {
    const results = { "Artesiete Las Terrazas": [] };
    const url = "https://terrazas.artesiete.es/Cine/1/ARTESIETE%20Las%20Terrazas/Total";
    const todayStr = `${today.day2}/${today.month2}`;

    try {
        const res = await fetch(url, {
            headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" }
        });
        if (!res.ok) return results;
        const html = await res.text();

        // Dividimos por tarjetas principales usando los bloques con posters
        const blocks = html.split(/(?=<div[^>]*class="[^"]*\bgrid\b[^"]*")/i);
        const seenTitles = new Set();
        const candidates = [];

        for (const block of blocks) {
            const imgMatch = block.match(/<img[^>]*src="[^"]*posters[^"]*"[^>]*alt="([^"]+)"/i)
                || block.match(/<img[^>]*alt="([^"]+)"[^>]*src="[^"]*posters[^"]*"/i);
            if (!imgMatch) continue;

            const cleanAlt = toTitleCase(imgMatch[1].replace(/\(.*?\)/g, "").trim());
            if (!cleanAlt || seenTitles.has(cleanAlt)) continue;
            seenTitles.add(cleanAlt);

            // Descartar venta anticipada
            if (/\d{2}\/\d{2}\/2\d{3}/.test(block)) continue;

            // Localizar el ID del tab de hoy
            const escapedToday = todayStr.replace("/", "\\/");
            const tabMatch = block.match(new RegExp(`<a[^>]*id="([^"]+)"[^>]*mostrar="[^"]*\\/${escapedToday}[^"]*"`, "i"))
                || block.match(new RegExp(`<a[^>]*mostrar="[^"]*\\/${escapedToday}[^"]*"[^>]*id="([^"]+)"`, "i"))
                || block.match(new RegExp(`<a[^>]*id="([^"]+)"[^>]*>[^<]*${escapedToday}`, "i"));
            const targetId = tabMatch ? tabMatch[1] : "0";

            const dayDivRegex = new RegExp(`<div[^>]*id="${targetId}"[^>]*>([\\s\\S]*?)<\\/div>`, "i");
            const dayDivMatch = block.match(dayDivRegex);
            if (!dayDivMatch) continue;

            const timeMatches = dayDivMatch[1].match(/\b\d{1,2}:\d{2}\b/g);
            if (!timeMatches || timeMatches.length === 0) continue;

            const times = [...new Set(timeMatches)].sort();
            candidates.push({ title: cleanAlt, times });
        }

        const resolvedInfos = await Promise.all(candidates.map((c) => resolveMovie(c.title)));
        candidates.forEach((c, idx) => {
            for (const time of c.times) {
                results["Artesiete Las Terrazas"].push({
                    title: c.title,
                    time,
                    ...resolvedInfos[idx]
                });
            }
        });
    } catch {
        // Devolvemos vacío si Artesiete falla
    }
    return results;
}

export default async function handler(req, res) {
    if (req.method !== "GET" && req.method !== "POST") {
        res.status(405).json({ error: "Method not allowed" });
        return;
    }

    try {
        const today = getCanaryToday();
        const resolveMovie = await createTmdbResolver();

        const [yelmo, ocine, artesiete] = await Promise.all([
            scrapeYelmo(today, resolveMovie),
            scrapeOcine(today, resolveMovie),
            scrapeArtesiete(today, resolveMovie)
        ]);

        const movieData = {
            ...yelmo,
            ...artesiete,
            ...ocine
        };

        res.setHeader("Cache-Control", "no-store, max-age=0");
        res.status(200).json({
            updatedAt: today.iso,
            movieData
        });
    } catch (err) {
        res.status(500).json({ error: err.message || "Error actualizando cartelera" });
    }
}
