"""Generate the orchestration overview diagram (diagram-design default skin)."""
import math
import sys
import unicodedata
from pathlib import Path

PAPER, INK, MUTED, SOFT, ACCENT, LINK = "#f5f5f5", "#2d3142", "#4f5d75", "#7a8399", "#eb6c36", "#2e5aa8"
SANS = "'Geist', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
MONO = "'Geist Mono', monospace"
SERIF = "'Instrument Serif', 'Noto Serif KR', serif"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600"
         "&family=Geist+Mono:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@400&display=swap")

KINDS = {  # fill, stroke, dash, tag colour
    "focal": ("rgba(235,108,54,0.08)", ACCENT, None, ACCENT),
    "backend": ("#ffffff", INK, None, INK),
    "store": ("rgba(45,49,66,0.05)", MUTED, None, MUTED),
    "external": ("rgba(45,49,66,0.03)", "rgba(45,49,66,0.30)", None, INK),
    "input": ("rgba(79,93,117,0.10)", SOFT, None, MUTED),
}
STROKES = {"default": (MUTED, "arrow"), "accent": (ACCENT, "arrow-accent"), "link": (LINK, "arrow-link")}


def wide(s):
    return any(unicodedata.east_asian_width(c) in "WF" for c in s)


def tw(s, size, mono=False):
    return sum(size if unicodedata.east_asian_width(c) in "WF" else size * (0.62 if mono else 0.60) for c in s)


def up4(v):
    return int(math.ceil(v / 4.0) * 4)


def up8(v):  # label masks are centred, so half the width must stay on the 4px grid
    return int(math.ceil(v / 8.0) * 8)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=12, weight=None, fill=INK, font=SANS, anchor="middle", extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}"{w} font-family="{font}" '
            f'text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def tag(x, y, s, colour):
    w = up4(tw(s, 7, True) + len(s) * 0.56 + 12)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="2" fill="transparent" stroke="{colour}" '
            f'stroke-opacity="0.4" stroke-width="0.8"/>'
            + text(x + w / 2, y + 9, s, 7, None, colour, MONO, extra=' fill-opacity="0.8" letter-spacing="0.08em"'))


def box(x, y, w, h, kind, rx=6):
    fill, stroke, dash, _ = KINDS[kind]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{PAPER}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1"{d}/>')


def node(x, y, w, h, kind, name, sub=None, tg=None, rx=6):
    cx, cy = x + w / 2, y + h / 2
    out = [box(x, y, w, h, kind, rx)]
    shift = 0
    if tg:
        out.append(tag(x + 8, y + 6, tg, KINDS[kind][3]))
        shift = 4 if h >= 64 else 0
    if sub:
        out.append(text(cx, cy + 2 + shift, name, 12, 600))
        out.append(text(cx, cy + 18 + shift, sub, 9, None, MUTED, MONO))
    else:
        out.append(text(cx, cy + 4 + shift, name, 12, 600))
    return "".join(out)


def zone(x, y, w, h, label, dashed=False):
    stroke = 'stroke="rgba(45,49,66,0.20)" stroke-dasharray="4,4"' if dashed else 'stroke="rgba(45,49,66,0.10)"'
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="rgba(45,49,66,0.02)" {stroke} stroke-width="0.8"/>']
    if wide(label):
        lw = up4(tw(label, 12) + 12)
        out.append(f'<rect x="{x + 12}" y="{y + 4}" width="{lw}" height="16" rx="2" fill="{PAPER}"/>')
        out.append(text(x + 12 + lw / 2, y + 16, label, 12, 500, "rgba(45,49,66,0.55)"))
    else:
        lw = up4(tw(label, 7, True) + len(label) * 0.98 + 12)
        out.append(f'<rect x="{x + 12}" y="{y + 4}" width="{lw}" height="12" rx="2" fill="{PAPER}"/>')
        out.append(text(x + 12 + lw / 2, y + 13, label, 7, None, "rgba(45,49,66,0.40)", MONO, extra=' letter-spacing="0.14em"'))
    return "".join(out)


def arrow(pts, kind="default", dashed=False, r=8, marker=True, width=1.2):
    stroke, mk = STROKES[kind]
    d = f"M {pts[0][0]},{pts[0][1]}"
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        sg = lambda v: (v > 0) - (v < 0)
        a = (p1[0] - sg(p1[0] - p0[0]) * r, p1[1] - sg(p1[1] - p0[1]) * r)
        b = (p1[0] + sg(p2[0] - p1[0]) * r, p1[1] + sg(p2[1] - p1[1]) * r)
        d += f" L {a[0]},{a[1]} Q {p1[0]},{p1[1]} {b[0]},{b[1]}"
    d += f" L {pts[-1][0]},{pts[-1][1]}"
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    m = f' marker-end="url(#{mk})"' if marker else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{1 if dashed else width}"{dash}{m}/>'


def _label(s):
    if wide(s):
        return up8(tw(s, 12) + 8), 16, 12, dict(size=12, weight=500, font=SANS, extra="")
    return up8(tw(s, 8, True) + len(s) * 0.48 + 8), 12, 9, dict(size=8, weight=None, font=MONO, extra=' letter-spacing="0.06em"')


def hlabel(cx, line_y, s, below=False, fill=SOFT):
    w, h, base, st = _label(s)
    y = line_y + 8 if below else line_y - 8 - h
    return (f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" rx="2" fill="{PAPER}"/>'
            + text(cx, y + base, s, st["size"], st["weight"], fill, st["font"], extra=st["extra"]))


def vlabel(line_x, cy, s, left=False, fill=SOFT):
    w, h, base, st = _label(s)
    x = line_x - 8 - w if left else line_x + 8
    return (f'<rect x="{x}" y="{cy - h / 2}" width="{w}" height="{h}" rx="2" fill="{PAPER}"/>'
            + text(x + w / 2, cy - h / 2 + base, s, st["size"], st["weight"], fill, st["font"], extra=st["extra"]))


def callout(x, y, s, leader, dot, accent=False, anchor="start"):
    col = ACCENT if accent else INK
    lead = "rgba(235,108,54,0.50)" if accent else "rgba(45,49,66,0.40)"
    return (text(x, y, s, 14, None, col, SERIF, anchor, ' font-style="italic"')
            + f'<path d="{leader}" fill="none" stroke="{lead}" stroke-width="1" stroke-dasharray="4,3"/>'
            + f'<circle cx="{dot[0]}" cy="{dot[1]}" r="2" fill="{col}"/>')


def legend(y, width, items):
    out = [f'<line x1="32" y1="{y - 8}" x2="{width - 32}" y2="{y - 8}" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>',
           text(32, y + 12, "LEGEND", 8, None, MUTED, MONO, "start", ' letter-spacing="0.14em"')]
    x = 104
    for kind, label in items:
        if kind in KINDS:
            fill, stroke, dash, _ = KINDS[kind]
            out.append(f'<rect x="{x}" y="{y + 4}" width="16" height="12" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        elif kind == "oval":
            out.append(f'<rect x="{x}" y="{y + 4}" width="16" height="12" rx="6" fill="#ffffff" stroke="{INK}" stroke-width="1"/>')
        elif kind == "diamond":
            out.append(f'<polygon points="{x + 8},{y} {x + 16},{y + 8} {x + 8},{y + 16} {x},{y + 8}" fill="#ffffff" stroke="{INK}" stroke-width="1"/>')
        elif kind == "zone":
            out.append(f'<rect x="{x}" y="{y + 4}" width="16" height="12" rx="2" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="3,2"/>')
        elif kind == "chip":
            out.append(f'<rect x="{x}" y="{y + 4}" width="16" height="12" rx="4" fill="rgba(45,49,66,0.05)" stroke="{MUTED}" stroke-width="0.8"/>')
        else:  # line kinds: "default", "link", "accent", optionally "-dash"
            base = kind.replace("-dash", "")
            stroke, mk = STROKES[base]
            dash = ' stroke-dasharray="5,4"' if kind.endswith("-dash") else ""
            out.append(f'<line x1="{x}" y1="{y + 8}" x2="{x + 20}" y2="{y + 8}" stroke="{stroke}" stroke-width="1.2"{dash} marker-end="url(#{mk})"/>')
            x += 8
        out.append(text(x + 24, y + 12, label, 12, None, MUTED, SANS, "start"))
        x += 24 + up4(tw(label, 12)) + 28
    return "".join(out)


def page(slug, eyebrow, title, desc, w, h, body):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <link href="{FONTS}" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --color-paper: {PAPER}; --color-ink: {INK}; --color-muted: {MUTED}; --color-accent: {ACCENT};
      --font-sans: 'Geist', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, sans-serif;
      --font-serif: 'Instrument Serif', 'Noto Serif KR', serif;
      --font-mono: 'Geist Mono', ui-monospace, monospace;
    }}
    body {{ font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink);
           min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 3rem 2rem; }}
    .frame {{ max-width: {w}px; width: 100%; }}
    .eyebrow {{ font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em;
               text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }}
    h1 {{ font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 400;
         letter-spacing: -0.02em; line-height: 1.15; color: var(--color-ink); margin-bottom: 1.5rem; }}
    svg {{ width: 100%; min-width: 900px; display: block; }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h1>{esc(title)}</h1>
    <svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
      <title id="{slug}-title">{esc(title)}</title>
      <desc id="{slug}-desc">{esc(desc)}</desc>
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
        <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
        <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
      </defs>
      <rect x="0" y="0" width="{w}" height="{h}" fill="{PAPER}"/>
{body}
    </svg>
  </div>
</body>
</html>
"""


def join(*groups):
    return "\n".join("      <g>" + "".join(g) + "</g>" for g in groups)



def d_overview():
    W, H = 1120, 520
    zones = [zone(800, 128, 288, 240, "WORKERS · CMUX TERMINALS", dashed=True)]
    arrows = [
        arrow([(144, 252), (248, 252)]),
        arrow([(332, 208), (332, 76), (496, 76)]),
        arrow([(416, 252), (800, 252)]),
        arrow([(944, 368), (944, 420), (696, 420)]),
        arrow([(944, 128), (944, 76), (696, 76)]),
        arrow([(332, 296), (332, 420), (496, 420)]),
    ]
    labels = [
        hlabel(196, 252, "방향 · 승인"),
        hlabel(414, 76, "① 브리프 작성"),
        hlabel(608, 252, "② 한 줄 전달"),
        hlabel(608, 252, "orc task · cmux send", below=True),
        hlabel(820, 420, "③ 담당 경로 안에서 수행"),
        hlabel(820, 76, "④ 같은 파일에 결과 보고"),
        hlabel(414, 420, "⑤ 검수 · 커밋"),
        hlabel(414, 420, "git diff · tests", below=True),
    ]
    nodes = [
        node(32, 224, 112, 56, "input", "사용자", "human", "USER"),
        node(248, 208, 168, 88, "focal", "지휘자", "Claude Code", "CONDUCTOR"),
        node(496, 48, 200, 56, "store", "브리프 파일", ".orchestration/tasks/*.md", "FILE"),
        node(824, 152, 240, 56, "backend", "핵심 로직 · 진단", "codex · agy (cross-check)", "CORE"),
        node(824, 224, 240, 56, "backend", "도구 · 문서 생성", "agy2 · codex3", "BUILD"),
        node(824, 296, 240, 56, "backend", "반복 실행 · 감시", "codex2", "CHORE"),
        node(496, 392, 200, 56, "store", "작업 저장소", "code · tests · docs", "GIT"),
    ]
    notes = [
        callout(456, 164, "긴 지시는 파일에 쓰고, 터미널에는 한 줄만 보낸다", "M 470,172 Q 462,212 478,248", (480, 252), accent=True),
        callout(456, 340, "보고서가 아니라 git diff 와 테스트로 판정한다", "M 448,336 Q 392,332 336,346", (332, 348)),
    ]
    lg = [legend(480, W, [("focal", "지휘자"), ("backend", "워커"), ("store", "파일 · 저장소"), ("input", "사용자"),
                          ("zone", "터미널 묶음"), ("default", "흐름")])]
    return ("orchestration-overview", "Architecture · Agent Orchestration", "오케스트레이션 — 구성과 한 건의 흐름",
            "사용자가 방향을 정하면 지휘자인 Claude Code 가 브리프 파일을 쓰고 워커 터미널에 한 줄만 전달하며, 워커는 담당 경로 안에서 "
            "작업한 뒤 같은 브리프 파일에 결과를 적고, 지휘자가 git diff 와 테스트로 검수해 커밋하는 흐름을 보여 준다.",
            W, H, join(zones, arrows, labels, nodes, notes, lg))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    slug, eyebrow, title, desc, w, h, body = d_overview()
    (out / f"{slug}.html").write_text(page(slug, eyebrow, title, desc, w, h, body), encoding="utf-8")
    print(slug, w, h)
