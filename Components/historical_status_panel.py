import streamlit as st
import pandas as pd


def render_historical_status_panel(
    historical_df,
    queue_master_df
):

    if historical_df is None or historical_df.empty:

        st.subheader(
            "Historical Data Status"
        )

        st.error(
            "🔴 Historical Data Missing"
        )

        return

    historical_records = len(
        historical_df
    )

    configured_queues = set(

        queue_master_df["queue"]

        .dropna()

        .astype(str)

        .str.strip()
    )

    historical_queues = set(

        historical_df["queue"]

        .dropna()

        .astype(str)

        .str.strip()
    )

    covered_queues = sorted(

        configured_queues.intersection(
            historical_queues
        )
    )

    missing_queues = sorted(

        configured_queues
        - historical_queues
    )

    total_queues = len(
        configured_queues
    )

    covered_queue_count = len(
        covered_queues
    )

    historical_dates = pd.to_datetime(

        historical_df["date"],

        format="%d/%m/%Y",

        errors="coerce"
    )

    if historical_dates.isna().all():

        start_date = "Unknown"

        end_date = "Unknown"

        latest_actual = "Unknown"

    else:

        start_date = (

            historical_dates.min()

            .strftime("%d/%m/%Y")
        )

        end_date = (

            historical_dates.max()

            .strftime("%d/%m/%Y")
        )

        latest_actual = end_date

    if len(missing_queues) > 0:

        health_message = (
            "🟠 Historical Coverage Incomplete"
        )

        validation_status = (

            f"{len(missing_queues)} queue(s) missing"
        )

    else:

        health_message = (
            "🟢 Historical Data Healthy"
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




    st.subheader(
        "Historical Data Status"
    )

    st.success(
        health_message
    )
    
    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
**Historical Records = {historical_records:,}**

**Latest Actual = {latest_actual}**

**Queue Coverage = {covered_queue_count}/{total_queues}**
"""
        )

        st.markdown(
                queue_html,
                unsafe_allow_html=True
            )

    with col2:

        st.markdown(
            f"""
**Historical Range = {start_date} → {end_date}**

**Validation = {validation_status}**
"""
        )
        
    st.divider()    