# blog-assets

티스토리 블로그(TIL) 글에 넣는 이미지 저장소. **공개 저장소**이므로 글에 실제로 쓰는 이미지만 올린다.
원본 스크린샷은 여기 두지 않는다.

## 흐름

1. **모으기** — `python collect.py`
   스크린샷 폴더, `~/Pictures/글감/`, 각 프로젝트의 `.wf/issues/*/` 캡처를 해시로 중복 제거해
   `_staging/<날짜>/<그룹>/`에 모은다(git 제외). 그룹마다 `_grid.png` 미리보기와 `목록.md`(출처)를 만든다.
   첫 실행만 `--since YYYY-MM-DD`가 필요하다.
2. **고르고 묶기** — 비슷한 검토 캡처는 그리드 한 장으로 합친다. 오류 콘솔처럼 글자를 읽어야 하는 것은 따로 둔다.
   ```bash
   python grid.py out.png a.png b.png c.png d.png --cols 2 --labels "평소" "조준" "벽 옆" "수정 후"
   ```
3. **올리기** — `python add.py out.png --name m06-fox-detect`
   `YYYY/MM/DD/` 아래로 복사·커밋·push한 뒤, 커밋 해시로 고정한 jsDelivr `<img>` 태그를 출력한다.

## 올리기 전 확인

- 브랜치명·이메일·로컬 경로·토큰 등 노출하면 안 되는 정보가 보이면 잘라내거나 가린다.
- 한 번 push한 파일은 이력에 남는다. 지워도 이전 커밋 주소로 계속 열린다.
