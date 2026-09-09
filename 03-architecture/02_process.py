# ============================================================
# [2. 처리] Raw Data -> 정제 -> Aggregation -> Feature Engineering
#
# 원시 로그(1000건, 고객당 여러 행)를 고객 1명당 1행으로 집계하고,
# 활동 점수(activity_score)라는 파생 변수를 만듭니다.
# ============================================================
import pandas as pd
import os

df = pd.read_csv("data/raw/customer_log.csv")
print("원본 데이터")
print(df.head())

# 고객별 데이터 집계
processed = (
    df.groupby("customer_id")
    .agg(
        login_count=("login_count", "sum"),
        purchase_count=("purchase_count", "sum"),
        session_time=("session_time", "mean"),
    )
    .reset_index()
)

# 파생 변수 생성 — 로그인/구매/세션시간에 가중치를 줘서 활동 점수 하나로 요약
processed["activity_score"] = (
    processed["login_count"] * 0.3
    + processed["purchase_count"] * 0.5
    + processed["session_time"] * 0.2
)

os.makedirs("data/processed", exist_ok=True)
processed.to_csv("data/processed/customer.csv", index=False)

print("처리 완료")
print(processed.head())
