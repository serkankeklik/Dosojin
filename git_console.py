import requests
import base64
import os

GITHUB_USER = "serkankeklik"
REPO_NAME = "Dosojin"
GITHUB_TOKEN = "your_token_here"   # <-- CHANGE THIS

API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents"
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def get_file_sha(path):
    resp = requests.get(f"{API_URL}/{path}", headers=headers)
    return resp.json().get("sha") if resp.status_code == 200 else None

def upload_file(local_path, remote_path=None):
    if remote_path is None:
        remote_path = local_path
    try:
        with open(local_path, "rb") as f:
            content = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        print(f"Missing: {local_path}")
        return False
    sha = get_file_sha(remote_path)
    data = {"message": f"Update {remote_path}", "content": content, "branch": "main"}
    if sha:
        data["sha"] = sha
    resp = requests.put(f"{API_URL}/{remote_path}", headers=headers, json=data)
    if resp.status_code in [200, 201]:
        print(f"Uploaded: {remote_path}")
        return True
    print(f"Failed: {resp.text}")
    return False

def download_file(remote_path, local_path=None):
    if local_path is None:
        local_path = remote_path
    resp = requests.get(f"{API_URL}/{remote_path}", headers=headers)
    if resp.status_code != 200:
        print(f"Not found: {remote_path}")
        return False
    content = base64.b64decode(resp.json()["content"])
    with open(local_path, "wb") as f:
        f.write(content)
    print(f"Downloaded: {remote_path}")
    return True

def push_all_files():
    for item in os.listdir("."):
        if os.path.isfile(item) and not item.endswith(".pyc"):
            upload_file(item)

def pull_all_files():
    resp = requests.get(f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents?ref=main", headers=headers)
    if resp.status_code != 200:
        print("Failed to get file list")
        return
    for item in resp.json():
        if item["type"] == "file":
            download_file(item["path"])

def main():
    if GITHUB_TOKEN == "your_token_here":
        print("ERROR: Please set your GitHub token in the script")
        return
    while True:
        print("\n1. Push all files\n2. Pull all files\n3. Exit")
        choice = input("Choice: ")
        if choice == "1":
            push_all_files()
        elif choice == "2":
            pull_all_files()
        elif choice == "3":
            break
        else:
            print("Invalid")

if __name__ == "__main__":
    main()