# ============================================================
# 5강 심화 — 경량 Airflow (SequentialExecutor + SQLite, 컨테이너 1개)
#
# 공식 docker-compose(CeleryExecutor)는 Postgres+Redis+webserver+
# scheduler+worker+triggerer까지 6개 컨테이너, 최소 4GB(권장 8GB)를
# 요구합니다. 이 회차는 이미 MySQL+API+MinIO+Jupyter가 떠 있는
# 상태라, 그 위에 공식 방식을 얹으면 너무 무거워집니다.
#
# 대신 "airflow standalone" 명령 하나로 뜨는 가벼운 방식을 씁니다 —
# 메타데이터 DB로 SQLite를 쓰고, 스케줄러·웹서버가 한 프로세스
# 그룹으로 같이 뜹니다. 공식 문서도 이 방식을 "학습·로컬 실험용"
# 이라고 명시합니다 — 지금 우리 목적과 정확히 일치합니다.
# ============================================================
FROM apache/airflow:2.10.5-python3.11

# ETL DAG가 쓰는 라이브러리 — Spark/Java 없이 pandas로 가볍게 처리
RUN pip install --no-cache-dir \
    pymysql==1.1.1 \
    s3fs==2024.10.0 \
    pyarrow==17.0.0

# 예시 DAG를 꺼서 우리 DAG만 목록에 보이게 함
ENV AIRFLOW__CORE__LOAD_EXAMPLES=false
