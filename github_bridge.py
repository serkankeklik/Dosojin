import urllib.request
import urllib.error
import base64
import json
import os

# ========== YOUR SETTINGS ==========
USER = "serkankeklik"
REPO = "Dosojin"
# Get token at https://github.com/settings/tokens (scope: repo)
TOKEN = "your_github_token_here"   # <-- CHANGE THIS
# ===================================

API_ROOT = f"https://api.github.com/repos/{USER}/{REPO}/contents"

def get_file_sha(path):
    """Return SHA of file if it exists on GitHub, else None."""
    url = f"{API_ROOT}/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {TOKEN}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp).get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"⚠️ Error checking {path}: {e}")
        return None

def upload_file(local_path):
    """Upload a single file to GitHub (creates or updates)."""
    if not os.path.isfile(local_path):
        print(f"❌ Not a file: {local_path}")
        return False

    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    sha = get_file_sha(local_path)
    data = {
        "message": f"Upload {local_path} from Pyto",
        "content": content_b64,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha

    url = f"{API_ROOT}/{local_path}"
    req = urllib.request.Request(url, method="PUT")
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, data=json.dumps(data).encode())
        print(f"✅ Uploaded: {local_path}")
        return True
    except Exception as e:
        print(f"❌ Upload failed {local_path}: {e}")
        return False

def download_file(remote_path):
    """Download a file from GitHub to current folder."""
    url = f"{API_ROOT}/{remote_path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {TOKEN}")
    try:
        with urllib.request.urlopen(req) as resp:
            info = json.load(resp)
            content = base64.b64decode(info["content"])
            with open(remote_path, "wb") as f:
                f.write(content)
            print(f"✅ Downloaded: {remote_path}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ Not on GitHub: {remote_path}")
        else:
            print(f"❌ Download error {remote_path}: {e}")
        return False

def list_remote_files():
    """Return list of file names in repo root."""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents?ref=main"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {TOKEN}")
    try:
        with urllib.request.urlopen(req) as resp:
            items = json.load(resp)
            return [item["name"] for item in items if item["type"] == "file"]
    except Exception as e:
        print(f"❌ Could not list remote files: {e}")
        return []

def push_all():
    """Upload all local files (except this script and cache files)."""
    print("\n📤 Pushing local files to GitHub...")
    count = 0
    for item in os.listdir("."):
        if os.path.isfile(item) and not item.endswith((".pyc", ".DS_Store")):
            if item == "github_bridge.py":
                print(f"⏩ Skipping bridge script (optional)")
                continue
            if upload_file(item):
                count += 1
    print(f"\n✅ Pushed {count} file(s).")

def pull_all():
    """Download all files from GitHub repo (overwrites local)."""
    print("\n📥 Pulling files from GitHub...")
    remote_files = list_remote_files()
    if not remote_files:
        print("No files found in GitHub repo.")
        return
    count = 0
    for fname in remote_files:
        if download_file(fname):
            count += 1
    print(f"\n✅ Pulled {count} file(s).")

def main():
    if TOKEN == "your_github_token_here":
        print("⚠️ ERROR: You must set your GitHub token in the script.")
        print("   Get one at https://github.com/settings/tokens (check 'repo')")
        return

    while True:
        print("\n" + "="*35)
        print("  SIMPLE GITHUB BRIDGE")
        print("="*35)
        print("1. Push all local files → GitHub")
        print("2. Pull all files from GitHub → here")
        print("3. Exit")
        choice = input("Choice (1/2/3): ").strip()

        if choice == "1":
            push_all()
        elif choice == "2":
            pull_all()
        elif choice == "3":
            print("Bye! 👋")
            break
        else:
            print("❌ Invalid choice, enter 1, 2 or 3.")

if __name__ == "__main__":
    main()