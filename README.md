# 데이터 속에서 인사이트를 캐내는 분석 도구 — 실습 저장소

과정 전 회차의 실습 환경과 코드를 모아둔 저장소입니다.
**한 번만 내려받으면 과정 내내 사용**합니다.

## 1. 실습 파일 내려받기 (수업 전에 완료)

**방법 A — ZIP 다운로드 (Git을 몰라도 됨, 권장)**

1. https://github.com/jasonlee8318/data-analysis-labs 접속
2. 초록색 **Code** 버튼 → **Download ZIP**
3. 압축을 풀어 원하는 위치에 둡니다 (경로에 한글·공백이 없는 곳을 권장)

**방법 B — Git 사용**

```bash
git clone https://github.com/jasonlee8318/data-analysis-labs.git
```

## 2. Docker Desktop 설치 (수업 전에 완료)

https://www.docker.com/products/docker-desktop 에서 본인 OS용을 설치하고 실행합니다.

- **Windows**: 설치 중 WSL2 옵션을 켭니다. 설치 후 재부팅이 필요할 수 있습니다.
- **공통**: Docker Desktop 우측 상단 톱니바퀴 → Resources → 메모리를 **6GB 이상**으로 설정
- 설치 확인: 터미널(Windows는 PowerShell)에서 `docker --version` 실행 → 버전이 나오면 완료

## 3. 회차별 실습

각 폴더에 실습 파일과 **그 회차의 README**가 들어 있습니다.
실습을 시작할 때는 **반드시 해당 폴더로 이동**한 뒤 명령을 실행하세요.

```bash
cd data-analysis-labs/03-architecture     # 예: 3회차
```

| 폴더 | 원본 회차 | 내용 |
|---|---|---|
| `03-architecture/` | 3회차 | 수집→처리→분석→시각화 4계층을 Python 파이프라인으로 직접 구현 (도커 불필요) |
| `03b-worker-scaling-design/` | (3회차 심화) | 시나리오 기반으로 워커 확장 시점·방식을 직접 설계 (코드 실행 없음) |
| `03c-four-layer-design/` | (3회차 심화) | 수집·저장/처리/분석/시각화 계층별 도구를 시나리오 기반으로 직접 설계 (코드 실행 없음) |
| `04-env-setup/` | 4회차 | 빈 리눅스에 아나콘다·JDK·PySpark를 직접 설치하고 10개 항목 점검 |
| `05-etl/` | 5회차 | MySQL·REST API·데이터 레이크에서 추출 → 정제 → 적재 |
| `06-visualization/` | 6회차 | Power BI/Tableau(또는 Grafana 대안)로 정제 데이터 대시보드 구성 |
| `08-09-preprocess-stats/` | 8·9회차 | 카페 매출 데이터 전처리 파이프라인 + 상관·회귀 분석 |
| `10-mllib-classification/` | 10회차 | Spark MLlib 분류 모델 3종 비교 + CrossValidator 튜닝 |
| `11-result-interpretation/` | 11회차 | 혼동행렬·ROC·Feature Importance 시각화 + 인사이트 리포트 |
| `12-integration-testing/` | 12회차 | 전체 모듈 통합 테스트 + 모델 재학습 전략 설계 (캡스톤) |

폴더 번호가 원본 강의계획서 회차 번호와 동일하게 맞춰져 있습니다.
실제 수업은 표 순서(3→4→5→6→8·9→10→11→12) 그대로 진행하시면 됩니다.
1·2·7회차는 원본 강의계획서 기준 실습이 없는 회차입니다.

## ⚠️ 회차를 넘어갈 때 꼭 확인 (가장 흔한 오류)

**3회차(`03-architecture`)는 도커를 쓰지 않습니다** — 로컬 파이썬으로
바로 실행합니다. 그 외 회차는 대부분 같은 포트(8888 등)를 사용하므로,
**이전 회차 환경을 끄지 않으면 다음 실습이 시작되지 않습니다.**

```bash
cd ../04-env-setup      # 직전에 사용한 회차 폴더로 이동
./lab.sh reset          # 또는 해당 회차의 종료 방법
cd ../05-etl            # 이번 회차 폴더로 이동
docker compose down     # (도커 기반 회차라면) 필요 시 이전 컨테이너 정리
```

지금 무엇이 켜져 있는지 모르겠다면, 아무 폴더에서나:

```bash
docker ps               # 실행 중인 컨테이너 목록 확인
```

## 사전 준비 요약 (수강생 공지용)

수업 전에 이 세 가지만 해오시면 됩니다.

1. Docker Desktop 설치 + 메모리 6GB 이상 설정
2. 이 저장소 다운로드 (ZIP 또는 clone)
3. 해당 회차 폴더에서 `docker compose pull` 실행 (이미지 미리 받기 — 당일 대기시간 방지)
