import streamlit as st

from Components.data_editor_container import (
    render_data_editor
)

from Engine.historical_data_engine import (
    validate_historical_data,
    promote_staging_to_production,
    reset_staging_from_production
)

from Components.historical_actuals_upload import (
    render_historical_actuals_upload
)

from Components.historical_upload_audit_panel import (
    render_historical_upload_audit_panel
)

def render_historical_staging_editor(

    staging_df,

    queue_master_df,
    

):

    st.subheader(
        "Historical Staging Editor"
    )

    if staging_df.empty:

        st.info(
            "No staging data available"
        )

        return

    def save_staging(
        edited_df
    ):

        validation_result = (

            validate_historical_data(

                edited_df,

                queue_master_df
            )
        )

        if not validation_result["valid"]:

            st.error(

                validation_result["message"]
            )

            return

        edited_df.to_csv(

            "Data/historical_actuals_staging.csv",

            index=False
        )

        st.success(
            "Staging data saved"
        )

    # -----------------------------------
    # QUEUE DROPDOWN OPTIONS
    # -----------------------------------

    validation_result = (

        validate_historical_data(

            staging_df,

            queue_master_df
        )
    )

    queue_options = sorted(

        queue_master_df["queue"]

        .dropna()

        .astype(str)

        .unique()

        .tolist()
    )

    column_config = {

        "queue": st.column_config.SelectboxColumn(

            "Queue",

            options=queue_options,

            required=True
        ),

        "historical_demand": st.column_config.NumberColumn(

            "Historical Demand",

            min_value=0,

            step=1
        ),

        "historical_aht": st.column_config.NumberColumn(

            "Historical AHT",

            min_value=0,

            step=1
        ),

        "historical_sla": st.column_config.NumberColumn(

            "Historical SLA",

            min_value=0,

            max_value=100,

            step=1
        ),

        
    }

    render_data_editor(

        dataframe=staging_df,

        save_button_label=(
            "Save Staging Data"
        ),

        save_callback=save_staging,

        editor_key=(
            "historical_staging_editor"
        ),

        column_config=column_config
    )
    
    confirm_promotion = st.checkbox(

        "I understand Promoting To Production will replace the production historical dataset"
    )

    if not validation_result["valid"]:

        st.error(

            "Promotion disabled: staging validation failed."
        )

    promote_clicked = st.button(

        "Promote To Production",

        key="historical_promote_button",

        disabled=(
            not validation_result["valid"]
        )
    )

    if promote_clicked:

        if not confirm_promotion:

            st.warning(

                "Please confirm promotion first."
            )

        else:

            result = (

                promote_staging_to_production()
            )

            st.session_state[
                "promotion_success"
            ] = result["message"]

            st.rerun()

        if not confirm_promotion:

            st.warning(

                "Please confirm promotion first."
            )

        else:

            result = (

                promote_staging_to_production()
            )

            st.session_state[
                "promotion_success"
            ] = result["message"]

            st.rerun()
        
    with st.expander(
        "Advanced Options"
    ):

        if st.button(
            "Reset Staging From Production"
        ):

            result = (

                reset_staging_from_production()
            )

            st.session_state[
                "staging_reset_success"
            ] = result["message"]

            st.rerun()

        st.divider()

        render_historical_actuals_upload(
            queue_master_df
        )

        st.markdown(
            """
    Bulk import should only be used for:

    - New implementations
    - Historical backfills
    - Large corrections
    """
        )
        
        st.divider()

        render_historical_upload_audit_panel()