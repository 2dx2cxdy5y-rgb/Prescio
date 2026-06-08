import streamlit as st
import pandas as pd


def render_forecast_status_panel(
    forecast_df,
    forecast_source,
    forecast_profile,
    queue_master_df,
    freeze_weeks,
    horizon_weeks
):
    """
    Render operational forecast status summary.
    """

    # -----------------------------------
    # SAFETY CHECK
    # -----------------------------------

    if forecast_df is None or forecast_df.empty:

        st.subheader(
            "Forecast Governance"
        )

        st.error(
            "🔴 Forecast Missing"
        )

        return

    # -----------------------------------
    # BASIC METRICS
    # -----------------------------------

    forecast_rows = len(
        forecast_df
    )

    configured_queues = set(

        queue_master_df["queue"]

        .dropna()

        .astype(str)

        .str.strip()
    )

    forecast_queues = set(

        forecast_df["queue"]

        .dropna()

        .astype(str)

        .str.strip()
    )

    covered_queues = sorted(

        configured_queues

        .intersection(
            forecast_queues
        )
    )

    missing_queues = sorted(

        configured_queues

        - forecast_queues
    )

    total_queues = len(
        configured_queues
    )

    covered_queue_count = len(
        covered_queues
    )

    # -----------------------------------
    # DATE RANGE
    # -----------------------------------



    dates = pd.to_datetime(

        forecast_df["date"],

        format="%d/%m/%Y",

        errors="coerce"
    )
    
    if dates.isna().all():

        start_date = "Unknown"
        end_date = "Unknown"

    else:

        start_date = (

            dates.min()

            .strftime("%d/%m/%Y")
        )

        end_date = (

            dates.max()

            .strftime("%d/%m/%Y")
        )

    # -----------------------------------
    # HEALTH
    # -----------------------------------

    if len(missing_queues) > 0:

        health_message = (
            "🟠 Forecast Requires Review"
        )

        validation_status = (
            f"{len(missing_queues)} queue(s) missing"
        )

    else:

        health_message = (
            "🟢 Forecast Healthy"
        )

        validation_status = (
            "Passed"
        )

    queue_status_lines = []

    for queue in covered_queues:

        queue_status_lines.append(
            f"<span style='color:#28a745'>✓ {queue}</span>"
        )

    for queue in missing_queues:

        queue_status_lines.append(
            f"<span style='color:#dc3545'>✗ {queue}</span>"
        )

    queue_html = "<br>".join(
        queue_status_lines
    )

    # -----------------------------------
    # HEADER
    # -----------------------------------

    st.subheader(
        "Forecast Status"
    )

    st.success(
        health_message
    )

    # -----------------------------------
    # STATUS METRICS
    # -----------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
    **Forecast Source =** {forecast_source}

    **Forecast Profile =** {forecast_profile}

    **Queue Coverage =** {covered_queue_count}/{total_queues}
    """
        )

        st.markdown(
            queue_html,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
    **Freeze Horizon =** {freeze_weeks} Weeks

    **Planning Horizon =** {horizon_weeks} Weeks

    **Forecast Rows =** {forecast_rows:,}

    **Forecast Range =** {start_date} → {end_date}

    **Validation =** {validation_status}
    """
        )

