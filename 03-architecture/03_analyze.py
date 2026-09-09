# ============================================================
# [3. 분석] Feature 선택 -> StandardScaler -> K-Means -> 고객 Segment
#
# 복잡한 예측 모델보다, 비지도학습인 K-Means 군집화로
# "레이블 없이도 고객을 그룹으로 나눌 수 있다"는 걸 먼저 체감합니다.
# ============================================================
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/processed/customer.csv")
features = ["login_count", "purchase_count", "session_time"]
X = df[features]

# 표준화가 필요한 이유: login_count(0~20대)와 session_time(1~120대)처럼
# 단위/스케일이 다른 값을 그대로 넣으면 값이 큰 변수가 거리 계산을 지배합니다.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 고객을 3개 그룹으로 분류 (그룹 수 3은 임의 선택 — 실무에서는 Elbow Method 등으로 결정)
model = KMeans(n_clusters=3, random_state=42)
df["customer_group"] = model.fit_predict(X_scaled)

df.to_csv("data/processed/customer_analysis.csv", index=False)

print("분석 완료")
print(df.head())
print("\n그룹별 인원수:")
print(df["customer_group"].value_counts().sort_index())
