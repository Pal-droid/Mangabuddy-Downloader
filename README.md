# Mangaxyz Downloader

A command-line tool to search, view, and download manga chapters from [Mangaxyz](https://mangaxyz.com).

## Features

- Search manga by title
- View available chapters
- Download selected or all chapters
- Extracts images using headless Chromium via Pyppeteer

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mangaxyz-downloader.git
cd mangaxyz-downloader
```

2. Install Dependencies

```pip install -r requirements.txt```

3. Install Chromium (Required for Pyppeteer)

If you're using Termux, install Chromium with:

```pkg install chromium```

Then set the path in the code:

CHROMIUM_PATH = '/path/to/your/chromium'

For Linux/Windows/Mac users, set the appropriate path to your Chromium or Chrome executable.

Also set your desired output path where the downloads will be saved:

OUTPUT_PATH = '/path/to/your/desired/output/folder'

---

Usage

Run the script:

`python mangaxyz.py`

## Example output:

```
~ $ python mangaxyz.py
Enter manga name to search: alya

Search results:
1. Alya Sometimes Hides Her Feelings in Russian - https://mangaxyz.com/alya-sometimes-hides-her-feelings-in-russian
2. Alya, Who Sits Next to Me, Sometimes Whispers Sweet Nothings in Russian - https://mangaxyz.com/alya-who-sits-next-to-me-sometimes-whispers-sweet-nothings-in-russian
3. Alya-san Sometimes Hides Her Feelings in Russian - https://mangaxyz.com/alya-san-sometimes-hides-her-feelings-in-russian
4. Alya Sometimes Hides Her Feelings in Russian «Official» - https://mangaxyz.com/alya-sometimes-hides-her-feelings-in-russian-official
Choose manga number: 1

Fetching chapters for 'Alya Sometimes Hides Her Feelings in Russian' ...

Available chapters:
1. Alya Sometimes Hides Her Feelings in Russian - Chapter 61
2. Alya Sometimes Hides Her Feelings in Russian - Chapter 60
3. Alya Sometimes Hides Her Feelings in Russian - Chapter 59
4. Alya Sometimes Hides Her Feelings in Russian - Chapter 58
5. Alya Sometimes Hides Her Feelings in Russian - Chapter 57

...more results here...

Enter chapters to download (e.g. 1,3,5-7 or 'all'): 1

Downloading chapter Alya Sometimes Hides Her Feelings in Russian - Chapter 61 ...
[!] HTML image scraping failed, falling back to network intercept...
[✓] Saved /data/data/com.termux/files/home/Alya Sometimes Hides Her Feelings in Russian/Alya Sometimes Hides Her Feelings in Russian - Chapter 61/page_1.jpeg
[✓] Saved /data/data/com.termux/files/home/Alya Sometimes Hides Her Feelings in Russian/Alya Sometimes Hides Her Feelings in Russian - Chapter 61/page_2.jpeg

...more downloads here...
```
