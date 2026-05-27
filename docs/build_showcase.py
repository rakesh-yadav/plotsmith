"""Assemble README hero (2x3 grid of plotsmith charts) + side-by-side comparison."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PS = ROOT / "benchmark" / "plotsmith"
BL = ROOT / "benchmark" / "baseline"
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)


def fit(img: Image.Image, w: int, h: int) -> Image.Image:
    """Resize preserving aspect, then pad to exactly (w, h) on white."""
    ratio = min(w / img.width, h / img.height)
    new_w, new_h = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), "white")
    canvas.paste(img, ((w - new_w) // 2, (h - new_h) // 2))
    return canvas


# ---------------- Hero: 2x3 grid of the 6 strongest plotsmith charts -----------------
HERO_PICKS = [
    "02_regional.png",      # multi-series highlight
    "06_waterfall.png",     # business analytics
    "07_ltv.png",           # distribution
    "10_corr.png",          # correlation heatmap
    "12_roc.png",           # ML
    "14_survival.png",      # survival
]
CELL_W, CELL_H = 900, 500
PAD = 24
cols, rows = 3, 2
hero_w = cols * CELL_W + (cols + 1) * PAD
hero_h = rows * CELL_H + (rows + 1) * PAD
hero = Image.new("RGB", (hero_w, hero_h), "white")
for i, fname in enumerate(HERO_PICKS):
    img = Image.open(PS / fname).convert("RGB")
    cell = fit(img, CELL_W, CELL_H)
    r, c = divmod(i, cols)
    x = PAD + c * (CELL_W + PAD)
    y = PAD + r * (CELL_H + PAD)
    hero.paste(cell, (x, y))
hero_path = OUT / "hero.png"
hero.save(hero_path, "PNG", optimize=True)
print(f"hero  : {hero_path}  ({hero.size})")


# ---------------- Side-by-side: correlation heatmap baseline vs plotsmith ------------
def stack_side_by_side(bl_name: str, ps_name: str, out_name: str,
                       cell_w: int = 1100, cell_h: int = 850,
                       label_h: int = 60) -> Path:
    bl = Image.open(BL / bl_name).convert("RGB")
    ps = Image.open(PS / ps_name).convert("RGB")
    total_w = 2 * cell_w + 3 * PAD
    total_h = cell_h + label_h + 2 * PAD
    canvas = Image.new("RGB", (total_w, total_h), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except Exception:
        font_label = ImageFont.load_default()

    # labels
    draw.text((PAD + cell_w // 2 - 90, PAD // 2), "Baseline agent",
              fill="#444", font=font_label)
    draw.text((2 * PAD + cell_w + cell_w // 2 - 110, PAD // 2),
              "PlotSmith agent", fill="#1f6feb", font=font_label)

    # charts
    canvas.paste(fit(bl, cell_w, cell_h), (PAD, label_h))
    canvas.paste(fit(ps, cell_w, cell_h), (2 * PAD + cell_w, label_h))

    path = OUT / out_name
    canvas.save(path, "PNG", optimize=True)
    print(f"compare: {path}  ({canvas.size})")
    return path


stack_side_by_side("10_corr.png", "10_corr.png", "compare_corr.png")
stack_side_by_side("12_roc.png",  "12_roc.png",  "compare_roc.png")
