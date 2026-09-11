# 5강 — 데이터 접근 및 통합 구성 (Airflow ETL, 3원천 통합)

MySQL·REST API·데이터 레이크(MinIO, S3 호환) 세 원천을 **Airflow가
직접 연결**해서, 단순히 각각 추출만 하는 게 아니라 **세 원천을 실제로
합쳐 이전에는 없던 새로운 통합 테이블 하나**를 만드는 ETL 파이프라인을
경험합니다. 원천 연결 등록부터 자동 실행까지 Airflow 하나로 전부
진행합니다.

## 사전 준비

```bash
docker compose pull
docker compose up -d --build
```

MySQL(더티 데이터 자동 적재) + REST API + MinIO(버킷 자동 생성) +
Airflow, 4개 서비스가 기동됩니다. 최초 빌드는 Airflow 이미지가 커서
1~2분 정도 걸릴 수 있습니다.

## 1단계 — Airflow 접속

1. 관리자 비밀번호 확인:
   ```bash
   docker compose exec airflow cat /opt/airflow/standalone_admin_password.txt
   ```
2. http://localhost:8081 접속 → 계정 `admin` / 위에서 확인한 비밀번호로 로그인

## 2단계 — MySQL·API·MinIO 연결 등록 (여기가 진짜 시작점)

DAG 코드 어디에도 비밀번호가 적혀 있지 않습니다. **Airflow의 표준
방식대로, "어디에 어떻게 접속할지"를 UI에서 먼저 등록해두고 코드에서는
이름(conn_id)만 참조**합니다.

**Admin → Connections → +(연결 추가)**에서 아래 3개를 각각 등록합니다.

| Connection Id | Connection Type | Host | Schema | Login | Password | Port |
|---|---|---|---|---|---|---|
| `mysql_shop` | Generic | `shop-mysql` | `shop` | `analyst` | `analyst123` | `3306` |
| `sales_api` | Generic | `sales-api` | (비움) | (비움) | (비움) | `5000` |
| `minio_s3` | Generic | `datalake-minio` | (비움) | `admin` | `minio12345` | `9000` |

세 개 다 저장하면 **Admin → Connections** 목록에 3개가 보여야 합니다.

## 3단계 — DAG 활성화 및 실행

1. DAG 목록에서 **`cafe_shop_etl`** 찾기 → 왼쪽 토글을 켜서 활성화
2. 오른쪽 **▶(Trigger DAG)** 버튼으로 즉시 1회 실행
3. **Graph** 보기에서 아래 순서로 각 Task가 초록색(성공)이 되는지 확인:
   `extract_mysql` · `extract_api` · `extract_minio_logs`(3개 병렬)
   → `combine_all_sources` → `load_result`
4. `combine_all_sources` Task의 **Logs**에서 "세 원천이 합쳐진 최종
   결과" 표가 찍히는지 확인 — `name`(MySQL), `total_amount`(MySQL),
   `visit_count`(MinIO), `daily_total_revenue_allchannels`(API)가
   **한 표 안에 전부** 들어있어야 합니다
5. MinIO 콘솔(localhost:9001, admin/minio12345)에서
   `my-datalake/analytics/member_summary_airflow/`에 파일이 생겼는지 확인
6. **Trigger DAG를 한 번 더 눌러보세요** — 타임스탬프가 다른 새 파일이
   하나 더 생기는 걸 확인할 수 있습니다

## 데이터 구조 — 일부러 심어둔 더티 데이터

`mysql-init/init.sql`에 전처리 4대 항목이 심어져 있습니다:
이메일 NULL(2건), 나이 250세(도메인 이상치), 음수 주문(-5000),
100억 주문(IQR 이상치), 완전 중복 행(회원 1건·주문 1건),
문자열로 저장된 age/amount(타입 변환 필요).

`combine_all_sources` Task가 이 데이터를 **타입변환 → 결측치 →
이상치(도메인+IQR) → 중복 제거** 순서로 정제한 뒤, MinIO·API 데이터와
결합합니다.

## 핵심 구조 — 세 원천이 실제로 하나로 합쳐지는 여정

```
Connections 등록 (mysql_shop / sales_api / minio_s3)   ← 2단계에서 미리 등록
        │
        ▼
extract_mysql ────────┐
extract_api ──────────┼─→ combine_all_sources ─→ load_result ─→ 새 Parquet 파일 적재
extract_minio_logs ───┘        │
                                ├─ MySQL: member_id별 총 구매액 (회원·주문 조인)
                                ├─ MinIO: member_id로 진짜 조인 → 회원별 방문 횟수 추가
                                └─ API: 조인 키가 없어 "오늘의 회사 전체 매출/최고 채널"로
                                        모든 행에 공통 부착
```

**세 원천이 각각 무엇을 보태는지**

| 원천 | Connection | 무엇을 추출하나 | `combine_all_sources`에서 어떻게 쓰이나 |
|---|---|---|---|
| MySQL | `mysql_shop` | 회원(members) + 주문(orders) | 정제 후 `member_id`로 조인·집계 → 회원별 총 구매액(`total_amount`)의 뼈대 |
| MinIO | `minio_s3` | 방문 로그(`visit_logs.parquet`, 최초 1회 자동 생성) | `member_id`로 **진짜 조인** → 회원별 방문 횟수(`visit_count`) 추가 |
| API | `sales_api` | 채널별(web/mobile/ads) 매출 | 회원 단위 키가 없어 조인 대신, 오늘의 전체 매출·최고 채널을 모든 행에 공통 지표로 부착 |

**MySQL·MinIO는 `member_id`라는 공통 키로 진짜 조인**되고, **API는
조인 키가 없는 회사 전체 지표라서 "컨텍스트 정보"로 나란히 붙는다**는
차이를 구분해서 보는 게 이번 회차의 핵심입니다 — 실무에서도 원천마다
조인 가능한 것과, 그냥 같은 리포트에 나란히 붙이기만 하는 것이
섞이는 경우가 흔합니다.

**Load**: `load_result`가 `s3fs`로 MinIO에 Parquet 적재. 실행할 때마다
파일명에 타임스탬프가 붙어서(`member_summary_20260911T041000.parquet`
형태), DAG를 여러 번 트리거하면 MinIO 콘솔에 파일이 계속 새로
쌓이는 걸 직접 볼 수 있습니다.

## 자주 겪는 문제

- **Airflow 웹 화면이 안 뜸** → 최초 빌드는 이미지가 커서(1GB 안팎) 시간이
  걸립니다. `docker compose logs airflow`에서 `Airflow is ready` 문구
  확인 후 재시도
- **DAG 목록에 `cafe_shop_etl`이 안 보임** → `docker compose logs airflow`에서
  DAG 파일 파싱 에러가 있는지 확인. 보통 1분 이내에 자동으로 스캔됩니다
- **Task가 빨간색(실패)** → 로그를 열어보면 대부분 연결 실패입니다.
  `docker compose ps`로 mysql/sales-api가 Up 상태인지 먼저 확인하세요
- **`airflow.exceptions.AirflowNotFoundException: The conn_id 'mysql_shop' isn't defined`**
  → 2단계(Connections 등록)를 건너뛰신 경우입니다. Admin → Connections에서
  세 개(`mysql_shop`/`sales_api`/`minio_s3`)가 전부 등록돼 있는지 확인
- **`combine_all_sources`에서 `visit_count`가 전부 0** → `extract_minio_logs`가
  로그를 못 심었을 수 있습니다. MinIO 콘솔에서 `my-datalake/logs/visit_logs.parquet`가
  있는지 확인
- **포트 충돌(3306/5000/8081/9000/9001)** → compose에서 왼쪽 포트만 변경
- **전부 초기화** → `docker compose down -v` 후 다시 `up -d --build`
  (DB 더티 데이터도, Airflow의 DAG 실행 이력도, 심어둔 방문 로그도
  함께 초기화됨)
