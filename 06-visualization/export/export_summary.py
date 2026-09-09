# ============================================================
# 6강 실습 준비 — Power BI / Tableau에 연결할 대시보드용 데이터 내보내기
#
# 8회차(전처리)에서 배운 정제 로직(결측·이상치 처리)을 그대로 적용한 뒤,
# 매장별·요일별·날씨별로 집계해 대시보드 도구가 바로 읽기 좋은
# 형태(cafe_dashboard_data.csv)로 저장합니다.
#
# Spark 없이 pandas만으로 동작합니다 — 이 회차의 목적은 "시각화 도구
# 연결과 대시보드 설계"이지 Spark 재학습이 아니기 때문입니다.
# ============================================================
import pandas as pd

SRC = "../../08-09-preprocess-stats/data/cafe_sales.csv"
OUT = "cafe_dashboard_data.csv"

df = pd.read_csv(SRC)

# 8회차와 동일한 정제 로직 (요약)
df["weather"] = df["weather"].fillna("Unknown")      # 범주형 결측 → Unknown
df = df.dropna(subset=["sales"])                       # 매출(라벨) 결측 → 삭제
df = df[(df["sales"] >= 0) & (df["temp"].between(-30, 45))]

q1, q3 = df["sales"].quantile([0.25, 0.75])
iqr = q3 - q1
df = df[df["sales"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]

df["is_weekend"] = df["weekday"].isin(["Sat", "Sun"]).astype(int)

# 대시보드에서 바로 쓸 수 있게 매장×요일×날씨 단위로 집계
summary = (
    df.groupby(["store_id", "weekday", "weather"], as_index=False)
    .agg(
        avg_sales=("sales", "mean"),
        total_sales=("sales", "sum"),
        avg_customers=("customer_cnt", "mean"),
        days=("date", "count"),
    )
    .round(0)
)

summary.to_csv(OUT, index=False, encoding="utf-8-sig")  # BOM 포함: 한글 Excel/PowerBI 호환
print(f"저장 완료: {OUT} ({len(summary)}행)")
print(summary.head())
