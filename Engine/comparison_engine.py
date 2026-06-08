import pandas as pd

from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------
# COMPARE SCENARIOS
# -----------------------------

def compare_scenarios(

    baseline_df,
    comparison_df
):

    # -----------------------------
    # FORECAST COLUMN DETECTION
    # -----------------------------

    baseline_forecast_column = (

        "resolved_forecast"

        if "resolved_forecast"
        in baseline_df.columns

        else "demand"
    )

    comparison_forecast_column = (

        "resolved_forecast"

        if "resolved_forecast"
        in comparison_df.columns

        else "demand"
    )

    # -----------------------------
    # COMPARISON RESULTS
    # -----------------------------

    comparison_results = {

        "Demand Delta": round(

            comparison_df[
                comparison_forecast_column
            ].sum()

            -

            baseline_df[
                baseline_forecast_column
            ].sum(),

            2
        ),

        "Gap Delta": round(

            comparison_df[
                "fte_gap"
            ].mean()

            -

            baseline_df[
                "fte_gap"
            ].mean(),

            2
        ),

    }

    return pd.DataFrame(

        comparison_results.items(),

        columns=[
            "Metric",
            "Delta"
        ]
    )