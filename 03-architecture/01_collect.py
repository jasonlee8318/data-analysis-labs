# ============================================================
# [1. 수집] 고객 행동 로그 생성
#
# 실제 시스템에서는 API, MQTT, Kafka, DB 등에서 데이터가 들어오지만,
# 이번 실습에서는 파이썬 프로그램 자체를 데이터 Source로 사용합니다.
# ============================================================
import pandas as pd
import random
from datetime import datetime, timedelta
import os

os.makedirs("data/raw", exist_ok=True)

rows = []
for i in range(1000):
    customer_id = random.randint(1, 100)
    login_count = random.randint(0, 20)
    purchase_count = random.randint(0, 10)
    session_time = random.randint(1, 120)
    event_time = datetime.now() - timedelta(days=random.randint(0, 30))
    rows.append({
        "customer_id": customer_id,
        "login_count": login_count,
        "purchase_count": purchase_count,
        "session_time": session_time,
        "event_time": event_time,
    })

df = pd.DataFrame(rows)
df.to_csv("data/raw/customer_log.csv", index=False)

print("데이터 수집 완료")
print(df.head())
