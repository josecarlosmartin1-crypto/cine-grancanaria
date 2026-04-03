import cloudscraper
import json

def probe_yelmo_full():
    print("Checking full Yelmo API response...")
    url = "https://www.yelmocines.es/now-playing.aspx/GetNowPlaying"
    scraper = cloudscraper.create_scraper()
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
    }
    payload = {"cityKey": "las-palmas"}
    
    try:
        res = scraper.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            cinemas = data.get("d", {}).get("Cinemas", [])
            for c in cinemas:
                movies = c.get("Dates", [{}])[0].get("Movies", [])
                if movies:
                    print(f"Sample Movie Data structure (from {c.get('Name')}):")
                    print(json.dumps(movies[0], indent=2, ensure_ascii=False))
                    break
        else:
            print(f"Error {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_yelmo_full()
