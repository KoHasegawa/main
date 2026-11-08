# Crypto market-cap TOP10 race (v4)

Archived 9:16 bar-chart race. The MP4 in this folder is the finished v4 render and is stored as-is. This import does not regenerate it.

## Files

| File | Role |
| --- | --- |
| `crypto_mcap_top10_9x16_v4.mp4` | Finished video. 1080×1920, 30 fps, H.264 yuv420p, 535 frames, 17.833 s. |
| `proof_v4.png` | Still of the early frame (1080×1920). |
| `theme_corner.png` | Bottom-right corner mark (600×600 RGBA). |
| `crypto_mcap_raw.csv` | CoinMarketCap historical listings, one row per coin per date. |
| `crypto_mcap_wide.csv` | Same snapshots pivoted to one row per date. This is what the generator reads. |
| `generate_race_v4.py` | Matplotlib / Pillow / imageio renderer. |
| `fetch_cmc_historical.py` | Downloader that wrote the raw CSV. Unchanged. |
| `requirements.txt` | Python packages to import those scripts. |

`crypto_mcap_wide.csv` matches the raw file: 143 dates, 56 coin columns, market caps equal to the raw values, and `0` where a coin is absent that day. No pivot script is included.

## Picture

English UI only (`THE CRYPTO 10`, `MARKET CAP LEADERBOARD`, `MARKET CAP • USD`, `Mon DD, YYYY`, USD value labels, source line). Rank positions are not numbered. Each badge is the coin color with the ticker’s first letter.

Bars use a small fixed corner radius (`FIXED_ROUND_Y = 0.05`, about 7 px), capped so the radius stays under a quarter of the bar height. The horizontal axis maximum is the market cap of the coin currently leading the visible top 10, with no extra headroom, so that leader fills the track.

The corner mark is drawn at 220 px and 35% opacity. Those are the constants in `generate_race_v4.py`. An older note in the module docstring still says 240 px and 0.40.

## Date coverage

Both CSVs are snapshots every 3 days from **2017-11-01** through **2019-01-01** (143 dates, 25 coins on each raw date, 3,575 raw rows, 56 distinct names).

The renderer keeps rows on or after **2017-12-01** (133 dates) and holds the last frame for 1.6 s. November 2017 is in the CSVs and is not in the video.

## Setup

Python 3. `ffmpeg` with libx264 must be on `PATH` (`imageio` calls it when writing the MP4). The archived file was encoded by Lavf/Lavc 63.1.102.

```bash
cd ranking-in-motion/crypto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Fonts are Barlow, six files:

- `Barlow-BlackItalic.ttf`
- `Barlow-Black.ttf`
- `Barlow-Bold.ttf`
- `Barlow-SemiBold.ttf`
- `Barlow-Medium.ttf`
- `Barlow-Regular.ttf`

The script uses the first directory that contains all six:

1. `/usr/share/fonts/truetype/sand-box/google/Barlow` (path used for the archived render)
2. `fonts/Barlow/` next to `generate_race_v4.py`

Barlow is the [SIL Open Font License](https://openfontlicense.org/) family from [Google Fonts](https://fonts.google.com/specimen/Barlow). The font files are not in this folder. Another family will change name widths and the layout, so the script does not substitute one.

## Reproduce

From this directory, with the venv active and Barlow installed:

```bash
python3 generate_race_v4.py
```

That overwrites `crypto_mcap_top10_9x16_v4.mp4` and `proof_v4.png`, and also writes `proof_v4_early.png` and `proof_v4_mid.png` (gitignored). A new encode will not match the archived MP4 byte for byte: matplotlib, Pillow, Barlow file revisions, and ffmpeg all affect the pixels and the bitstream. The archived MP4 is the deliverable.

Refreshing the download overwrites `crypto_mcap_raw.csv` in the current working directory and does not rebuild the wide CSV:

```bash
python3 fetch_cmc_historical.py
```

Run it from this directory. It requests `https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical` every 3 days from 2017-11-01 through 2019-01-01. That endpoint can change, rate-limit, or reject the client; nothing here retries beyond the script’s three attempts per date. Do not commit `.venv/`, `__pycache__/`, or API credentials.
