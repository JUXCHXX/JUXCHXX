#!/usr/bin/env python3
"""
make_info_card.py
Neofetch-style SVG panel. EDIT ROWS + HOST below with your real info,
then run: python scripts/make_info_card.py  -> info-card.svg
"""

HOST = "juxchxx@kyro"

# (label, value) -- label=None for a plain line, label="" for a blank spacer,
# label="---" for a divider
ROWS = [
    ("OS", "Pop!_OS 24.04 (COSMIC)"),
    ("Location", "Barranquilla, Colombia"),
    ("Study", "Ing. Sistemas -- CUC, 5to sem."),
    ("---", ""),
    ("Stack", "React / TypeScript / Node.js"),
    ("Also", "Python / Flask / REST / GraphQL"),
    ("---", ""),
    ("Founder", "Wappy -- WhatsApp AI (prod)"),
    ("", "  -> client: DriverPlus LLC (NJ, US)"),
    ("Co-founder", "Velto AI -- AI menus + POS"),
    ("", "  -> client: Fabian's Mexican Rest."),
    ("Projects", "GitScope, ATELIER, Nuvek"),
    ("---", ""),
    ("Status", "Open to fullstack roles"),
]

OUT = "info-card.svg"
W = 490
H = 398          # match the portrait height -- bump if content overflows
PAD_X = 26
LINE_H = 22
FONT_SIZE = 14
LABEL_COLOR = "#8b949e"
VALUE_COLOR = "#c9d1d9"
ACCENT = "#6e7681"
BG = "transparent"

TYPE_DUR_PER_ROW = 0.5
STAGGER = 0.08

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main():
    svg = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace" font-size="{FONT_SIZE}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'<style>.lbl{{fill:{ACCENT};font-weight:bold}} .val{{fill:{VALUE_COLOR}}}</style>',
        f'<text x="{PAD_X}" y="32" font-size="16" fill="{VALUE_COLOR}" font-weight="bold">{esc(HOST)}</text>',
        f'<line x1="{PAD_X}" y1="42" x2="{W-PAD_X}" y2="42" stroke="{ACCENT}" stroke-width="1" opacity="0.4"/>',
    ]

    y = 68
    delay = 0.2
    for label, value in ROWS:
        if label == "---":
            svg.append(f'<line x1="{PAD_X}" y1="{y-14}" x2="{W-PAD_X}" y2="{y-14}" '
                        f'stroke="{ACCENT}" stroke-width="1" opacity="0.25"/>')
            y += 8
            continue
        row_id = f"row{y}"
        content = f'<tspan class="lbl">{esc(label)+": " if label else ""}</tspan><tspan class="val">{esc(value)}</tspan>'
        svg.append(
            f'<text x="{PAD_X}" y="{y}" opacity="0">{content}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
            f'dur="0.35s" fill="freeze"/></text>'
        )
        y += LINE_H
        delay += STAGGER

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(svg))
    print(f"saved {OUT}  ({len(ROWS)} rows)")

if __name__ == "__main__":
    main()
