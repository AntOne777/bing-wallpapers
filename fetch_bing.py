import requests
import json
import os

# Список регионов для сбора обоев
MARKETS = ['en-US', 'zh-CN', 'ja-JP', 'de-DE', 'fr-FR', 'ru-RU']

def fetch_wallpapers():
    # Загружаем текущую базу данных, если она есть и не пустая
    if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
        with open('data.json', 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = {}
    else:
        db = {}

    updated = False

    for mkt in MARKETS:
        # Официальный URL API Bing
        url = f"https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=5&mkt={mkt}"
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                images = data.get('images', [])
                
                print(f"Регион {mkt}: найдено {len(images)} картинок.")
                
                for img in images:
                    # Создаем уникальный ключ для картинки (дата + регион)
                    date = img.get('startdate')
                    if not date:
                        continue
                    
                    key = f"{date}_{mkt}"
                    
                    if key not in db:
                        # Принудительно меняем разрешение на максимальное 4K (UHD)
                        base_url = "https://www.bing.com" + img['urlbase'] + "_UHD.jpg"
                        
                        db[key] = {
                            "date": f"{date[:4]}-{date[4:6]}-{date[6:]}",
                            "market": mkt,
                            "url": base_url,
                            "title": img.get('title', 'Bing Wallpaper'),
                            "copyright": img.get('copyright', '')
                        }
                        updated = True
            else:
                print(f"Ошибка при запросе {mkt}: статус {response.status_code}")
        except Exception as e:
            print(f"Не удалось получить данные для {mkt}: {e}")

    # Сохраняем обратно, только если появились новые данные или база была совсем пустой
    if updated or not db:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        print("База данных успешно обновлена в файле data.json")
    else:
        print("Новых картинок не обнаружено, база не перезаписана.")

if __name__ == "__main__":
    fetch_wallpapers()
