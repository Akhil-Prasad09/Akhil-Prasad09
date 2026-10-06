"""Neofetch-style info card (info-card.svg). Static: rerun only when these details change.

Every number here must match the resume and the repos it links to.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"

ROWS = [
    ("Name", "Akhil Prasad Chinthala"),
    ("Role", "AI/ML engineer: LLMs and computer vision"),
    ("Now", "AI Engineering Intern, AMIK Technologies"),
    ("Also", "Freelance AI Trainer, Handshake AI"),
    ("Study", "B.Tech IT, Matrusri Engineering College"),
    ("", "CGPA 8.64, graduating 2027"),
    ("Base", "Hyderabad, India"),
    ("Stack", "Python, PyTorch, Hugging Face, OpenCV"),
    ("", "FastAPI, SQL, React, Docker, Linux"),
    ("Results", "Knee MRI abnormality AUC 0.943"),
    ("", "FER-2013 70.6% at ~8 ms/frame on CPU"),
    ("", "RAG correct refusals 33% to 75%"),
    ("Seeking", "AI/ML and Python backend roles"),
]

W, PAD, LH, BAR = 490, 22, 23, 34
H = BAR + PAD + LH * (len(ROWS) + 2) + 40   # + prompt line, rule, colour blocks
KEY_X = PAD
VAL_X = PAD + 9 * 8.4                        # 9 monospace columns at 14px


def line(i, body):
    return f'<g class="ln" style="animation-delay:{250 + i * 90}ms">{body}</g>'


def render():
    y0 = BAR + PAD + 12
    out = [line(0, f'<text x="{KEY_X}" y="{y0}"><tspan class="u">akhil</tspan><tspan class="v">@</tspan><tspan class="u">github</tspan></text>'),
           line(1, f'<text class="dim" x="{KEY_X}" y="{y0 + LH}">{"-" * 12}</text>')]
    for i, (k, v) in enumerate(ROWS, start=2):
        y = y0 + i * LH
        out.append(line(i, f'<text x="{KEY_X}" y="{y}"><tspan class="k">{escape(k)}</tspan></text>'
                           f'<text class="v" x="{VAL_X}" y="{y}">{escape(v)}</text>'))
    by = y0 + (len(ROWS) + 2) * LH - 6
    blocks = "".join(f'<rect class="b{j}" x="{KEY_X + j * 26}" y="{by}" width="22" height="12" rx="2"/>' for j in range(8))
    out.append(line(len(ROWS) + 2, blocks))
    dots = "".join(f'<circle class="d{j}" cx="{18 + j * 18}" cy="{BAR / 2}" r="5.5"/>' for j in range(3))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Akhil Prasad Chinthala. AI/ML engineer. AI Engineering Intern at AMIK Technologies, freelance AI trainer at Handshake AI. B.Tech IT, CGPA 8.64. Seeking AI/ML and Python backend roles.">
<style>
  text {{ font: 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .panel {{ fill: #ffffff; stroke: #d0d7de; }} .bar {{ fill: #f6f8fa; }} .rule {{ stroke: #d0d7de; }}
  .t {{ font-size: 12px; fill: #57606a; }}
  .u {{ fill: #1a7f37; font-weight: 700; }} .k {{ fill: #0969da; font-weight: 700; }} .v {{ fill: #1f2328; }} .dim {{ fill: #8c959f; }}
  .d0 {{ fill: #ff5f57; }} .d1 {{ fill: #febc2e; }} .d2 {{ fill: #28c840; }}
  .b0 {{ fill: #1f2328; }} .b1 {{ fill: #cf222e; }} .b2 {{ fill: #1a7f37; }} .b3 {{ fill: #9a6700; }}
  .b4 {{ fill: #0969da; }} .b5 {{ fill: #8250df; }} .b6 {{ fill: #1b7c83; }} .b7 {{ fill: #d0d7de; }}
  .ln {{ opacity: 0; animation: in 380ms cubic-bezier(.2, .8, .2, 1) forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-color-scheme: dark) {{
    .panel {{ fill: #0d1117; stroke: #30363d; }} .bar {{ fill: #161b22; }} .rule {{ stroke: #30363d; }} .t {{ fill: #8b949e; }}
    .u {{ fill: #3fb950; }} .k {{ fill: #58a6ff; }} .v {{ fill: #e6edf3; }} .dim {{ fill: #6e7681; }}
    .b0 {{ fill: #484f58; }} .b1 {{ fill: #ff7b72; }} .b2 {{ fill: #3fb950; }} .b3 {{ fill: #d29922; }}
    .b4 {{ fill: #58a6ff; }} .b5 {{ fill: #bc8cff; }} .b6 {{ fill: #39c5cf; }} .b7 {{ fill: #e6edf3; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .ln {{ opacity: 1; animation: none; }} }}
</style>
<rect class="panel" x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10"/>
<path class="bar" d="M1 11a10 10 0 0 1 10-10h{W - 22}a10 10 0 0 1 10 10v{BAR - 11}h-{W - 2}z"/>
<line class="rule" x1="1" y1="{BAR}" x2="{W - 1}" y2="{BAR}"/>
{dots}<text class="t" x="{W / 2}" y="{BAR / 2 + 4}" text-anchor="middle">akhil@github: ~ neofetch</text>
{"".join(out)}
</svg>
'''


if __name__ == "__main__":
    OUT.write_text(render())
    print(f"wrote {OUT.name} ({W}x{H})")
