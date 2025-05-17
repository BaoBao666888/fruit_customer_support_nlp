from bs4 import BeautifulSoup
import requests
import urllib.parse

def scrape_nongnghiep(page=1):
    base_url = "https://nongsanviet.nongnghiep.vn/trái+cây-search/from-to-sign-/"
    url = base_url if page == 1 else f"{base_url}p{page}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # response.status_code == 202 có vẻ là đặc trưng của trang này, bình thường là 200
        if response.status_code != 200 and response.status_code != 202:
            print(f"Không thể tải trang nongnghiep {page}, mã trạng thái: {response.status_code}")
            return []
        response.raise_for_status() # Báo lỗi cho các mã 4xx/5xx
    except requests.exceptions.RequestException as e:
        print(f"Lỗi request cho trang nongnghiep {page}: {e}")
        return []
    except Exception as e:
        print(f"Lỗi không xác định khi tải trang nongnghiep {page}: {e}")
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
        
        article_url = title_tag.get("href", "")
        if article_url and not article_url.startswith(('http://', 'https://')):
            base_domain = "https://nongsanviet.nongnghiep.vn" 
            article_url = requests.compat.urljoin(base_domain, article_url)

        image_src = img_tag.get("src") if img_tag else ""
        if image_src and not image_src.startswith(('http://', 'https://')):
            base_domain = "https://nongsanviet.nongnghiep.vn"
            image_src = requests.compat.urljoin(base_domain, image_src)

        article = {
            "title": title_tag.get("title", "Không có tiêu đề").strip(),
            "summary": summary_tag.text.strip() if summary_tag else "Không có tóm tắt.",
            "url": article_url,
            "category": category_tag.text.strip() if category_tag else "",
            "image": image_src
        }
        results.append(article)
    return results

def scrape_vnexpress(page=1):
    query = "trái cây"
    base_url = "https://timkiem.vnexpress.net"
    encoded_query = urllib.parse.quote(query) # Mã hóa query cho URL
    url = f"{base_url}/?q={encoded_query}" if page == 1 else f"{base_url}?q={encoded_query}&page={page}"

    headers = {"User-Agent": "Mozilla/5.0"} # User agent đơn giản
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi request cho trang VnExpress {page}: {e}")
        return []
    except Exception as e:
        print(f"Lỗi không xác định khi tải trang VnExpress {page}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    # Selector có thể cần cập nhật nếu cấu trúc VnExpress thay đổi
    items = soup.select("div.width_common.list-news-subfolder article.item-news")
    if not items: # Thử selector khác nếu không tìm thấy
        items = soup.select("#result_search article.item_news")


    results = []
    for item in items:
        title_tag = item.select_one("h3.title-news a")
        summary_tag = item.select_one("p.description a") # VnExpress thường có link trong summary
        
        thumb_art_div = item.select_one("div.thumb-art")
        img_tag_in_thumb = thumb_art_div.select_one("picture source[data-srcset], picture img[data-src], img[data-src], img[src]") if thumb_art_div else None

        image_url = ""
        if img_tag_in_thumb:
            if img_tag_in_thumb.has_attr("data-srcset"):
                image_url = img_tag_in_thumb["data-srcset"].split(" ")[0] # Lấy URL đầu tiên từ srcset
            elif img_tag_in_thumb.has_attr("data-src"):
                image_url = img_tag_in_thumb["data-src"]
            elif img_tag_in_thumb.has_attr("src"):
                image_url = img_tag_in_thumb["src"]
        
        if not title_tag: # Bài viết phải có tiêu đề
            continue
        
        article_url = title_tag.get("href", "")
        # Đảm bảo URL là tuyệt đối
        if article_url and not article_url.startswith(('http://', 'https://')):
            # VnExpress thường trả về URL tuyệt đối, nhưng kiểm tra cho chắc
             article_url = requests.compat.urljoin("https://vnexpress.net", article_url)


        results.append({
            "title": title_tag.text.strip() if title_tag else "Không có tiêu đề",
            "summary": summary_tag.text.strip() if summary_tag else "Không có tóm tắt.",
            "url": article_url,
            "image": image_url
            # VnExpress không có category rõ ràng trong trang tìm kiếm
        })
    return results

def scrape_baomoi(page=1):
    # Chức năng này chưa được triển khai
    print(f"Chức năng cào dữ liệu từ Báo Mới (trang {page}) chưa được cài đặt.")
    return [] # Luôn trả về danh sách rỗng để tránh lỗi

def load_news(source="nongnghiep", page=1):
    print(f"Đang tải tin từ nguồn: {source}, trang: {page}")
    if source == "vnexpress":
        return scrape_vnexpress(page)
    elif source == "baomoi":
        return scrape_baomoi(page)
    # Mặc định hoặc nếu source là 'nongnghiep'
    return scrape_nongnghiep(page)

# Ví dụ để kiểm tra scraper (bỏ chú thích nếu muốn chạy riêng file này)
# if __name__ == "__main__":
#     print("--- Kiểm tra Nông Nghiệp ---")
#     news_nn = scrape_nongnghiep(1)
#     if news_nn:
#         for i, article in enumerate(news_nn[:2]): # In 2 bài đầu tiên
#             print(f"Bài {i+1}: {article['title']}")
#             print(f"  URL: {article['url']}")
#             print(f"  Ảnh: {article['image']}")
#     else:
#         print("Không lấy được tin từ Nông Nghiệp.")

#     print("\n--- Kiểm tra VnExpress ---")
#     news_vn = scrape_vnexpress(1)
#     if news_vn:
#         for i, article in enumerate(news_vn[:2]):
#             print(f"Bài {i+1}: {article['title']}")
#             print(f"  URL: {article['url']}")
#             print(f"  Ảnh: {article['image']}")
#     else:
#         print("Không lấy được tin từ VnExpress.")

#     print("\n--- Kiểm tra Báo Mới ---")
#     news_bm = scrape_baomoi(1) # Sẽ in thông báo chưa triển khai và trả về []
#     if not news_bm:
#         print("Đúng như dự kiến, Báo Mới chưa có dữ liệu.")