import streamlit as st

from core.positions import PositionBook
from core.breakeven import BreakevenCalculator
from core.margin import MarginEngine
from core.session import ZerodhaSession
from core.utils import format_money


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
        placeholder="Paste positions here (FUT / CE / PE supported)",
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

            # 🔒 SANITY CHECK (temporary, safe)
            if not isinstance(rows, list):
                raise RuntimeError("PositionBook.rows() did not return list")

            total_value = book.total_value()

            # ---------------- Breakeven ----------------
            be_calc = BreakevenCalculator(rows)
            breakevens = be_calc.breakevens()

            # ---------------- Margin ----------------
            engine = MarginEngine(session.client())
            margin = engine.compute_margin(rows)

            # ---------------- Summary ----------------
            st.subheader("Summary")

            c1, c2, c3, c4 = st.columns(4)

            c1.markdown("**Total Value**")
            c1.markdown(format_money(total_value))

            c2.markdown("**Breakeven**")
            if breakevens:
                c2.markdown(" / ".join(f"{x:.2f}" for x in breakevens))
            else:
                c2.markdown("—")

            c3.markdown("**Final Margin**")
            c3.markdown(format_money(margin["final"]["total"]))

            c4.markdown("**Initial Margin**")
            c4.markdown(format_money(margin["initial"]["total"]))

            st.markdown("---")

            c5, c6 = st.columns(2)

            c5.markdown("**SPAN**")
            c5.markdown(format_money(margin["initial"]["span"]))

            c6.markdown("**Exposure**")
            c6.markdown(format_money(margin["initial"]["exposure"]))

            # ---------------- Positions table ----------------
            with st.expander("Show Position Book", expanded=False):
                st.dataframe(rows, use_container_width=True)

        except Exception as e:
            st.error(str(e))
