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
                    
                    urlbase = img.get('urlbase', '')
                    if '?id=OHR.' in urlbase:
                        raw_id = urlbase.split('?id=OHR.')[-1]
                    else:
                        raw_id = urlbase.split('/')[-1]
                    
                    # Отрезаем ВСЁ лишнее после названия картинки (коды стран, цифры)
                    # Из 'VictoriaBeach_EN-US7607379912' получаем чистый 'VictoriaBeach'
                    clean_id = raw_id.split('_')[0]
                    
                    # Жесткий уникальный ключ: Дата + Чистое Название
                    key = f"{date}_{clean_id}"
                    
                    if key not in db:
                        base_url = "https://www.bing.com" + urlbase + "_UHD.jpg"
                        
                        db[key] = {
                            "date": f"{date[:4]}-{date[4:6]}-{date[6:]}",
                            "url": base_url,
                            "img_id": clean_id
                        }
                        updated = True
        except Exception as e:
            print(f"Ошибка {mkt}: {e}")

    if updated or not db:
        # Сортируем базу по дате, чтобы новые обои всегда шли первыми
        db = dict(sorted(db.items(), key=lambda item: item[0], reverse=True))
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        print("База очищена от абсолютно всех скрытых дубликатов!")

if __name__ == "__main__":
    fetch_wallpapers()
