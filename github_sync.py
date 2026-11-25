"""
SoundCraft GitHub Sync Utility
Allows syncing/pushing this repository directly to any GitHub remote URL using Dulwich.
"""

import sys
import argparse
from dulwich import porcelain

def main():
    parser = argparse.ArgumentParser(description="Push SoundCraft project to GitHub")
    parser.add_argument("--url", help="GitHub repository URL (e.g. https://github.com/username/repo.git)")
    parser.add_argument("--token", help="GitHub Personal Access Token (PAT)")
    args = parser.parse_args()

    repo = porcelain.open_repo('.')
    if not args.url:
        print("[INFO] Git repository is initialized and committed locally on branch 'main'.")
        print("To push to your GitHub repo, run:")
        print("  python github_sync.py --url https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git --token <YOUR_TOKEN>")
        return

    remote_url = args.url
    if args.token and "@" not in remote_url:
        remote_url = remote_url.replace("https://", f"https://{args.token}@")

    print(f"Connecting to {args.url}...")
    try:
        porcelain.push(repo, remote_url, refspecs=[b"refs/heads/main:refs/heads/main"])
        print("[SUCCESS] All files and backend code successfully pushed to GitHub!")
    except Exception as e:
        print(f"[ERROR] Push failed: {e}")

if __name__ == "__main__":
    main()
