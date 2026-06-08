import streamlit as st
import pandas as pd
import io


# -----------------------------------
# STYLING
# -----------------------------------

def highlight_section_rows(row):

    section_rows = [
        "■■ DEMAND",
        "■■ WORKFORCE",
        "■■ BUDGET",
        "■■ GAP ANALYSIS"
    ]

    if row.name in section_rows:

        return [
            """
            background-color:#0F172A;
            color:#60A5FA;
            font-weight:bold;
            """
        ] * len(row)

    return [""] * len(row)


def highlight_key_rows(row):

    key_rows = [
        "Final Forecast",
        "Closing FTE",
        "Productive Supply",
        "Budget FTE",
        "Required FTE (Incl Occ & Shrink)"
    ]

    if row.name in key_rows:

        return [
            """
            background-color:#1E3552;
            color:white;
            font-weight:bold;
            """
        ] * len(row)

    return [""] * len(row)


def highlight_gap_rows(row):

    # -------------------------
    # FTE GAP
    # Positive = Good
    # -------------------------

    if row.name == "FTE Gap":

        return [
            (
                "background-color:#2E7D32;color:white;font-weight:bold"
                if value > 0
                else
                "background-color:#C62828;color:white;font-weight:bold"
                if value < 0
                else ""
            )
            for value in row
        ]

    # -------------------------
    # SUPPLY VS BUDGET
    # Positive = Bad
    # -------------------------

    if row.name == "Supply vs Budget":

        return [
            (
                "background-color:#C62828;color:white;font-weight:bold"
                if value > 0
                else
                "background-color:#2E7D32;color:white;font-weight:bold"
                if value < 0
                else ""
            )
            for value in row
        ]

    # -------------------------
    # REQUIREMENT VS BUDGET
    # Positive = Bad
    # -------------------------

    if row.name == "Requirement vs Budget":

        return [
            (
                "background-color:#C62828;color:white;font-weight:bold"
                if value > 0
                else
                "background-color:#2E7D32;color:white;font-weight:bold"
                if value < 0
                else ""
            )
            for value in row
        ]

    return [""] * len(row)


# -----------------------------------
# MAIN GRID
# -----------------------------------

def render_planning_grid(
    forecast_df,
    selected_queue,
    DATASETS
):

    st.title("Planning Table")

    if selected_queue == "All Queues":

        st.warning(
            "Please select a specific queue to view the Planning Grid."
        )

        return

    st.write(
        f"Queue: {selected_queue}"
    )

    queue_df = (
        forecast_df[
            forecast_df["queue"] == selected_queue
        ]
        .copy()
    )


    queue_df["date"] = pd.to_datetime(
        queue_df["date"],
        dayfirst=True
    )

    today = pd.Timestamp.today()

    queue_df = queue_df[
        queue_df["date"] >= (
            today - pd.Timedelta(days=7)
        )
    ]

    opening_fte = []

    for i in range(len(queue_df)):

        if i == 0:

            opening_fte.append(
                queue_df[
                    "default_opening_fte"
                ].iloc[0]
            )

        else:

            opening_fte.append(
                queue_df[
                    "available_supply"
                ].iloc[i - 1]
            )

    queue_df["opening_fte"] = opening_fte

    planning_grid = pd.DataFrame(
        {

            # -------------------------
            # DEMAND
            # -------------------------

            "■■ DEMAND":
                [""] * len(queue_df),

            "Baseline Forecast":
                queue_df["base_layer"].values,

            "Growth Impact":
                queue_df["growth_layer"].values,

            "Seasonality Impact":
                queue_df["seasonality_layer"].values,

            "Transformation Impact":
                queue_df["transformation_layer"].values,

            "Operational Impact":
                queue_df["operational_layer"].values,

            "Final Forecast":
                queue_df["resolved_forecast"].values,

            # -------------------------
            # WORKFORCE
            # -------------------------

            " ":
                [""] * len(queue_df),

            "■■ WORKFORCE":
                [""] * len(queue_df),

            "Opening FTE":
                queue_df["opening_fte"].values,

            "New Hires":
                queue_df["new_hires"].values,

            "Attrition":
                queue_df["total_attrition"].values,

            "Closing FTE":
                queue_df["available_supply"].values,

            "Effective AHT":
                queue_df["effective_aht"].values,

            "Productive Supply":
                queue_df["productive_supply"].values,

            # -------------------------
            # BUDGET
            # -------------------------

            "  ":
                [""] * len(queue_df),

            "■■ BUDGET":
                [""] * len(queue_df),

            "Budget FTE":
                queue_df["budgeted_fte_new"].values,

            # -------------------------
            # GAP ANALYSIS
            # -------------------------

            "   ":
                [""] * len(queue_df),

            "■■ GAP ANALYSIS":
                [""] * len(queue_df),

            "Required FTE (Incl Occ & Shrink)":
                queue_df["gross_requirement"].values,

            "FTE Gap":
                queue_df["fte_gap"].values,

            "Supply vs Budget":
                queue_df["budget_variance"].values,

            "Requirement vs Budget":
                queue_df["requirement_vs_budget"].values,

        },
        index=queue_df["date_display"]
    ).T

    # -----------------------------------
    # ROUND NUMBERS
    # -----------------------------------

    planning_grid = planning_grid.round(0)
    planning_grid = planning_grid.astype(object)

    for col in planning_grid.columns:

        planning_grid[col] = planning_grid[col].apply(
            lambda x:
            int(x)
            if isinstance(x, (int, float))
            and pd.notnull(x)
            else x
        )

    # -----------------------------------
    # EXPORT DATASET
    # -----------------------------------

    export_grid = planning_grid.copy()

    # -----------------------------------
    # STYLING
    # -----------------------------------

    styled_grid = (
        planning_grid
        .style
        .apply(
            highlight_section_rows,
            axis=1
        )
        .apply(
            highlight_key_rows,
            axis=1
        )
        .apply(
            highlight_gap_rows,
            axis=1
        )
    )

    # -----------------------------------
    # DISPLAY
    # -----------------------------------

    st.caption(

        f"Active Plan | {queue_df['date'].min():%d/%m/%Y}"
        f" to "
        f"{queue_df['date'].max():%d/%m/%Y}"

    )

    # -----------------------------------
    # EXPORT TO EXCEL
    # -----------------------------------

    csv_data = export_grid.to_csv()

    st.download_button(

        label="📊 Export Planning Grid",

        data=csv_data,

        file_name=(
            f"planning_grid_{selected_queue}.csv"
        ),

        mime="text/csv"
    )

    st.dataframe(
        styled_grid,
        use_container_width=True,
        height=910,
        column_config={
            "_index": st.column_config.TextColumn(
                width="large"
            )
        }
    )


