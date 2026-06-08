import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from Components.kpi_bar import (
    render_kpi_bar
)

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

from Components.file_upload_container import (
    render_file_upload
)

from Components.render_modes import (

    is_intelligence_mode,
    is_engineering_mode
)

from Engine.commentary_renderer import (
    render_commentary_card
)


# =====================================================
# FORECAST DETAIL
# =====================================================

def render_workforce_detail(
    filtered_forecast_df
):

    # -----------------------------
    # DETAIL EXPANDER
    # -----------------------------

    with st.expander(
        "View Forecast Data"
    ):

        st.dataframe(

            filtered_forecast_df,

            width="stretch"
        )
        
def render_workforce_tab(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_workforce_commentary,

    render_insight,
    
    DATASETS, 
    
    validate_columns,
    run_planning_engine,

    mode="intelligence"

):

    if is_intelligence_mode(mode):

        render_title(
            "Workforce Intelligence",
            divider=False
        )

    else:

        render_title(
            "Workforce Workbench",
            divider=False
        )

    if is_intelligence_mode(mode):
    
        # ---------------------------------
        # WORKFORCE COMMENTARY
        # ---------------------------------

        workforce_commentary = (

            generate_workforce_commentary(

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

            workforce_commentary[0]
        )



        # -----------------------------
        # FORECAST SUMMARY KPIs
        # -----------------------------

        peak_requirement = (

            filtered_forecast_df[
                "gross_requirement"
            ].max()
        )

        peak_supply = (

            filtered_forecast_df[
                "available_supply"
            ].max()
        )

        average_gap = (

            filtered_forecast_df[
                "fte_gap"
            ].mean()
        )

        # -----------------------------------
        # WORKFORCE OVERVIEW
        # -----------------------------------

        render_section_header(
            "Workforce Overview",
            divider=False
        )

        avg_gap = round(

            filtered_forecast_df[
                "fte_gap"
            ].mean(),

            1
        )

        avg_occupancy = round(

            filtered_forecast_df[
                "occupancy"
            ].mean(),

            1
        )

        avg_shrinkage = round(

            filtered_forecast_df[
                "shrinkage"
            ].mean(),

            1
        )
        
        # -----------------------------
        # KPI BAR
        # -----------------------------
                
        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Average FTE Gap",
                f"{avg_gap:,.1f}"
            )

        with col2:

            st.metric(
                "Average Occupancy %",
                f"{avg_occupancy:,.1f}%"
            )

        with col3:

            st.metric(
                "Average Shrinkage %",
                f"{avg_shrinkage:,.1f}%"
            )

        queue_gap_chart = (

            filtered_forecast_df

            .groupby("date")[
                "fte_gap"
            ]

            .mean()

            .reset_index()
        )
 
        def render_queue_gap_chart():

            chart_df = (
                queue_gap_chart
                .set_index("date")
            )

            st.line_chart(
                chart_df
            ) 
        

            



    # -----------------------------
    # REQUIREMENT VS SUPPLY
    # -----------------------------
    
    workforce_chart = (

        filtered_forecast_df

        .groupby("date")[
            [
                "gross_requirement",
                "available_supply",
                "productive_supply"
            ]
        ]

        .sum()

        .sort_index()
    )

    def render_workforce_profile_chart():

        st.line_chart(
            workforce_chart
        )

    render_chart_container(

        "Workforce Profile",

        render_workforce_profile_chart
    )    

    # -----------------------------------
    # WORKFORCE FTE GAP TREND
    # -----------------------------------

    workforce_gap_chart = (

        filtered_forecast_df

        .groupby("date")[
            "fte_gap"
        ]

        .sum()

        .sort_index()
    )

    def render_workforce_gap_chart():

        st.bar_chart(
            workforce_gap_chart
        )

    render_chart_container(

        "Workforce FTE Gap Trend",

        render_workforce_gap_chart
    )

    if is_engineering_mode(mode):
    
        # -----------------------------
        # WORKFORCE DATA VALIDATION
        # -----------------------------

        render_section_header(
            "Workforce Validation",
            divider=False
        )

        workforce_validation_df = pd.read_csv(
            DATASETS["workforce_supply"]["path"]
        )

        validation_col1, validation_col2, validation_col3 = (
            st.columns(3)
        )

        validation_col1.metric(

            "Rows",

            len(workforce_validation_df)
        )

        validation_col2.metric(

            "Missing Values",

            int(
                workforce_validation_df
                .isnull()
                .sum()
                .sum()
            )
        )

        validation_col3.metric(

            "Duplicate Rows",

            int(
                workforce_validation_df
                .duplicated()
                .sum()
            )
        )

        # -----------------------------
        # WORKFORCE CHANGE DIAGNOSTICS
        # -----------------------------

        render_section_header(
            "Workforce Change Diagnostics",
            divider=False
        )

        workforce_change_df = pd.read_csv(
            DATASETS["workforce_supply"]["path"]
        )

        workforce_change_df["date"] = pd.to_datetime(
            workforce_change_df["date"],
            dayfirst=True,
            errors="coerce"
        )

        workforce_change_chart = (

            filtered_forecast_df

            .groupby("date")[
                [
                    "new_hires",
                    "structural_attrition",
                    "manual_attrition"
                ]
            ]

            .sum()

            .sort_index()
        )

        def render_workforce_change_chart():

            st.line_chart(
                workforce_change_chart
            )

        render_chart_container(

            "Hiring vs Attrition Trend",

            render_workforce_change_chart,

            divider=False
        )
                
        # -----------------------------
        # WORKFORCE UPLOAD
        # -----------------------------

        render_file_upload(

            label="Upload Workforce Supply",

            dataset_path=DATASETS[
                "workforce_supply"
            ]["path"],

            required_columns=DATASETS[
                "workforce_supply"
            ]["required_columns"],

            validate_columns=validate_columns,

            success_message="Workforce supply updated.",

            uploader_key="workforce_upload"
        )
                
        # -----------------------------
        # WORKFORCE EDITOR
        # -----------------------------

        render_section_header(
            "Edit Workforce Supply"
        )

        editable_workforce = pd.read_csv(
            DATASETS["workforce_supply"]["path"]
        )

        editable_workforce["attrition"] = (

            editable_workforce["attrition"]

            .fillna(0)
        )

        editable_workforce["new_hires"] = (

            editable_workforce["new_hires"]

            .fillna(0)
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

        def save_workforce_changes(
            edited_df
        ):

            edited_df.to_csv(

                DATASETS["workforce_supply"]["path"],

                index=False
            )

            if run_planning_engine():

                st.success(
                    "Workforce updated and engine refreshed."
                )

                st.rerun()


        render_data_editor(

            dataframe=editable_workforce,

            save_button_label="Save Workforce Changes",

            save_callback=save_workforce_changes,

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

        queue_config_df = pd.read_csv(
            DATASETS["queue_config"]["path"]
        )

        render_section_header(
            "Queue Opening FTE"
        )

        def save_queue_config_changes(
            edited_df
        ):

            edited_df.to_csv(

                DATASETS["queue_config"]["path"],

                index=False
            )

            st.success(
                "Queue opening FTE updated."
            )


        render_data_editor(

            dataframe=queue_config_df,

            save_button_label="Save Queue FTE",

            save_callback=save_queue_config_changes,

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
        

        # -----------------------------
        # BUDGET POSITION CHANGES
        # -----------------------------

        render_section_header(
            "Budget Position Changes"
        )

        st.info(
            "Budget changes override the "
            "Queue Master budget position "
            "from the effective date forward."
        )

        budget_changes_df = pd.read_csv(

            DATASETS[
                "budget_changes"
            ]["path"]

        )

        def save_budget_changes(
            edited_df
        ):

            edited_df.to_csv(

                DATASETS[
                    "budget_changes"
                ]["path"],

                index=False
            )

            if run_planning_engine():

                st.success(
                    "Budget changes updated and engine refreshed."
                )

                st.rerun()


        render_data_editor(

            dataframe=budget_changes_df,

            save_button_label=
                "Save Budget Changes",

            save_callback=
                save_budget_changes,

            column_config={

                "queue":

                    st.column_config.SelectboxColumn(

                        "queue",

                        options=valid_queues,

                        help=(
                            "Select a governed queue "
                            "from Queue Master."
                        )
                    )
            }
        )
                
        render_workforce_detail(
            filtered_forecast_df
        )

