# ============================================================
# [4. 시각화] Streamlit Dashboard
#
# 코드 몇 줄로 실제 브라우저 대시보드를 띄웁니다.
# 실행: streamlit run 04_dashboard.py
# ============================================================
import streamlit as st
import pandas as pd

df = pd.read_csv("data/processed/customer_analysis.csv")

st.title("Customer Analytics Dashboard")

# KPI 카드
st.metric("고객 수", df["customer_id"].nunique())
st.metric("평균 구매", round(df["purchase_count"].mean(), 1))
st.metric("평균 세션 시간", round(df["session_time"].mean(), 1))

st.subheader("고객 그룹 분포")
group_count = df["customer_group"].value_counts().sort_index()
st.bar_chart(group_count)

st.subheader("로그인 수 vs 구매 수")
st.scatter_chart(df, x="login_count", y="purchase_count")

st.subheader("분석 데이터")
st.dataframe(df)
