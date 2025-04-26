import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

BASE_URL = "https://www.ordolife.com"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        print(f"Ошибка загрузки страницы {url}: {response.status_code}")
        return None

def scrape_products():
    print("Стартуем парсинг OrdoLife...")
    url = f"{BASE_URL}/collections/all"
    soup = get_soup(url)

    if not soup:
        print("Ошибка: не удалось получить главную страницу товаров.")
        return

    products = []
    product_cards = soup.select('a.full-unstyled-link')

    product_links = list(set(BASE_URL + card['href'] for card in product_cards if card.get('href')))

    print(f"Найдено {len(product_links)} товаров. Начинаем детальный парсинг...")

    for link in product_links:
        time.sleep(1)  # пауза чтобы не забанили

        product_soup = get_soup(link)
        if not product_soup:
            continue

        title_tag = product_soup.find('h1', class_='product-title')
        price_tag = product_soup.find('span', class_='price-item')
        description_tag = product_soup.find('div', class_='product__description')
        
        title = title_tag.get_text(strip=True) if title_tag else 'Без названия'
        price = price_tag.get_text(strip=True) if price_tag else 'Цена не указана'
        description = description_tag.get_text(strip=True) if description_tag else 'Описание отсутствует'

        # Варианты товаров (цвета, размеры)
        variants = []
        variant_elements = product_soup.select('select.product-form__input option')

        for var in variant_elements:
            variant_text = var.get_text(strip=True)
            if variant_text:
                variants.append(variant_text)

        products.append({
            "name": title,
            "price": price,
            "description": description,
            "variants": variants,
            "link": link
        })

        print(f"✔️ Спарсили товар: {title}")

    # Сохраняем в CSV
    df = pd.DataFrame(products)
    df.to_csv('products.csv', index=False)
    print("📄 Файл products.csv успешно сохранён!")

    # Сохраняем в JSON
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("📄 Файл products.json успешно сохранён!")

    print("✅ Парсинг завершён успешно!")

if __name__ == "__main__":
    scrape_products()
