#!/usr/bin/env bash
# Run this from the "Master thesis" folder AFTER:
#   1. sudo apt install git    (or your distro’s git package)
#   2. gh auth login           (choose GitHub.com, HTTPS, login via browser)
#
# Edit REPO_NAME if you want a different repository name on GitHub.

set -euo pipefail
cd "$(dirname "$0")"

REPO_NAME="${REPO_NAME:-master-thesis}"
GITHUB_EMAIL="${GITHUB_EMAIL:-areejmohamedsaad@gmail.com}"
# Set your name as it should appear on commits:
GIT_NAME="${GIT_NAME:-Areej Mohamed Saad}"

if ! command -v git >/dev/null 2>&1; then
  echo "Install git first, e.g.: sudo apt install git"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) not found."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Run: gh auth login"
  exit 1
fi

if [ ! -d .git ]; then
  git init
fi

git config user.email "$GITHUB_EMAIL"
git config user.name "$GIT_NAME"

git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit."
else
  git commit -m "Initial commit: thesis notes and resources" || true
fi

# Create private repo on GitHub and push (skip if remote already exists)
if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" --private --source=. --remote=origin --push
  echo "Done. Private repo: https://github.com/$(gh api user -q .login)/$REPO_NAME"
else
  echo "Remote 'origin' already set. Pushing..."
  git push -u origin HEAD
fi
