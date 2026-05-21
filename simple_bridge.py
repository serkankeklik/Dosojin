import urllib.request
import urllib.error
import base64
import json
import os

# ========== CONFIGURATION ==========
USER = "serkankeklik"
REPO = "Dosojin"
# Get your token at https://github.com/settings/tokens (select 'repo' scope)
TOKEN = "your_github_token_here"   # <-- CHANGE THIS
# ===================================

API_ROOT = f"https://api.github.com/repos/{USER}/{REPO}/contents"

def http_request(url, data=None, method="GET"):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if data:
        req.add_header("Content-Type", "application/json")
        req.method = method
        return urllib.request.urlopen(req, data=json.dumps(data).encode())
    else:
        req.method = method
        return urllib.request.urlopen(req)

def upload_file(local_path):
    if not os.path.isfile(local_path):
        print(f"❌ File not found: {local_path}")
        return False
    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()
    # Try to get existing file SHA
    sha = None
    try:
        req = urllib.request.Request(f"{API_ROOT}/{local_path}")
        req.add_header("Authorization", f"token {TOKEN}")
        resp = urllib.request.urlopen(req)
        sha = json.load(resp).get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"⚠️ Error checking file: {e}")
    # Prepare upload data
    data = {
        "message": f"Upload {local_path} from Pyto",
        "content": content_b64,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    try:
        req = urllib.request.Request(f"{API_ROOT}/{local_path}", method="PUT")
        req.add_header("Authorization", f"token {TOKEN}")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, data=json.dumps(data).encode())
        print(f"✅ Uploaded: {local_path}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def download_file(remote_path):
    url = f"{API_ROOT}/{remote_path}"
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"token {TOKEN}")
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            content = base64.b64decode(data["content"])
            with open(remote_path, "wb") as f:
                f.write(content)
            print(f"✅ Downloaded: {remote_path}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ File not on GitHub: {remote_path}")
        else:
            print(f"❌ Error: {e}")
        return False

def list_remote_files():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents?ref=main"
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"token {TOKEN}")
        with urllib.request.urlopen(req) as resp:
            items = json.load(resp)
            files = [item["name"] for item in items if item["type"] == "file"]
            return files
    except:
        return []

def push_all():
    print("\n📤 Pushing all files...")
    for f in os.listdir("."):
        if os.path.isfile(f) and not f.endswith(".pyc"):
            upload_file(f)

def pull_all():
    print("\n📥 Pulling all files...")
    remote_files = list_remote_files()
    if not remote_files:
        print("No files found in repo or cannot connect.")
        return
    for f in remote_files:
        download_file(f)

def main():
    if TOKEN == "your_github_token_here":
        print("⚠️ ERROR: You need to set your GitHub token.")
        print("   Get one at https://github.com/settings/tokens (select 'repo')")
        return
    while True:
        print("\n" + "="*35)
        print("  SIMPLE GITHUB BRIDGE")
        print("="*35)
        print("1. Push all local files → GitHub")
        print("2. Pull all files from GitHub → here")
        print("3. Exit")
        choice = input("Choice (1/2/3): ")
        if choice == "1":
            push_all()
        elif choice == "2":
            pull_all()
        elif choice == "3":
            print("Bye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()