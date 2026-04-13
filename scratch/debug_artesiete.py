import cloudscraper
import re
import datetime
from bs4 import BeautifulSoup

def debug_artesiete():
    url = "https://terrazas.artesiete.es/Cine/1/ARTESIETE%20Las%20Terrazas/Total"
    scraper = cloudscraper.create_scraper()
    res = scraper.get(url, timeout=20)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        today_str = datetime.date.today().strftime("%d/%m")
        print(f"Buscando fecha: {today_str}")
        
        found_any = False
        for img in soup.find_all('img'):
            alt = img.get('alt', '')
            if 'posters' in img.get('src', '').lower() and alt:
                clean_alt = re.sub(r'\(.*?\)', '', alt).strip().title()
                card = None
                tp = img.parent
                while tp and tp.name != 'body':
                    if tp.name == 'div' and 'grid' in tp.get('class', []):
                        card = tp
                        break
                    tp = tp.parent
                
                if card:
                    # Buscar el tab de hoy
                    target_id = None
                    for a in card.find_all('a'):
                        if today_str in a.get_text():
                            target_id = a.get('id')
                            break
                    
                    if target_id:
                        day_div = card.find('div', id=target_id)
                        if day_div:
                            times = day_div.find_all(string=re.compile(r'\b\d{1,2}:\d{2}\b'))
                            if times:
                                print(f"  [OK] {clean_alt}: {times}")
                                found_any = True
                            else:
                                print(f"  [FAIL] {clean_alt}: No se encontraron horas en div id={target_id}")
                        else:
                            print(f"  [FAIL] {clean_alt}: No se encontró div id={target_id}")
                    else:
                        print(f"  [FAIL] {clean_alt}: No se encontró pestaña para {today_str}")
        
        if not found_any:
            print("CRÍTICO: No se encontró ninguna película para hoy.")

if __name__ == "__main__":
    debug_artesiete()
