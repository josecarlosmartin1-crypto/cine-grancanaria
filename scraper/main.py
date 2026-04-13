import cloudscraper
import json
import re
import os
import sys
import datetime
from bs4 import BeautifulSoup

# Forzamos encoding UTF-8 para consola en Windows si es necesario
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuración TMDb
TMDB_API_KEY = "f93979c3b2100a4a37b08d7c1228f32c"
CACHE_FILE = "scraper/tmdb_cache.json"
TMDB_CACHE = {} 
GENRE_MAP = {} # ID -> Nombre

def load_cache():
    """Carga la memoria histórica de TMDb desde el archivo JSON."""
    global TMDB_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                TMDB_CACHE = json.load(f)
            print(f"  -> Memoria histórica cargada ({len(TMDB_CACHE)} películas recordadas).")
        except Exception as e:
            print(f"     Error cargando caché: {e}")
            TMDB_CACHE = {}
    else:
        print("  -> Iniciando memoria nueva (sin historial previo).")

def save_cache():
    """Guarda la memoria actualizada en el archivo JSON."""
    try:
        # Aseguramos que la carpeta exista
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(TMDB_CACHE, f, indent=2, ensure_ascii=False)
        print(f"  -> Memoria actualizada y guardada en {CACHE_FILE}.")
    except Exception as e:
        print(f"     Error guardando caché: {e}")

def get_tmdb_genres():
    """Descarga la lista maestra de géneros de TMDb al inicio."""
    global GENRE_MAP
    print("  -> Obteniendo catálogo de géneros de TMDb...")
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": TMDB_API_KEY, "language": "es-ES"}
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(url, params=params, timeout=10)
        if res.status_code == 200:
            genres_list = res.json().get("genres", [])
            GENRE_MAP = {g["id"]: g["name"] for g in genres_list}
            print(f"     Catálogo de géneros cargado ({len(GENRE_MAP)} categorías).")
    except Exception as e:
        print(f"     Error cargando géneros: {e}")

def get_movie_tmdb_info(title, fallback_summary=""):
    """Busca nota, poster, resumen y géneros en TMDb con caché persistente."""
    clean_title = re.sub(r'\(.*?\)', '', title).strip()
    clean_title = clean_title.replace("¡", "").replace("!", "")
    
    if clean_title in TMDB_CACHE:
        # Si ya la conocemos, no preguntamos a internet
        return TMDB_CACHE[clean_title]
    
    print(f"  -> Consultando TMDb (NUEVA): {clean_title}...")
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": clean_title, "language": "es-ES"}
    
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(url, params=params, timeout=10)
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                movie = results[0]
                genre_ids = movie.get("genre_ids", [])
                genres = [GENRE_MAP.get(gid) for gid in genre_ids if GENRE_MAP.get(gid)][:3]
                
                info = {
                    "rating": round(movie.get("vote_average", 0), 1),
                    "poster": f"https://image.tmdb.org/t/p/w342{movie.get('poster_path')}" if movie.get("poster_path") else None,
                    "summary": movie.get("overview", fallback_summary) or fallback_summary,
                    "genres": genres
                }
                TMDB_CACHE[clean_title] = info
                return info
    except Exception as e:
        print(f"    Error TMDb: {e}")
    
    # Si falla la búsqueda, devolvemos un objeto vacío con el resumen original si existe
    fallback = {"rating": 0, "poster": None, "summary": fallback_summary, "genres": []}
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
                            info = get_movie_tmdb_info(title, m.get("Synopsis", ""))
                            times = sorted(list(set([s.get("Time", "") for f in m.get("Formats", []) for s in f.get("Showtimes", []) if s.get("Time")])))
                            for t in times:
                                results[target].append({
                                    "title": title, "time": t, "rating": info["rating"],
                                    "poster": info["poster"], "summary": info["summary"], "genres": info["genres"]
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
                info = get_movie_tmdb_info(title, (peli2.get("pel2_sinopsis") if isinstance(peli2, dict) else "") or "")
                for s in m.get("Planificacions", []):
                    if today and s.get("plan_data") == today:
                        time_val = s.get("plan_horainici", "")
                        if time_val:
                            results["Ocine Premium Siete Palmas"].append({
                                "title": title, "time": ":".join(time_val.split(":")[:2]),
                                "rating": info["rating"], "poster": info["poster"], "summary": info["summary"], "genres": info["genres"]
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
                    clean_alt = re.sub(r'\(.*?\)', '', alt).strip().title()
                    # Evitamos procesar la misma película dos veces si tiene varias imágenes
                    if any(m["title"] == clean_alt for m in results["Artesiete Las Terrazas"]):
                        continue

                    # Buscamos el contenedor raíz de la película (el grid)
                    card = None
                    tp = img.parent
                    while tp and tp.name != 'body':
                        if tp.name == 'div' and 'grid' in tp.get('class', []):
                            card = tp
                            break
                        tp = tp.parent
                    
                    if card:
                        # 1. ¿Es venta anticipada?
                        if card.find(string=re.compile(r'\d{2}/\d{2}/2\d{3}')):
                            continue
                            
                        # 2. Localizar el ID de HOY (evitando IDs fijos/rotativos)
                        today_str = datetime.date.today().strftime("%d/%m")
                        today_tab = card.select_one(f'a[mostrar*="/{today_str}"], a:-soup-contains("{today_str}")')
                        
                        target_id = "0" # Fallback
                        if today_tab:
                            target_id = today_tab.get('id', '0')
                        
                        # 3. ¿Tiene sesiones para ese ID?
                        day_div = card.find('div', id=target_id)
                        if day_div:
                            times = day_div.find_all(string=re.compile(r'\b\d{1,2}:\d{2}\b'))
                            if times:
                                info = get_movie_tmdb_info(clean_alt)
                                movie_times = sorted(list(set([ti.strip() for ti in times if ":" in ti])))
                                for t in movie_times:
                                    results["Artesiete Las Terrazas"].append({
                                        "title": clean_alt, "time": t, "rating": info["rating"],
                                        "poster": info["poster"], "summary": info["summary"], "genres": info["genres"]
                                    })
    except Exception as e: print(f"  Error Artesiete: {e}")
    return results

def main():
    load_cache() # 1. Cargamos memoria histórica
    get_tmdb_genres() # 2. Cargamos catálogo de géneros
    all_data = {}
    all_data.update(scrape_yelmo_api())
    all_data.update(scrape_ocine_api())
    all_data.update(scrape_artesiete())
    with open("src/data.js", "w", encoding="utf-8") as f:
        f.write(f"export const MOVIE_DATA = {json.dumps(all_data, indent=2, ensure_ascii=False)};\n")
        f.write("export const movieData = MOVIE_DATA;\nexport const cinemas = Object.keys(MOVIE_DATA);\n")
    save_cache() # 3. Guardamos la memoria actualizada
    print("\nActualizacion completada con memoria persistente.")

if __name__ == "__main__":
    main()
