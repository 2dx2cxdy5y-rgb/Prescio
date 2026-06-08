import streamlit as st
import pandas as pd
import os

from Engine.historical_data_engine import (
    validate_historical_data,
    reset_staging_from_production,
    promote_staging_to_production
)

from Components.historical_actuals_upload import (
    render_historical_actuals_upload
)

def render_historical_staging_status_panel(

    staging_df,

    queue_master_df
):

    st.subheader(
        "Historical Staging Status"
    )

    if (

        "staging_reset_success"

        in st.session_state
    ):

        st.success(

            st.session_state[
                "staging_reset_success"
            ]
        )

        del st.session_state[
            "staging_reset_success"
        ]

    if (

        "promotion_success"

        in st.session_state
    ):

        st.success(

            st.session_state[
                "promotion_success"
            ]
        )

        del st.session_state[
            "promotion_success"
        ]
        
    if staging_df.empty:

        st.warning(
            "🟠 Staging Dataset Empty - Upload historical actuals to begin validation."
        )

        return

    st.success(
        "🟢 Staging Dataset Available"
    )

    rows = len(
        staging_df
    )

    queues = staging_df[
        "queue"
    ].nunique()
    
    validation_result = (

        validate_historical_data(

            staging_df,

            queue_master_df
        )
    )

    archive_count = len(

        [

            file

            for file in os.listdir(
                "Data/Archive"
            )

            if file.endswith(
                ".csv"
            )
        ]
    )

    if validation_result["valid"]:

        promotion_status = (
            "🟢 Validation Passed"
        )

    else:

        promotion_status = (
            "🔴 Validation Failed"
        )

    
    dates = pd.to_datetime(

        staging_df["date"],

        dayfirst=True,

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
    
    col1, col2 = st.columns(2)
    
    with col1:

        st.markdown(
            f"""
    **Rows = {rows:,}**

    **Queues = {queues}**

    **Archives = {archive_count}**
    """
        )
        
    with col2:

        st.markdown(
            f"""
    **Date Range = {start_date} → {end_date}**

    **Status = {promotion_status}**
    """
        )
        
