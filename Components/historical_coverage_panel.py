import streamlit as st
import pandas as pd

def render_historical_coverage_panel(
    historical_df,
    queue_master_df
):
    
    if historical_df is None or historical_df.empty:

        return
    
    coverage_df = (

        historical_df

        .groupby("queue")

        .size()

        .reset_index(
            name="weeks_available"
        )
    )

    all_queues = pd.DataFrame({

        "queue":

        queue_master_df["queue"]

        .dropna()

        .astype(str)

        .str.strip()

        .unique()
    })
    
    coverage_df = pd.merge(

        all_queues,

        coverage_df,

        on="queue",

        how="left"
    )
    
    coverage_df[
        "weeks_available"
    ] = (

        coverage_df[
            "weeks_available"
        ]

        .fillna(0)

        .astype(int)
    )
    
    coverage_df = (

        coverage_df

        .sort_values(

            "weeks_available",

            ascending=False
        )
    )
    
    st.subheader(
        "Historical Coverage Analysis"
    )

    st.dataframe(

        coverage_df,

        use_container_width=True
    )