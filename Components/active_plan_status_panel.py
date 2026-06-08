import streamlit as st
import pandas as pd


def render_active_plan_status_panel(
    active_plan_df,
    freeze_weeks
):

    if active_plan_df.empty:

        st.warning(
            "No Active Plan available."
        )

        return

    dates = pd.to_datetime(

        active_plan_df["date"],

        errors="coerce",

        dayfirst=True
    )

    plan_start = (

        dates.min()

        .strftime("%d/%m/%Y")
    )

    unique_dates = sorted(

        dates.dropna()

        .unique()
    )

    frozen_dates = (

        unique_dates[
            :freeze_weeks
        ]
    )

    future_dates = (

        unique_dates[
            freeze_weeks:
        ]
    )

    frozen_rows = len(

        active_plan_df[

            active_plan_df["date"].isin(

                [

                    pd.Timestamp(d)

                    .strftime("%d/%m/%Y")

                    for d in frozen_dates

                ]
            )
        ]
    )

    live_rows = len(

        active_plan_df[

            active_plan_df["date"].isin(

                [

                    pd.Timestamp(d)

                    .strftime("%d/%m/%Y")

                    for d in future_dates

                ]
            )
        ]
    )

    published_start = (

        pd.Timestamp(
            frozen_dates[0]
        )

        .strftime("%d/%m/%Y")
    )

    published_end = (

        pd.Timestamp(
            frozen_dates[-1]
        )

        .strftime("%d/%m/%Y")
    )

    if len(
        future_dates
    ) > 0:

        live_start = (

            pd.Timestamp(
                future_dates[0]
            )

            .strftime("%d/%m/%Y")
        )

    else:

        live_start = (
            "N/A"
        )



    plan_end = (

        dates.max()

        .strftime("%d/%m/%Y")
    )

    plan_rows = len(
        active_plan_df
    )

    queue_count = (

        active_plan_df["queue"]

        .nunique()
    )

    st.subheader(
        "Active Plan Status"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
    **Rows =** {plan_rows:,}

    **Queues =** {queue_count}

    **Frozen Rows =** {frozen_rows:,}

    **Live Forecast Rows =** {live_rows:,}

    **Plan Range =**
    {plan_start} → {plan_end}
    """
        )

    with col2:

        st.markdown(
            f"""
    **Freeze Horizon =**
    {freeze_weeks} Weeks

    **Published Period =**
    {published_start} → {published_end}

    **Live Forecast Starts =**
    {live_start}
    """
        )