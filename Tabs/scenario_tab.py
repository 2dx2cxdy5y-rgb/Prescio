import streamlit as st
import pandas as pd
import os


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

# =====================================================
# HEADER + VALIDATION
# =====================================================

def render_scenario_header(

    list_scenarios
):

    render_title(

        "Scenario Comparison",

        divider=False,

        caption=(
            "Strategic scenario comparison, "
            "delta analysis, "
            "and executive planning insight."
        )
    )

    # -----------------------------
    # AVAILABLE SCENARIOS
    # -----------------------------

    scenario_files = (
        list_scenarios()
    )

    # -----------------------------
    # VALIDATION
    # -----------------------------

    if len(scenario_files) < 2:

        st.warning(
            "At least two saved scenarios are required."
        )

        return None

    return scenario_files

# =====================================================
# SCENARIO SELECTION + LOADING
# =====================================================

def render_scenario_selection(

    scenario_files,

    load_scenario
):

    render_section_header(
        "Scenario Selection"
    )


    # -------------------------
    # SCENARIO SELECTORS
    # -------------------------



    comparison_col1, comparison_col2 = (
        st.columns(2)
    )

    with comparison_col1:

        baseline_scenario = (
            st.selectbox(

                "Baseline Scenario",

                scenario_files,

                key="baseline_scenario"
            )
        )

    with comparison_col2:

        comparison_scenario = (
            st.selectbox(

                "Comparison Scenario",

                scenario_files,

                index=1,

                key="comparison_scenario"
            )
        )

    # -------------------------
    # LOAD FORECASTS
    # -------------------------

    baseline_df = pd.read_csv(
        f"output/scenarios/{baseline_scenario}_forecast.csv"
    )

    comparison_df = pd.read_csv(
        f"output/scenarios/{comparison_scenario}_forecast.csv"
    )

    # -------------------------
    # LOAD METADATA
    # -------------------------

    baseline_metadata = load_scenario(
        baseline_scenario
    )

    comparison_metadata = load_scenario(
        comparison_scenario
    )

    return {

        "baseline_scenario":
            baseline_scenario,

        "comparison_scenario":
            comparison_scenario,

        "baseline_df":
            baseline_df,

        "comparison_df":
            comparison_df,

        "baseline_metadata":
            baseline_metadata,

        "comparison_metadata":
            comparison_metadata
    }

# =====================================================
# SCENARIO COMPARISON RESULTS
# =====================================================

def render_scenario_comparison_results(

    scenario_context,

    compare_scenarios
):

    # -------------------------
    # CONTEXT EXTRACTION
    # -------------------------

    baseline_scenario = (
        scenario_context[
            "baseline_scenario"
        ]
    )

    comparison_scenario = (
        scenario_context[
            "comparison_scenario"
        ]
    )

    baseline_df = (
        scenario_context[
            "baseline_df"
        ]
    )

    comparison_df = (
        scenario_context[
            "comparison_df"
        ]
    )

    baseline_metadata = (
        scenario_context[
            "baseline_metadata"
        ]
    )

    comparison_metadata = (
        scenario_context[
            "comparison_metadata"
        ]
    )


    # -------------------------
    # RUN COMPARISON
    # -------------------------


    comparison_results = (
        compare_scenarios(

            baseline_df,
            comparison_df
        )
    )

    # =================================================
    # KPI SUMMARY
    # =================================================


    baseline_gap = (
        baseline_df[
            "fte_gap"
        ].min()
    )

    comparison_gap = (
        comparison_df[
            "fte_gap"
        ].min()
    )

    gap_delta = (
        comparison_gap
        - baseline_gap
    )

    render_kpi_bar([

        {
            "label": "Baseline Worst Gap",
            "value": f"{baseline_gap:,.1f}"
        },

        {
            "label": "Comparison Worst Gap",
            "value": f"{comparison_gap:,.1f}"
        },

        {
            "label": "Gap Delta",
            "value": f"{gap_delta:,.1f}"
        }
    ])

    # =================================================
    # SCENARIO DETAIL
    # =================================================

    render_section_header(
        "Scenario Delta Summary"
    )

    meta_col1, meta_col2 = st.columns(2)

    with meta_col1:

        st.info(

            f"""
### {baseline_scenario}

{baseline_metadata.get(
    "scenario_description",
    "No description provided."
)}
"""
        )

    with meta_col2:

        st.info(

            f"""
### {comparison_scenario}

{comparison_metadata.get(
    "scenario_description",
    "No description provided."
)}
"""
        )

    # =================================================
    # COMPARISON TABLE
    # =================================================

    def render_comparison_table():

        st.dataframe(

            comparison_results,

            width="stretch"
        )

    render_chart_container(

        "Scenario Comparison Results",

        render_comparison_table,

        divider=False
    )

    return {

        "comparison_results":
            comparison_results,

        "baseline_df":
            baseline_df,

        "comparison_df":
            comparison_df,

        "baseline_scenario":
            baseline_scenario,

        "comparison_scenario":
            comparison_scenario
    }

# =====================================================
# CHARTS
# =====================================================


def render_workforce_profile_comparison(
    comparison_context
):

    baseline_df = (
        comparison_context["baseline_df"]
    )

    comparison_df = (
        comparison_context["comparison_df"]
    )

    baseline_scenario = (
        comparison_context["baseline_scenario"]
    )

    comparison_scenario = (
        comparison_context["comparison_scenario"]
    )

    baseline_chart = (

        baseline_df

        .groupby("date")[
            [
                "gross_requirement",
                "productive_supply"
            ]
        ]

        .sum()
        .reset_index()
        .sort_values("date")
    )

    comparison_chart = (

        comparison_df

        .groupby("date")[
            [
                "gross_requirement",
                "productive_supply"
            ]
        ]

        .sum()
        .reset_index()
    )

    chart_df = pd.DataFrame({

        "date":
            baseline_chart["date"],

        f"{baseline_scenario} Requirement":
            baseline_chart[
                "gross_requirement"
            ],

        f"{baseline_scenario} Productive":
            baseline_chart[
                "productive_supply"
            ],

        f"{comparison_scenario} Requirement":
            comparison_chart[
                "gross_requirement"
            ],

        f"{comparison_scenario} Productive":
            comparison_chart[
                "productive_supply"
            ]
    })

    def render_chart():

        st.line_chart(
            chart_df.set_index("date")
        )

    render_chart_container(

        "Workforce Profile Comparison",

        render_chart,

        divider=False
    )


    
def render_workforce_gap_comparison(
    comparison_context
):

    baseline_df = (
        comparison_context["baseline_df"]
    )

    comparison_df = (
        comparison_context["comparison_df"]
    )

    baseline_scenario = (
        comparison_context["baseline_scenario"]
    )

    comparison_scenario = (
        comparison_context["comparison_scenario"]
    )

    baseline_gap = (

        baseline_df

        .groupby("date")["fte_gap"]

        .sum()

        .reset_index()
        
        .sort_values("date")

    )

    comparison_gap = (

        comparison_df

        .groupby("date")["fte_gap"]

        .sum()

        .reset_index()

    )
    
    chart_df = pd.DataFrame({

        "date":
            baseline_gap["date"],

        baseline_scenario:
            baseline_gap["fte_gap"],

        comparison_scenario:
            comparison_gap["fte_gap"]

    })

    def render_chart():

        st.line_chart(
            chart_df.set_index("date")
        )

    render_chart_container(

        "Workforce FTE Gap Trend Comparison",

        render_chart,

        divider=False
    )

# =====================================================
# MAIN TAB RENDERER
# =====================================================

def render_scenario_tab(

    list_scenarios,

    load_scenario,

    compare_scenarios
):

    scenario_files = (

        render_scenario_header(

            list_scenarios
        )
    )

    if scenario_files is None:

        return

    scenario_context = (

        render_scenario_selection(

            scenario_files,

            load_scenario
        )
    )

    comparison_context = (

        render_scenario_comparison_results(

            scenario_context,

            compare_scenarios
        )
    )

    render_workforce_profile_comparison(

        comparison_context
    )

    render_workforce_gap_comparison(

        comparison_context
    )