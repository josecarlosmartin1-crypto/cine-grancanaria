import requests
from bs4 import BeautifulSoup
import os

CINEMAS = [
    {"name": "Artesiete", "url": "https://artesiete.es/Cine/14/ARTESIETE-LAS-TERRAZAS"},
    {"name": "Yelmo", "url": "https://www.yelmocines.es/cartelera/las-palmas/vecindario"},
    {"name": "Ocine", "url": "https://www.ocine.es/cine/ocine-premium-siete-palmas"}
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9',
}

def debug_cinema(cinema):
    print(f"\n--- Analizando {cinema['name']} ---")
    try:
        response = requests.get(cinema['url'], headers=HEADERS, timeout=20)
        print(f"Status Code: {response.status_code}")
        
        # Save a snippet to file for the AI to read
        filename = f"debug_{cinema['name']}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text[:20000]) # First 20k chars
        print(f"Snippet guardado en {filename}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Test common containers
        containers = [
            "article", ".movie-card", ".peli", ".item-peli", ".movie-info", 
            ".film", ".movie-item", "div[data-movie]", "section"
        ]
        
        for selector in containers:
            found = soup.select(selector)
            if found:
                print(f"Selector '{selector}' encontró {len(found)} elementos.")
                # Show first 100 chars of one element
                print(f"  Ejemplo: {str(found[0])[:150]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if not os.path.exists("debug"):
        os.makedirs("debug")
    os.chdir("debug")
    for c in CINEMAS:
        debug_cinema(c)
    print("\nDebug finalizado. Por favor, avisa al asistente.")
