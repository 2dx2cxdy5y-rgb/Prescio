import pandas as pd


# -----------------------------
# FINANCIAL CALCULATIONS
# -----------------------------

def calculate_financials(

    forecast_df,
    supply_df,
    salary_per_fte,
    recruitment_cost_per_hire,
    contractor_cost_per_fte,
    overtime_cost_per_fte
):

    # -------------------------
    # SALARY COST
    # -------------------------

    forecast_df["salary_cost"] = (

        forecast_df["gross_requirement"]

        * salary_per_fte
    )

    # -------------------------
    # RECRUITMENT COST
    # -------------------------

    forecast_df["recruitment_cost"] = (

        supply_df["new_hires"]

        * recruitment_cost_per_hire
    )

    # -------------------------
    # CONTRACTOR COST
    # -------------------------

    forecast_df["contractor_cost"] = (

        forecast_df["fte_gap"]

        .apply(
            lambda x: abs(x)
            if x < 0
            else 0
        )

        * contractor_cost_per_fte
    )

    # -------------------------
    # OVERTIME COST
    # -------------------------

    forecast_df["overtime_cost"] = (

        forecast_df["fte_gap"]

        .apply(
            lambda x: abs(x)
            if x < 0
            else 0
        )

        * overtime_cost_per_fte
    )

    # -------------------------
    # TOTAL COST
    # -------------------------

    forecast_df["total_cost"] = (

        forecast_df["salary_cost"]

        + forecast_df["recruitment_cost"]

        + forecast_df["contractor_cost"]

        + forecast_df["overtime_cost"]

        + forecast_df["investment_cost"]
    )

    # -------------------------
    # ROUNDING
    # -------------------------

    financial_columns = [

        "salary_cost",
        "recruitment_cost",
        "contractor_cost",
        "overtime_cost",
        "total_cost"
    ]

    forecast_df[financial_columns] = (

        forecast_df[financial_columns]

        .round(2)
    )

    return forecast_df