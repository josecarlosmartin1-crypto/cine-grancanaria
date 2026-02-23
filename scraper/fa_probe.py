import requests
from bs4 import BeautifulSoup

PROBE_IDS = [3142, 418, 415, 3115, 2495, 3217]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def probe_fa(fa_id):
    url = f"https://www.filmaffinity.com/es/theatre.php?theatre_id={fa_id}"
    print(f"\nProbing ID {fa_id}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check cinema name
        name_elem = soup.select_one('#theatre-info h1, h1')
        name = name_elem.text.strip() if name_elem else "Not found"
        print(f"  Name: {name}")
        
        # Check if it has movies
        movies = soup.select('.theatre-movie-title')
        if movies:
            print(f"  First Movie: {movies[0].text.strip()}")
        else:
            print("  No movies found on this page.")
            
    except Exception as e:
        print(f"  Error probing {fa_id}: {e}")

if __name__ == "__main__":
    for pid in PROBE_IDS:
        probe_fa(pid)
