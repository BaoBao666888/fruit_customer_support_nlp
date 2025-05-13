from bs4 import BeautifulSoup
import requests


def scrape_nongnghiep(page=1):
    base_url = "https://nongsanviet.nongnghiep.vn/trái+cây-search/from-to-sign-/"
    url = base_url if page == 1 else f"{base_url}p{page}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 202:
        print(f"Failed to fetch page {page}")
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

        article = {
            "title": title_tag.get("title", "").strip(),
            "summary": summary_tag.text.strip() if summary_tag else "",
            "url": title_tag["href"],
            "category": category_tag.text.strip() if category_tag else "",
            "image": img_tag.get("src") if img_tag else ""
        }

        results.append(article)

    return results


def scrape_vnexpress(page=1):
    import requests
    from bs4 import BeautifulSoup
    import urllib.parse

    query = "trái cây"
    base_url = "https://timkiem.vnexpress.net"
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}/?q={encoded_query}" if page == 1 else f"{base_url}?q={encoded_query}&page={page}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch VnExpress page {page}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div.width_common.list-news-subfolder article.item-news")

    results = []
    for item in items:
        title_tag = item.select_one("h3.title-news a")
        summary_tag = item.select_one("p.description a")
        picture_tag = item.select_one("picture source")

        # Lấy ảnh từ data-srcset
        image_url = ""
        if picture_tag and picture_tag.has_attr("data-srcset"):
            srcset = picture_tag["data-srcset"]
            image_url = srcset.split(",")[0].split()[0]  # Lấy URL đầu tiên (1x)

        if not title_tag or not summary_tag:
            continue

        results.append({
            "title": title_tag.text.strip(),
            "summary": summary_tag.text.strip(),
            "url": title_tag.get("href"),
            "image": image_url
        })

    return results


    

def scrape_baomoi(page=1):
    pass

def load_news(source="nongnghiep", page=1):
    if source == "vnexpress":
        return scrape_vnexpress(page)
    elif source == "baomoi":
        return scrape_baomoi(page)
    else:
        return scrape_nongnghiep(page)
    
# if __name__ == "__main__":
#     news = scrape_vnexpress(1)
#     for a in news:
#         print(f"{a['title']}")
#         print(f"  → {a['url']}")
#         print(f"  📝 {a['summary']}")
#         print(f"  📷 {a['image']}\n")
#         break
