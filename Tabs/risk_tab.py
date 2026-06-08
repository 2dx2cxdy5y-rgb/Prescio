import streamlit as st

from Components.section_header import (
    render_section_header
)

from Components.page_title import (
    render_title
)

from Components.kpi_bar import (
    render_kpi_bar
)

from Engine.commentary_renderer import (
    render_commentary_card
)

# =====================================================
# COMMENTARY
# =====================================================

def render_risk_commentary(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_risk_commentary,

    render_insight
):

    # ---------------------------------
    # GENERATE COMMENTARY
    # ---------------------------------

    risk_commentary = (

        generate_risk_commentary(

            forecast_df,

            filtered_forecast_df,

            selected_queue
        )
    )

    # ---------------------------------
    # SECTION TITLE
    # ---------------------------------

    render_title(
        "Risk Intelligence",
        divider=False
    )

    # ---------------------------------
    # ENTERPRISE COMMENTARY
    # ---------------------------------

    render_commentary_card(
        st,
        risk_commentary[0]
    )



# =====================================================
# RISK STATUS + KPIS
# =====================================================

def render_risk_kpis(

    overall_risk,

    risk_df
):

    # -----------------------------
    # OVERALL RISK STATUS
    # -----------------------------

    if overall_risk == "Critical":

        st.error(
            "Critical operational risk exposure."
        )

    elif overall_risk == "High":

        st.warning(
            "High operational risk exposure."
        )

    elif overall_risk == "Medium":

        st.warning(
            "Moderate operational risk exposure."
        )

    else:

        st.success(
            "Operational risk within expected tolerance."
        )

    # -----------------------------
    # KPI STRIP
    # -----------------------------

    risk_row = risk_df.iloc[0]

    render_kpi_bar([

        {
            "label": "Service Delivery",
            "value": risk_row["service_delivery_risk"]
        },

        {
            "label": "Budget Risk",
            "value": risk_row["budget_risk"]
        }
    ])

# =====================================================
# VISUAL RISK INDICATORS
# =====================================================

def render_risk_visual_indicators(
    risk_df
):

    # -----------------------------
    # RISK ROW
    # -----------------------------

    risk_row = risk_df.iloc[0]

    risk_alert_triggered = False

    # -----------------------------
    # SERVICE DELIVERY
    # -----------------------------

    if risk_row["service_delivery_risk"] in [
        "High",
        "Critical"
    ]:

        st.error(
            "Service delivery stability at risk."
        )

        risk_alert_triggered = True

    # -----------------------------
    # BUDGET PRESSURE
    # -----------------------------

    if risk_row["budget_risk"] in [
        "High",
        "Critical"
    ]:

        st.warning(
            "Budget pressure indicators elevated."
        )

        risk_alert_triggered = True

    # -----------------------------
    # STABLE STATE
    # -----------------------------

    if not risk_alert_triggered:

        st.info(
            "No elevated operational risk indicators detected."
        )

    st.divider()

# =====================================================
# RISK DETAIL
# =====================================================

def render_risk_detail(
    risk_df
):

    # -----------------------------
    # DETAIL EXPANDER
    # -----------------------------

    with st.expander(
        "View Risk Detail"
    ):

        st.dataframe(
            risk_df,
            width="stretch"
        )

# =====================================================
# MAIN TAB RENDERER
# =====================================================

def render_risk_tab(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    overall_risk,

    risk_df,

    generate_risk_commentary,

    render_insight
):


    render_risk_commentary(

        forecast_df,
        filtered_forecast_df,

        selected_queue,

        generate_risk_commentary,

        render_insight
    )

    render_risk_kpis(

        overall_risk,

        risk_df
    )

    render_risk_visual_indicators(
        risk_df
    )

    render_risk_detail(
        risk_df
    )