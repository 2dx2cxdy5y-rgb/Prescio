import streamlit as st
import pandas as pd


def render_published_plan_status_panel():

    st.subheader(
        "Published Plan Status"
    )

    try:

        published_df = pd.read_csv(
            "Data/published_plan.csv"
        )

    except Exception:

        st.warning(
            "No published plan available."
        )

        return

    if published_df.empty:

        st.warning(
            "No published plan available."
        )

        return

    rows = len(
        published_df
    )

    queues = published_df[
        "queue"
    ].nunique()

    dates = pd.to_datetime(

        published_df["date"],

        dayfirst=True,

        errors="coerce"
    )

    start_date = (
        dates.min()
        .strftime("%d/%m/%Y")
    )

    end_date = (
        dates.max()
        .strftime("%d/%m/%Y")
    )

    last_published = (
        "Unknown"
    )

    snapshot_count = 0

    try:

        history_df = pd.read_csv(
            "Data/published_plan_snapshot_history.csv"
        )

        if (

            not history_df.empty

            and

            "snapshot_date"

            in history_df.columns
        ):

            snapshot_count = (

                history_df[
                    "snapshot_date"
                ]

                .nunique()
            )

            last_published = (

                history_df[
                    "snapshot_date"
                ].max()
            )

            last_published = (

                history_df[
                    "snapshot_date"
                ].max()
            )

    except Exception:

        pass

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
**Rows = {rows:,}**

**Queues = {queues}**
"""
        )

    with col2:

        st.markdown(
            f"""
    **Date Range = {start_date} → {end_date}**

    **Last Published = {last_published}**

    **Snapshots Stored = {snapshot_count}**
    """
        )
    
    st.divider()