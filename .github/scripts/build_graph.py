"""Genera assets/contribuciones.svg: mapa de contribuciones oscuro, azul y animado."""
import re
import sys
import urllib.request

USER = "UCandelario"
SRC = f"https://github.com/users/{USER}/contributions"
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/contribuciones.svg"

LEVELS = ["#161b22", "#0a3d62", "#1565a8", "#2c9cdb", "#5fd0ff"]
PAD_X, PAD_TOP, PAD_BOTTOM = 18, 14, 34


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")


def level(score, top):
    if score <= 0:
        return 0
    return min(4, 1 + int(3 * (score - 1) / max(top - 1, 1) + 0.5)) if top > 1 else 3


src = fetch(SRC)
# Calendario público de GitHub: incluye contribuciones privadas si están activadas en el perfil.
counts = {}
for cid, txt in re.findall(r'for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)<', src):
    m = re.match(r"(\d+) contribution", txt.strip())
    counts[cid] = int(m.group(1)) if m else 0
cells, dates = [], {}
for m in re.finditer(r'data-date="([\d-]+)" id="contribution-day-component-(\d+)-(\d+)"', src):
    date, row, col = m.group(1), int(m.group(2)), int(m.group(3))
    cells.append((col * 12 + 27, row * 12, counts.get(f"contribution-day-component-{row}-{col}", 0)))
    dates[(row, col)] = date
labels = []
for row, name in ((1, "Lun"), (3, "Mié"), (5, "Vie")):
    labels.append((0, row * 12 + PAD_TOP + 9, name))
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
last = None
for col in range(max(c for _, c in dates) + 1):
    d = dates.get((0, col)) or next((dates[(r, col)] for r in range(7) if (r, col) in dates), None)
    if d and d[5:7] != last:
        last = d[5:7]
        if col * 12 + 27 + 30 < max(c for c, _, _ in cells):
            labels.append((col * 12 + 27, 10, MESES[int(last) - 1]))
if not cells:
    sys.exit("No se pudieron leer las contribuciones")

top = max(sc for _, _, sc in cells)
total = sum(sc for _, _, sc in cells)
w = max(x for x, _, _ in cells) + 10 + 2 * PAD_X
h = max(y for _, y, _ in cells) + 10 + PAD_TOP + PAD_BOTTOM
xmax = max(x for x, _, _ in cells)

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
    "<style>"
    ".bg{fill:#0d1117;stroke:#21303f;stroke-width:1}"
    ".c{opacity:0;animation:pop .6s ease-out forwards}"
    ".a{animation:pop .6s ease-out forwards,glow 2.8s ease-in-out infinite}"
    "@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:scale(1)}}"
    "@keyframes glow{0%,100%{filter:brightness(1)}50%{filter:brightness(1.7)}}"
    ".c,.a{transform-box:fill-box;transform-origin:center}"
    ".t{fill:#7d8590;font:9px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
    ".s{fill:#9fb3c8;font:11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
    "</style>",
    f'<rect class="bg" x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10"/>',
]
for x, y, t in labels:
    out.append(f'<text class="t" x="{x + PAD_X}" y="{y}">{t}</text>')
for x, y, sc in cells:
    lv = level(sc, top)
    delay = round(x / max(xmax, 1) * 2.2, 2)
    cls = "a" if lv else "c"
    out.append(
        f'<rect class="{cls}" x="{x + PAD_X}" y="{y + PAD_TOP}" width="10" height="10" '
        f'rx="2" fill="{LEVELS[lv]}" style="animation-delay:{delay}s"/>'
    )
ly = h - 14
out.append(
    f'<text class="s" x="{PAD_X}" y="{ly + 3}">{total} contribuciones en el último año</text>'
)
lx = w - PAD_X - 5 * 14 - 60
out.append(f'<text class="t" x="{lx}" y="{ly + 3}">Menos</text>')
for i, c in enumerate(LEVELS):
    out.append(f'<rect x="{lx + 32 + i * 14}" y="{ly - 6}" width="10" height="10" rx="2" fill="{c}"/>')
out.append(f'<text class="t" x="{lx + 32 + 5 * 14 + 2}" y="{ly + 3}">Más</text>')
out.append("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(out))
print(f"{OUT}: {len(cells)} días, {total} contribuciones")
