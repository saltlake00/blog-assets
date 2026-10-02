"""여러 세션이 남긴 캡처를 _staging/ 에 모으고 그룹별 그리드 미리보기를 만든다.

사용법:
    python collect.py --since 2026-10-02   # 첫 실행: 이 날짜부터
    python collect.py                      # 이후: 마지막 실행일부터
    python collect.py --dry-run            # 무엇을 모을지 출력만

- 수집 위치는 아래 SOURCES. 내용(SHA-1)이 같은 파일은 한 번만 모은다.
- 이미 모은 해시는 _staging/seen.json 에 남아 다음 실행에서 건너뛴다.
- 날짜는 같은 내용 사본들 중 가장 이른 수정 시각. 워크트리 체크아웃은 수정 시각을
  새로 찍으므로, 처음 수집할 때 예전 캡처가 오늘로 잡힐 수 있다.
- _staging/ 은 .gitignore 대상이다. 공개는 고른 이미지만 add.py 로 한다.
"""
import argparse
import datetime
import hashlib
import io
import json
import pathlib
import re
import shutil
import sys

from grid import make_grid

HOME = pathlib.Path.home()
ROOT = pathlib.Path(__file__).resolve().parent
STAGING = ROOT / "_staging"
SEEN = STAGING / "seen.json"
LAST_RUN = STAGING / "last_run.txt"
EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

# (그룹 이름을 정하는 함수, 훑을 경로 목록)
SOURCES = [
    # 사용자가 직접 찍은 스크린샷
    (lambda p: "screenshots", [HOME / "Pictures" / "Screenshots"]),
    # 워크플로 밖 작업에서 세션이 남긴 캡처: ~/Pictures/글감/<주제>/...
    (lambda p: "글감-" + p.relative_to(HOME / "Pictures" / "글감").parts[0]
        if len(p.relative_to(HOME / "Pictures" / "글감").parts) > 1 else "글감",
     [HOME / "Pictures" / "글감"]),
]
# 워크플로 QA 캡처: <프로젝트>/.wf/issues/<이슈>/...
PROJECT_ROOTS = [HOME / "Documents" / "UnityProject", HOME / "Documents" / "GitHub"]


def wf_group(p):
    parts = p.parts
    i = parts.index(".wf")
    project = re.sub(r"-dev\d*$", "", parts[i - 1])  # 워크트리 사본은 같은 프로젝트로 본다
    return f"{project}-{parts[i + 2]}"


def candidates():
    for group_of, roots in SOURCES:
        for r in roots:
            if r.is_dir():
                for p in r.rglob("*"):
                    if p.suffix.lower() in EXTS and p.is_file():
                        yield group_of(p), p
    for base in PROJECT_ROOTS:
        if not base.is_dir():
            continue
        for issues in base.glob("*/.wf/issues"):
            for p in issues.rglob("*"):
                if p.suffix.lower() in EXTS and p.is_file():
                    yield wf_group(p), p


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--since", help="이 날짜(YYYY-MM-DD) 이후 수정된 파일만 본다")
    a = ap.parse_args()
    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    seen = json.loads(SEEN.read_text(encoding="utf-8")) if SEEN.exists() else {}
    if a.since:
        since_day = datetime.date.fromisoformat(a.since)
    elif LAST_RUN.exists():
        since_day = datetime.date.fromisoformat(LAST_RUN.read_text().strip())
    else:
        sys.exit("첫 실행입니다. 어디부터 모을지 --since YYYY-MM-DD 로 정해 주세요.")
    since = datetime.datetime.combine(since_day, datetime.time()).timestamp()

    # 해시별로 사본을 모은다
    found = {}
    for group, p in candidates():
        st = p.stat()
        if st.st_mtime < since:
            continue
        digest = sha1(p)
        if digest in seen:
            continue
        found.setdefault(digest, []).append((st.st_mtime, group, p))

    touched = {}
    for digest, copies in found.items():
        copies.sort()
        mtime, group, src = copies[0]
        day = datetime.date.fromtimestamp(mtime).isoformat()
        dst_dir = STAGING / day / group
        dst = dst_dir / src.name
        if dst.exists():  # 같은 이름의 다른 내용
            dst = dst_dir / f"{src.stem}-{digest[:6]}{src.suffix}"
        rel = dst.relative_to(STAGING).as_posix()
        if a.dry_run:
            out.write(f"[모을 것] {rel} <- {src}\n")
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        seen[digest] = {"staged": rel, "sources": [str(c[2]) for c in copies]}
        touched.setdefault(day, set()).add(group)

    if a.dry_run:
        out.write(f"새 이미지 {len(found)}장 (실행하지 않음)\n")
        out.flush()
        return

    STAGING.mkdir(exist_ok=True)
    SEEN.write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")
    LAST_RUN.write_text(datetime.date.today().isoformat())

    for day, groups in sorted(touched.items()):
        for g in sorted(groups):
            imgs = sorted(p for p in (STAGING / day / g).iterdir()
                          if p.suffix.lower() in EXTS and not p.name.startswith("_"))
            make_grid(imgs, STAGING / day / g / "_grid.png", cols=4, width=320)
        write_index(day, seen)
        out.write(f"{day}: {', '.join(sorted(groups))}\n")
    out.write(f"새 이미지 {len(found)}장 수집 → {STAGING}\n")
    out.flush()


def write_index(day, seen):
    """그날 모은 이미지를 그룹별로 출처와 함께 적는다."""
    rows = {}
    for info in seen.values():
        if info["staged"].startswith(day + "/"):
            _, g, name = info["staged"].split("/", 2)
            rows.setdefault(g, []).append((name, info["sources"][0]))
    lines = [f"# {day} 수집 이미지", "",
             "공개 전 확인: 브랜치명·이메일·로컬 경로·토큰이 보이면 가리고 올린다.", ""]
    for g in sorted(rows):
        lines += [f"## {g} ({len(rows[g])}장)", "", f"![미리보기]({g}/_grid.png)", ""]
        lines += [f"- `{n}` ← `{s}`" for n, s in sorted(rows[g])]
        lines.append("")
    (STAGING / day / "목록.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
