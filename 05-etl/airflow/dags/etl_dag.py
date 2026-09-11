# ============================================================
# 5강 — Airflow로 MySQL·API·MinIO 세 원천을 하나로 합치기
#
# 원래 Jupyter에서 셀을 하나씩 눌러 수동으로 실행하던 ETL 흐름을,
# Airflow가 자동으로 스케줄링·실행·재시도하도록 옮긴 버전입니다.
#
# 이 DAG의 핵심은 "추출만 세 번 하고 끝"이 아니라, **세 원천을 실제로
# 합쳐서 이전에는 없던 새로운 결과물 하나를 만드는 것**입니다.
#
#   MySQL(회원+주문) ──┐
#                      ├─→ member_id로 실제 조인/집계 ─→ 새로운 통합 테이블
#   MinIO(방문 로그) ───┤     (구매액 + 방문횟수 + 오늘의 전체 매출)
#                      │
#   API(채널별 매출) ───┘
#
# ⚠️ MySQL/API/MinIO 접속 정보는 이 코드 안에 없습니다. Airflow의
# 표준 방식대로, **Airflow UI(Admin → Connections)**에서 미리 등록해둔
# 연결 정보를 `BaseHook.get_connection(conn_id)`로 이름만으로 불러와
# 씁니다 — 코드에 비밀번호를 그대로 적어두는 건 Airflow가 권장하지
# 않는 방식입니다. README의 "2단계"에서 이 세 개 연결(mysql_shop /
# sales_api / minio_s3)을 먼저 등록해야 이 DAG가 동작합니다.
#
# Spark를 다시 띄우진 않습니다 — 이 회차의 데이터는 아주 작아서
# pandas만으로 충분하고, Airflow 컨테이너를 가볍게 유지하기 위해
# 일부러 Spark/Java를 넣지 않았습니다.
# ============================================================
from __future__ import annotations

import pendulum
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook

# MinIO에 미리 있다고 가정하는 방문 로그 — 실제 현장이라면 웹서버가
# 계속 쌓아둔 로그가 이미 데이터 레이크에 있을 텐데, 이 실습에서는
# 그 상황을 재현하기 위해 이 값을 최초 1회 MinIO에 직접 심어둡니다.
SEED_LOGS = [
    {"member_id": 1, "page": "/home", "ts": "2026-04-29 09:01"},
    {"member_id": 2, "page": "/product/7", "ts": "2026-04-29 09:02"},
    {"member_id": 3, "page": "/cart", "ts": "2026-04-29 09:05"},
    {"member_id": 1, "page": "/order", "ts": "2026-04-29 09:07"},
    {"member_id": 5, "page": "/home", "ts": "2026-04-29 09:10"},
]
LOGS_PATH = "my-datalake/logs/visit_logs.parquet"


@dag(
    dag_id="cafe_shop_etl",
    description="MySQL + REST API + MinIO 세 원천을 합쳐 회원별 통합 리포트 생성",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,  # 과거 스케줄을 소급 실행하지 않음 (실습용)
    tags=["5강", "etl"],
)
def cafe_shop_etl():

    # ── Extract 1: MySQL (JDBC 대신 pymysql로 가볍게) ──
    # 접속 정보는 코드가 아니라 Airflow Connection "mysql_shop"에서 가져옵니다.
    @task
    def extract_mysql() -> dict:
        import pymysql

        c = BaseHook.get_connection("mysql_shop")
        conn = pymysql.connect(
            host=c.host, port=c.port or 3306,
            user=c.login, password=c.password, database=c.schema,
        )
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM members")
                members = cur.fetchall()
                cur.execute("SELECT * FROM orders")
                orders = cur.fetchall()
        finally:
            conn.close()
        print(f"members {len(members)}행, orders {len(orders)}행 추출 완료")
        return {"members": members, "orders": orders}

    # ── Extract 2: REST API — 채널별 매출(회사 전체 지표) ──
    # 접속 정보는 Airflow Connection "sales_api"에서 가져옵니다.
    @task
    def extract_api() -> list:
        import requests

        c = BaseHook.get_connection("sales_api")
        url = f"http://{c.host}:{c.port}/sales"
        resp = requests.get(url, params={"date": "2026-04-29"}, timeout=5)
        records = resp.json()["records"]
        print(f"API({url})에서 채널별 매출 {len(records)}건 추출 완료")
        return records

    # ── Extract 3: MinIO(데이터 레이크) — 회원별 방문 로그 ──
    # 접속 정보는 Airflow Connection "minio_s3"에서 가져옵니다.
    # 로그가 아직 레이크에 없으면(최초 1회) 먼저 심어둔 뒤 읽어옵니다 —
    # 실제 현장이라면 이 Extract 시점엔 이미 웹서버가 쌓아둔 로그가
    # 존재한다고 보면 됩니다.
    @task
    def extract_minio_logs() -> list:
        import pandas as pd
        import s3fs

        c = BaseHook.get_connection("minio_s3")
        endpoint = c.host if c.host.startswith("http") else f"http://{c.host}:{c.port}"
        fs = s3fs.S3FileSystem(
            key=c.login, secret=c.password,
            client_kwargs={"endpoint_url": endpoint},
        )

        if not fs.exists(LOGS_PATH):
            pd.DataFrame(SEED_LOGS).to_parquet(f"s3://{LOGS_PATH}", filesystem=fs)
            print(f"레이크에 방문 로그가 없어 최초 1회 심어둠: s3a://{LOGS_PATH}")

        logs = pd.read_parquet(f"s3://{LOGS_PATH}", filesystem=fs)
        print(f"MinIO에서 방문 로그 {len(logs)}행 추출 완료")
        return logs.to_dict(orient="records")

    # ── Transform: 세 원천을 실제로 합쳐서 새로운 통합 테이블 생성 ──
    @task
    def combine_all_sources(mysql_data: dict, api_data: list, minio_logs: list) -> list:
        import pandas as pd

        members = pd.DataFrame(mysql_data["members"])
        orders = pd.DataFrame(mysql_data["orders"])
        logs = pd.DataFrame(minio_logs)

        # 2-1) 타입 변환 — 다른 정제보다 반드시 먼저
        # (문자열 상태로 두면 사전식 비교가 일어나 이후 필터가 오작동함)
        members["age"] = pd.to_numeric(members["age"], errors="coerce")
        orders["amount"] = pd.to_numeric(orders["amount"], errors="coerce")

        # 2-2) 결측치 처리 — 이메일 없는 회원 삭제
        before = len(members)
        members = members.dropna(subset=["email"])
        print(f"결측치 처리: 회원 {before} → {len(members)}행")

        # 2-3) 이상치 처리 — 도메인 기준 + IQR 기준
        members = members[members["age"].between(0, 120)]
        orders = orders[orders["amount"] > 0]

        q1, q3 = orders["amount"].quantile([0.25, 0.75])
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        before = len(orders)
        orders = orders[orders["amount"].between(low, high)]
        print(f"IQR 이상치 제거: 주문 {before} → {len(orders)}행 (허용범위 {low:,.0f}~{high:,.0f})")

        # 2-4) 중복 제거
        orders = orders.drop_duplicates()
        members = members.drop_duplicates(subset=["member_id"])

        # 2-5) MySQL 내부 통합 — 회원별 총 주문금액 (1차 결과)
        summary = (
            members.merge(orders, on="member_id")
            .groupby(["member_id", "name"], as_index=False)["amount"]
            .sum()
            .rename(columns={"amount": "total_amount"})
        )

        # 3-1) MinIO 로그와 결합 — member_id로 실제 조인 (진짜 통합 지점)
        # MySQL 회원 데이터와 MinIO 방문 로그는 둘 다 member_id를 갖고
        # 있어서, 서로 다른 두 원천을 키 값으로 정확히 이어붙일 수 있습니다.
        visit_counts = logs.groupby("member_id").size().reset_index(name="visit_count")
        summary = summary.merge(visit_counts, on="member_id", how="left")
        summary["visit_count"] = summary["visit_count"].fillna(0).astype(int)

        # 3-2) API 데이터 결합 — 회원별 키가 없는 회사 전체 지표라서,
        # 조인이 아니라 "오늘의 컨텍스트 지표"로 모든 행에 부착합니다.
        # (실무에서도 원천마다 조인 가능한 것과, 그냥 같은 리포트에
        #  나란히 붙이기만 하는 것이 섞이는 경우가 흔합니다.)
        api_df = pd.DataFrame(api_data)
        if not api_df.empty:
            total_revenue = int(api_df["revenue"].sum())
            top_channel = api_df.loc[api_df["revenue"].idxmax(), "channel"]
        else:
            total_revenue, top_channel = 0, None
        summary["daily_total_revenue_allchannels"] = total_revenue
        summary["daily_top_channel"] = top_channel

        summary = summary.sort_values("member_id")
        print("=== 세 원천이 합쳐진 최종 결과 ===")
        print(summary)
        return summary.to_dict(orient="records")

    # ── Load: MinIO(S3 호환)에 통합 결과를 Parquet으로 적재 ──
    # 접속 정보는 Airflow Connection "minio_s3"에서 가져옵니다.
    # 매번 실행할 때마다 타임스탬프가 파일명에 들어가서, 트리거할
    # 때마다 "새로운 파일이 쌓이는 것"을 MinIO 콘솔에서 직접 볼 수 있습니다
    # (같은 파일에 매번 덮어쓰면 몇 번을 실행해도 새로 쌓인 게 안 보입니다).
    @task
    def load_result(summary: list, **kwargs) -> None:
        import pandas as pd
        import s3fs

        c = BaseHook.get_connection("minio_s3")
        endpoint = c.host if c.host.startswith("http") else f"http://{c.host}:{c.port}"

        df = pd.DataFrame(summary)
        fs = s3fs.S3FileSystem(
            key=c.login,
            secret=c.password,
            client_kwargs={"endpoint_url": endpoint},
        )
        ts = kwargs["ts_nodash"]  # 이번 DAG 실행의 타임스탬프 (예: 20260911T041000)
        path = f"my-datalake/analytics/member_summary_airflow/member_summary_{ts}.parquet"
        with fs.open(path, "wb") as f:
            df.to_parquet(f)
        print(f"적재 완료: s3a://{path} ({len(df)}행, 컬럼: {list(df.columns)})")

    mysql_data = extract_mysql()
    api_data = extract_api()
    minio_logs = extract_minio_logs()
    summary = combine_all_sources(mysql_data, api_data, minio_logs)
    load_result(summary)


cafe_shop_etl()
