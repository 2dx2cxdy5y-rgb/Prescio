import streamlit as st

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

from Engine.commentary_renderer import (
    render_commentary_card
)

# =====================================================
# COMMENTARY
# =====================================================

def render_budget_commentary(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_budget_commentary,

    render_insight
):

    # ---------------------------------
    # GENERATE COMMENTARY
    # ---------------------------------

    budget_commentary = (

        generate_budget_commentary(

            forecast_df,

            filtered_forecast_df,

            selected_queue
        )
    )

    # ---------------------------------
    # SECTION TITLE
    # ---------------------------------

    render_title(
        "Financial Intelligence",
        divider=False
    )

    # ---------------------------------
    # ENTERPRISE COMMENTARY
    # ---------------------------------

    render_commentary_card(
        st,
        budget_commentary[0]
    )



# =====================================================
# KPI SECTION
# =====================================================

def render_budget_kpis(
    filtered_forecast_df
):

    # ---------------------------------
    # KPI CALCULATIONS
    # ---------------------------------

    total_budget = (
        filtered_forecast_df[
            "budgeted_fte_new"
        ].sum()
    )

    total_requirement = (
        filtered_forecast_df[
            "gross_requirement"
        ].sum()
    )

    total_available = (
        filtered_forecast_df[
            "available_supply"
        ].sum()
    )

    total_budget_gap = (
        total_budget
        - total_requirement
    )

    # ---------------------------------
    # KPI STRIP
    # ---------------------------------

    render_kpi_bar([

        {
            "label": "Budgeted FTE",
            "value": f"{total_budget:,.1f}"
        },

        {
            "label": "Required FTE",
            "value": f"{total_requirement:,.1f}"
        },

        {
            "label": "Budget Variance",
            "value": f"{total_budget_gap:,.1f}"
        }
    ])

# =====================================================
# BUDGET CHART
# =====================================================

def render_budget_chart(
    filtered_forecast_df
):


    # ---------------------------------
    # BUILD CHART DATAFRAME
    # ---------------------------------

    budget_chart = (

        filtered_forecast_df

        .groupby("date")[
            [
                "gross_requirement",
                "budgeted_fte_new",
                "available_supply"
            ]
        ]

        .sum()

        .sort_index()
    )


    # ---------------------------------
    # CHART RENDER
    # ---------------------------------

    def render_chart():

        st.line_chart(
            budget_chart
        )

    render_chart_container(

        "Budget vs Requirement",

        render_chart,

        divider=False
    )

# =====================================================
# QUEUE BUDGET POSITION
# =====================================================

def render_queue_budget_position(
    filtered_forecast_df
):

    # ---------------------------------
    # BUILD DATAFRAME
    # ---------------------------------

    queue_budget_view = (
        filtered_forecast_df
        .groupby("queue")[
            [
                "gross_requirement",
                "budgeted_fte_new",
                "available_supply"
            ]
        ]
        .mean()
        .round(2)
    )

    queue_budget_view["requirement_vs_budget"] = (
        queue_budget_view["budgeted_fte_new"]
        - queue_budget_view["gross_requirement"]
    ).round(2)

    # ---------------------------------
    # TABLE RENDER
    # ---------------------------------

    def render_table():

        st.dataframe(

            queue_budget_view,

            width="stretch"
        )

    render_chart_container(

        "Queue Budget Position",

        render_table,

        divider=False
    )

# =====================================================
# MAIN TAB RENDERER
# =====================================================

def render_budget_tab(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_budget_commentary,

    render_insight
):



    render_budget_commentary(

        forecast_df,
        filtered_forecast_df,

        selected_queue,

        generate_budget_commentary,

        render_insight
    )

    render_budget_kpis(
        filtered_forecast_df
    )

    render_budget_chart(
        filtered_forecast_df
    )

    render_queue_budget_position(
        filtered_forecast_df
    )