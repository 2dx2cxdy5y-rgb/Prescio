import streamlit as st
import pandas as pd

from Components.section_header import (
    render_section_header
)

from Components.page_title import (
    render_title
)

from Components.chart_container import (
    render_chart_container
)

from Components.data_editor_container import (
    render_data_editor
)

from Components.help_header import (
    render_help_header
)

from Components.historical_status_panel import (
    render_historical_status_panel
)

from Components.historical_actuals_upload import (
    render_historical_actuals_upload
)

from Components.historical_coverage_panel import (
    render_historical_coverage_panel
)

from Components.historical_upload_audit_panel import (
    render_historical_upload_audit_panel
)

from Components.historical_staging_status_panel import (
    render_historical_staging_status_panel
)

from Components.historical_staging_editor import (
    render_historical_staging_editor
)

from Components.published_plan_status_panel import (
    render_published_plan_status_panel
)

from Components.publish_plan_panel import (
    render_publish_plan_panel
)

# =====================================================
# CAPABILITY DATASET VIEW
# =====================================================

def render_capability_dataset(

    filtered_forecast_df,

    selected_queue
):



    # ---------------------------------
    # BUILD CAPABILITY DATAFRAME
    # ---------------------------------

    capability_df = (
        filtered_forecast_df.copy()
    )

    # ---------------------------------
    # SAFE AI DEFLECTION
    # ---------------------------------

    safe_ai_deflection = (

        capability_df[
            "ai_deflection"
        ]

        .clip(
            upper=0.95
        )
    )

    # ---------------------------------
    # BASELINE REQUIREMENT
    # ---------------------------------

    capability_df[
        "baseline_requirement"
    ] = (

        capability_df[
            "gross_requirement"
        ]

        / (
            1
            - safe_ai_deflection
        )
    )

    # ---------------------------------
    # SELECT DISPLAY COLUMNS
    # ---------------------------------

    capability_view = capability_df[

        [
            "date",
            "queue",
            "demand",
            "resolved_demand",
            "aht_seconds",
            "baseline_requirement",
            "gross_requirement",
            "available_supply",
            "fte_gap"
        ]

    ].copy()

    # ---------------------------------
    # RENAME COLUMNS
    # ---------------------------------

    capability_view.columns = [

        "Week",
        "Queue",
        "Baseline Demand",
        "Adjusted Demand",
        "AHT",
        "Baseline FTE Requirement",
        "Adjusted FTE Requirement",
        "Available FTE",
        "FTE Gap"
    ]

    capability_view["Week"] = pd.to_datetime(

        capability_view["Week"]
    )

    # ---------------------------------
    # REMOVE QUEUE COLUMN
    # ---------------------------------

    if selected_queue != "All Queues":

        capability_view = (

            capability_view.drop(

                columns=["Queue"]
            )
        )

    # ---------------------------------
    # FORMAT NUMBERS
    # ---------------------------------

    numeric_columns = [

        "Baseline Demand",
        "Adjusted Demand",
        "AHT",
        "Baseline FTE Requirement",
        "Adjusted FTE Requirement",
        "Available FTE",
        "FTE Gap"
    ]

    capability_view[
        numeric_columns
    ] = capability_view[
        numeric_columns
    ].round(2)

    # ---------------------------------
    # SORT DATA
    # ---------------------------------

    capability_view = (

        capability_view.sort_values(
            by="Week"
        )
    )

    # ---------------------------------
    # TABLE RENDER
    # ---------------------------------

    def render_table():

        st.dataframe(

            capability_view,

            column_config={

                "Week": st.column_config.DateColumn(

                    "Week",

                    format="DD/MM/YYYY"
                )
            },

            width="stretch",

            height=700,

            hide_index=True
        )

    render_chart_container(

        "Capability Dataset",

        render_table,

        divider=False
    )

    st.divider()

# =====================================================
# HISTORICAL NORMALISATION
# =====================================================

def render_historical_normalisation(

    DATASETS
):

    render_help_header(

        "Historical Normalisation",

        """
    ### Historical Normalisation Guidance

    #### Purpose

    Historical normalisation allows exceptional events to be adjusted before forecast generation.

    Use this to remove one-off operational anomalies that would otherwise distort future forecasts.

    ---

    #### Queue

    Select a governed queue from Queue Master.

    Click inside the queue cell to select a valid queue.

    ---

    #### Date

    Date of the historical event being adjusted.

    Only periods requiring correction should be included.

    ---

    #### Adjustment Value

    Adjustment applied to historical demand.

    Positive values increase historical demand.

    Negative values reduce historical demand.

    Examples:

    - +100 = add 100 contacts
    - -250 = remove 250 contacts

    Values are entered as contact volumes, not percentages.

    ---

    #### Typical Use Cases

    Examples include:

    - System outages
    - Telephony failures
    - Major incidents
    - Marketing campaigns
    - Weather disruption
    - Industrial action
    - Data quality issues

    ---

    #### Forecast Impact

    Normalisation adjustments influence the historical baseline used by the forecasting engine.

    Only genuine anomalies should be adjusted.
    """
    )

    # -----------------------------------
    # LOAD ADJUSTMENTS
    # -----------------------------------

    adjustments_df = pd.read_csv(

        DATASETS[
            "historical_adjustments"
        ]["path"]
    )

    queue_master_df = pd.read_csv(

        DATASETS[
            "queue_master"
        ]["path"]
    )

    valid_queues = sorted(

        queue_master_df[
            "queue"
        ]

        .dropna()

        .unique()
    )

    # -----------------------------------
    # SAVE CALLBACK
    # -----------------------------------

    def save_adjustments(
        edited_df
    ):

        edited_df.to_csv(

            DATASETS[
                "historical_adjustments"
            ]["path"],

            index=False
        )

        st.success(
            "Historical adjustments updated."
        )

        st.rerun()

    # -----------------------------------
    # EDITOR
    # -----------------------------------

    render_data_editor(

        dataframe=adjustments_df,

        save_button_label=(
            "Save Historical Adjustments"
        ),

        save_callback=save_adjustments,

        editor_key=(
            "historical_adjustment_editor"
        ),

        column_config={

            "queue": st.column_config.SelectboxColumn(

                "queue",

                options=valid_queues,

                help=(
                    "Select a valid queue "
                    "from Queue Master."
                )
            )
        }
    )

# =====================================================
# MAIN TAB RENDERER
# =====================================================

def render_dataset_tab(

    filtered_forecast_df,

    selected_queue,

    DATASETS,
    
    historical_actuals_staging
):

    historical_df = pd.read_csv(

        DATASETS[
            "historical_operational_data"
        ]["path"]
    )

    queue_master_df = pd.read_csv(

        DATASETS[
            "queue_master"
        ]["path"]
    )

    historical_upload_audit = pd.read_csv(

        DATASETS[
            "historical_upload_audit"
        ]["path"]
    )

    render_title(

        "Dataset",

        divider=False,

        caption=(
            "Detailed dataset information "
            "based on selected queue."
        )
    )

    render_historical_status_panel(

        historical_df,

        queue_master_df
    )

    render_historical_staging_status_panel(

        historical_actuals_staging,

        queue_master_df,

    )
    
    render_historical_staging_editor(

        historical_actuals_staging,

        queue_master_df,
        
    )

#    render_historical_actuals_upload(
#        queue_master_df
#    )
    
#    render_historical_upload_audit_panel()




    render_historical_coverage_panel(

        historical_df,

        queue_master_df
    )
 
    st.divider()
        
    render_capability_dataset(

        filtered_forecast_df,

        selected_queue
    )

    # render_historical_normalisation(

    #     DATASETS
    # )
    

    