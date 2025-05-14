from bs4 import BeautifulSoup
import requests
import urllib.parse # Voeg deze import toe

def scrape_nongnghiep(page=1):
    base_url = "https://nongsanviet.nongnghiep.vn/trái+cây-search/from-to-sign-/"
    url = base_url if page == 1 else f"{base_url}p{page}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Het is ongebruikelijk, maar als 202 de success code is voor deze site, is het ok.
        # Meestal is het 200. Controleer dit.
        if response.status_code != 200 and response.status_code != 202: # 200 is gebruikelijker
            print(f"Failed to fetch nongnghiep page {page}, status: {response.status_code}")
            return []
        response.raise_for_status() # Gooit een error voor 4xx/5xx codes
    except requests.exceptions.RequestException as e:
        print(f"Request error for nongnghiep page {page}: {e}")
        return []


    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div.container_left div.list-news-home div.news-home-item")

    results = []
    for item in items:
        title_tag = item.select_one(".main-title a")
        summary_tag = item.select_one(".main-intro")
        category_tag = item.select_one(".cate_info a")
        img_tag = item.select_one("a.expthumb img")

        if not title_tag:
            continue
        
        # Zorg ervoor dat URL's compleet zijn
        article_url = title_tag.get("href", "")
        if article_url and not article_url.startswith(('http://', 'https://')):
            # Pas dit aan als de basis URL voor artikelen anders is
            base_domain = "https://nongsanviet.nongnghiep.vn" 
            article_url = requests.compat.urljoin(base_domain, article_url)

        image_src = img_tag.get("src") if img_tag else ""
        if image_src and not image_src.startswith(('http://', 'https://')):
            base_domain = "https://nongsanviet.nongnghiep.vn" # Pas dit aan indien nodig
            image_src = requests.compat.urljoin(base_domain, image_src)


        article = {
            "title": title_tag.get("title", "").strip(),
            "summary": summary_tag.text.strip() if summary_tag else "",
            "url": article_url,
            "category": category_tag.text.strip() if category_tag else "",
            "image": image_src
        }
        results.append(article)
    return results


def scrape_vnexpress(page=1):
    query = "trái cây"
    base_url = "https://timkiem.vnexpress.net"
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}/?q={encoded_query}" if page == 1 else f"{base_url}?q={encoded_query}&page={page}"

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request error for VnExpress page {page}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div.width_common.list-news-subfolder article.item-news")
    # Alternatieve selector als de bovenstaande niet werkt:
    # items = soup.select("#result_search article.item_news") 

    results = []
    for item in items:
        title_tag = item.select_one("h3.title-news a")
        summary_tag = item.select_one("p.description a")
        # picture_tag = item.select_one("picture source") # data-srcset is betrouwbaarder
        thumb_art_div = item.select_one("div.thumb-art")
        img_tag_in_thumb = thumb_art_div.select_one("img") if thumb_art_div else None

        image_url = ""
        if img_tag_in_thumb and img_tag_in_thumb.has_attr("data-src"):
            image_url = img_tag_in_thumb["data-src"]
        elif img_tag_in_thumb and img_tag_in_thumb.has_attr("src"): # fallback
             image_url = img_tag_in_thumb["src"]
        # Oude logica voor picture tag, kan als fallback dienen
        # if not image_url:
        #     picture_tag = item.select_one("picture source[data-srcset]")
        #     if picture_tag:
        #         srcset = picture_tag["data-srcset"]
        #         image_url = srcset.split(",")[0].split()[0]

        if not title_tag or not summary_tag:
            continue
        
        article_url = title_tag.get("href")
        if article_url and not article_url.startswith(('http://', 'https://')):
            # VnExpress links zijn meestal al absoluut, maar voor de zekerheid
            if "vnexpress.net" not in article_url: # Voorkom dubbele domeinen
                 article_url = requests.compat.urljoin("https://vnexpress.net", article_url)


        results.append({
            "title": title_tag.text.strip(),
            "summary": summary_tag.text.strip(),
            "url": article_url,
            "image": image_url
        })
    return results


def scrape_baomoi(page=1):
    print("scrape_baomoi is nog niet geïmplementeerd.")
    return [] # Retourneer een lege lijst om fouten te voorkomen

def load_news(source="nongnghiep", page=1):
    if source == "vnexpress":
        return scrape_vnexpress(page)
    elif source == "baomoi":
        return scrape_baomoi(page)
    else: # Default naar nongnghiep
        return scrape_nongnghiep(page)

# Voor testen:
# if __name__ == "__main__":
#     print("Testing nongnghiep:")
#     news_nn = scrape_nongnghiep(1)
#     for a in news_nn[:2]: # Print eerste 2
#         print(f"  Title: {a['title']}")
#         print(f"  URL: {a['url']}")
#         print(f"  Image: {a['image']}\n")

#     print("\nTesting vnexpress:")
#     news_vn = scrape_vnexpress(1)
#     for a in news_vn[:2]: # Print eerste 2
#         print(f"  Title: {a['title']}")
#         print(f"  URL: {a['url']}")
#         print(f"  Image: {a['image']}\n")

#     print("\nTesting baomoi:")
#     news_bm = scrape_baomoi(1) # Zou lege lijst moeten printen
#     print(news_bm)