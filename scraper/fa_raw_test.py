import requests

URL = "https://www.filmaffinity.com/es/theatre.php?theatre_id=3142"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
}

try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    print(f"Status: {response.status_code}")
    with open("raw_fa.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved raw_fa.html")
except Exception as e:
    print(f"Error: {e}")
