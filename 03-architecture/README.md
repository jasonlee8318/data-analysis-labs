# 3회차 — 분석 시스템 아키텍처 설계 (4계층 파이프라인 실습)

수집 → 처리 → 분석 → 시각화, 4계층이 실제 코드에서 어떻게 연결되는지
직접 만들어봅니다. Kafka·Spark 같은 무거운 도구 대신, **Python 하나로
전체 흐름을 압축**해서 "도구를 배우는 실습"이 아니라 **"데이터가 계층을
이동하며 가치가 만들어지는 과정"**을 체감하는 데 집중합니다.

가상의 고객 행동 로그로 이탈 위험 분석을 흉내 냅니다.

```
[1. 수집]        고객 행동 데이터 생성 → data/raw/customer_log.csv
      ↓
[2. 처리]        결측치 제거 / 집계 / 파생변수 → data/processed/customer.csv
      ↓
[3. 분석]        K-Means 고객 군집화 → customer_analysis.csv
      ↓
[4. 시각화]      Streamlit Dashboard
```

## 사전 준비

```bash
cd 03-architecture
pip install -r requirements.txt --break-system-packages
```

(도커 없이 로컬 파이썬으로 바로 진행합니다 — 무거운 환경 없이 4계층
구조 자체에 집중하기 위해서입니다.)

## 실행 순서

```bash
python 01_collect.py       # 1. 수집 — 가상 고객 행동 로그 1,000건 생성
python 02_process.py       # 2. 처리 — 고객 단위 집계 + activity_score 파생
python 03_analyze.py       # 3. 분석 — K-Means로 고객을 3개 그룹으로 분류
streamlit run 04_dashboard.py   # 4. 시각화 — 브라우저 대시보드
```

`04_dashboard.py`를 실행하면 브라우저에서 자동으로 열리거나,
안 열리면 터미널에 뜨는 `Local URL`(보통 http://localhost:8501)로 접속하세요.

## 각 단계에서 확인할 것

| 단계 | 핵심 흐름 |
|---|---|
| 수집 | 실제 환경의 API/MQTT/Kafka/DB 자리를 파이썬 스크립트가 대신함 |
| 처리 | Raw Data → 정제 → Aggregation → Feature Engineering |
| 분석 | Feature 선택 → StandardScaler(표준화) → K-Means → 고객 Segment |
| 시각화 | 집계 결과를 KPI 카드·차트·표로 사람이 읽을 수 있게 전달 |

## 이렇게 보면 정확히 4계층입니다

| 계층 | 역할 | 이번 실습 | 실제 기업 환경 |
|---|---|---|---|
| 수집 | 데이터 획득 | Python | MQTT, Kafka, API, Flume |
| 저장/처리 | 정제·변환 | CSV + Pandas | S3, Spark, Flink |
| 분석 | 패턴/예측 | Scikit-learn | Spark ML, SageMaker |
| 시각화 | 결과 전달 | Streamlit | Tableau, Power BI, Grafana |

이번 실습에서 쓴 도구는 실제 기업 환경의 "축소판"입니다. 도구 이름이
아니라 **각 계층이 데이터를 어떻게 변형시켜 다음 계층에 넘기는지**가
핵심입니다.

## 데이터 변화를 직접 확인하기

```bash
wc -l data/raw/customer_log.csv          # 1,000건 (원시 이벤트)
wc -l data/processed/customer.csv        # 100건 안팎 (고객 단위로 집계)
```

1,000건의 Raw Event가 → 고객 단위 데이터 → 고객 행동 Feature →
고객 Segment → Dashboard Insight로 좁혀지는 과정을 행 수 변화로도
확인할 수 있습니다.

## 3c(4계층 설계 과제)와의 연결

`../03c-four-layer-design/`에서 시나리오를 보고 "어느 계층에 어떤
도구를 쓸지" 종이 위에서 설계해봤다면, 이 실습은 **그 설계도가 실제
코드에서는 무슨 일을 하는지**를 보여줍니다. 두 실습을 이어서 진행하면
"설계 → 구현"의 흐름이 자연스럽게 연결됩니다.

## 자주 겪는 문제

- **02_process.py에서 파일을 못 찾음** → 반드시 01_collect.py를 먼저
  실행해 `data/raw/customer_log.csv`를 만들어야 합니다
- **Streamlit이 브라우저를 자동으로 못 엶** → 터미널에 출력된
  `Local URL`을 직접 복사해서 열면 됩니다
- **포트 충돌(8501)** → `streamlit run 04_dashboard.py --server.port 8502`
  처럼 포트를 지정해 실행
- **다시 처음부터** → `data/raw`, `data/processed` 안의 CSV 파일만
  지우고 01번부터 다시 실행하면 됩니다

## 심화 — 엣지컴퓨팅형 구조로 확장하고 싶다면

이 구조를 실시간·엣지 버전으로 발전시키려면 다음 흐름이 더 어울립니다.

```
IoT Sensor(Python) → MQTT → Mosquitto → Python Consumer
  → Pandas → 이상탐지 → Streamlit
```

엣지 과정(`edge-blueprint-labs`)의 4강(MQTT 연동)·6강(스트림 처리)이
정확히 이 구조를 다루고 있으니, 관심 있으면 그쪽 실습과 비교해보세요.
