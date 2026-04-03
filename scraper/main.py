import cloudscraper
import json
import re
import os
import sys
from bs4 import BeautifulSoup

# Forzamos encoding UTF-8 para consola en Windows si es necesario
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuración TMDb
TMDB_API_KEY = "f93979c3b2100a4a37b08d7c1228f32c"
TMDB_CACHE = {}

def get_movie_tmdb_info(title, fallback_summary=""):
    """Busca nota, poster y resumen en TMDb con caché."""
    clean_title = re.sub(r'\(.*?\)', '', title).strip()
    clean_title = clean_title.replace("¡", "").replace("!", "")
    
    if clean_title in TMDB_CACHE:
        return TMDB_CACHE[clean_title]
    
    print(f"  -> Consultando TMDb: {clean_title}...")
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": clean_title,
        "language": "es-ES"
    }
    
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(url, params=params, timeout=10)
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                movie = results[0]
                info = {
                    "rating": round(movie.get("vote_average", 0), 1),
                    "poster": f"https://image.tmdb.org/t/p/w342{movie.get('poster_path')}" if movie.get("poster_path") else None,
                    "summary": movie.get("overview", fallback_summary) or fallback_summary
                }
                TMDB_CACHE[clean_title] = info
                return info
    except Exception as e:
        print(f"    Error TMDb: {e}")
    
    fallback = {"rating": 0, "poster": None, "summary": fallback_summary or "Ver detalles en web."}
    TMDB_CACHE[clean_title] = fallback
    return fallback

def scrape_yelmo_api():
    print("Obteniendo cartelera: Yelmo Cines...")
    url = "https://www.yelmocines.es/now-playing.aspx/GetNowPlaying"
    scraper = cloudscraper.create_scraper()
    headers = {"Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/json; charset=UTF-8", "X-Requested-With": "XMLHttpRequest"}
    payload = {"cityKey": "las-palmas"}
    results = {"Cine Yelmo Vecindario": [], "Cine Yelmo Las Arenas": [], "Cine Yelmo Premium Alisios": []}
    try:
        res = scraper.post(url, headers=headers, json=payload, timeout=20)
        if res.status_code == 200:
            for c in res.json().get("d", {}).get("Cinemas", []):
                name = c.get("Name", "")
                target = None
                if "Vecindario" in name: target = "Cine Yelmo Vecindario"
                elif "Las Arenas" in name: target = "Cine Yelmo Las Arenas"
                elif "Alisios" in name: target = "Cine Yelmo Premium Alisios"
                if target:
                    dates = c.get("Dates", [])
                    if dates:
                        for m in dates[0].get("Movies", []):
                            title = m.get("Title", "").title()
                            # El resumen de Yelmo a veces es muy corto o inexistente
                            yelmo_summary = m.get("Synopsis", "")[:150]
                            info = get_movie_tmdb_info(title, yelmo_summary)
                            times = sorted(list(set([s.get("Time", "") for f in m.get("Formats", []) for s in f.get("Showtimes", []) if s.get("Time")])))
                            for t in times:
                                results[target].append({
                                    "title": title, "time": t, "rating": info["rating"],
                                    "poster": info["poster"], "summary": info["summary"]
                                })
    except Exception as e: print(f"  Error Yelmo: {e}")
    return results

def scrape_ocine_api():
    print("Obteniendo cartelera: Ocine Siete Palmas...")
    url = "https://www.ocinepremium7palmas.es/components/com_cines/json/es_cartellera.json"
    scraper = cloudscraper.create_scraper()
    results = {"Ocine Premium Siete Palmas": []}
    try:
        res = scraper.get(url, timeout=20)
        if res.status_code == 200:
            data = res.json()
            today = data.get("date", "")
            for m in data.get("data", []):
                title = m.get("peli_titol", "").title()
                if not title: continue
                peli2 = m.get("Pelicules2", {})
                ocine_summary = (peli2.get("pel2_sinopsis") if isinstance(peli2, dict) else "") or ""
                info = get_movie_tmdb_info(title, ocine_summary)
                for s in m.get("Planificacions", []):
                    if today and s.get("plan_data") == today:
                        time_val = s.get("plan_horainici", "")
                        if time_val:
                            results["Ocine Premium Siete Palmas"].append({
                                "title": title, "time": ":".join(time_val.split(":")[:2]),
                                "rating": info["rating"], "poster": info["poster"], "summary": info["summary"]
                            })
    except Exception as e: print(f"  Error Ocine: {e}")
    return results

def scrape_artesiete():
    print("Obteniendo cartelera: Artesiete Las Terrazas...")
    url = "https://terrazas.artesiete.es/Cine/1/ARTESIETE%20Las%20Terrazas/Total"
    scraper = cloudscraper.create_scraper()
    results = {"Artesiete Las Terrazas": []}
    try:
        res = scraper.get(url, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for img in soup.find_all('img'):
                alt = img.get('alt', '')
                if 'posters' in img.get('src', '').lower() and alt:
                    parent = img.parent
                    while parent and parent.name != 'body':
                        if parent.name == 'div' and ('px-2' in parent.get('class', []) or 'relative' in parent.get('class', [])):
                            times = parent.find_all(string=re.compile(r'\b\d{1,2}:\d{2}\b'))
                            if times:
                                title = alt.title()
                                info = get_movie_tmdb_info(title, "Ver detalles en la web oficial.")
                                movie_times = sorted(list(set([ti.strip() for ti in times if ":" in ti])))
                                for t in movie_times:
                                    results["Artesiete Las Terrazas"].append({
                                        "title": title, "time": t, "rating": info["rating"],
                                        "poster": info["poster"], "summary": info["summary"]
                                    })
                                break
                        parent = parent.parent
    except Exception as e: print(f"  Error Artesiete: {e}")
    return results

def main():
    all_data = {}
    all_data.update(scrape_yelmo_api())
    all_data.update(scrape_ocine_api())
    all_data.update(scrape_artesiete())
    with open("src/data.js", "w", encoding="utf-8") as f:
        f.write(f"export const MOVIE_DATA = {json.dumps(all_data, indent=2, ensure_ascii=False)};\n")
        f.write("export const movieData = MOVIE_DATA;\nexport const cinemas = Object.keys(MOVIE_DATA);\n")
    print("\nActualizacion completada exitosamente con Sinopsis reales.")

if __name__ == "__main__":
    main()
