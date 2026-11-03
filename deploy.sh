#!/usr/bin/env bash
# Build every deck and publish docs/ to GitHub Pages.
#
# Idempotent: first run creates the repo and turns Pages on; later runs just
# commit and push. Pages is served from the main branch /docs folder, so no
# extra branch or Actions workflow is involved.
#
# Usage:
#   ./deploy.sh                 # commit, push, report the URL
#   ./deploy.sh -m "message"    # custom commit message
#   ./deploy.sh --private       # create the repo private (first run only)
#   ./deploy.sh --name my-repo  # repo name (default: directory name)

set -euo pipefail

cd "$(dirname "$0")"

REPO_NAME="$(basename "$PWD")"
VISIBILITY="--public"
MSG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message) MSG="$2"; shift 2 ;;
    --private) VISIBILITY="--private"; shift ;;
    --public)  VISIBILITY="--public";  shift ;;
    --name) REPO_NAME="$2"; shift 2 ;;
    -h|--help) sed -n '2,13p' "$0" | sed 's/^# \?//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

die() { printf '\nerror: %s\n' "$1" >&2; exit 1; }

# --- Preconditions ----------------------------------------------------------

command -v git >/dev/null || die "git is not installed"
command -v gh  >/dev/null || die "the GitHub CLI (gh) is not installed"

if ! gh auth status >/dev/null 2>&1; then
  cat >&2 <<'EOF'

error: not logged in to GitHub.

Run this yourself (it needs an interactive browser/device prompt):

    gh auth login

Choose: GitHub.com → HTTPS → authenticate with a browser, and make sure the
token includes the 'repo' and 'workflow' scopes. Then re-run ./deploy.sh
EOF
  exit 1
fi

# --- Build ------------------------------------------------------------------

echo "==> building"
python3 build.py

echo "==> checking"
if ! python3 check.py; then
  die "check.py reported errors — fix them, or run build/deploy again once resolved"
fi

[[ -f docs/index.html ]] || die "docs/index.html missing after build"

# --- Git repo ---------------------------------------------------------------

if [[ ! -d .git ]]; then
  echo "==> initialising git repo"
  git init -q
  git symbolic-ref HEAD refs/heads/main
fi

# Identity, only if unset, so we never clobber a real global config.
git config user.name  >/dev/null 2>&1 || git config user.name  "deck-bot"
git config user.email >/dev/null 2>&1 || git config user.email "deck-bot@users.noreply.github.com"

CURRENT_BRANCH="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo main)"
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  echo "==> on branch '$CURRENT_BRANCH' (not main); Pages reads main/docs"
fi

git add -A
if git diff --cached --quiet 2>/dev/null; then
  echo "==> no changes to commit"
else
  if [[ -z "$MSG" ]]; then
    N=$(find decks -maxdepth 2 -name slides.html 2>/dev/null | wc -l | tr -d ' ')
    MSG="Publish ${N} deck(s)"
  fi
  git commit -q -m "$MSG

Co-Authored-By: Claude <noreply@anthropic.com>"
  echo "==> committed: $MSG"
fi

# --- Remote -----------------------------------------------------------------

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "==> creating GitHub repo '$REPO_NAME'"
  gh repo create "$REPO_NAME" $VISIBILITY --source=. --remote=origin \
    --description "HTML presentation decks" \
    || die "could not create the repo (does '$REPO_NAME' already exist on your account?)"
fi

SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
OWNER="${SLUG%%/*}"
NAME="${SLUG##*/}"

echo "==> pushing to $SLUG"
git push -u origin "$CURRENT_BRANCH"

# --- Pages ------------------------------------------------------------------

echo "==> configuring GitHub Pages (branch: $CURRENT_BRANCH, folder: /docs)"
if gh api "repos/$SLUG/pages" >/dev/null 2>&1; then
  gh api -X PUT "repos/$SLUG/pages" \
    -f "source[branch]=$CURRENT_BRANCH" -f "source[path]=/docs" >/dev/null \
    || echo "    ! could not update the Pages source; check Settings → Pages"
else
  gh api -X POST "repos/$SLUG/pages" \
    -f "source[branch]=$CURRENT_BRANCH" -f "source[path]=/docs" >/dev/null \
    || echo "    ! could not enable Pages automatically; set it in Settings → Pages"
fi

URL="https://${OWNER}.github.io/${NAME}/"

# Pages builds asynchronously; poll briefly so we can report real status.
echo "==> waiting for the first Pages build"
for i in $(seq 1 20); do
  STATUS="$(gh api "repos/$SLUG/pages" -q .status 2>/dev/null || echo unknown)"
  if [[ "$STATUS" == "built" ]]; then break; fi
  sleep 6
done

CODE="$(curl -sS -o /dev/null -w '%{http_code}' -L "$URL" 2>/dev/null || echo 000)"

cat <<EOF

────────────────────────────────────────────────────────────
  Live at:  $URL
  Repo:     https://github.com/$SLUG
  Pages:    status=${STATUS:-unknown}  http=${CODE}
────────────────────────────────────────────────────────────
EOF

if [[ "$CODE" != "200" ]]; then
  cat <<EOF
The first Pages build can take 1-3 minutes. If the URL 404s, wait a moment and
reload, or check: https://github.com/$SLUG/settings/pages
EOF
fi
