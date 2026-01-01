import streamlit as st
import pandas as pd

# 디자인 설정
st.set_page_config(page_title="재호의 연말정산 솔루션", layout="centered")
st.title("💰 2026 연말정산 신용카드 계산기")
st.write("내 소비 습관을 분석하고 환급액을 극대화하는 솔루션을 확인하세요.")

# 사용자 입력 섹션
with st.sidebar:
    st.header("📋 정보 입력")
    salary = st.number_input("연봉 (원)", value=40000000, step=1000000)
    credit_card = st.number_input("신용카드 사용액 (원)", value=15000000, step=100000)
    debit_card = st.number_input("체크카드/현금영수증 (원)", value=5000000, step=100000)

# 연말정산 로직 계산
threshold = salary * 0.25 # 공제 문턱 (25%)
total_spent = credit_card + debit_card

if total_spent <= threshold:
    deduction = 0
    message = "아직 공제 문턱(25%)을 넘지 못했습니다. 혜택이 많은 신용카드를 더 사용하세요!"
else:
    excess = total_spent - threshold
    deduction = (credit_card * 0.15) + (debit_card * 0.30)
    deduction = min(deduction, 3000000)
    message = "축하합니다! 소득공제 대상입니다. 이제부터는 체크카드 비중을 높이세요."

# 결과 화면 구성
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.metric("나의 예상 소득공제액", f"{int(deduction):,} 원")
    
with col2:
    target_spent = int(threshold)
    st.metric("공제 문턱 (연봉의 25%)", f"{target_spent:,} 원")

# 소비 비교 시각화
st.subheader("📊 비슷한 연봉 그룹과 비교")
comparison_data = pd.DataFrame({
    "구분": ["나", "상위 10% 환급러", "평균"],
    "체크카드 사용 비중": [debit_card/(total_spent+1)*100, 65, 40]
})
st.bar_chart(comparison_data.set_index("구분"))

st.info(f"💡 **솔루션:** {message}")
