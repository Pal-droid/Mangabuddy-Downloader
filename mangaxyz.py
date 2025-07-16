import asyncio
import os
import re
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch

CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser'
BASE_URL = 'https://mangaxyz.com'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

async def get_cookies_for_search(query):
    browser = await launch(
        executablePath=CHROMIUM_PATH,
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    search_url = f"{BASE_URL}/search?status=all&sort=views&q={query}"
    await page.goto(search_url, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(2)
    cookies = await page.cookies()
    cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    await browser.close()
    return cookie_str

def call_search_api(query, cookie_str):
    api_url = f"{BASE_URL}/api/manga/search"
    params = {'q': query, 'sort': 'views', 'status': 'all'}
    headers = HEADERS.copy()
    headers['cookie'] = cookie_str
    headers['referer'] = f"{BASE_URL}/search?status=all&sort=views&q={query}"
    response = requests.get(api_url, headers=headers, params=params)
    return response.text if response.status_code == 200 else None

def parse_search_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for item_div in soup.select('div.novel__item'):
        a_tag = item_div.select_one('a[title][href]')
        if not a_tag:
            continue
        title = a_tag['title']
        href = a_tag['href']
        link = BASE_URL + href
        img = a_tag.find('img')
        img_url = img['src'] if img else ''
        results.append((title, link, img_url))
    return results

async def fetch_chapters(manga_url):
    browser = await launch(
        executablePath=CHROMIUM_PATH,
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    await page.goto(manga_url, {'waitUntil': 'networkidle2'})

    try:
        await page.waitForSelector('#show-more-chapters', timeout=3000)
        await page.click('#show-more-chapters')
        await asyncio.sleep(2)
    except Exception:
        pass

    await page.waitForSelector('#chapter-list li a')

    chapters = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('#chapter-list li a')).map(a => ({
            title: a.getAttribute('title') || a.innerText.trim(),
            url: a.href
        }));
    }''')

    await browser.close()
    return chapters

async def fetch_images(chapter_url):
    images = []
    browser = await launch(
        executablePath=CHROMIUM_PATH,
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    await page.goto(chapter_url, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(2)

    # HTML scraping first
    try:
        await page.waitForSelector('img.page-img', timeout=5000)
        html_images = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('img.page-img')).map(img => img.src);
        }''')
        images.extend([img for img in html_images if img and not img.lower().endswith('.gif')])
    except Exception:
        print("[!] HTML image scraping failed, falling back to network intercept...")

    # Network intercept fallback
    if not images:
        def intercept_response(response):
            try:
                url = response.url
                ct = response.headers.get('content-type', '')
                if ('image' in ct) and url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    if not url.lower().endswith('.gif') and url not in images:
                        images.append(url)
            except:
                pass

        page.on('response', intercept_response)
        await page.reload({'waitUntil': 'networkidle2'})
        await asyncio.sleep(3)

    cookies = await page.cookies()
    cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    await browser.close()
    return images, cookie_str

def download_image(url, path, cookie_str):
    if url.lower().endswith('.gif'):
        print(f"[!] Skipping GIF image: {url}")
        return
    headers = HEADERS.copy()
    headers['cookie'] = cookie_str
    headers['referer'] = BASE_URL
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            print(f"[✓] Saved {path}")
        else:
            print(f"[✗] Failed to download {url} (status {r.status_code})")
    except Exception as e:
        print(f"[✗] Error downloading {url}: {e}")

async def main():
    query = input("Enter manga name to search: ").strip()
    cookie_str = await get_cookies_for_search(query)
    api_html = call_search_api(query, cookie_str)
    if not api_html:
        print("No results or failed to get API response.")
        return

    results = parse_search_html(api_html)
    if not results:
        print("No manga found.")
        return

    print("\nSearch results:")
    for i, (title, link, _) in enumerate(results, 1):
        print(f"{i}. {title} - {link}")

    choice = int(input("Choose manga number: "))
    manga_title, manga_link, _ = results[choice - 1]

    print(f"\nFetching chapters for '{manga_title}' ...")
    chapters = await fetch_chapters(manga_link)
    if not chapters:
        print("No chapters found.")
        return

    print("\nAvailable chapters:")
    for i, ch in enumerate(chapters, 1):
        print(f"{i}. {ch['title']}")

    chapter_input = input("Enter chapters to download (e.g. 1,3,5-7 or 'all'): ").strip()
    if chapter_input.lower() == 'all':
        chosen = range(1, len(chapters) + 1)
    else:
        chosen = set()
        for part in chapter_input.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                chosen.update(range(start, end + 1))
            else:
                chosen.add(int(part))

    base_dir = os.path.join(os.getcwd(), sanitize_filename(manga_title))
    os.makedirs(base_dir, exist_ok=True)

    for i in sorted(chosen):
        ch = chapters[i - 1]
        ch_title = sanitize_filename(ch['title'])
        ch_url = ch['url']
        print(f"\nDownloading chapter {ch['title']} ...")

        images, chapter_cookies = await fetch_images(ch_url)
        if not images:
            print(f"[!] No images found in chapter {ch['title']}, skipping.")
            continue

        ch_dir = os.path.join(base_dir, ch_title)
        os.makedirs(ch_dir, exist_ok=True)

        for idx, img_url in enumerate(images, 1):
            ext = os.path.splitext(img_url)[1].split('?')[0] or '.jpg'
            filename = os.path.join(ch_dir, f'page_{idx}{ext}')
            download_image(img_url, filename, chapter_cookies)

if __name__ == '__main__':
    asyncio.run(main())
