import streamlit as st
import pandas as pd

from Components.section_header import (
    render_section_header
)

from Components.page_title import (
    render_title
)

from Components.kpi_bar import (
    render_kpi_bar
)

from Components.chart_container import (
    render_chart_container
)

from Components.data_editor_container import (
    render_data_editor
)


from Components.render_modes import (

    is_intelligence_mode,
    is_engineering_mode
)

from Components.file_upload_container import (
    render_file_upload
)

from Components.help_header import (
    render_help_header
)

from Engine.profile_config_engine import (
    load_forecast_profiles
)

from Components.forecast_status_panel import (
    render_forecast_status_panel
)

from Components.active_plan_status_panel import (
    render_active_plan_status_panel
)

from Components.published_plan_status_panel import (
    render_published_plan_status_panel
)

from Components.forecast_accuracy_panel import (
    render_forecast_accuracy_panel
)

from Tabs.dataset_tab import (
    render_historical_normalisation
)

from Engine.commentary_renderer import (
    render_commentary_card
)

# =====================================================
# COMMENTARY
# =====================================================

def render_demand_commentary(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_demand_commentary,

    render_insight
):

    # ---------------------------------
    # GENERATE COMMENTARY
    # ---------------------------------

    demand_commentary = (

        generate_demand_commentary(

            forecast_df,

            filtered_forecast_df,

            selected_queue
        )
    )


    # ---------------------------------
    # ENTERPRISE COMMENTARY
    # ---------------------------------

    render_commentary_card(
        st,
        demand_commentary[0]
    )



# =====================================================
# KPI SECTION
# =====================================================

def render_demand_kpis(
    filtered_forecast_df
):

    # -----------------------------------
    # ENTERPRISE AGGREGATION
    # -----------------------------------

    enterprise_forecast = (

        filtered_forecast_df

        .groupby("date")[
            "resolved_forecast"
        ]

        .sum()
    )

    # -----------------------------------
    # KPI RENDER
    # -----------------------------------

    render_kpi_bar([

        {
            "label": "Peak Demand",

            "value": (
                f"{enterprise_forecast.max():,.0f}"
            )
        },

        {
            "label": "Average Demand",

            "value": (
                f"{enterprise_forecast.mean():,.0f}"
            )
        },

        {
            "label": "Total Demand",

            "value": (
                f"{enterprise_forecast.sum():,.0f}"
            )
        }
    ])

# =====================================================
# DEMAND FORECAST CHART
# =====================================================

def render_demand_forecast_chart(
    filtered_forecast_df
):

    # -----------------------------------
    # BUILD FORECAST CHART DATAFRAME
    # -----------------------------------

    demand_chart = (

        filtered_forecast_df

        .groupby("date")[

        [
            "base_layer",
            "growth_layer",
            "transformation_layer",
            "operational_layer",
            "resolved_forecast"
        ]

        ]

        .sum()

        .sort_index()
    )

    # -----------------------------------
    # RENAME COLUMNS
    # -----------------------------------

    demand_chart.columns = [

        "Base Forecast",

        "Growth Forecast",

        "Transformation Forecast",

        "Operational Forecast",

        "Resolved Forecast"
    ]

    # -----------------------------------
    # CHART RENDER
    # -----------------------------------

    def render_chart():

        st.line_chart(
            demand_chart
        )

    render_chart_container(

        "Enterprise Forecast Composition",

        render_chart,

        divider=False
    )

# =====================================================
# HISTORICAL DEMAND VARIANCE
# =====================================================

def render_historical_demand_variance_chart(

    filtered_forecast_df,
    filtered_historical_df
):

    # -----------------------------------
    # FORECAST SERIES
    # -----------------------------------

    forecast_series = (

        filtered_forecast_df

        .groupby("date")[
            "demand"
        ]

        .sum()

        .sort_index()
    )

    # -----------------------------------
    # HISTORICAL SERIES
    # -----------------------------------

    historical_series = (

        filtered_historical_df

        .groupby("date")[
            "historical_demand"
        ]

        .sum()

        .sort_index()
    )

    # -----------------------------------
    # BUILD COMBINED DATAFRAME
    # -----------------------------------

    historical_demand_chart = pd.DataFrame({

        "Forecast Demand":
            forecast_series,

        "Historical Demand":
            historical_series
    })

    # -----------------------------------
    # CHART RENDER
    # -----------------------------------

    def render_chart():

        st.line_chart(

            historical_demand_chart,

            width="stretch"
        )

    render_chart_container(

        "Actual Demand & Forecast Trajectory",

        render_chart,

        divider=False
    )

# =====================================================
# VARIANCE KPI SECTION
# =====================================================

def render_demand_variance_kpis(
    variance_df
):

    # -----------------------------------
    # FILTER TO ACTUALS AVAILABLE
    # -----------------------------------

    actuals_available_df = (

        variance_df[

            variance_df[
                "historical_demand"
            ].notna()
        ]
    )

    # -----------------------------------
    # SAFE KPI CALCULATIONS
    # -----------------------------------

    avg_demand_variance = (

        actuals_available_df[
            "demand_variance"
        ].mean()
    )

    avg_demand_variance_pct = (

        actuals_available_df[
            "demand_variance_pct"
        ]

        .replace(
            [float("inf"), float("-inf")],
            pd.NA
        )

        .dropna()

        .mean()
    )

    # -----------------------------------
    # KPI DISPLAY
    # -----------------------------------

    render_kpi_bar([

        {
            "label": "Average Demand Variance",

            "value": (

                f"{avg_demand_variance:,.0f}"

                if pd.notna(
                    avg_demand_variance
                )

                else "0"
            )
        },

        {
            "label": "Average Demand Variance %",

            "value": (

                f"{avg_demand_variance_pct:.1f}%"

                if pd.notna(
                    avg_demand_variance_pct
                )

                else "0%"
            )
        }
    ])

    st.divider()

# =====================================================
# IMPORTED FORECAST UPLOAD
# =====================================================

def render_imported_forecast_upload(

    DATASETS,

    validate_columns
):

    render_help_header(

        "Upload Imported Forecast",

        """

### Imported Forecast Format

Required Columns:

- date
- queue
- demand

Example:

date,queue,demand

01/01/2027,Voice,12500

01/01/2027,Chat,3800

08/01/2027,Voice,12750

08/01/2027,Chat,3900

---

The uploaded forecast becomes the source
of truth when Forecast Source is set
to Imported.

"""
    )

    render_file_upload(

        label="Upload Forecast CSV",

        dataset_path=DATASETS[
            "imported_forecast"
        ]["path"],

        required_columns=[

            "date",
            "queue",
            "demand"
        ],

        validate_columns=validate_columns,

        success_message=(
            "Imported forecast updated."
        ),

        uploader_key="imported_forecast_upload"
    )
    
# =====================================================
# DEMAND OVERLAY UPLOAD
# =====================================================

def render_overlay_upload(

    DATASETS,

    validate_columns
):

    render_section_header(
        "Upload Demand Overlays"
    )

    render_file_upload(

        label="Upload Demand Overlay File",

        dataset_path=DATASETS[
            "demand_overlays"
        ]["path"],

        required_columns=[

            "queue",
            "start_date",
            "end_date",
            "overlay_type",
            "adjustment_value",
            "reason"
        ],

        validate_columns=validate_columns,

        success_message="Demand overlays updated.",

        uploader_key="overlay_upload"
    )


# =====================================================
# DEMAND OVERLAY EDITOR
# =====================================================

def render_overlay_editor(

    DATASETS,

    run_planning_engine
):

    render_section_header(
        "Edit Demand Overlays"
    )

    overlay_df = pd.read_csv(

        DATASETS[
            "demand_overlays"
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

    def save_overlay_changes(
        edited_df
    ):

        edited_df.to_csv(

            DATASETS[
                "demand_overlays"
            ]["path"],

            index=False
        )

        if run_planning_engine():

            st.success(
                "Demand overlays updated."
            )

            st.rerun()

    render_data_editor(

        dataframe=overlay_df,

        save_button_label="Save Overlay Changes",

        save_callback=save_overlay_changes,

        editor_key="overlay_editor",

        column_config={

            "queue": st.column_config.SelectboxColumn(

                "queue",

                options=valid_queues,

                help=(
                    "Select a governed queue "
                    "from Queue Master."
                )
            )
        }
    )

# =====================================================
# MAIN TAB RENDERER
# =====================================================

def render_demand_tab(

    forecast_df,
    filtered_forecast_df,

    filtered_historical_df,

    variance_df,

    selected_queue,

    DATASETS,
    
    validate_columns,

    run_planning_engine,

    generate_demand_commentary,

    render_insight,
    
    mode="intelligence"
):

    if is_intelligence_mode(mode):

        render_title(
            "Demand Intelligence",
            divider=False
        )

    else:

        render_title(
            "Demand Workbench",
            divider=False
        )
    
    if is_intelligence_mode(mode):

        render_demand_commentary(

            forecast_df,
            filtered_forecast_df,

            selected_queue,

            generate_demand_commentary,

            render_insight
        )

        render_demand_kpis(
            filtered_forecast_df
        )
        
    
        
    # -----------------------------------
    # LOAD FORECAST PROFILES
    # -----------------------------------

    FORECAST_PROFILES = (
        load_forecast_profiles()
    )

    forecast_config_df = pd.read_csv(

        DATASETS[
            "forecast_configuration"
        ]["path"]
    )

    overlays_enabled = (

        str(

            forecast_config_df.loc[
                0,
                "overlays_enabled"
            ]

        ).lower() == "true"
    )

    forecast_source = (

        forecast_config_df.loc[
            0,
            "forecast_source"
        ]
    )

    forecast_profile = (
        st.session_state.get(
            "forecast_profile",
            "Not Selected"
        )
    )

    freeze_weeks = int(

        forecast_config_df.loc[
            0,
            "forecast_offset_weeks"
        ]
    )

    horizon_weeks = int(

        forecast_config_df.loc[
            0,
            "forecast_horizon_weeks"
        ]
    )

    queue_master_df = pd.read_csv(

        DATASETS[
            "queue_master"
        ]["path"]
    )

    active_plan_df = pd.read_csv(

        DATASETS[
            "active_plan"
        ]["path"]
    )

    imported_forecast_df = pd.read_csv(

        DATASETS[
            "imported_forecast"
        ]["path"]
    )

    if (

        forecast_source == "Imported"

        and

        imported_forecast_df.empty
    ):

        st.error(

            "Imported Forecast mode is active "
            "but no imported forecast exists."
        )

        return

    freeze_weeks = int(

        forecast_config_df.loc[
            0,
            "forecast_offset_weeks"
        ]
    )

    horizon_weeks = int(

        forecast_config_df.loc[
            0,
            "forecast_horizon_weeks"
        ]
    )



    if is_engineering_mode(mode):

        render_forecast_status_panel(
            forecast_df,
            forecast_source,
            forecast_profile,
            queue_master_df,
            freeze_weeks,
            horizon_weeks
        )

        render_active_plan_status_panel(
            active_plan_df,
            freeze_weeks
        )

        render_published_plan_status_panel()



    render_forecast_accuracy_panel(
        selected_queue
    )

    # -----------------------------------
    # FORECAST PROFILE SELECTION
    # -----------------------------------

    if is_engineering_mode(mode):

        if forecast_source == "Generated":

            selected_profile = st.selectbox(

                "Forecast Profile",

                list(
                    FORECAST_PROFILES.keys()
                ),

                index=1
            )

            st.session_state[
                "forecast_profile"
            ] = selected_profile

            st.caption(

                FORECAST_PROFILES[
                    selected_profile
                ]["description"]
            )

            if st.button(

                "Apply Forecast Profile",

                width="stretch"
            ):

                with st.spinner(

                    "Regenerating forecast..."
                ):

                    if run_planning_engine():

                        st.success(

                            f"{selected_profile} "
                            f"profile applied."
                        )

                        st.rerun()

        if forecast_source == "Imported":

            st.info(

                "Imported Forecast mode is active. "
                "Forecast profiles are disabled."
            )

            render_imported_forecast_upload(

                DATASETS,

                validate_columns
            )

            st.divider()
        

    render_demand_forecast_chart(
        filtered_forecast_df
    )

    render_historical_demand_variance_chart(

        filtered_forecast_df,

        filtered_historical_df
    )

    render_demand_variance_kpis(
        variance_df
    )

    if is_engineering_mode(mode):

        # -----------------------------------
        # FORECAST VOLATILITY DIAGNOSTICS
        # -----------------------------------

        render_section_header(

            "Forecast Volatility Diagnostics",

            divider=False
        )

        volatility_df = (

            filtered_forecast_df

            .groupby("date")[
                "resolved_forecast"
            ]

            .sum()

            .sort_index()

            .to_frame()
        )

        volatility_df[
            "week_on_week_change"
        ] = (

            volatility_df[
                "resolved_forecast"
            ]

            .diff()

            .abs()
        )

        avg_volatility = (

            volatility_df[
                "week_on_week_change"
            ]

            .mean()
        )

        max_volatility = (

            volatility_df[
                "week_on_week_change"
            ]

            .max()
        )

        volatility_col1, volatility_col2 = (
            st.columns(2)
        )

        volatility_col1.metric(

            "Average Weekly Movement",

            f"{avg_volatility:,.0f}"
        )

        volatility_col2.metric(

            "Peak Weekly Movement",

            f"{max_volatility:,.0f}"
        )
        st.divider()
        # -----------------------------------
        # VOLATILITY CHART
        # -----------------------------------

        def render_volatility_chart():

            st.bar_chart(

                volatility_df[
                    "week_on_week_change"
                ]
            )

        render_chart_container(

            "Forecast Movement Profile",

            render_volatility_chart,

            divider=False
        )

    if is_engineering_mode(mode):


    
        overlay_df = pd.read_csv(

            DATASETS[
                "demand_overlays"
            ]["path"]
        )

        st.divider()
        
        # -----------------------------------
        # HISTORICAL NORMALISATION
        # -----------------------------------

        render_historical_normalisation(
            DATASETS
        )



        # -----------------------------------
        # DEMAND OVERLAYS
        # -----------------------------------

        if overlays_enabled:

            render_overlay_editor(

                DATASETS,

                run_planning_engine
            )

        else:

            st.info(

                "Demand overlays are disabled "
                "in Forecast Configuration."
            )

        st.divider()

        # -----------------------------------
        # OVERLAY TELEMETRY
        # -----------------------------------

        render_section_header(

            "Overlay Impact Diagnostics",

            divider=False
        )

        active_overlay_count = (
            overlay_df.shape[0]
        )

        impacted_queues = (

            overlay_df[
                "queue"
            ]

            .nunique()
        )

        total_adjustment = (

            overlay_df[
                "adjustment_value"
            ]

            .sum()
        )

        telemetry_col1, telemetry_col2, telemetry_col3 = (
            st.columns(3)
        )

        telemetry_col1.metric(

            "Active Overlays",

            int(active_overlay_count)
        )

        telemetry_col2.metric(

            "Impacted Queues",

            int(impacted_queues)
        )

        telemetry_col3.metric(

            "Total Adjustment",

            f"{total_adjustment:.2f}"
        )

        # -----------------------------------
        # OVERLAY DISTRIBUTION
        # -----------------------------------

        overlay_summary_df = (

            overlay_df

            .groupby("queue")[
                "adjustment_value"
            ]

            .sum()

            .sort_values(
                ascending=False
            )
        )

        def render_overlay_chart():

            st.bar_chart(
                overlay_summary_df
            )

        render_chart_container(

            "Overlay Distribution",

            render_overlay_chart,

            divider=False
        )
        st.divider()
        # -----------------------------------
        # OVERLAY LIFECYCLE
        # -----------------------------------

        render_section_header(

            "Overlay Lifecycle Status",

            divider=False
        )

        current_date = pd.Timestamp.today()

        overlay_df["start_date"] = pd.to_datetime(

            overlay_df["start_date"],

            dayfirst=True,

            errors="coerce"
        )

        overlay_df["end_date"] = pd.to_datetime(

            overlay_df["end_date"],

            dayfirst=True,

            errors="coerce"
        )

        active_overlays = (

            overlay_df[

                (
                    overlay_df["start_date"]
                    <= current_date
                )

                &

                (
                    overlay_df["end_date"]
                    >= current_date
                )
            ]
        )

        future_overlays = (

            overlay_df[

                overlay_df["start_date"]
                > current_date
            ]
        )

        expired_overlays = (

            overlay_df[

                overlay_df["end_date"]
                < current_date
            ]
        )

        lifecycle_col1, lifecycle_col2, lifecycle_col3 = (
            st.columns(3)
        )

        lifecycle_col1.metric(

            "Active",

            active_overlays.shape[0]
        )

        lifecycle_col2.metric(

            "Upcoming",

            future_overlays.shape[0]
        )

        lifecycle_col3.metric(

            "Expired",

            expired_overlays.shape[0]
        )

