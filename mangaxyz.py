import asyncio
import os
import re
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch

CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser'
BASE_URL = 'https://mangaxyz.com'
# Change this to your desired download directory
OUTPUT_PATH = '/storage/emulated/0/manga_downloads'

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

    base_dir = os.path.join(OUTPUT_PATH, sanitize_filename(manga_title))
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
=======
import os
import re
import html
import json
import asyncio
import random
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

# -----------------------------
# Load manifest & config
# -----------------------------
with open("manifest.json", "r", encoding="utf-8") as mf:
    manifest = json.load(mf)

with open("config.json", "r", encoding="utf-8") as cf:
    config = json.load(cf)

BASE_URL = config.get("mirror_domain", "https://mangaxyz.com")
OUTPUT_PATH = config.get("output_path", "./downloads")
DEBUG = config.get("debug", False)
TIMEOUT = config.get("timeout_seconds", 15)
MAX_RETRIES = config.get("max_retries", 3)
AUTO_SWITCH = config.get("auto_switch_mirror", True)

# -----------------------------
# Helpers
# -----------------------------
def debug(msg: str):
    if DEBUG:
        console.log(f"[bold blue][DEBUG][/bold blue] {msg}")

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def save_config():
    with open("config.json", "w", encoding="utf-8") as cf:
        json.dump(config, cf, indent=2)

async def auto_switch_mirror():
    mirrors = [m["value"] for m in manifest["supported_mirrors"]]
    new_mirror = random.choice(mirrors)
    config["mirror_domain"] = new_mirror
    save_config()
    console.print(f"[yellow]⚠ Mirror switched to [bold]{new_mirror}[/bold][/yellow]")

# -----------------------------
# Provider
# -----------------------------
class Provider:
    def __init__(self, api: str):
        self.api = api
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{api}/",
        }

    async def fetch(self, client, url):
        debug(f"Fetching: {url}")
        resp = await client.get(url, headers=self.headers)
        resp.raise_for_status()
        return html.unescape(resp.text)

    async def search(self, query: str):
        url = f"{self.api}/search?q={query}"
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                text = await self.fetch(client, url)
            except Exception as e:
                console.print(f"[red]Search error:[/red] {e}")
                if AUTO_SWITCH:
                    await auto_switch_mirror()
                return []

        results = []
        entry_pattern = re.compile(r'<div\s+class="book-item">([\s\S]*?)<\/div>\s*<\/div>', re.I)
        for match in entry_pattern.finditer(text):
            chunk = match.group(1)
            id_match = re.search(r'href="\/([^"]+)"', chunk)
            title_match = re.search(r'<h3>\s*<a[^>]+title="([^"]+)"', chunk)
            thumb_match = re.search(r'data-src="([^"]+\.(?:png|jpg|jpeg))"', chunk)

            if not id_match or not thumb_match:
                continue

            manga_id = id_match.group(1)
            title = title_match.group(1).strip() if title_match else manga_id.replace("-", " ")
            thumb = thumb_match.group(1)
            if not thumb.startswith("http"):
                thumb = f"{self.api}{thumb}"

            results.append({"id": manga_id, "title": title, "image": thumb})
        return results

    async def find_chapters(self, manga_id: str):
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                detail_html = await self.fetch(client, f"{self.api}/{manga_id}")
                book_id = re.search(r"var\s+bookId\s*=\s*(\d+);", detail_html)
                if not book_id:
                    console.print("[red]No bookId found.[/red]")
                    return []

                api_url = f"{self.api}/api/manga/{book_id.group(1)}/chapters?source=detail"
                chapters_html = await self.fetch(client, api_url)
            except Exception as e:
                console.print(f"[red]findChapters error:[/red] {e}")
                return []

        chapters = []
        ch_pattern = re.compile(
            r'<li[^>]*>[\s\S]*?<a[^>]+href="([^"]+)"[^>]*>[\s\S]*?<strong[^>]*class="chapter-title"[^>]*>([^<]+)<\/strong>',
            re.I,
        )

        for match in ch_pattern.finditer(chapters_html):
            href = match.group(1).strip()
            title = match.group(2).strip()
            ch_id = href.lstrip("/")
            ch_num = re.search(r"Chapter\s+([\d.]+)", title, re.I)
            num = ch_num.group(1) if ch_num else "0"

            chapters.append({
                "id": ch_id,
                "url": f"{self.api}/{ch_id}",
                "title": title,
                "chapter": num
            })

        chapters.sort(key=lambda c: float(c["chapter"]) if c["chapter"].replace('.', '', 1).isdigit() else 0)
        for i, ch in enumerate(chapters):
            ch["index"] = i
        return chapters

    async def find_chapter_pages(self, chapter_id: str):
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            html_page = await self.fetch(client, f"{self.api}/{chapter_id}")
        img_var = re.search(r"var\s+chapImages\s*=\s*'([^']+)'", html_page)
        if not img_var:
            debug(f"No chapImages found for {chapter_id}")
            return []
        imgs = [x.strip() for x in img_var.group(1).split(",") if x.strip()]
        pages = []
        for i, img in enumerate(imgs):
            full_url = img if img.startswith("http") else f"{self.api}{img}"
            pages.append({"url": full_url, "index": i, "headers": {"Referer": self.api}})
        return pages

# -----------------------------
# Downloader
# -----------------------------
async def download_image(client, img_url, path, headers, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            r = await client.get(img_url, headers=headers)
            if r.status_code == 200 and r.content:
                with open(path, "wb") as f:
                    f.write(r.content)
                return True
        except Exception as e:
            debug(f"Retry {attempt} failed: {e}")
        await asyncio.sleep(1)
    return False

# -----------------------------
# Main
# -----------------------------
async def main():
    console.print(f"\n[bold cyan]{manifest['name']}[/bold cyan] v{manifest['version']}")
    console.print(f"[dim]{manifest['description']}[/dim]\n")

    provider = Provider(BASE_URL)
    query = console.input("[bold]Enter manga name:[/bold] ").strip()

    with console.status("🔍 Searching...", spinner="dots"):
        results = await provider.search(query)

    if not results:
        console.print("[red]No results found.[/red]")
        return

    for i, r in enumerate(results, 1):
        console.print(f"{i}. {r['title']}")

    choice = int(console.input("\nSelect manga number: ")) - 1
    manga = results[choice]
    manga_dir = os.path.join(OUTPUT_PATH, sanitize_filename(manga["title"]))
    os.makedirs(manga_dir, exist_ok=True)

    with console.status("📚 Fetching chapters...", spinner="line"):
        chapters = await provider.find_chapters(manga["id"])

    if not chapters:
        console.print("[red]No chapters found.[/red]")
        return

    for i, ch in enumerate(chapters, 1):
        console.print(f"{i}. {ch['title']}")

    ch_input = console.input("\nEnter chapters to download (e.g. 1,3,5-7 or all): ").strip()
    if ch_input.lower() == "all":
        selected = range(1, len(chapters) + 1)
    else:
        selected = set()
        for part in ch_input.split(","):
            if "-" in part:
                a, b = map(int, part.split("-"))
                selected.update(range(a, b + 1))
            else:
                selected.add(int(part))

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for i in sorted(selected):
            ch = chapters[i - 1]
            ch_title = sanitize_filename(ch["title"])
            ch_dir = os.path.join(manga_dir, ch_title)
            os.makedirs(ch_dir, exist_ok=True)

            console.print(f"\n[bold green]⬇ Downloading {ch['title']}[/bold green]")
            pages = await provider.find_chapter_pages(ch["id"])
            if not pages:
                console.print("[yellow]No pages found.[/yellow]")
                continue

            with Progress(
                SpinnerColumn(),
                BarColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Downloading...", total=len(pages))
                for p in pages:
                    ext = os.path.splitext(p["url"])[1].split("?")[0] or ".jpg"
                    filename = os.path.join(ch_dir, f"page_{p['index']+1}{ext}")
                    ok = await download_image(client, p["url"], filename, p["headers"])
                    progress.advance(task)

            console.print(f"[cyan]✔ Chapter complete:[/cyan] {ch['title']}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user.[/red]")
