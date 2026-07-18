# Profile art pipeline

Scripts that generate the animated SVGs on my GitHub profile. Everything is a
self-contained SVG committed to this repo — no third-party stats services, no
token required for the daily refresh.

## Scripts

| Script | Input | Output | When it runs |
|---|---|---|---|
| `prep_photo.py` | `source-photo.jpg` | `source-prepped.png` | Locally, when the photo changes |
| `make_ascii_svg.py` | `source-prepped.png` | `avi-ascii.svg` | Locally, after `prep_photo.py` |
| `make_info_card.py` | (edit script) | `info-card.svg` | Locally, when details change |
| `make_typing_svg.py` | (edit `PHRASES`) | `typing-header.svg` | Locally, when phrases change |
| `make_stack_svg.py` | (edit `TECHS`) | `stack.svg` | Locally, when stack changes |
| `make_pixel_svg.py` | (edit `TEXT`) | `pixel-banner.svg` | Locally, retro banner |
| `make_terminal_quest.py` | (edit `STORY`) | injects into `README.md` | Locally, choose-your-path game |
| `fetch_contributions.py` | public GitHub HTML | `data/contributions.json` | Daily (Actions) |
| `render_heatmap_svg.py` | `data/contributions.json` | `contrib-heatmap.svg` | Daily (Actions) |
| `render_streak_svg.py` | `data/contributions.json` | `streak-stats.svg` | Daily (Actions) |

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt   # add rembg[cpu] for the portrait
```

## Regenerate the static art

```bash
python scripts/prep_photo.py source-photo.jpg
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/make_typing_svg.py
```

## Refresh the live data (also automated daily)

```bash
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
python scripts/render_streak_svg.py
```

## Why self-hosted SVG

Hosted README widgets render on someone else's server, rate-limit, and
occasionally break with a broken-image icon. Generating our own SVGs means the
art is committed here, loads instantly, and the only moving part is a public
GitHub HTML endpoint that needs no auth.
