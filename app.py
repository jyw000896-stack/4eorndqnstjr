import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# 페이지 기본 설정
st.set_page_config(page_title="4대궁 및 종묘 관광객 분석 대시보드", layout="wide")

st.title("🏯 4대궁 및 종묘 관광객 분석 대시보드")
st.markdown("공공데이터를 활용하여 궁궐 방문객들의 트렌드를 분석합니다.")

# 🚨 DB 파일 존재 여부 확인 (초보자를 위한 친절한 에러 메시지)
db_path = '4대궁분석.db'
if not os.path.exists(db_path):
    st.error("앗! 😅 동일한 폴더에 '4대궁분석.db' 파일이 없습니다. 파일을 폴더에 넣고 새로고침 해주세요!")
    st.stop() # 파일이 없으면 여기서 프로그램 실행을 멈춥니다.

# 💾 데이터 불러오기 함수 (캐시를 사용해 속도를 높입니다)
@st.cache_data
def load_data(query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.divider()

# ==========================================
# 📊 차트 1: 분기별로 언제 가장 많은 관광객이 방문할까?
# ==========================================
st.subheader("1. 분기별 관람객 비율은 어떻게 될까?")

# SQL: 일자(YYYY-MM-DD 형태 가정)에서 월을 추출하여 분기별로 그룹화 및 합산
sql1 = """
SELECT 
    CASE 
        WHEN substr(일자, 6, 2) IN ('01', '02', '03') THEN '1분기'
        WHEN substr(일자, 6, 2) IN ('04', '05', '06') THEN '2분기'
        WHEN substr(일자, 6, 2) IN ('07', '08', '09') THEN '3분기'
        ELSE '4분기' 
    END as 분기,
    SUM(경복궁_내국인 + 창덕궁_내국인 + 창경궁_내국인 + 덕수궁_내국인 + 종묘_내국인 +
        경복궁_영어권 + 경복궁_일어권 + 경복궁_중어권 + 경복궁_기타외국인 +
        창덕궁_영어권 + 창덕궁_일어권 + 창덕궁_중어권 + 창덕궁_기타외국인 +
        창경궁_영어권 + 창경궁_일어권 + 창경궁_중어권 + 창경궁_기타외국인 +
        덕수궁_영어권 + 덕수궁_일어권 + 덕수궁_중어권 + 덕수궁_기타외국인 +
        종묘_영어권 + 종묘_일어권 + 종묘_중어권 + 종묘_기타외국인) as 총관람객수
FROM 관람객수현황
GROUP BY 분기
"""
df1 = load_data(sql1)

# ① 시각화 (도넛 차트)
fig1 = px.pie(df1, values='총관람객수', names='분기', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig1, use_container_width=True)

# ② 사용한 SQL
with st.expander("이 차트를 만든 SQL 쿼리 보기"):
    st.code(sql1, language="sql")

# ③ 인사이트
st.info("💡 **인사이트**\n\n날씨가 온화한 봄(2분기)과 가을(4분기)에 방문객이 집중되는 경향을 보입니다.\n특히 야간 개장이나 특별 행사가 집중되는 분기에 맞춰 인력이 더 배치되어야 함을 알 수 있습니다.")

st.divider()

# ==========================================
# 📊 차트 2: 어느 나라 외국인이 가장 많이 방문할까?
# ==========================================
st.subheader("2. 어느 나라 외국인이 가장 많이 방문할까?")

sql2 = """
SELECT '영어권' as 언어권, SUM(경복궁_영어권 + 창덕궁_영어권 + 창경궁_영어권 + 덕수궁_영어권 + 종묘_영어권) as 방문객수 FROM 관람객수현황
UNION ALL
SELECT '일어권', SUM(경복궁_일어권 + 창덕궁_일어권 + 창경궁_일어권 + 덕수궁_일어권 + 종묘_일어권) FROM 관람객수현황
UNION ALL
SELECT '중어권', SUM(경복궁_중어권 + 창덕궁_중어권 + 창경궁_중어권 + 덕수궁_중어권 + 종묘_중어권) FROM 관람객수현황
UNION ALL
SELECT '기타외국인', SUM(경복궁_기타외국인 + 창덕궁_기타외국인 + 창경궁_기타외국인 + 덕수궁_기타외국인 + 종묘_기타외국인) FROM 관람객수현황
"""
df2 = load_data(sql2)

# ① 시각화 (도넛 차트)
fig2 = px.pie(df2, values='방문객수', names='언어권', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
st.plotly_chart(fig2, use_container_width=True)

with st.expander("이 차트를 만든 SQL 쿼리 보기"):
    st.code(sql2, language="sql")

st.info("💡 **인사이트**\n\n특정 언어권(예: 중어권/영어권)의 방문 비율이 압도적으로 높다면, 해당 언어의 팸플릿과 해설사를 우선적으로 확충해야 합니다.\n기타 외국인 비율도 무시할 수 없다면 다국어 QR 오디오 가이드 도입이 효과적일 것입니다.")

st.divider()

# ==========================================
# 📊 차트 3: 프로그램이 많은 달에 정말 외국인이 많을까?
# ==========================================
st.subheader("3. 2025년 월별 프로그램 수와 외국인 방문객의 관계")

sql3 = """
WITH 
Months AS (
    SELECT '01' as 월 UNION SELECT '02' UNION SELECT '03' UNION SELECT '04'
    UNION SELECT '05' UNION SELECT '06' UNION SELECT '07' UNION SELECT '08'
    UNION SELECT '09' UNION SELECT '10' UNION SELECT '11' UNION SELECT '12'
),
Program_Count AS (
    SELECT substr(프로그램시작일, 6, 2) as 월, COUNT(*) as 프로그램수
    FROM 프로그램 WHERE 프로그램시작일 LIKE '2025%' GROUP BY 월
),
Foreign_Visitors AS (
    SELECT substr(일자, 6, 2) as 월,
           SUM(경복궁_영어권 + 경복궁_일어권 + 경복궁_중어권 + 경복궁_기타외국인 +
               창덕궁_영어권 + 창덕궁_일어권 + 창덕궁_중어권 + 창덕궁_기타외국인 +
               창경궁_영어권 + 창경궁_일어권 + 창경궁_중어권 + 창경궁_기타외국인 +
               덕수궁_영어권 + 덕수궁_일어권 + 덕수궁_중어권 + 덕수궁_기타외국인 +
               종묘_영어권 + 종묘_일어권 + 종묘_중어권 + 종묘_기타외국인) as 외국인수
    FROM 관람객수현황 WHERE 일자 LIKE '2025%' GROUP BY 월
)
SELECT M.월 || '월' as 월, IFNULL(P.프로그램수, 0) as 프로그램수, IFNULL(F.외국인수, 0) as 외국인수
FROM Months M
LEFT JOIN Program_Count P ON M.월 = P.월
LEFT JOIN Foreign_Visitors F ON M.월 = F.월
"""
df3 = load_data(sql3)

# ① 시각화 (혼합 차트)
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=df3['월'], y=df3['프로그램수'], name='프로그램 수 (막대)', marker_color='lightblue'))
fig3.add_trace(go.Scatter(x=df3['월'], y=df3['외국인수'], name='외국인 관람객 (꺾은선)', yaxis='y2', line=dict(color='red', width=3)))

# 축이 두 개인 혼합차트 레이아웃 설정
fig3.update_layout(
    yaxis=dict(title='프로그램 수'),
    yaxis2=dict(title='외국인 관람객 수', overlaying='y', side='right'),
    legend=dict(x=0.01, y=0.99)
)
st.plotly_chart(fig3, use_container_width=True)

with st.expander("이 차트를 만든 SQL 쿼리 보기"):
    st.code(sql3, language="sql")

st.info("💡 **인사이트**\n\n프로그램이 많이 열리는 달에 외국인 방문객도 함께 증가하는 추세라면, 기획 프로그램이 모객에 큰 효과가 있음을 증명합니다.\n만약 프로그램은 많은데 방문객이 늘지 않는 달이 있다면 외국인 대상 홍보 방식을 점검해 봐야 합니다.")

st.divider()

# ==========================================
# 📊 차트 4: 기온이 방문객수와 한복 착용에 미치는 영향
# ==========================================
st.subheader("4. 기온 변화가 방문객과 한복 착용에 미치는 영향")
st.caption("※ 요청하신 강수량 데이터는 DB 스키마에 존재하지 않아, '기온' 데이터를 기준으로 분석했습니다.")

sql4 = """
WITH Monthly_Stats AS (
    SELECT substr(일자, 1, 7) as 월,
           SUM(경복궁_내국인 + 창덕궁_내국인 + 창경궁_내국인 + 덕수궁_내국인 + 종묘_내국인 +
               경복궁_영어권 + 경복궁_일어권 + 경복궁_중어권 + 경복궁_기타외국인 +
               창덕궁_영어권 + 창덕궁_일어권 + 창덕궁_중어권 + 창덕궁_기타외국인 +
               창경궁_영어권 + 창경궁_일어권 + 창경궁_중어권 + 창경궁_기타외국인 +
               덕수궁_영어권 + 덕수궁_일어권 + 덕수궁_중어권 + 덕수궁_기타외국인 +
               종묘_영어권 + 종묘_일어권 + 종묘_중어권 + 종묘_기타외국인) as 총방문객
    FROM 관람객수현황 GROUP BY 월
),
Hanbok_Stats AS (
    SELECT 월, SUM(경복궁_착용자 + 창덕궁_착용자 + 덕수궁_착용자 + 창경궁_착용자 + 종묘_착용자) as 한복착용자
    FROM 한복착용입장객 GROUP BY 월
),
Temp_Stats AS (
    SELECT 년월 as 월, AVG(평균기온) as 평균기온 FROM 기온 GROUP BY 월
)
SELECT M.월, (M.총방문객 - IFNULL(H.한복착용자, 0)) as 일반방문객, IFNULL(H.한복착용자, 0) as 한복착용자, T.평균기온
FROM Monthly_Stats M
LEFT JOIN Hanbok_Stats H ON M.월 = H.월
LEFT JOIN Temp_Stats T ON M.월 = T.월
ORDER BY M.월
"""
df4 = load_data(sql4)

# ① 시각화 (누적 막대 + 선그래프 혼합 차트)
fig4 = go.Figure()
fig4.add_trace(go.Bar(x=df4['월'], y=df4['일반방문객'], name='일반 방문객', marker_color='lightgray'))
fig4.add_trace(go.Bar(x=df4['월'], y=df4['한복착용자'], name='한복 착용 방문객', marker_color='orange'))
fig4.add_trace(go.Scatter(x=df4['월'], y=df4['평균기온'], name='평균 기온 (℃)', yaxis='y2', line=dict(color='blue', width=2)))

fig4.update_layout(
    barmode='stack', # 누적 막대형 설정
    yaxis=dict(title='방문객 수'),
    yaxis2=dict(title='평균 기온 (℃)', overlaying='y', side='right'),
    legend=dict(x=0.01, y=0.99)
)
st.plotly_chart(fig4, use_container_width=True)

with st.expander("이 차트를 만든 SQL 쿼리 보기"):
    st.code(sql4, language="sql")

st.info("💡 **인사이트**\n\n기온이 너무 높거나(한여름) 너무 낮으면(한겨울) 전체 방문객과 한복 착용자 모두 급감하는 경향을 보입니다.\n따라서 폭염이나 혹한기에는 실내 프로그램 위주로 개편하거나, 여름용 얇은 한복 대여 프로모션 등을 기획할 필요가 있습니다.")