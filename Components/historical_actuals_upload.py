import streamlit as st
import pandas as pd

from Engine.historical_data_engine import (

    validate_historical_data,

    process_historical_actuals
)

def render_historical_actuals_upload(
    queue_master_df
):

    st.subheader(
        "Historical Actuals Upload"
    )

    if (

        "historical_upload_success"

        in st.session_state
    ):

        st.success(

            st.session_state[
                "historical_upload_success"
            ]
        )

        del st.session_state[
            "historical_upload_success"
        ]
        
    uploaded_file = st.file_uploader(

        "Upload Historical Actuals",

        type=["csv"],

        key="historical_actuals_upload"
    )

    if uploaded_file is not None:

        upload_df = pd.read_csv(
            uploaded_file
        )

        validation_result = (

            validate_historical_data(

                upload_df,

                queue_master_df
            )
        )

        if validation_result.get(
            "warning"
        ):

            st.warning(

                validation_result[
                    "warning"
                ]
            )

        if not validation_result["valid"]:

            st.error(

                validation_result["message"]
            )

            return


        # -----------------------------------
        # PROCESS HISTORICAL ACTUALS
        # -----------------------------------

        processing_result = (

            process_historical_actuals(

                upload_df
            )
        )

        st.session_state[
            "historical_upload_success"
        ] = (

            processing_result[
                "message"
            ]
        )

        st.rerun()


        
        
        # -----------------------------------
        # UPLOAD SUMMARY
        # -----------------------------------

        rows_uploaded = len(
            upload_df
        )

        queues_uploaded = (

            upload_df["queue"]

            .nunique()
        )

        parsed_dates = pd.to_datetime(

            upload_df["date"],

            format="%d/%m/%Y",

            errors="coerce"
        )

        start_date = (

            parsed_dates.min()

            .strftime("%d/%m/%Y")
        )

        end_date = (

            parsed_dates.max()

            .strftime("%d/%m/%Y")
        )

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.markdown(
                f"""
        **Rows Uploaded = {rows_uploaded:,}**

        **Queues Included = {queues_uploaded}**
        """
            )
            
        with summary_col2:

            st.markdown(
                f"""
        **Start Date = {start_date}**

        **End Date = {end_date}**
        """
            )            
            
            
            
            
            
            
            
        st.dataframe(
            upload_df.head()
        )