# 📚 Mangabuddy Downloader

A sleek **command-line tool** to search, view, and download manga chapters from [Mangabuddy](https://mangabuddy.com).  
> Also known as [Mangaxyz](https://mangaxyz.com) — many mirrors share the same database and structure.

---

## 🎬 Preview

### 🔍 Search
<img src="https://raw.githubusercontent.com/Pal-droid/Mangabuddy-Downloader/main/images/search.gif" alt="preview" width="80%"/>

### 💾 Download
<img src="https://raw.githubusercontent.com/Pal-droid/Mangabuddy-Downloader/main/images/downloading.gif" alt="preview" width="80%"/>

---

## ✨ Features

- 🔎 Search manga by title  
- 📖 View available chapters  
- ⬇️ Download selected or all chapters  
- ⚡ Uses fast `httpx` requests (no headless browser required)  
- 🪞 Supports multiple mirrors (Mangabuddy, Mangaxyz, Mangapuma, Mangacute, etc.)  
- ⚙️ Configurable `config.json` for custom paths and mirrors  
- 🌀 CLI animations and progress feedback  
- 🔁 Auto-updater via `update.py`

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Pal-droid/Mangabuddy-Downloader
cd Mangabuddy-Downloader
```

### 2. Install Dependencies

```bash
make install
```

### 3. Configure Settings

Edit the `config.json` file to set your paths and preferences:

```json
{
  "output_path": "/path/to/downloads",
  "debug": false,
  "mirror_domain": "https://mangabuddy.com"
}
```

**Available mirrors:**
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
make run
```

---

## 🧠 Updating

Check for updates and automatically pull the latest version:

```bash
make update
```

---

## 🐧 Ubuntu / Debian Setup

```bash
git clone https://github.com/Pal-droid/Mangabuddy-Downloader
cd Mangabuddy-Downloader
python3 -m venv MangaBuddy-Downloader-venv
MangaBuddy-Downloader-venv/bin/pip install -r requirements.txt
```

Then run:

```bash
MangaBuddy-Downloader-venv/bin/python3 mangaxyz.py
```

---

## PR'S Welcomed!
