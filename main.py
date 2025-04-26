import os
import csv
import json
import time
import requests
from bs4 import BeautifulSoup

def scrape_ordolife():
    base_url = "https://www.ordolife.com"
    collection_url = f"{base_url}/collections/all"
    headers = {"User-Agent": "Mozilla/5.0"}

    os.makedirs("output", exist_ok=True)

    response = requests.get(collection_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []
    product_cards = soup.select("a.full-unstyled-link")
    product_links = list(set(base_url + card["href"] for card in product_cards))

    for link in product_links:
        try:
            prod_resp = requests.get(link, headers=headers)
            prod_soup = BeautifulSoup(prod_resp.text, "html.parser")

            title_tag = prod_soup.find("h1")
            title = title_tag.text.strip() if title_tag else "No Title"

            price_tag = prod_soup.select_one(".price__container .price-item--regular")
            price = price_tag.text.strip() if price_tag else "No Price"

            desc_tag = prod_soup.find("div", {"class": "product__description"})
            description = desc_tag.text.strip() if desc_tag else ""

            img_tags = prod_soup.select(".product__media-item img")
            images = [img.get("src").replace("//", "https://") for img in img_tags]

            variants = []
            option_tags = prod_soup.select("select")
            for option_tag in option_tags:
                for opt in option_tag.select("option"):
                    variants.append(opt.text.strip())

            products.append({
                "name": title,
                "price": price,
                "description": description,
                "images": images,
                "variants": variants,
                "link": link
            })

            time.sleep(1)

        except Exception as e:
            print(f"Error parsing {link}: {e}")

    # Сохраняем CSV
    csv_path = os.path.join("output", "products.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "description", "images", "variants", "link"])
        writer.writeheader()
        for product in products:
            writer.writerow(product)

    # Сохраняем JSON
    json_path = os.path.join("output", "products.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_ordolife()