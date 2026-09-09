# 6강 — 시각화 및 리포팅 구성 (Power BI / Tableau)

8회차(전처리)에서 정제한 카페 매출 데이터를 매장·요일·날씨 단위로
집계해, Power BI 또는 Tableau로 대시보드를 만듭니다. **두 도구 다
데스크톱/클라우드 앱이라 도커로 띄울 수 없어서**, 이번 회차는
"데이터 내보내기 + 도구 연결" 순서로 진행합니다.

## 1단계 — 대시보드용 데이터 내보내기

```bash
cd export
python3 export_summary.py
```

`8회차`의 정제 로직(결측치 처리, IQR 이상치 제거)을 그대로 적용한 뒤,
매장×요일×날씨 단위로 집계한 `cafe_dashboard_data.csv`가 생성됩니다
(89행, 평균/합계 매출, 평균 고객 수 포함).

## 2단계 — Power BI 또는 Tableau에 연결

**Power BI Desktop** (Windows, 무료)
1. 홈 → 데이터 가져오기 → 텍스트/CSV
2. `export/cafe_dashboard_data.csv` 선택 → 로드
3. 시각화 만들기 예시:
   - 막대 차트: `weekday`별 `total_sales` 합계
   - 매트릭스: `store_id` × `weather`, 값은 `avg_sales`
4. **자동 갱신 설정**: Power BI Desktop 자체는 파일이 바뀌어도 수동
   새로고침(홈 → 새로고침)이 필요합니다. 정말 자동 갱신을 하려면
   Power BI Service(클라우드)에 게시한 뒤 "예약된 새로고침"을 설정해야
   합니다 — 이 차이 자체가 "로컬 파일 vs 클라우드 서비스"의 실무
   차이를 보여주는 좋은 토론 소재입니다.

**Tableau Public** (무료)
1. 데이터 연결 → 텍스트 파일 → `cafe_dashboard_data.csv`
2. 시트에서 `weekday`를 열, `avg_sales`를 행으로 드래그해 막대 차트 생성
3. 대시보드 탭에서 여러 시트를 하나의 화면으로 조합

## 3단계 (Power BI/Tableau가 없다면) — Grafana로 동일한 걸 해보기

```bash
cd grafana-alternative
docker compose up -d
```

- http://localhost:3000 (admin/admin) 접속
- **Dashboards → New → Add visualization** → Infinity 데이터소스 선택
- Type: `CSV`, Source: `URL`, URL: `http://csv-server:8000/cafe_dashboard_data.csv`
- Format을 `Table`로 설정하면 컬럼들이 그대로 나타납니다 — Bar Chart
  패널로 바꿔 `weekday`별 `avg_sales`를 시각화해보세요

이 대안은 진짜 Power BI/Tableau 실습을 대체하는 게 아니라, **도구가
없는 환경에서도 "정제된 데이터를 시각화 도구에 연결한다"는 이 회차의
핵심 흐름만큼은 체험할 수 있게** 하는 보조 장치입니다.

## 자주 겪는 문제

- **export_summary.py 실행 오류(FileNotFoundError)** → 반드시
  `06-visualization/export` 폴더 안에서 실행하세요 (8회차 폴더를
  상대 경로로 참조합니다)
- **한글이 깨져서 보임(Excel/Power BI)** → CSV는 이미 BOM 포함으로
  저장되어 있어 정상적으로는 발생하지 않습니다. 다른 도구로 CSV를
  다시 저장했다면 인코딩이 바뀌었을 수 있습니다
- **Grafana 대안에서 CSV가 안 보임** → `docker compose logs csv-server`로
  파일 서버가 떠 있는지, `docker compose logs grafana`로 Infinity
  플러그인 설치가 끝났는지 확인
