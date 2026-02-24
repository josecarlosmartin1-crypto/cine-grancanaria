import cloudscraper
import json
import re
import os

CINEMAS = [
    {"name": "Artesiete Las Terrazas", "url": "https://artesiete.es/Cine/14/ARTESIETE-LAS-TERRAZAS"},
    {"name": "Cine Yelmo Vecindario", "url": "https://www.yelmocines.es/cartelera/las-palmas/vecindario"},
    {"name": "Cine Yelmo Las Arenas", "url": "https://www.yelmocines.es/cartelera/las-palmas/las-arenas"},
    {"name": "Cine Yelmo Premium Alisios", "url": "https://www.yelmocines.es/cartelera/las-palmas/alisios"},
    {"name": "Ocine Premium Siete Palmas", "url": "https://www.ocinepremium7palmas.es/cartelera"}
]

def scrape_yelmo_api():
    print("Obteniendo cartelera desde la API oficial de Yelmo Cines...")
    url = "https://www.yelmocines.es/now-playing.aspx/GetNowPlaying"
    scraper = cloudscraper.create_scraper()
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
    }
    payload = {"cityKey": "las-palmas"}
    
    results = {
        "Cine Yelmo Vecindario": [],
        "Cine Yelmo Las Arenas": [],
        "Cine Yelmo Premium Alisios": []
    }
    
    try:
        res = scraper.post(url, headers=headers, json=payload, timeout=20)
        if res.status_code == 200:
            data = res.json()
            cinemas = data.get("d", {}).get("Cinemas", [])
            
            for c in cinemas:
                name = c.get("Name", "")
                target_key = None
                
                if "Vecindario" in name:
                    target_key = "Cine Yelmo Vecindario"
                elif "Las Arenas" in name:
                    target_key = "Cine Yelmo Las Arenas"
                elif "Alisios" in name:
                    target_key = "Cine Yelmo Premium Alisios"
                    
                if target_key:
                    dates = c.get("Dates", [])
                    if dates:
                        # Extraemos peliculas de hoy (primer elemento)
                        movies = dates[0].get("Movies", [])
                        for m in movies:
                            title = m.get("Title", "")
                            synopsis = m.get("Synopsis", "")[:100] + "..." if m.get("Synopsis") else "Ver cartelera para detalles."
                            # Juntamos los horarios de todos los formatos
                            all_times = set()
                            for f in m.get("Formats", []):
                                for s in f.get("Showtimes", []):
                                    time_str = s.get("Time", "")
                                    if time_str:
                                        all_times.add(time_str)
                            
                            for t in sorted(all_times):
                                results[target_key].append({
                                    "title": title.title(),
                                    "time": t,
                                    "rating": 4.5, # Dummy rating for UI
                                    "summary": synopsis
                                })
                    print(f"  -> {target_key}: Encontradas {len(results[target_key])} sesiones.")
        else:
            print(f"  Error en API Yelmo: Status {res.status_code}")
    except Exception as e:
        print(f"  Error obteniendo datos de Yelmo: {e}")
        
    return results

def scrape_ocine_api():
    print("Obteniendo cartelera desde la API json de Ocine Premium Siete Palmas...")
    url = "https://www.ocinepremium7palmas.es/components/com_cines/json/es_cartellera.json"
    scraper = cloudscraper.create_scraper()
    
    results = {
        "Ocine Premium Siete Palmas": []
    }
    
    try:
        res = scraper.get(url, timeout=20)
        if res.status_code == 200:
            data = res.json()
            movies = data.get("data", [])
            today_date = data.get("date", "")
            
            for m in movies:
                title = m.get("peli_titol", "")
                if not title:
                    continue
                
                peli2 = m.get("Pelicules2", {})
                synopsis = peli2.get("pel2_sinopsis", "") if isinstance(peli2, dict) else ""
                summary = synopsis[:100] + "..." if synopsis else m.get("peli_generacomercial", "Ver detalles.")

                all_times = set()
                sessions = m.get("Planificacions", [])
                
                for s in sessions:
                    if today_date and s.get("plan_data") != today_date:
                        continue
                    
                    time_val = s.get("plan_horainici", "")
                    if time_val:
                        time_str = ":".join(time_val.split(":")[:2])
                        all_times.add(time_str)
                
                for t in sorted(all_times):
                    results["Ocine Premium Siete Palmas"].append({
                        "title": title.title(),
                        "time": t,
                        "rating": 4.5,
                        "summary": summary
                    })
            print(f"  -> Ocine Premium Siete Palmas: Encontradas {len(results['Ocine Premium Siete Palmas'])} sesiones.")
        else:
            print(f"  Error en API Ocine: Status {res.status_code}")
    except Exception as e:
        print(f"  Error obteniendo datos de Ocine: {e}")
        
    return results

def main():
    all_data = {}
    
    # Fully detailed manual data for fallback / missing APIs
    manual_data = {
        "Artesiete Las Terrazas": [
            {"title": "Little Amelie", "time": "16:15", "rating": 4.4, "summary": "Animación entrañable."},
            {"title": "Greenland 2", "time": "19:30", "rating": 4.2, "summary": "Supervivencia al límite."},
            {"title": "Hamnet", "time": "17:15", "rating": 4.6, "summary": "Drama basado en el hijo de Shakespeare."},
            {"title": "La Asistenta", "time": "17:40", "rating": 4.5, "summary": "Intriga psicológica basada en el éxito literario."},
            {"title": "La Asistenta", "time": "18:00", "rating": 4.5, "summary": "Intriga psicológica basada en el éxito literario."},
            {"title": "La Asistenta", "time": "21:45", "rating": 4.5, "summary": "Intriga psicológica basada en el éxito literario."},
            {"title": "La Asistenta", "time": "22:15", "rating": 4.5, "summary": "Intriga psicológica basada en el éxito literario."}
        ]
    }

    # Fetch Yelmo live data
    yelmo_live_data = scrape_yelmo_api()
    all_data.update(yelmo_live_data)

    # Fetch Ocine live data
    ocine_live_data = scrape_ocine_api()
    all_data.update(ocine_live_data)

    # Use fallback data for Artesiete as it is a dynamic app without public API
    for name in ["Artesiete Las Terrazas"]:
        print(f"Cargando datos locales para {name} (sitio dinámico sin API pública)")
        all_data[name] = manual_data[name]

    # Save to src/data.js
    data_content = f"""export const MOVIE_DATA = {json.dumps(all_data, indent=2, ensure_ascii=False)};
export const movieData = MOVIE_DATA;
export const cinemas = Object.keys(MOVIE_DATA);
"""
    with open("src/data.js", "w", encoding="utf-8") as f:
        f.write(data_content)
    
    # Update PRUEBA_RAPIDA.html safely for standalone preview
    try:
        html_path = "PRUEBA_RAPIDA.html"
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()
            
            new_data_json = json.dumps(all_data, indent=2, ensure_ascii=False)
            replacement = f"const MOVIE_DATA = {new_data_json};"
            pattern = re.compile(r"const MOVIE_DATA = \{.*?\};", flags=re.DOTALL)
            match = pattern.search(html)
            if match:
                new_html = html[:match.start()] + replacement + html[match.end():]
                if new_html != html:
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(new_html)
                    print("PRUEBA_RAPIDA.html updated successfully.")
    except Exception as e:
        print(f"Error updating HTML: {e}")

    print(f"Data updated successfully.")

if __name__ == "__main__":
    main()
