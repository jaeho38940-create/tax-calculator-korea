import streamlit as st
import pandas as pd
import altair as alt

# --- 1. 디자인 및 스타일 설정 ---
st.set_page_config(page_title="연말정산 계산기", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #F2F4F6; }

    [data-testid="stForm"] {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }

    .stButton > button {
        width: 100%;
        background-color: #3182F6; 
        color: white;
        border-radius: 12px;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1B64DA;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 함수: 연봉별 세율 계산 ---
def get_tax_rate_info(salary):
    if salary <= 5000000:
        labor_deduction = salary * 0.7
    elif salary <= 15000000:
        labor_deduction = 3500000 + (salary - 5000000) * 0.4
    elif salary <= 45000000:
        labor_deduction = 7500000 + (salary - 15000000) * 0.15
    elif salary <= 100000000:
        labor_deduction = 12000000 + (salary - 45000000) * 0.05
    else:
        labor_deduction = 14750000 + (salary - 100000000) * 0.02

    tax_base = salary - labor_deduction - 1500000

    if tax_base < 0:
        return 0, "면세 구간"

    if tax_base <= 14000000:
        return 0.066, "6.6% (과표 1,400만원 이하)"
    elif tax_base <= 50000000:
        return 0.165, "16.5% (과표 5,000만원 이하)"
    elif tax_base <= 88000000:
        return 0.264, "26.4% (과표 8,800만원 이하)"
    elif tax_base <= 150000000:
        return 0.385, "38.5% (과표 1.5억원 이하)"
    elif tax_base <= 300000000:
        return 0.418, "41.8% (과표 3억원 이하)"
    elif tax_base <= 500000000:
        return 0.440, "44.0% (과표 5억원 이하)"
    elif tax_base <= 1000000000:
        return 0.462, "46.2% (과표 10억원 이하)"
    else:
        return 0.495, "49.5% (과표 10억원 초과)"

st.title("💰 연말정산 예상 환급액 찾기")
st.caption("국세청 최신 세율 정보를 반영하여 정확하게 계산합니다.")

# --- 2. 입력 화면 ---
with st.form("calc_form"):
    st.subheader("정보를 입력해주세요")

    salary_manwon = st.number_input("연간 총 급여 (세전)", value=4000, step=100)
    st.caption(f"📍 입력: {salary_manwon:,}만원")

    st.divider() 

    credit_card_manwon = st.number_input("신용카드 사용액", value=1500, step=50)
    debit_cash_manwon = st.number_input("체크카드 + 현금영수증", value=500, step=50)

    st.write("") 
    st.write("") 

    submitted = st.form_submit_button("계산하기")

# --- 3. 계산 및 결과 화면 ---
if submitted:
    salary = salary_manwon * 10000
    credit_card = credit_card_manwon * 10000
    debit_cash = debit_cash_manwon * 10000

    threshold = salary * 0.25 

    # [수정됨] 불필요한 설명을 제거하고 금액만 남겼습니다!
    if salary >= 70000000:
        limit = 2500000 
        limit_desc = "250만원" 
    else:
        limit = 3000000 
        limit_desc = "300만원"

    tax_rate, tax_desc = get_tax_rate_info(salary)

    total_spent = credit_card + debit_cash
    result_container = st.container()

    with result_container:
        if total_spent <= threshold:
            raw_deduction = 0
            final_deduction = 0
            is_overflow = False
            bar_color = "#3182F6" 

            remaining_spent = threshold - total_spent
            st.warning("😢 아직 공제 문턱(연봉 25%)을 넘지 못했어요.")
            st.write(f"최소 **{int(remaining_spent/10000):,}만원**을 더 써야 공제가 시작됩니다.")

            refund_estimate = 0

        else:
            used_credit = min(credit_card, threshold)
            remaining_threshold = threshold - used_credit
            used_debit = min(debit_cash, remaining_threshold)

            taxable_credit = credit_card - used_credit
            taxable_debit = debit_cash - used_debit

            raw_deduction = (taxable_credit * 0.15) + (taxable_debit * 0.30)
            final_deduction = min(raw_deduction, limit)

            if raw_deduction > limit:
                is_overflow = True
                # [수정됨] 이제 깔끔하게 "한도(250만원)를 초과 달성했습니다!" 라고 나옵니다.
                st.success(f"🎉 한도({limit_desc})를 초과 달성했습니다!")
                bar_color = "#FF6B6B" # 빨강
            else:
                is_overflow = False
                gap = limit - raw_deduction
                st.info(f"💸 한도까지 **{int(gap/10000):,}만원** 남았습니다.")
                bar_color = "#3182F6" # 파랑

            refund_estimate = final_deduction * tax_rate 

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("예상 소득공제 금액", f"{int(final_deduction/10000):,} 만원")
            with col2:
                st.metric("실제 절세 효과 (예상)", f"{int(refund_estimate/10000):,} 만원")
                st.caption(f"적용 세율: {tax_desc}")

        # --- 4. 오버랩 차트 ---
        source = pd.DataFrame([
            {"category": "현황", "value": int(limit/10000), "type": "최대 한도"}, 
            {"category": "현황", "value": int(raw_deduction/10000), "type": "내 공제액"} 
        ])

        base = alt.Chart(source).encode(
            x=alt.X('category', axis=None) 
        )

        bar_limit = base.transform_filter(
            alt.datum.type == '최대 한도'
        ).mark_bar(
            size=50,
            color='#E5E8EB',
            cornerRadius=8
        ).encode(
            y=alt.Y('value', title='금액 (만원)')
        )

        bar_mine = base.transform_filter(
            alt.datum.type == '내 공제액'
        ).mark_bar(
            size=50,
            color=bar_color, 
            cornerRadius=8
        ).encode(
            y=alt.Y('value', title='금액 (만원)'),
            tooltip=['type', 'value']
        )

        if is_overflow:
            chart = (bar_mine + bar_limit)
        else:
            chart = (bar_limit + bar_mine)

        chart = chart.properties(
            height=350
        ).configure_axis(
            grid=False,
            labelFontSize=12
        ).configure_view(
            strokeWidth=0 
        )

        st.altair_chart(chart, use_container_width=True)
