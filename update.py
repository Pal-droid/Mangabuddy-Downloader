import os
import json
import subprocess
import sys
import httpx
from yaspin import yaspin
from yaspin.spinners import Spinners

# ✅ Correct repo URLs
REPO_URL = "https://github.com/Pal-droid/Mangabuddy-Downloader"
RAW_MANIFEST_URL = "https://raw.githubusercontent.com/Pal-droid/Mangabuddy-Downloader/main/manifest.json"
LOCAL_MANIFEST_PATH = "manifest.json"


def load_local_manifest():
    if not os.path.exists(LOCAL_MANIFEST_PATH):
        print("[!] No local manifest.json found.")
        return None
    with open(LOCAL_MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


async def fetch_remote_manifest():
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        resp = await client.get(RAW_MANIFEST_URL)
        resp.raise_for_status()
        return resp.json()


async def main():
    local_manifest = load_local_manifest()
    if not local_manifest:
        return

    with yaspin(Spinners.dots, text="💥 Checking for updates...") as spinner:
        try:
            remote_manifest = await fetch_remote_manifest()
        except Exception as e:
            spinner.fail("💥")
            print(f"Failed to fetch remote manifest: {e}")
            return

        local_version = local_manifest.get("version")
        remote_version = remote_manifest.get("version")

        if not local_version or not remote_version:
            spinner.fail("⚠️")
            print("Manifest missing version info.")
            return

        if local_version == remote_version:
            spinner.ok("✅")
            print(f"You're up to date (v{local_version})")
            return

        spinner.text = f"New version available: {remote_version} (local v{local_version})"
        spinner.ok("⬇️")
        print("Updating repository...")

        if not os.path.exists(".git"):
            print("[!] No .git folder found — performing fresh clone.")
            repo_name = REPO_URL.split("/")[-1]
            os.chdir(os.path.expanduser("~"))
            subprocess.run(["rm", "-rf", repo_name], check=False)
            subprocess.run(["git", "clone", REPO_URL], check=True)
        else:
            subprocess.run(["git", "pull", "origin", "main"], check=True)

        print("✅ Update complete! Restart your tool to use the latest version.")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled.")