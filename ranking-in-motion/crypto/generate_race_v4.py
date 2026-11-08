#!/usr/bin/env python3
"""
Crypto Market Cap TOP10 bar race — v4 dark navy leaderboard.
vmax = current visible #1 market cap (no padding; leader fills track).
Builds on v3 fixes. Plus:
  - Bar scale vmax = max among currently displayed TOP10 (prefer #1 value); no *1.02 pad
Fixes vs v2 (retained):
  - Solid horizontal pills (rounding capped to half height & half width; no pinch)
  - Smaller watermark (240px, opacity 0.40)
  - Ticker placed after measured name width (no overlap)
  - Leader glow via soft ellipses (does not distort bar shape)
9:16 YouTube Short, English UI, no rank numbers, absolute $B values.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Ellipse, PathPatch, Rectangle
from matplotlib.path import Path as MPath
from matplotlib.colors import to_rgb
import numpy as np
import pandas as pd
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT_MP4 = ROOT / "crypto_mcap_top10_9x16_v4.mp4"
PROOF = ROOT / "proof_v4.png"
PROOF_EARLY = ROOT / "proof_v4_early.png"
PROOF_MID = ROOT / "proof_v4_mid.png"
DATA_CSV = ROOT / "crypto_mcap_wide.csv"
THEME_IMG = ROOT / "theme_corner.png"

WATERMARK_OPACITY = 0.35
WATERMARK_SIZE = 220
WATERMARK_MARGIN_R = 20
WATERMARK_MARGIN_B = 36

W, H = 1080, 1920
DPI = 100
FIGSIZE = (W / DPI, H / DPI)
FPS = 30

# Dark navy palette (mockup)
BG = "#070B18"
HEADER_LINE = "#2A3350"
TRACK = "#141C2E"
MUTED = "#8B95B0"
WHITE = "#FFFFFF"
GOLD = "#D4C4A8"
AXIS = "#5A6580"

# Barlow (SIL OFL). The v4 frames used the absolute path below. A checkout can
# instead drop the same six files in fonts/Barlow next to this script.
_BARLOW_FILES = (
    "Barlow-BlackItalic.ttf",
    "Barlow-Black.ttf",
    "Barlow-Bold.ttf",
    "Barlow-SemiBold.ttf",
    "Barlow-Medium.ttf",
    "Barlow-Regular.ttf",
)
_BARLOW_CANDIDATES = (
    Path("/usr/share/fonts/truetype/sand-box/google") / "Barlow",
    ROOT / "fonts" / "Barlow",
)


def _resolve_barlow_dir() -> Path:
    for cand in _BARLOW_CANDIDATES:
        if all((cand / name).is_file() for name in _BARLOW_FILES):
            return cand
    tried = ", ".join(str(p) for p in _BARLOW_CANDIDATES)
    raise SystemExit(
        "Barlow font files not found. Place "
        + ", ".join(_BARLOW_FILES)
        + f" in one of: {tried}. See README.md."
    )


BARLOW = _resolve_barlow_dir()
TITLE_ITALIC = str(BARLOW / "Barlow-BlackItalic.ttf")
TITLE_BOLD = str(BARLOW / "Barlow-Black.ttf")
BODY_BOLD = str(BARLOW / "Barlow-Bold.ttf")
BODY_SEMI = str(BARLOW / "Barlow-SemiBold.ttf")
BODY_MED = str(BARLOW / "Barlow-Medium.ttf")
BODY_REG = str(BARLOW / "Barlow-Regular.ttf")

TICKERS = {
    "Bitcoin": "BTC",
    "Ethereum": "ETH",
    "XRP": "XRP",
    "Bitcoin Cash": "BCH",
    "Litecoin": "LTC",
    "Cardano": "ADA",
    "EOS": "EOS",
    "Stellar": "XLM",
    "IOTA": "IOTA",
    "Tether": "USDT",
    "Monero": "XMR",
    "Neo": "NEO",
    "TRON": "TRX",
    "NEM": "XEM",
    "Dash": "DASH",
    "Bitcoin SV": "BSV",
    "Bitcoin Gold": "BTG",
    "Ethereum Classic": "ETC",
    "Binance Coin": "BNB",
    "BNB": "BNB",
    "Zcash": "ZEC",
    "Qtum": "QTUM",
    "OmiseGO": "OMG",
    "VeChain": "VET",
    "Vechain [Token]": "VEN",
    "Icon": "ICX",
    "ICON": "ICX",
    "Tezos": "XTZ",
    "Ontology": "ONT",
    "Zilliqa": "ZIL",
    "Dogecoin": "DOGE",
    "Maker": "MKR",
    "Waves": "WAVES",
    "Decred": "DCR",
    "BitConnect": "BCC",
    "Lisk": "LSK",
    "Stratis": "STRAT",
    "Verge": "XVG",
    "Siacoin": "SC",
    "Bytecoin": "BCN",
    "Steem": "STEEM",
    "Nano": "NANO",
    "0x": "ZRX",
    "Ardor": "ARDR",
    "Ark": "ARK",
    "BitShares": "BTS",
    "Bitcore": "BTX",
    "Bytom": "BTM",
    "HyperCash": "HC",
    "Komodo": "KMD",
    "MonaCoin": "MONA",
    "Nxt": "NXT",
    "Populous": "PPT",
    "Pundi X": "NPXS",
    "Status": "SNT",
    "TrueUSD": "TUSD",
    "USD Coin": "USDC",
    "ERC20": "ERC20",
}

COIN_COLORS = {
    "Bitcoin": "#F7931A",
    "Ethereum": "#8A92B2",
    "XRP": "#00A2E8",
    "Bitcoin Cash": "#0AC18E",
    "Litecoin": "#345D9D",
    "Cardano": "#3468FC",
    "EOS": "#8B90A5",
    "Stellar": "#14B6E7",
    "IOTA": "#00E0C3",
    "Tether": "#26A17B",
    "Monero": "#FF6600",
    "Neo": "#00E599",
    "TRON": "#FF060A",
    "NEM": "#67B2E8",
    "Dash": "#008DE4",
    "Bitcoin SV": "#EAB300",
    "Bitcoin Gold": "#EBA809",
    "Ethereum Classic": "#3AB83A",
    "Binance Coin": "#F3BA2F",
    "BNB": "#F3BA2F",
    "Zcash": "#F4B728",
    "Qtum": "#2E9AD0",
    "OmiseGO": "#1A53F0",
    "VeChain": "#15BDFF",
    "Vechain [Token]": "#15BDFF",
    "ICON": "#1FC5C9",
    "Tezos": "#2C7DF7",
    "Ontology": "#32A4BE",
    "Zilliqa": "#49C1BF",
    "Dogecoin": "#C2A633",
    "Maker": "#1AAB9B",
    "Waves": "#0055FF",
    "Decred": "#2ED6A1",
    "BitConnect": "#F7931A",
    "Lisk": "#1A78F0",
    "Stratis": "#1382C4",
    "Verge": "#37B0E9",
    "Siacoin": "#20EE82",
    "Bytecoin": "#F04036",
    "Steem": "#1A5099",
    "Nano": "#4A90E2",
    "0x": "#6B6B8A",
}

PALETTE_FALLBACK = [
    "#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#44AF69",
    "#F8333C", "#FCAB10", "#2B9EB3", "#7D53DE", "#3B1F2B",
]

# Axes geometry (must match draw_frame)
AX_LEFT, AX_BOTTOM, AX_W, AX_H = 0.055, 0.072, 0.89, 0.78
AXES_PX_W = AX_W * W  # ~961 px


def setup_fonts():
    for p in (TITLE_ITALIC, TITLE_BOLD, BODY_BOLD, BODY_SEMI, BODY_MED, BODY_REG):
        try:
            font_manager.fontManager.addfont(p)
        except Exception:
            pass
    return {
        "title_it": font_manager.FontProperties(fname=TITLE_ITALIC),
        "title": font_manager.FontProperties(fname=TITLE_BOLD),
        "bold": font_manager.FontProperties(fname=BODY_BOLD),
        "semi": font_manager.FontProperties(fname=BODY_SEMI),
        "med": font_manager.FontProperties(fname=BODY_MED),
        "reg": font_manager.FontProperties(fname=BODY_REG),
    }


FP = setup_fonts()

_PIL_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def pil_font(path: str, size_pt: int) -> ImageFont.FreeTypeFont:
    # Matplotlib fontsize is in points; PIL size is roughly px at 96dpi ≈ pt * 96/72
    # Our figure is 100 dpi, so px ≈ pt * 100/72
    key = (path, size_pt)
    if key not in _PIL_FONT_CACHE:
        px = max(1, int(round(size_pt * DPI / 72.0)))
        _PIL_FONT_CACHE[key] = ImageFont.truetype(path, px)
    return _PIL_FONT_CACHE[key]


def text_width_axes(text: str, fontsize: int, font_path: str) -> float:
    """Return text width in axes x-units (xlim 0..1)."""
    font = pil_font(font_path, fontsize)
    bbox = font.getbbox(text)
    w_px = max(1, bbox[2] - bbox[0])
    return w_px / AXES_PX_W


def fmt(v: float) -> str:
    if v >= 1e12:
        return f"${v / 1e12:.2f}T"
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    if v >= 1e6:
        return f"${v / 1e6:.0f}M"
    return f"${v:,.0f}"


def ticker_for(name: str) -> str:
    if name in TICKERS:
        return TICKERS[name]
    cleaned = "".join(ch for ch in name if ch.isalnum())
    return (cleaned[:4] or "??").upper()


def color_for(name: str) -> str:
    return COIN_COLORS.get(name, PALETTE_FALLBACK[hash(name) % len(PALETTE_FALLBACK)])


def icon_letter(name: str) -> str:
    t = ticker_for(name)
    return t[0] if t else "?"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_CSV, parse_dates=["date"])
    cols = [c for c in df.columns if c != "date"]
    return df.set_index("date")[cols]


def top_ranks(values: pd.Series, n: int = 10) -> dict[str, float]:
    top = values.sort_values(ascending=False).head(n)
    return {name: float(i) for i, name in enumerate(top.index.tolist())}


def visible_vmax(values: pd.Series, y_pos: dict[str, float], y_cut: float = 10.0) -> float:
    """Scale max = market cap of the current visible #1 (fills the track, no pad)."""
    visible = [
        (name, float(y))
        for name, y in y_pos.items()
        if y < y_cut and float(values.get(name, 0.0) or 0.0) > 0
        and np.isfinite(float(values.get(name, 0.0) or 0.0))
    ]
    if not visible:
        m = float(values.max()) if len(values) else 1.0
        return m if m > 0 else 1.0
    # Rank-1 among displayed rows = smallest y
    leader = min(visible, key=lambda item: item[1])[0]
    vmax = float(values.get(leader, 0.0) or 0.0)
    if not np.isfinite(vmax) or vmax <= 0:
        vmax = max(float(values.get(n, 0.0) or 0.0) for n, _ in visible)
    return vmax if vmax > 0 else 1.0


def ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


_WATERMARK_RGBA = None


def prepare_watermark() -> Image.Image:
    global _WATERMARK_RGBA
    if _WATERMARK_RGBA is not None:
        return _WATERMARK_RGBA
    im = Image.open(THEME_IMG).convert("RGBA")
    im.thumbnail((WATERMARK_SIZE, WATERMARK_SIZE), Image.Resampling.LANCZOS)
    r, g, b, a = im.split()
    a = a.point(lambda p: int(p * WATERMARK_OPACITY))
    _WATERMARK_RGBA = Image.merge("RGBA", (r, g, b, a))
    print(f"watermark={THEME_IMG.name} size={_WATERMARK_RGBA.size} opacity={WATERMARK_OPACITY}")
    return _WATERMARK_RGBA


def composite_watermark(rgb: np.ndarray) -> np.ndarray:
    base = Image.fromarray(rgb).convert("RGBA")
    wm = prepare_watermark()
    x = base.width - wm.width - WATERMARK_MARGIN_R
    y = base.height - wm.height - WATERMARK_MARGIN_B
    base.alpha_composite(wm, (x, y))
    return np.asarray(base.convert("RGB"))


def lighten(hex_color: str, amount: float = 0.35) -> str:
    r, g, b = to_rgb(hex_color)
    r = min(1.0, r + (1 - r) * amount)
    g = min(1.0, g + (1 - g) * amount)
    b = min(1.0, b + (1 - b) * amount)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def contrast_text(hex_color: str) -> str:
    r, g, b = to_rgb(hex_color)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#0A0E18" if lum > 0.55 else "#FFFFFF"


# Axes data → display scale (xlim 0..1, ylim span below).
YLIM_BOTTOM, YLIM_TOP = 9.85, -0.55
YLIM_SPAN = YLIM_BOTTOM - YLIM_TOP  # 10.4
PX_PER_X = (AX_W * W) / 1.0
PX_PER_Y = (AX_H * H) / YLIM_SPAN

# SMALL FIXED corner radius in *y data units* — NOT half the bar height.
# Same mistake as CSS border-radius: 50% (v2 used rounding_size ≈ 0.5 * height).
# Keep ~20–25% of typical bar height max, and always < 50% of min(w, h).
FIXED_ROUND_Y = 0.05  # ≈ 7px on screen; ~19% of bar_h=0.26


def add_h_pill(ax, x0: float, y_center: float, width: float, height: float, **kwargs):
    """
    Solid horizontal rounded bar (CSS border-radius: Npx — NOT 50%).

    Uses a small FIXED corner radius (FIXED_ROUND_Y ≈ 0.05 data-y), aspect-
    corrected for screen pixels. Hard-capped to ≤25% of bar height and
    ≤50% of bar width. v2's bug was rounding_size ≈ 0.5 * height, which is
    the same failure mode as border-radius: 50% on a short element.
    """
    w = max(float(width), 1e-4)
    h = max(float(height), 1e-4)

    # Design radius: small fixed — never half-height
    ry = min(FIXED_ROUND_Y, 0.25 * h)
    rx = ry * PX_PER_Y / PX_PER_X  # equal pixel radius → circular corners on screen
    # Width floor: if bar shorter than 2*rx, shrink both radii (still ≤25% h)
    if w < 2 * rx:
        rx = 0.5 * w
        ry = min(ry, 0.25 * h, rx * PX_PER_X / PX_PER_Y)
    # Absolute safety: never ≥ 50% of either dimension (prevents hourglass path)
    rx = min(rx, 0.499 * w)
    ry = min(ry, 0.499 * h, 0.25 * h)

    facecolor = kwargs.pop("facecolor", None)
    alpha = kwargs.pop("alpha", 1.0)
    zorder = kwargs.pop("zorder", 3)
    kwargs.pop("edgecolor", None)

    y0 = y_center - h / 2
    # Single path = flat body + small rounded corners (no seam)
    path = _rounded_rect_path(x0, y0, w, h, rx, ry)
    ax.add_patch(PathPatch(
        path,
        facecolor=facecolor,
        edgecolor="none",
        linewidth=0,
        alpha=alpha,
        zorder=zorder,
    ))


def _rounded_rect_path(x0: float, y0: float, w: float, h: float, rx: float, ry: float) -> MPath:
    """Axis-aligned rounded rect path; y0 is bottom. rx/ry independent (data units)."""
    rx = min(max(rx, 1e-9), w * 0.5)
    ry = min(max(ry, 1e-9), h * 0.5)
    x1, y1 = x0 + w, y0 + h
    k = 0.5522847498
    ox, oy = rx * k, ry * k
    verts = [
        (x0 + rx, y0),
        (x1 - rx, y0),
        (x1 - rx + ox, y0), (x1, y0 + ry - oy), (x1, y0 + ry),
        (x1, y1 - ry),
        (x1, y1 - ry + oy), (x1 - rx + ox, y1), (x1 - rx, y1),
        (x0 + rx, y1),
        (x0 + rx - ox, y1), (x0, y1 - ry + oy), (x0, y1 - ry),
        (x0, y0 + ry),
        (x0, y0 + ry - oy), (x0 + rx - ox, y0), (x0 + rx, y0),
        (0, 0),
    ]
    codes = [
        MPath.MOVETO,
        MPath.LINETO,
        MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
        MPath.LINETO,
        MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
        MPath.LINETO,
        MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
        MPath.LINETO,
        MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
        MPath.CLOSEPOLY,
    ]
    return MPath(verts, codes)


def draw_frame(
    date: pd.Timestamp,
    values: pd.Series,
    y_pos: dict[str, float],
    vmax: float,
) -> np.ndarray:
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor=BG)

    # subtle top glow wash
    fig.add_artist(Rectangle(
        (0, 0.88), 1.0, 0.12, transform=fig.transFigure,
        facecolor="#1B1240", edgecolor="none", alpha=0.55, zorder=0,
    ))
    fig.add_artist(Rectangle(
        (0.55, 0.90), 0.45, 0.10, transform=fig.transFigure,
        facecolor="#0E1A3A", edgecolor="none", alpha=0.45, zorder=0,
    ))

    # Title block
    fig.text(
        0.055, 0.965,
        "THE CRYPTO ",
        ha="left", va="top",
        color=WHITE, fontsize=46,
        fontproperties=FP["title_it"],
        zorder=5,
    )
    fig.text(
        0.055 + 0.455, 0.965,
        "10",
        ha="left", va="top",
        color=GOLD, fontsize=46,
        fontproperties=FP["title_it"],
        zorder=5,
    )
    fig.text(
        0.055, 0.928,
        "MARKET CAP LEADERBOARD",
        ha="left", va="top",
        color=WHITE, fontsize=13,
        fontproperties=FP["semi"],
        zorder=5,
    )
    fig.add_artist(Rectangle(
        (0.055, 0.905), 0.89, 0.0018, transform=fig.transFigure,
        facecolor=HEADER_LINE, edgecolor="none", zorder=5,
    ))
    fig.text(
        0.055, 0.888,
        date.strftime("%b %d, %Y").upper(),
        ha="left", va="center",
        color=WHITE, fontsize=18,
        fontproperties=FP["bold"],
        zorder=5,
    )
    fig.text(
        0.945, 0.888,
        "MARKET CAP  •  USD",
        ha="right", va="center",
        color=MUTED, fontsize=12,
        fontproperties=FP["med"],
        zorder=5,
    )

    ax = fig.add_axes([AX_LEFT, AX_BOTTOM, AX_W, AX_H])
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(9.85, -0.55)
    ax.set_yticks([])
    ax.tick_params(left=False, bottom=False, labelbottom=False)

    items = [(name, y) for name, y in y_pos.items() if y < 10.3]
    items.sort(key=lambda x: x[1])

    icon_x = 0.045
    name_x = 0.095
    bar_x0 = 0.095
    bar_xmax = 0.65
    value_x = 0.78
    bar_span = bar_xmax - bar_x0

    # recessed tracks
    track_h = 0.32
    for i in range(10):
        add_h_pill(
            ax, bar_x0, i, bar_span, track_h,
            facecolor=TRACK, zorder=1, alpha=0.95,
        )

    # x-axis ticks
    tick_vals = [0.0, 0.25, 0.5, 0.75, 1.0]
    for tv in tick_vals:
        x = bar_x0 + bar_span * tv
        ax.plot([x, x], [9.55, 9.72], color=AXIS, lw=1.0, zorder=2, solid_capstyle="round")
        label_v = vmax * tv
        ax.text(
            x, 9.88,
            fmt(label_v) if tv > 0 else "$0",
            ha="center", va="top",
            color=AXIS, fontsize=10,
            fontproperties=FP["med"],
            zorder=2,
        )

    leader_y = min((yy for _, yy in items), default=0.0)

    for name, y in items:
        v = float(values.get(name, 0.0))
        if v <= 0 or not np.isfinite(v):
            continue
        c = color_for(name)
        c_hi = lighten(c, 0.45)
        tkr = ticker_for(name)
        is_leader = abs(y - leader_y) < 0.35 and y < 0.7

        frac = min(1.0, v / max(vmax, 1.0))
        # Keep short bars readable as short solid pills (min width ~ half bar height)
        bar_h = 0.40 if is_leader else 0.26
        # Tiny floor only — just enough for small corner radii to render.
        # Do NOT use ~0.5*bar_h (that made every short bar the same width).
        min_w = max(0.016, 2 * (FIXED_ROUND_Y * PX_PER_Y / PX_PER_X) + 0.006)
        bar_w = max(bar_span * frac, min_w)

        name_fs = 16 if is_leader else 15
        label_y = y - 0.34
        ax.text(
            name_x, label_y,
            name,
            ha="left", va="center",
            color=WHITE, fontsize=name_fs,
            fontproperties=FP["bold"],
            zorder=6,
            clip_on=False,
        )
        # Real measured name width + clear gap before ticker
        name_w = text_width_axes(name, name_fs, BODY_BOLD)
        gap = 0.022
        ax.text(
            name_x + name_w + gap, label_y,
            tkr,
            ha="left", va="center",
            color=MUTED, fontsize=11,
            fontproperties=FP["med"],
            zorder=6,
            clip_on=False,
        )
        ax.text(
            value_x, label_y,
            fmt(v),
            ha="right", va="center",
            color=WHITE, fontsize=name_fs,
            fontproperties=FP["bold"],
            zorder=6,
            clip_on=False,
        )

        if is_leader:
            # Soft glow behind — ellipses only, never FancyBbox with oversized radius
            for sx, sy, alpha in (
                (1.08, 1.55, 0.10),
                (1.04, 1.30, 0.16),
                (1.02, 1.12, 0.22),
            ):
                ax.add_patch(Ellipse(
                    (bar_x0 + bar_w / 2, y),
                    width=bar_w * sx,
                    height=bar_h * sy,
                    facecolor=c,
                    edgecolor="none",
                    alpha=alpha,
                    zorder=2,
                ))
            add_h_pill(ax, bar_x0, y, bar_w, bar_h, facecolor=c, zorder=3)
            # Top sheen — inset slightly so rounding stays valid
            sheen_h = bar_h * 0.48
            sheen_inset = min(0.006, bar_w * 0.08)
            add_h_pill(
                ax,
                bar_x0 + sheen_inset,
                y - bar_h * 0.12,
                max(bar_w - 2 * sheen_inset, min_w * 0.5),
                sheen_h,
                facecolor=c_hi, alpha=0.50, zorder=4,
            )
        else:
            add_h_pill(ax, bar_x0, y, bar_w, bar_h, facecolor=c, zorder=3)

    # Circular badges in figure space (correct 9:16 aspect)
    diam_px = 44
    ew = diam_px / W
    eh = diam_px / H
    bottom, top = 9.85, -0.55
    for name, y in items:
        v = float(values.get(name, 0.0))
        if v <= 0 or not np.isfinite(v):
            continue
        c = color_for(name)
        axes_frac_y = (y - bottom) / (top - bottom)
        fig_y = AX_BOTTOM + AX_H * axes_frac_y - 0.006
        fig_x = AX_LEFT + AX_W * icon_x
        fig.add_artist(Ellipse(
            (fig_x, fig_y),
            width=ew,
            height=eh,
            transform=fig.transFigure,
            facecolor=c,
            edgecolor=lighten(c, 0.35),
            linewidth=1.5,
            zorder=20,
            clip_on=False,
        ))
        fig.text(
            fig_x, fig_y,
            icon_letter(name),
            ha="center", va="center",
            color=contrast_text(c),
            fontsize=14,
            fontproperties=FP["bold"],
            zorder=21,
            transform=fig.transFigure,
        )

    fig.text(
        0.055, 0.028,
        "Source: CoinMarketCap historical snapshots",
        ha="left", va="center",
        color=AXIS, fontsize=10,
        fontproperties=FP["med"],
    )

    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    rgb = buf[:, :, :3].copy()
    plt.close(fig)
    return composite_watermark(rgb)


def build_frames_meta(df: pd.DataFrame):
    dates = df.index.to_list()
    n_seg = len(dates) - 1
    frames_meta = []
    for i in range(n_seg):
        steps = 2 if i < 12 else (3 if i < 30 else 4)
        a, b = dates[i], dates[i + 1]
        va, vb = df.loc[a], df.loc[b]
        ra, rb = top_ranks(va), top_ranks(vb)
        for s in range(steps):
            t = ease_in_out(s / steps)
            vals = va * (1 - t) + vb * t
            keys = set(ra) | set(rb)
            y = {}
            for k in keys:
                ya = ra.get(k, 10.6)
                yb = rb.get(k, 10.6)
                y[k] = ya * (1 - t) + yb * t
            stamp = a if t < 0.5 else b
            frames_meta.append((stamp, vals, y))
    last = dates[-1]
    frames_meta.append((last, df.loc[last], top_ranks(df.loc[last])))
    hold = int(FPS * 1.6)
    for _ in range(hold):
        frames_meta.append(frames_meta[-1])
    return frames_meta, hold


def main():
    df_full = load_data()
    df = df_full[df_full.index >= "2017-12-01"].copy()
    frames_meta, hold = build_frames_meta(df)
    total = len(frames_meta)
    print(f"points={len(df)} frames={total} duration≈{total / FPS:.1f}s hold={hold}")
    print(f"font_title={TITLE_ITALIC}")

    # Early proof (DEC 2017 — short bars visible) + mid proof
    early_idx = 0
    mid_idx = total // 2
    for label, idx, path in (
        ("early", early_idx, PROOF_EARLY),
        ("mid", mid_idx, PROOF_MID),
    ):
        date, vals, y_pos = frames_meta[idx]
        fm = visible_vmax(vals, y_pos)
        frame = draw_frame(date, vals, y_pos, fm)
        Image.fromarray(frame).save(path)
        print(f"Wrote {path.name} ({label} frame {idx}, {date.date()})")

    # Combined proof: early on left conceptually — save early as primary proof_v3
    Image.open(PROOF_EARLY).save(PROOF)
    print(f"Wrote primary proof {PROOF}")

    writer = imageio.get_writer(
        str(OUT_MP4),
        fps=FPS,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        macro_block_size=None,
        ffmpeg_params=["-movflags", "+faststart"],
    )
    try:
        for i, (date, vals, y_pos) in enumerate(frames_meta):
            fm = visible_vmax(vals, y_pos)
            frame = draw_frame(date, vals, y_pos, fm)
            writer.append_data(frame)
            if i % 40 == 0 or i == total - 1:
                print(f"  frame {i + 1}/{total}  {date.strftime('%Y-%m-%d')}")
    finally:
        writer.close()

    mb = OUT_MP4.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT_MP4} ({mb:.1f} MB)")


if __name__ == "__main__":
    main()
