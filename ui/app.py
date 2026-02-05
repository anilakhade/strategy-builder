import streamlit as st

from core.positions import PositionBook
from core.breakeven import BreakevenCalculator
from core.margin import MarginEngine
from core.session import ZerodhaSession
from core.utils import format_money
from core.probability_service import ProbabilityService


def run_app():
    st.set_page_config(
        page_title="Trading Dashboard",
        layout="wide",
    )

    st.title("Trading Dashboard")

    # ------------------------------------------------
    # Zerodha Session
    # ------------------------------------------------
    with st.expander("Zerodha Session", expanded=False):
        session = ZerodhaSession()

        if session.is_logged_in():
            st.success("Zerodha session active")
            kite = session.client()
        else:
            st.markdown("Login via Zerodha and paste `request_token`")
            st.code(session.login_url())

            request_token = st.text_input("request_token")

            if st.button("Login"):
                try:
                    session.generate_session(request_token)
                    st.success("Logged in successfully. Reload app.")
                    st.stop()
                except Exception as e:
                    st.error(str(e))
                    st.stop()

    # ------------------------------------------------
    # Position Input
    # ------------------------------------------------
    st.subheader("Paste Positions")

    raw_positions = st.text_area(
        "",
        height=220,
        placeholder="Paste positions here (CE / PE supported)",
    )

    vol = st.number_input(
        "Volatility (annualized, %)",
        min_value=1.0,
        max_value=200.0,
        value=18.0,
        step=0.5,
    )

    if st.button("Compute"):
        try:
            # ---------------- Parse positions ----------------
            book = PositionBook(raw_positions)
            rows = book.rows()
            total_value = book.total_value()

            # ---------------- Breakeven ----------------
            be_calc = BreakevenCalculator(rows)
            breakevens = be_calc.breakevens()

            # ---------------- Probability of Profit ----------------
            prob_service = ProbabilityService(session.client())
            pop = prob_service.probability_of_profit(
                rows=rows,
                volatility=vol / 100.0,
            )

            # ---------------- Margin ----------------
            engine = MarginEngine(session.client())
            margin = engine.compute_margin(rows)

            # ---------------- Summary ----------------
            st.subheader("Summary")

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.markdown("**Total Value**")
            c1.markdown(format_money(total_value))

            c2.markdown("**Breakeven**")
            if breakevens:
                c2.markdown(" / ".join(f"{x:.2f}" for x in breakevens))
            else:
                c2.markdown("—")

            # 🔥 NEW: Probability of Profit (exactly below Breakeven)
            c3.markdown("**Probability of Profit**")
            c3.markdown(f"{pop:.2f}%")

            c4.markdown("**Final Margin**")
            c4.markdown(format_money(margin["final"]["total"]))

            c5.markdown("**Initial Margin**")
            c5.markdown(format_money(margin["initial"]["total"]))

            st.markdown("---")

            c6, c7 = st.columns(2)

            c6.markdown("**SPAN**")
            c6.markdown(format_money(margin["initial"]["span"]))

            c7.markdown("**Exposure**")
            c7.markdown(format_money(margin["initial"]["exposure"]))

            # ---------------- Positions table ----------------
            with st.expander("Show Position Book", expanded=False):
                st.dataframe(rows, use_container_width=True)

        except Exception as e:
            st.error(str(e))


if __name__ == "__main__":
    run_app()
