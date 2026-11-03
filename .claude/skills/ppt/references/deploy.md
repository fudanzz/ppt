# Publishing

`./deploy.sh` builds, lints, commits, pushes, and turns on GitHub Pages. Pages
serves the `main` branch `/docs` folder, so generated output is committed to the
repo and no Actions workflow or `gh-pages` branch is involved.

## One-time authentication

`deploy.sh` stops with instructions if GitHub auth is missing. **You cannot do
this step for the user** — it needs an interactive browser or device prompt.
Ask them to run it in the session with the `!` prefix:

```
! gh auth login
```

They should pick: GitHub.com → HTTPS → authenticate with a browser, and the
token needs the `repo` scope (plus `workflow` if they later add Actions).

Verify with `gh auth status` before retrying the deploy.

## Normal run

```bash
./deploy.sh                        # default commit message
./deploy.sh -m "Add Q4 review"     # custom message
./deploy.sh --private              # private repo (first run only)
./deploy.sh --name my-decks        # repo name (default: directory name)
```

The final URL is `https://<owner>.github.io/<repo>/` — the gallery, with each
deck at `/<slug>/`.

## Visibility

A `--public` repo means **anyone with the link can read every deck**, and
GitHub Pages sites on free accounts are always public even from a private repo.
Before the first deploy, confirm with the user that the deck content is okay to
publish, and say so plainly rather than assuming. If the content is sensitive,
options are: a private repo on a paid plan (Pages access control), or skip
Pages and hand them the `docs/` folder.

## Timing

The first Pages build takes 1–3 minutes; later pushes are usually under a
minute. `deploy.sh` polls for up to two minutes and reports the HTTP status, so
a `200` means it is genuinely live. A non-200 at the end is normal on the very
first deploy — tell the user to reload shortly rather than treating it as a
failure.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `not logged in to GitHub` | Run `! gh auth login` |
| `could not create the repo` | Name already taken — rerun with `--name` |
| Pages 404 after several minutes | Check Settings → Pages shows `main` + `/docs` |
| CSS missing, unstyled slides | `.nojekyll` absent from `docs/` — rerun `build.py` |
| Changes not live | The build ran but the commit didn't; check `git status` |

## Local preview instead

To look at a deck without publishing:

```bash
python3 build.py --serve 8080
```

That serves `docs/` on port 8080. Note that in a sandboxed environment the host
may not be reachable from the user's own machine — in that case publishing is
the only way they will actually see it.
