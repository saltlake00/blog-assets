"""블로그 이미지를 날짜 폴더에 넣고 push한 뒤 jsDelivr <img> 태그를 출력한다.

사용법:
    python add.py 파일1.png 파일2.png [--date 2026-10-02] [--name 이름1 이름2]

- 파일은 YYYY/MM/DD/ 아래로 복사된다. 같은 경로가 있으면 덮어쓰지 않고 멈춘다.
- 주소는 커밋 해시로 고정한다(@main은 jsDelivr가 최대 7일 캐시한다).
- 이 저장소는 공개다. 브랜치명·이메일·경로 등이 보이면 먼저 가린다.
"""
import argparse
import datetime
import io
import pathlib
import shutil
import subprocess
import sys

REPO = "saltlake00/blog-assets"
ROOT = pathlib.Path(__file__).resolve().parent
EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} 실패 ({r.returncode}):\n{r.stderr}")
    return r.stdout.strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+")
    p.add_argument("--date", default=datetime.date.today().isoformat())
    p.add_argument("--name", nargs="*", help="저장할 파일명(확장자 제외), files와 같은 개수")
    a = p.parse_args()

    if a.name and len(a.name) != len(a.files):
        sys.exit("--name 개수가 파일 개수와 다릅니다.")
    y, m, d = a.date.split("-")
    dest_dir = ROOT / y / m / d
    dest_dir.mkdir(parents=True, exist_ok=True)

    added = []
    for i, f in enumerate(a.files):
        src = pathlib.Path(f)
        if not src.is_file():
            sys.exit(f"파일 없음: {src}")
        if src.suffix.lower() not in EXTS:
            sys.exit(f"이미지 확장자가 아님: {src}")
        stem = a.name[i] if a.name else src.stem
        dst = dest_dir / f"{stem}{src.suffix.lower()}"
        if dst.exists():
            sys.exit(f"이미 있음(덮어쓰지 않음): {dst.relative_to(ROOT)}")
        shutil.copy2(src, dst)
        added.append(dst.relative_to(ROOT).as_posix())

    git("add", "--", *added)
    git("commit", "-m", f"chore: {a.date} 이미지 {len(added)}장 추가")
    git("push")
    sha = git("rev-parse", "--short=12", "HEAD")

    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    for rel in added:
        out.write(f'<img class="wl-img" src="https://cdn.jsdelivr.net/gh/{REPO}@{sha}/{rel}" alt="">\n')
    out.flush()


if __name__ == "__main__":
    main()
