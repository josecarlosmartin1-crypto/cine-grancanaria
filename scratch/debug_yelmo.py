import cloudscraper
import json

def debug_yelmo():
    url = "https://www.yelmocines.es/now-playing.aspx/GetNowPlaying"
    scraper = cloudscraper.create_scraper()
    headers = {"Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/json; charset=UTF-8", "X-Requested-With": "XMLHttpRequest"}
    payload = {"cityKey": "las-palmas"}
    
    try:
        res = scraper.post(url, headers=headers, json=payload, timeout=20)
        if res.status_code == 200:
            cinemas = res.json().get("d", {}).get("Cinemas", [])
            for c in cinemas:
                name = c.get("Name", "")
                if "Vecindario" in name:
                    dates = c.get("Dates", [])
                    print(f"Cine: {name}")
                    for i, d in enumerate(dates):
                        # Intentar encontrar la fecha en el objeto d
                        print(f"  Index {i}: {d.get('DateDisplay', 'N/A')} | {d.get('Date', 'N/A')}")
                    break
    except Exception as e:
        print(f"Error Yelmo: {e}")

if __name__ == "__main__":
    debug_yelmo()
