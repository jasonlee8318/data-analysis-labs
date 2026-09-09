# 강사용 — 깃허브 업로드 절차

⚠️ 이 파일과 각 폴더의 `INSTRUCTOR.md`는 강사용입니다.
수강생에게 공개해도 큰 문제는 없지만, 정답이 담긴 `INSTRUCTOR.md`는
공개 저장소에 올리기 전에 삭제하거나 별도 비공개 저장소로 옮기는 것을 권합니다.

## 1. 저장소 만들기

1. https://github.com/new 접속 (jasonlee8318 계정으로 로그인된 상태)
2. Repository name: **data-analysis-labs**
3. Public 선택 (수강생이 로그인 없이 받을 수 있어야 하므로)
4. **"Add a README file" 체크는 해제** (이미 README.md가 있으므로 충돌 방지)
5. Create repository

> 다른 이름을 쓰고 싶다면 루트 `README.md`의 URL 두 곳도 함께 바꿔주세요.

## 2. 업로드 — 방법 A: 웹에서 드래그 (Git 몰라도 됨)

1. 만들어진 저장소 화면에서 **uploading an existing file** 링크 클릭
2. `data-analysis-labs` 폴더 **안의 내용물**(03-architecture, 04-env-setup, … , README.md)을
   드래그해서 놓기 — 폴더째로 끌어도 하위 구조가 유지됩니다
3. 아래 Commit changes 클릭

## 3. 업로드 — 방법 B: Git 명령

```bash
cd data-analysis-labs
git init
git add .
git commit -m "실습 환경 및 코드 초기 등록"
git branch -M main
git remote add origin https://github.com/jasonlee8318/data-analysis-labs.git
git push -u origin main
```

## 4. 업로드 후 확인

- 저장소 첫 화면에 README가 렌더링되는지
- Code → Download ZIP 이 정상 동작하는지 (수강생이 쓸 경로이므로 직접 한 번 받아보기)
- 받은 ZIP을 다른 폴더에 풀어서 `03-architecture`부터 리허설 1회

## 5. 수강생 공지문 (그대로 복사해 쓰세요)

> 수업 전에 아래 세 가지를 준비해 주세요.
>
> 1. Docker Desktop 설치 후 실행 (Windows는 설치 시 WSL2 옵션 체크)
>    → 설치 후 톱니바퀴 > Resources에서 메모리를 6GB 이상으로 설정
> 2. 실습 파일 내려받기: https://github.com/jasonlee8318/data-analysis-labs
>    → 초록색 Code 버튼 > Download ZIP > 압축 해제
>    (경로에 한글이나 공백이 없는 위치를 권장합니다)
> 3. 터미널에서 해당 회차 폴더로 이동 후 `docker compose pull` 실행
>    → 용량이 큰 파일을 미리 받아두는 과정으로, 수업 당일 대기 시간을 줄여줍니다
>
> 준비 중 막히시면 수업 시작 10분 전에 오셔서 도움을 받으실 수 있습니다.

## 6. 회차별 강사 참고

- 각 회차 폴더의 README가 수강생 실습 가이드입니다.
- `08-09-preprocess-stats/INSTRUCTOR.md`에 통계 분석 결과지 정답이 있습니다.
- 모든 회차가 8888 포트를 공유하므로, 회차 전환 시 이전 폴더에서
  `docker compose down`을 안내해 주세요. (각 README 상단에도 명시되어 있습니다)
