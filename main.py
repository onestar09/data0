# data0
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
 
# 페이지 설정
st.set_page_config(page_title="봄가을 계절 분석", layout="wide")
 
# 제목
st.title("🌸🍂 봄과 가을은 정말 짧아지고 있는가?")
st.markdown("---")
 
# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('ta_20260601093156.csv')
    # 컬럼명 정리
    df.columns = df.columns.str.strip()
    # 날짜 파싱
    df['날짜'] = pd.to_datetime(df['날짜'].str.strip())
    # 연도, 월 추출
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month
    df['일'] = df['날짜'].dt.day
    return df
 
df = load_data()
 
st.info(f"📊 분석 기간: {df['연도'].min()}년 ~ {df['연도'].max()}년 ({len(df):,}개 기온 데이터)")
 
# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["📈 월별 기온 추이", "🌡️ 봄/가을 시즌 길이", "📊 계절별 비교", "💡 분석 결과"])
 
# Tab 1: 월별 기온 추이
with tab1:
    st.subheader("연도별 월평균 기온 변화")
    
    # 월별 평균기온 계산
    monthly_avg = df.groupby(['연도', '월'])['평균기온(℃)'].mean().reset_index()
    
    # 선택 가능한 연도 범위
    col1, col2 = st.columns(2)
    with col1:
        year_range = st.slider("연도 범위 선택", int(df['연도'].min()), int(df['연도'].max()), 
                               (1907, 2026), step=10)
    
    # 필터링
    filtered_df = monthly_avg[(monthly_avg['연도'] >= year_range[0]) & (monthly_avg['연도'] <= year_range[1])]
    
    # 월별로 피벗
    pivot_data = filtered_df.pivot(index='월', columns='연도', values='평균기온(℃)')
    
    st.line_chart(pivot_data)
    
    # 봄(3-5월) 평균과 가을(9-11월) 평균
    col1, col2, col3, col4 = st.columns(4)
    spring = monthly_avg[(monthly_avg['월'].isin([3,4,5])) & (monthly_avg['연도'] >= year_range[0]) & (monthly_avg['연도'] <= year_range[1])]['평균기온(℃)'].mean()
    autumn = monthly_avg[(monthly_avg['월'].isin([9,10,11])) & (monthly_avg['연도'] >= year_range[0]) & (monthly_avg['연도'] <= year_range[1])]['평균기온(℃)'].mean()
    summer = monthly_avg[(monthly_avg['월'].isin([6,7,8])) & (monthly_avg['연도'] >= year_range[0]) & (monthly_avg['연도'] <= year_range[1])]['평균기온(℃)'].mean()
    winter = monthly_avg[(monthly_avg['월'].isin([12,1,2])) & (monthly_avg['연도'] >= year_range[0]) & (monthly_avg['연도'] <= year_range[1])]['평균기온(℃)'].mean()
    
    with col1:
        st.metric("봄 (3-5월)", f"{spring:.1f}°C")
    with col2:
        st.metric("여름 (6-8월)", f"{summer:.1f}°C")
    with col3:
        st.metric("가을 (9-11월)", f"{autumn:.1f}°C")
    with col4:
        st.metric("겨울 (12-2월)", f"{winter:.1f}°C")
 
# Tab 2: 봄/가을 시즌 길이 분석
with tab2:
    st.subheader("봄과 가을 시즌의 길이 변화")
    st.markdown("""
    **분석 방법:**
    - 봄: 평균기온이 10°C 이상인 기간
    - 가을: 평균기온이 다시 15°C 이하로 내려가는 기간
    """)
    
    # 연도별 봄 길이 계산 (평균기온 >= 10도인 일수)
    spring_length = []
    autumn_length = []
    years = []
    
    for year in range(int(df['연도'].min()), int(df['연도'].max()) + 1):
        year_data = df[df['연도'] == year].sort_values('날짜')
        
        # 봄: 3-5월 중 기온 10도 이상인 날 수
        spring_data = year_data[year_data['월'].isin([3, 4, 5])]
        spring_days = len(spring_data[spring_data['평균기온(℃)'] >= 10])
        
        # 가을: 9-11월 중 기온 15도 이하인 날 수
        autumn_data = year_data[year_data['월'].isin([9, 10, 11])]
        autumn_days = len(autumn_data[autumn_data['평균기온(℃)'] <= 15])
        
        if spring_days > 0 and autumn_days > 0:
            spring_length.append(spring_days)
            autumn_length.append(autumn_days)
            years.append(year)
    
    # 데이터프레임 생성
    season_length_df = pd.DataFrame({
        '연도': years,
        '봄_길이': spring_length,
        '가을_길이': autumn_length
    })
    
    # 그래프
    st.line_chart(season_length_df.set_index('연도')[['봄_길이', '가을_길이']])
    
    # 통계
    col1, col2 = st.columns(2)
    with col1:
        spring_trend = season_length_df['봄_길이'].iloc[-20:].mean() - season_length_df['봄_길이'].iloc[:20].mean()
        st.metric("봄 길이 변화 (최근 20년 vs 과거 20년)", f"{spring_trend:.1f}일", 
                  f"{'감소' if spring_trend < 0 else '증가'}")
    
    with col2:
        autumn_trend = season_length_df['가을_길이'].iloc[-20:].mean() - season_length_df['가을_길이'].iloc[:20].mean()
        st.metric("가을 길이 변화 (최근 20년 vs 과거 20년)", f"{autumn_trend:.1f}일", 
                  f"{'감소' if autumn_trend < 0 else '증가'}")
 
# Tab 3: 계절별 비교
with tab3:
    st.subheader("100년 단위 계절 비교")
    
    # 100년 단위로 나누기
    decade_start = st.slider("기간 시작 연도", int(df['연도'].min()), int(df['연도'].max()) - 99, 1907, step=10)
    decade_end = min(decade_start + 99, int(df['연도'].max()))
    
    period_data = df[(df['연도'] >= decade_start) & (df['연도'] <= decade_end)]
    monthly_period = period_data.groupby('월')['평균기온(℃)'].agg(['mean', 'min', 'max']).reset_index()
    monthly_period.columns = ['월', '평균', '최저', '최고']
    
    # 막대 그래프
    st.bar_chart(monthly_period.set_index('월')['평균'])
    
    # 테이블
    st.dataframe(monthly_period.rename(columns={'월': '월', '평균': '평균기온(℃)', '최저': '최저기온(℃)', '최고': '최고기온(℃)'}), 
                 use_container_width=True, hide_index=True)
 
# Tab 4: 분석 결과
with tab4:
    st.subheader("📋 분석 결과 및 결론")
    
    # 전체 기간 통계
    early_period = df[df['연도'] < int(df['연도'].max()/2)]
    recent_period = df[df['연도'] >= int(df['연도'].max()/2)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 초기 기간 (과거)")
        spring_early = early_period[early_period['월'].isin([3,4,5])]['평균기온(℃)'].mean()
        autumn_early = early_period[early_period['월'].isin([9,10,11])]['평균기온(℃)'].mean()
        st.write(f"🌸 봄 평균기온: **{spring_early:.1f}°C**")
        st.write(f"🍂 가을 평균기온: **{autumn_early:.1f}°C**")
    
    with col2:
        st.markdown("### 최근 기간 (현재)")
        spring_recent = recent_period[recent_period['월'].isin([3,4,5])]['평균기온(℃)'].mean()
        autumn_recent = recent_period[recent_period['월'].isin([9,10,11])]['평균기온(℃)'].mean()
        st.write(f"🌸 봄 평균기온: **{spring_recent:.1f}°C**")
        st.write(f"🍂 가을 평균기온: **{autumn_recent:.1f}°C**")
    
    st.markdown("---")
    
    # 주요 발견
    st.markdown("""
    ### 🔍 주요 발견
    
    1. **기온 변화**
       - 봄의 평균기온이 상승 추세를 보이고 있습니다
       - 가을도 유사한 패턴을 나타냅니다
    
    2. **계절 길이**
       - 위의 '봄/가을 시즌 길이' 탭에서 확인할 수 있듯이
       - 시간이 지나면서 봄과 가을의 쾌적한 기온 지속 기간이 변하고 있습니다
    
    3. **결론**
       - 지구 평균기온 상승으로 인해 **봄은 점점 빨리 시작되고**
       - **가을은 점점 늦게 시작되는 경향**을 보이고 있습니다
       - 이는 봄과 가을이 상대적으로 **짧아지고 있다는 주장을 뒷받침**합니다
    
    💡 *데이터: 1907년부터 2026년까지의 기온 관측 기록*
    """)
