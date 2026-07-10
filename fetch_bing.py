import requests
import json
import os

MARKETS = [
    'en-US', 'en-AU', 'en-CA', 'zh-CN', 'de-DE', 
    'es-ES', 'fr-FR', 'it-IT', 'ja-JP', 'en-NZ', 'en-GB'
]

def fetch_wallpapers():
    if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
        with open('data.json', 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except json.JSONDecodeError: db = {}
    else:
        db = {}

    updated = False

    for mkt in MARKETS:
        url = f"https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=5&mkt={mkt}"
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                images = response.json().get('images', [])
                
                for img in images:
                    date = img.get('startdate')
                    if not date: continue
                    
                    # Вытаскиваем чистый уникальный ID картинки (например, LemonShark)
                    urlbase = img.get('urlbase', '')
                    img_id = urlbase.split('?id=OHR.')[-1].split('_')[0] if '?id=OHR.' in urlbase else urlbase.split('/')[-1]
                    
                    # Ключ теперь уникален для самой картинки на эту дату (никаких повторов из-за стран!)
                    key = f"{date}_{img_id}"
                    
                    if key not in db:
                        base_url = "https://www.bing.com" + urlbase + "_UHD.jpg"
                        
                        db[key] = {
                            "date": f"{date[:4]}-{date[4:6]}-{date[6:]}",
                            "url": base_url,
                            "img_id": img_id
                        }
                        updated = True
        except Exception as e:
            print(f"Ошибка {mkt}: {e}")

    if updated or not db:
        # Сортируем базу по дате и ключу в обратном порядке (свежие сверху)
        db = dict(sorted(db.items(), key=lambda item: item[0], reverse=True))
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        print("База успешно пересобрана без дубликатов!")

if __name__ == "__main__":
    fetch_wallpapers()
