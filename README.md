# Mangabuddy Downloader

A command-line tool to search, view, and download manga chapters from [Mangabuddy](https://mangabuddy.com).

> Otherwise known as [Mangaxyz](mangaxyz.com) - *Site also has a bunch of other mirrors.*

## Features

- Search manga by title
- View available chapters
- Download selected or all chapters
- Extracts images using headless Chromium via Pyppeteer

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pal-droid/Mangabuddy-Downloader
cd Mangabuddy-Downloader
```

2. Install Dependencies

`pip install -r requirements.txt`

3. Install Chromium (Required for Pyppeteer)

If you're using Termux, install Chromium with:

```pkg install chromium```

Then set the path in the code:

`CHROMIUM_PATH = '/path/to/your/chromium'`

For Linux/Windows/Mac users, set the appropriate path to your Chromium or Chrome executable.

Also set your desired output path where the downloads will be saved:
`OUTPUT_PATH = '/path/to/your/desired/output/folder'`

---

## Usage

Run the script:

`python mangaxyz.py`

## Example output:

```
```
# Mangabuddy Downloader

A command-line tool to search, view, and download manga chapters from [Mangabuddy](https://mangabuddy.com).

> Also known as [Mangaxyz](https://mangaxyz.com) — this site and its mirrors share the same data and structure.

---

## ✨ Features

- Search manga by title  
- View available chapters  
- Download selected or all chapters  
- Supports multiple mirrors (Mangabuddy, Mangaxyz, Mangapuma, Mangacute, etc.)  
- Customizable output path and debug mode via `config.json`  
- Automatic version check and repository updater (`update.py`)  
- Smooth CLI animations with progress feedback  

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pal-droid/Mangabuddy-Downloader
cd Mangabuddy-Downloader
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Settings

Edit `config.json` to adjust your environment:

```json
{
  "output_path": "/path/to/downloads",
  "debug": false,
  "mirror_domain": "https://mangabuddy.com"
}
```

Available mirrors:
- mangabuddy.com  
- mangaforest.me  
- mangacute.com  
- mangaxyz.com  
- mangapuma.com  
- mangamirror.com  
- truemanga.com  
- mangafab.com  
- manhwatube.com  

---

## 🚀 Usage

Run the main script:

```bash
python mangaxyz.py
```

### Example output:

```
Mangabuddy-Downloader v1.3.0
Python CLI tool to download manga chapters from Mangabuddy mirrors with retry, debug logs, and
auto mirror switching.

Enter manga name: bluelock
1. Blue Lock

Select manga number: 1
1. Notice. : ANIME NEWS!!
2. Chapter 1: Dream
3. Chapter 2: Moving In
4. Chapter 3: Monster
5. Chapter 4: Now

Enter chapters to download (e.g. 1,3,5-7 or all): 1

⬇ Downloading Notice. : ANIME NEWS!!
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Downloading... 0:00:00
✔ Chapter complete: Notice. : ANIME NEWS!!```
```

---

## 🧠 Updating

To check for and automatically pull the latest version:

```bash
python update.py
```

---

## 🐧 Ubuntu / Debian Setup

```bash
git clone https://github.com/pal-droid/Mangabuddy-Downloader
cd Mangabuddy-Downloader
python3 -m venv MangaBuddy-Downloader-venv
MangaBuddy-Downloader-venv/bin/pip install -r requirements.txt
```

Run:

```bash
MangaBuddy-Downloader-venv/bin/python3 mangaxyz.py
```


## Installation and Usage in Ubuntu/Debian

```bash
git clone https://github.com/pal-droid/Mangabuddy-Downloader
cd Mangabuddy-Downloader
```

2. Install Dependencies

```bash
python3 -m venv MangaBuddy-Downloader-venv
MangaBuddy-Downloader-venv/bin/pip install -r requirements.txt
```
3. Install Chrome

Install Chrome so its dependencies will be installed as well.
```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update 
sudo apt install google-chrome-stable
```
Edit the code with the following changes:
`BASE_URL = 'https://mangabuddy.com'`
`CHROMIUM_PATH = '/usr/bin/google-chrome'`

Also set your desired output path where the downloads will be saved:
`OUTPUT_PATH = '/path/to/your/desired/output/folder'`

## Usage

Run the script:
`MangaBuddy-Downloader-venv/bin/python3 mangaxyz.py`
