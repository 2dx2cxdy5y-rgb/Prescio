import streamlit as st
import plotly.graph_objects as go
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

from Components.file_upload_container import (
    render_file_upload
)

from Components.render_modes import (

    is_intelligence_mode,
    is_engineering_mode
)

from Components.help_header import (
    render_help_header
)

from Engine.commentary_renderer import (
    render_commentary_card
)

# =====================================================
# COMMENTARY
# =====================================================

def render_transformation_commentary(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_transformation_commentary,

    render_insight
):

    transformation_commentary = (

        generate_transformation_commentary(

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
        transformation_commentary[0]
    )



# =====================================================
# KPI SECTION
# =====================================================

def render_transformation_kpis(

    portfolio_df,
    filtered_forecast_df
):

    total_delay = (
        portfolio_df["delay_weeks"]
        .sum()
    )

    # -----------------------------
    # STATUS MESSAGE
    # -----------------------------

    if total_delay > 10:

        st.error(
            "Transformation portfolio delays are severe."
        )

    elif total_delay > 3:

        st.warning(
            "Transformation delivery delays detected."
        )

    else:

        st.success(
            "Transformation portfolio on track."
        )

    # -----------------------------
    # KPI STRIP
    # -----------------------------

    render_kpi_bar([

        {
            "label": "Programmes",
            "value": len(portfolio_df)
        },

        {
            "label": "Total Delay",
            "value": f"{total_delay} weeks"
        },

        {
            "label": "AI Demand Reduction",
            "value": (
                f"{filtered_forecast_df['ai_deflection'].max() * 100:.0f}%"
            )
        }
    ])

# =====================================================
# TRANSFORMATION BENEFITS CHART
# =====================================================

def render_transformation_benefits_chart(
    filtered_forecast_df
):

    # ---------------------------------
    # BUILD TRANSFORMATION TIMELINE
    # ---------------------------------

    benefits_df = pd.read_csv(
        "Data/transformation_benefits.csv"
    )

    benefits_df["date"] = pd.to_datetime(

        benefits_df["date"],

        dayfirst=True,

        errors="coerce"
    )

    if "queue" in benefits_df.columns:

        if len(

            filtered_forecast_df[
                "queue"
            ].unique()

        ) == 1:

            selected_queue = (

                filtered_forecast_df[
                    "queue"
                ]

                .iloc[0]
            )

            benefits_df = (

                benefits_df[

                    benefits_df["queue"]

                    ==

                    selected_queue
                ]
            )

    transformation_timeline = (

        benefits_df

        .groupby("date")

        .agg({

            "ai_deflection": "mean",

            "aht_reduction": "mean",

            "productivity_gain": "mean"

        })

        .reset_index()
    )

    transformation_timeline["date_display"] = (

        transformation_timeline["date"]

        .dt.strftime(
            "%d/%m/%Y"
        )
    )
            
    # ---------------------------------
    # CREATE FIGURE
    # ---------------------------------

    fig_transform = go.Figure()

    # ---------------------------------
    # AI DEFLECTION
    # ---------------------------------

    fig_transform.add_trace(

        go.Scatter(

            x=transformation_timeline["date_display"],

            y=transformation_timeline[
                "ai_deflection"
            ],

            name="AI Deflection %"
        )
    )

    # ---------------------------------
    # PRODUCTIVITY GAIN
    # ---------------------------------

    fig_transform.add_trace(

        go.Scatter(

            x=transformation_timeline["date_display"],

            y=transformation_timeline[
                "productivity_gain"
            ],

            name="Productivity Gain %"
        )
    )

    # ---------------------------------
    # AHT CHANGE
    # ---------------------------------

    fig_transform.add_trace(

        go.Scatter(

            x=transformation_timeline["date_display"],

            y=(
                transformation_timeline[
                    "aht_reduction"
                ]
            ),

            name="AHT Change (secs)",

            yaxis="y2"
        )
    )

    # ---------------------------------
    # LAYOUT
    # ---------------------------------

    fig_transform.update_layout(

        height=450,

        template="plotly_dark",

        hovermode="x unified",

        yaxis=dict(
            title="Percentage Impact"
        ),

        yaxis2=dict(

            title="AHT Seconds",

            overlaying="y",

            side="right"
        )
    )

    # ---------------------------------
    # CHART RENDER
    # ---------------------------------

    def render_chart():

        st.plotly_chart(

            fig_transform,

            use_container_width=True
        )

    render_chart_container(

        "Transformation Adoption Curve",

        render_chart
    )

# =====================================================
# DEMAND COMPARISON CHART
# =====================================================

def render_transformation_demand_chart(
    filtered_forecast_df
):

    # ---------------------------------
    # BUILD COMPARISON DATAFRAME
    # ---------------------------------

    demand_comparison = (

        filtered_forecast_df

        .groupby("date_display")

        .agg({

            "demand": "sum",

            "resolved_forecast": "sum"

        })

        .reset_index()
    )

    # ---------------------------------
    # CREATE FIGURE
    # ---------------------------------

    fig_demand = go.Figure()

    # ---------------------------------
    # BASELINE DEMAND
    # ---------------------------------

    fig_demand.add_trace(

        go.Scatter(

            x=demand_comparison["date_display"],

            y=demand_comparison["demand"],

            name="Baseline Demand"
        )
    )

    # ---------------------------------
    # TRANSFORMED DEMAND
    # ---------------------------------

    fig_demand.add_trace(

        go.Scatter(

            x=demand_comparison["date_display"],

            y=demand_comparison[
                "resolved_forecast"
            ],

            name="Transformed Demand"
        )
    )

    # ---------------------------------
    # LAYOUT
    # ---------------------------------

    fig_demand.update_layout(

        height=450,

        template="plotly_dark",

        hovermode="x unified",

        yaxis=dict(

            title="Demand Volume"
        ),

        legend=dict(

            orientation="h"
        )
    )

    # ---------------------------------
    # CHART RENDER
    # ---------------------------------

    def render_chart():

        st.plotly_chart(

            fig_demand,

            use_container_width=True
        )

    render_chart_container(

        "Baseline vs Transformed Demand",

        render_chart
    )

# =====================================================
# REQUIREMENT COMPARISON CHART
# =====================================================

def render_transformation_requirement_chart(
    filtered_forecast_df
):

    # ---------------------------------
    # COPY DATAFRAME
    # ---------------------------------

    requirement_comparison = (

        filtered_forecast_df.copy()
    )

    # ---------------------------------
    # SAFE AI DEFLECTION
    # ---------------------------------

    safe_ai_deflection = (

        requirement_comparison[
            "ai_deflection"
        ]

        .clip(
            upper=0.95
        )
    )

    # ---------------------------------
    # BASELINE REQUIREMENT
    # ---------------------------------

    requirement_comparison[
        "baseline_requirement"
    ] = (

        requirement_comparison[
            "gross_requirement"
        ]

        / (
            1
            - safe_ai_deflection
        )
    )

    # ---------------------------------
    # GROUP DATA
    # ---------------------------------

    requirement_comparison = (

        requirement_comparison

        .groupby("date_display")

        .agg({

            "baseline_requirement": "sum",

            "gross_requirement": "sum"

        })

        .reset_index()
    )

    # ---------------------------------
    # CREATE FIGURE
    # ---------------------------------

    fig_requirement = go.Figure()

    # ---------------------------------
    # BASELINE REQUIREMENT
    # ---------------------------------

    fig_requirement.add_trace(

        go.Scatter(

            x=requirement_comparison["date_display"],

            y=requirement_comparison[
                "baseline_requirement"
            ],

            name="Baseline Requirement"
        )
    )

    # ---------------------------------
    # TRANSFORMED REQUIREMENT
    # ---------------------------------

    fig_requirement.add_trace(

        go.Scatter(

            x=requirement_comparison["date_display"],

            y=requirement_comparison[
                "gross_requirement"
            ],

            name="Transformed Requirement"
        )
    )

    # ---------------------------------
    # LAYOUT
    # ---------------------------------

    fig_requirement.update_layout(

        height=450,

        template="plotly_dark",

        hovermode="x unified",

        yaxis=dict(

            title="FTE Requirement"
        ),

        legend=dict(

            orientation="h"
        )
    )

    # ---------------------------------
    # CHART RENDER
    # ---------------------------------

    def render_chart():

        st.plotly_chart(

            fig_requirement,

            use_container_width=True
        )

    render_chart_container(

        "Baseline vs Transformed Requirement",

        render_chart
    )

# =====================================================
# PORTFOLIO UPLOAD
# =====================================================

def render_portfolio_upload(

    DATASETS,

    validate_columns
):

    render_section_header(
        "Upload Programme Portfolio"
    )

    render_file_upload(

        label="Upload Programme Portfolio",

        dataset_path=DATASETS[
            "programme_portfolio"
        ]["path"],

        required_columns=[

            "programme",
            "queue",
            "start_date",
            "end_date",
            "ai_deflection",
            "demand_change",
            "aht_change",
            "productivity_gain",
            "occupancy_change",
            "shrinkage_change",
            "delay_weeks",
            "dependency"
        ],

        validate_columns=validate_columns,

        success_message="Programme portfolio updated.",

        uploader_key="portfolio_upload"
    )
    st.divider()
# =====================================================
# PORTFOLIO EDITOR
# =====================================================

def render_portfolio_editor(

    DATASETS,

    run_planning_engine
):

    render_help_header(

        "Edit Programme Portfolio",

        """

    #### Queue Selection

    Queue values are controlled from the platform queue master.

    - Click inside the queue cell to select a valid queue
    - Free-text queue names are not permitted
    - This prevents spelling mismatches and forecast mapping errors
    
    ---
    
    ### Programme Portfolio Guidance

    #### AI Deflection
    Percentage reduction in incoming demand volume.

    Example:
    - 15 = 15% demand removed

    ---

    #### Demand Change
    Percentage increase or decrease in forecast demand.

    Example:
    - -5 = 5% demand reduction
    - 10 = 10% demand increase

    ---

    #### AHT Change
    Percentage change applied to Average Handle Time.

    Example:
    - -20 = 20% AHT reduction

    ---

    #### Productivity Gain
    Percentage workforce productivity improvement.

    Example:
    - 5 = 5% productivity increase

    ---

    #### Occupancy Change
    Absolute occupancy percentage-point adjustment.

    Example:
    - 3 = 85% → 88%

    ---

    #### Shrinkage Change
    Absolute shrinkage percentage-point adjustment.

    Example:
    - -2 = 30% → 28%

    ---

    #### Delay Weeks
    Implementation delay before benefits activate.

    Example:
    - 2 = benefits delayed by 2 weeks

    ---

    #### Dependency
    Programme dependency relationship.

    Example:
    - CRM Upgrade depends on AI Assistant

    """)

    editable_portfolio = pd.read_csv(

        DATASETS[
            "programme_portfolio"
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
        ].dropna().unique()
    )

    # ---------------------------------
    # SAVE CALLBACK
    # ---------------------------------

    def save_portfolio_changes(
        edited_df
    ):

        edited_df.to_csv(

            DATASETS[
                "programme_portfolio"
            ]["path"],

            index=False
        )

        if run_planning_engine():

            st.success(
                "Portfolio updated and engine refreshed."
            )

            st.rerun()

    # ---------------------------------
    # EDITOR
    # ---------------------------------

    render_data_editor(

        dataframe=editable_portfolio,

        save_button_label="Save Portfolio Changes",

        save_callback=save_portfolio_changes,

        editor_key="portfolio_editor",

        column_config={

            "queue": st.column_config.SelectboxColumn(

                "queue",

                options=valid_queues,

                help=(
                    "Select a valid operational queue."
                )
            )
        }
    )


# =====================================================
# MAIN TAB RENDERER
# =====================================================

def render_transformation_tab(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    portfolio_df,

    DATASETS,

    validate_columns,

    run_planning_engine,

    generate_transformation_commentary,

    render_insight,
    
    mode="intelligence"
    
):

    if is_intelligence_mode(mode):

        render_title(
            "Transformation Intelligence",
            divider=False
        )

    else:

        render_title(
            "Transformation Workbench",
            divider=False
        )

    if is_intelligence_mode(mode):

        render_transformation_commentary(

            forecast_df,
            filtered_forecast_df,

            selected_queue,

            generate_transformation_commentary,

            render_insight
            
        )

        render_transformation_kpis(

            portfolio_df,
            filtered_forecast_df
        )

    render_transformation_benefits_chart(

        filtered_forecast_df
    )

    render_transformation_demand_chart(
        filtered_forecast_df
    )

    render_transformation_requirement_chart(
        filtered_forecast_df
    )

    if is_engineering_mode(mode):

        # -----------------------------
        # DELIVERY RISK DIAGNOSTICS
        # -----------------------------

        render_section_header(
            "Transformation Delivery Diagnostics",
            divider=False
        )

        delivery_risk_df = (

            portfolio_df

            .groupby("programme", as_index=False)[
                "delay_weeks"
            ]

            .sum()
        )

        total_delay = (
            delivery_risk_df[
                "delay_weeks"
            ].sum()
        )

        delayed_programmes = (

            delivery_risk_df[
                delivery_risk_df[
                    "delay_weeks"
                ] > 0
            ]

            .shape[0]
        )

        diagnostic_col1, diagnostic_col2 = (
            st.columns(2)
        )

        diagnostic_col1.metric(

            "Total Delay Weeks",

            int(total_delay)
        )

        diagnostic_col2.metric(

            "Delayed Programmes",

            int(delayed_programmes)
        )

        # -----------------------------
        # DELAY TREND CHART
        # -----------------------------

        delay_chart_df = (

            delivery_risk_df

            .sort_values(
                by="delay_weeks",
                ascending=False
            )
        )

        def render_delay_chart():

            st.bar_chart(

                delay_chart_df.set_index(
                    "programme"
                )["delay_weeks"]
            )

        render_chart_container(

            "Programme Delay Exposure",

            render_delay_chart,

            divider=False
        )

    if is_engineering_mode(mode):

        render_portfolio_upload(

            DATASETS,

            validate_columns
        )

        render_portfolio_editor(

            DATASETS,

            run_planning_engine
        )
