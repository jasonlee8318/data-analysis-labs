# ============================================================
# 6강 실습 준비 — Power BI로 주별/월별 영업 실적을 시각화하기 위한
# 정제된 일별 매출 데이터 내보내기
#
# 8강에서 배운 정제 로직(결측·이상치 처리)을 그대로 적용합니다.
# 여기서는 매장×요일처럼 미리 뭉쳐서 집계하지 않고, "하루 단위" 그대로
# 내보냅니다 — 주별/월별로 묶는 작업 자체를 Power BI 안에서
# 직접 해보는 것이 이번 회차의 핵심이기 때문입니다.
# ============================================================
import pandas as pd

SRC = "../../08-09-preprocess-stats/data/cafe_sales.csv"
OUT = "cafe_sales_clean.csv"

df = pd.read_csv(SRC)
# 8강과 동일한 정제 로직
df["weather"] = df["weather"].fillna("Unknown")      # 범주형 결측 → Unknown
df = df.dropna(subset=["sales"])                       # 매출(라벨) 결측 → 삭제
df = df[(df["sales"] >= 0) & (df["temp"].between(-30, 45))]
df = df.drop_duplicates(subset=["store_id", "date"])   # 같은 매장·같은 날짜 중복 제거

q1, q3 = df["sales"].quantile([0.25, 0.75])
iqr = q3 - q1
df = df[df["sales"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]

# 날짜 타입을 명시적으로 맞춰서 저장 — Power BI가 날짜로 정확히
# 인식해야 자동으로 연/분기/월/일 계층을 만들어줍니다.
df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
df = df.sort_values(["store_id", "date"])

df.to_csv(OUT, index=False, encoding="utf-8-sig")  # BOM 포함: 한글 Power BI 호환
print(f"저장 완료: {OUT} ({len(df)}행, {df['store_id'].nunique()}개 매장)")
print(f"기간: {df['date'].min()} ~ {df['date'].max()}")
print(df.head())
