"""여러 이미지를 라벨 붙은 그리드 한 장으로 합친다.

사용법:
    python grid.py 출력.png 이미지1 이미지2 ... [--cols 3] [--width 480] [--labels 라벨1 라벨2 ...]

- 각 칸은 같은 너비로 맞추고 비율은 유지한다. 행 높이는 그 행의 가장 큰 칸에 맞춘다.
- 라벨을 안 주면 파일명(확장자 제외)을 쓴다.
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

BG = (24, 24, 27)
FG = (230, 230, 230)
GAP = 12
LABEL_H = 34


def font(size):
    for name in ("malgun.ttf", "NanumGothic.ttf", "AppleSDGothicNeo.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_grid(files, out, cols=3, width=480, labels=None):
    """files를 그리드 한 장으로 합쳐 out에 저장하고 (너비, 높이)를 돌려준다."""
    labels = labels or [pathlib.Path(f).stem for f in files]
    tiles = []
    for f in files:
        im = Image.open(f).convert("RGB")
        h = round(im.height * width / im.width)
        tiles.append(im.resize((width, h), Image.LANCZOS))

    cols = min(cols, len(tiles))
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    row_h = [max(t.height for t in r) + LABEL_H for r in rows]
    W = cols * width + (cols + 1) * GAP
    H = sum(row_h) + (len(rows) + 1) * GAP

    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)
    fnt = font(18)
    y = GAP
    for ri, r in enumerate(rows):
        for ci, t in enumerate(r):
            x = GAP + ci * (width + GAP)
            canvas.paste(t, (x, y))
            draw.text((x + 4, y + t.height + 7), labels[ri * cols + ci], fill=FG, font=fnt)
        y += row_h[ri] + GAP

    canvas.save(out, optimize=True)
    return W, H


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("files", nargs="+")
    p.add_argument("--cols", type=int, default=3)
    p.add_argument("--width", type=int, default=480, help="칸 하나의 너비(px)")
    p.add_argument("--labels", nargs="*")
    a = p.parse_args()

    if a.labels and len(a.labels) != len(a.files):
        sys.exit("--labels 개수가 이미지 개수와 다릅니다.")
    W, H = make_grid(a.files, a.out, a.cols, a.width, a.labels)
    sys.stdout.buffer.write(f"{a.out} {W}x{H} ({len(a.files)}칸)\n".encode("utf-8"))


if __name__ == "__main__":
    main()
