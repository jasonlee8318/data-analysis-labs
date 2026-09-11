# ============================================================
# 3회차 — 4계층 파이프라인 실습 환경
#
# pandas/scikit-learn/streamlit만 필요한 가벼운 실습이라, 무거운
# base 이미지 대신 python:3.11-slim에 딱 이 세 개만 설치합니다.
# ============================================================
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너를 계속 띄워둔 채로 대기 — 각 단계(01~04)는
# docker compose exec로 그때그때 실행합니다.
CMD ["sleep", "infinity"]
