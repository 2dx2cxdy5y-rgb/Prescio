import streamlit as st
import pandas as pd


def render_historical_upload_audit_panel():

    audit_df = pd.read_csv(

        "Data/historical_upload_audit.csv"
    )
    
    if audit_df.empty:

        st.subheader(
            "Historical Upload Audit"
        )

        st.info(
            "No upload history available"
        )

        return    

    latest_upload = (

        audit_df.iloc[-1]
    )

    total_uploads = len(
        audit_df
    )

    st.subheader(
        "Historical Upload Audit"
    )    

    st.success(
        "🟢 Audit Active"
    )
    
    col1, col2 = st.columns(2)    
    
    with col1:

        st.markdown(
            f"""
    **Last Upload = {latest_upload["timestamp"]}**

    **Rows Uploaded = {latest_upload["rows_uploaded"]}**

    **Queues Uploaded = {latest_upload["queues_uploaded"]}**
    """
        )

    with col2:

        st.markdown(
            f"""
    **Historical Range = {latest_upload["start_date"]} → {latest_upload["end_date"]}**

    **Upload Events = {total_uploads}**
    """
        )