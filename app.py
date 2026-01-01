import streamlit as st
import pandas as pd

# --- 1. 토스 스타일 UI 적용을 위한 마법의 CSS 코드 ---
# 이 부분은 디자인을 담당합니다. 복잡해 보이지만 그냥 두시면 됩니다!
st.markdown("""
<style>
    /* 전체 배경색을 토스처럼 부드러운 밝은 회색으로 변경 */
    .stApp {
        background-color: #F2F4F6;
    }
    
    /* 메인 화면의 컨테이너들을 둥글고 하얀 카드처럼 만들기 */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: white;
        padding: 25px;
        border-radius: 20px; /* 둥근 모서리 */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); /* 부드러운 그림자 */
        margin-bottom: 20px;
    }

    /* 입력창과 버튼들도 조금 더 둥글게 */
    .stTextInput input, .stNumberInput input {
        border-radius: 12px !important;
    }
    
    /* 사이드바 배경도 약간 조절 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
    }
    
    /* 메트릭(큰 숫자) 스타일 조정 */
    [data-testid="stMetricValue"] {
        font-weight: 700;
        color: #333D4B; /* 토스 스타일 진한 남색 */
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 앱 기본 설정 ---
st.set_page_config(page_title="재호의 연말정산", layout="centered")
st.title("💰 2026 연말정산 계산기")
st.caption("내 소비 습관을 분석하고 숨은 환급금을 찾아보세요.")

# --- 3. 사용자 입력 섹션 (단위를 '만원'으로 변경!) ---
with st.sidebar:
    st.header("📋 내 정보 입력")
    # 입력 단위는 만원, 기본값 4000만원, 100만원 단위로 조절
    salary_manwon = st.number_input("연봉 (단위: 만원)", value=4000, step=100, format="%d")
    credit_card_manwon = st.number_input("신용카드 사용액 (단위: 만원)", value=1500, step=50, format="%d")
    debit_card_manwon = st.number_input("체크카드/현금영수증 (단위: 만원)", value=500, step=50, format="%d")

# --- 4. 연말정산 핵심 로직 (내부 계산은 '원' 단위로 변환해서 정확하게) ---
# 입력받은 만원 단위를 다시 실제 원 단위로 변환
salary = salary_manwon * 10000
credit_card = credit_card_manwon * 10000
debit_card = debit_card_manwon * 10000

threshold = salary * 0.25 # 공제 문턱 (총 급여의 25%)
total_spent = credit_card + debit_card

if total_spent <= threshold:
    deduction = 0
    # 남은 금액 계산
    remaining = threshold - total_spent
    message = f"😢 공제 문턱까지 **{int(remaining/10000):,}만원** 더 써야 공제가 시작돼요. 혜택 좋은 신용카드를 사용해보세요!"
    alert_type = "warning"
else:
    # (단순화된 로직) 초과분에 대해 신용카드 15%, 체크카드 30% 비율적으로 적용 가정
    # 실제로는 신용카드 사용분부터 먼저 차감되는 복잡한 순서가 있습니다.
    deduction = (credit_card * 0.15) + (debit_card * 0.30)
    # 법적 한도 적용 (예: 300만원)
    deduction = min(deduction, 3000000)
    message = "🎉 축하합니다! 소득공제 대상이에요. 이제부터는 공제율이 높은 **체크카드**를 쓰면 환급액이 더 늘어나요!"
    alert_type = "success"

# --- 5. 결과 화면 구성 (토스 스타일 카드형 UI) ---

# 첫 번째 카드: 예상 결과 요약
with st.container():
    st.subheader("나의 예상 결과")
    
    # 결과를 다시 '만원' 단위로 보여주기 위해 나누기 10000
    deduction_manwon = int(deduction / 10000)
    threshold_manwon = int(threshold / 10000)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("예상 소득공제액", f"{deduction_manwon:,} 만원")
    with col2:
        st.metric("공제 시작 문턱 (연봉 25%)", f"{threshold_manwon:,} 만원", help="이 금액 이상 써야 공제가 시작됩니다.")
    
    st.divider()
    if alert_type == "success":
        st.success(message)
    else:
        st.warning(message)

# 두 번째 카드: 비교 차트
with st.container():
    st.subheader("📊 비슷한 연봉 그룹과 비교")
    st.caption("나와 비슷한 소득을 가진 사람들은 어떻게 쓰고 있을까요?")
    
    # 비교를 위한 가상 데이터 (체크카드 사용 비중 계산)
    my_debit_ratio = debit_card / (total_spent + 1) * 100 # 0으로 나누기 방지
    
    comparison_data = pd.DataFrame({
        "구분": ["나", "환급 상위 10%", "평균"],
        "체크카드 비중(%)": [my_debit_ratio, 65, 40]
    })
    
    # 차트 색상을 토스 파란색으로 변경
    st.bar_chart(comparison_data.set_index("구분"), color=["#3182F6"])
    st.caption("💡 환급을 많이 받는 사람들은 체크카드/현금영수증 사용 비중이 높습니다.")
