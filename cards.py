#!/usr/bin/env python3
import argparse
import math
from pathlib import Path

def latex_escape(text):
    return (
        text.replace("\\", "\\textbackslash{}")
            .replace("_", "\\_")
            .replace("&", "\\&")
            .replace("%", "\\%")
            .replace("#", "\\#")
    )

def main():
    parser = argparse.ArgumentParser(
        description="Generate A4 card sheets from PNG images"
    )
    parser.add_argument("image_dir", type=Path, help="Directory containing PNG images")
    parser.add_argument("output", type=Path, help="Output .tex file")
    parser.add_argument("--cols", type=int, default=5, help="Cards per row (default: 5)")
    parser.add_argument("--rows", type=int, default=4, help="Rows per page (default: 4)")

    args = parser.parse_args()

    images = sorted(args.image_dir.glob("*.png"))
    per_page = args.cols * args.rows
    pages = math.ceil(len(images) / per_page)

    lines = []

    for page in range(pages):
        start = page * per_page
        end = start + per_page
        page_imgs = images[start:end]

        while len(page_imgs) < per_page:
            page_imgs.append(None)

        for r in range(args.rows):
            row = []
            for c in range(args.cols):
                img = page_imgs[r * args.cols + c]
                if img is None:
                    row.append(r"\emptycard")
                else:
                    label = latex_escape(img.stem)
                    row.append(f"\\card{{{img.as_posix()}}}{{{label}}}")
            # unified vertical spacing
            lines.append(" & ".join(row) + r" \\[\cardgap]")

        if page != pages - 1:
            lines += [
                r"\end{tabular}",
                r"\end{center}",
                r"\newpage",
                r"\begin{center}",
                f"\\begin{{tabular}}{{{'p{{\\cardwidth}}' * args.cols}}}"
            ]

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(rf"""\documentclass[a4paper]{{article}}
\usepackage[a4paper,landscape,margin=18mm]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{array}}
\usepackage{{calc}}

\pagenumbering{{gobble}}
\setlength{{\parindent}}{{0pt}}

% ---- Unified spacing control ----
\newlength{{\cardgap}}
\setlength{{\cardgap}}{{6pt}} % <<< adjust this ONE value

\setlength{{\tabcolsep}}{{\cardgap}}
\setlength{{\fboxsep}}{{6pt}}
\setlength{{\fboxrule}}{{0.5pt}}

\newcommand{{\cardcols}}{{{args.cols}}}
\newcommand{{\cardrows}}{{{args.rows}}}

% ---- Card size calculations ----
\newlength{{\cardwidth}}
\setlength{{\cardwidth}}{{(\textwidth - 2\tabcolsep*\cardcols) / \cardcols}}

\newlength{{\cardheight}}
\setlength{{\cardheight}}{{(\textheight - 2\tabcolsep*\cardrows) / \cardrows}}

\newlength{{\innercardwidth}}
\setlength{{\innercardwidth}}{{\cardwidth - 2\fboxsep - 2\fboxrule}}

\newlength{{\innercardheight}}
\setlength{{\innercardheight}}{{\cardheight - 2\fboxsep - 2\fboxrule}}

% ---- Scalable label ----
\newcommand{{\cardlabel}}[1]{{%
  \fontsize{{0.11\innercardheight}}{{1.2em}}\selectfont #1
}}

\newcommand{{\card}}[2]{{
  \fbox{{
    \begin{{minipage}}[t][\innercardheight][c]{{\innercardwidth}}
      \centering
      \includegraphics[
        width=\linewidth,
        height=0.7\innercardheight,
        keepaspectratio
      ]{{#1}}\\[2mm]
      \cardlabel{{\textbf{{#2}}}}
    \end{{minipage}}
  }}
}}

\newcommand{{\emptycard}}{{
  \fbox{{
    \begin{{minipage}}[t][\innercardheight][c]{{\innercardwidth}}
    \end{{minipage}}
  }}
}}

\begin{{document}}
\begin{{center}}
""")

        f.write(
            f"\\begin{{tabular}}{{{'p{{\\cardwidth}}' * args.cols}}}\n"
        )

        for line in lines:
            f.write(line + "\n")

        f.write(r"""\end{tabular}
\end{center}
\end{document}
""")

    print(f"Generated {args.output} ({len(images)} cards)")

if __name__ == "__main__":
    main()
