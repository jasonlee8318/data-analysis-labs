# ETL 실습 — 데이터 접근 및 통합 구성

> **시작 전 체크**
> 1. 터미널에서 이 폴더로 이동했는지 확인: `cd data-analysis-labs/05-etl`
> 2. **이전 회차 환경을 껐는지 확인** (포트가 겹칩니다):
>    직전 회차 폴더에서 `docker compose down` 실행 후 돌아오세요.
>    실행 중인 것이 있는지는 `docker ps`로 확인할 수 있습니다.

MySQL(JDBC) + REST API + 데이터 레이크(MinIO/S3)라는 **세 원천이 실제로 떠 있는 환경**에서
Extract → Transform(전처리 4대 항목) → Load를 한 바퀴 도는 실습입니다.

## 환경 구성

`docker compose up -d` 한 줄로 다섯 개가 함께 뜹니다.

| 서비스 | 역할 | 접속 |
|---|---|---|
| shop-mysql | 회원/주문 DB (더티 데이터 자동 적재) | 컨테이너 내부 mysql:3306 |
| sales-api | 매출 REST API | http://localhost:5000/sales?date=2026-04-29 |
| datalake-minio | S3 호환 데이터 레이크 | 콘솔 http://localhost:9001 (admin/minio12345) |
| minio-setup | 버킷 생성 후 자동 종료 (Exited가 정상) | — |
| jupyter | PySpark 실습 환경 | http://localhost:8888/?token=spark |

## 사전 준비 (수업 전에 완료)

1. Docker Desktop 설치·실행 (메모리 6GB 이상 권장)
2. 저장소 다운로드 후 `docker compose pull`
3. **중요**: `docker compose up -d` 후 Jupyter에서 `etl_lab.ipynb`의
   **0번 셀을 한 번 실행**해 두세요. 최초 실행 시 JDBC 드라이버와 S3 커넥터를
   내려받는데(1~2분), 미리 해두면 수업 당일 전원 대기 시간이 사라집니다.

## 실습 진행

1. `docker compose up -d` → 30초 뒤 http://localhost:8888/?token=spark 접속
2. `work/etl_lab.ipynb` 열고 위에서부터 순서대로 실행:
   - **0**: SparkSession(드라이버/커넥터 로드) + 레이크에 로그 준비
   - **1. Extract**: JDBC(병렬 로딩 옵션) / API / s3a Parquet — 세 원천 수집
   - **2. Transform**: 타입 변환 → 결측치 → 이상치(IQR·도메인) → 중복 제거 → 조인·집계
   - **3. Load**: `s3a://my-datalake/analytics/`에 Parquet 적재 후 재조회 검증
3. MinIO 콘솔(localhost:9001)에서 적재된 파일을 눈으로 확인

데이터에는 전처리 4대 항목이 **일부러 심어져** 있습니다:
이메일 NULL, 나이 250세, 음수 주문, 100억 주문, 중복 행, 문자열 age/amount.

## 자주 겪는 문제

- **0번 셀에서 오래 멈춰 있음** → 최초 1회 드라이버 다운로드 중. 재실행 시 즉시 완료
- **JDBC 접속 오류** → MySQL 초기화에 최대 30초 소요. `docker compose logs mysql`에서 "ready for connections" 확인 후 재시도
- **minio-setup이 Exited** → 정상입니다 (버킷 만들고 종료되는 1회성 작업)
- **s3a 오류** → 0번 셀(엔드포인트 설정 포함)을 건너뛰고 아래 셀부터 실행한 경우. 커널 재시작 후 0번부터
- **포트 충돌(3306/5000/8888/9000)** → compose에서 왼쪽 포트만 변경
- **전부 초기화** → `docker compose down -v` 후 다시 `up -d` (DB 더티 데이터도 재적재됨)
