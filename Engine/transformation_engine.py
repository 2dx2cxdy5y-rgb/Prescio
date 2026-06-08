import pandas as pd
from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------
# APPLY BENEFITS
# -----------------------------

def apply_transformation_benefits(

    forecast_df,
    portfolio_df
):

    forecast_df = forecast_df.copy()

    # -------------------------
    # INITIALISE COLUMNS
    # -------------------------

    percentage_columns = [

        "ai_deflection",
        "demand_change",
        "productivity_gain"
    ]

    operational_columns = [

        "aht_change",
        "occupancy_change",
        "shrinkage_change"
    ]

    for col in percentage_columns + operational_columns:

        forecast_df[col] = 0.0
    
    
    # -------------------------
    # APPLY EACH PROGRAMME
    # -------------------------

    for _, row in portfolio_df.iterrows():

        queue = str(
            row["queue"]
        ).strip().lower()

        start_date = row["start_date"]

        delay_weeks = int(
            row.get(
                "delay_weeks",
                0
            )
        )

        start_date = (

            start_date

            + pd.Timedelta(
                weeks=delay_weeks
            )
        )
        
        end_date = row["end_date"]

        # ---------------------
        # BUILD ACTIVE MASK
        # ---------------------

        active_mask = (

            forecast_df["queue"]
            == queue
        )

        active_mask &= (

            forecast_df["date"]
            >= start_date
        )

        # ---------------------
        # OPTIONAL END DATE
        # ---------------------

        if pd.notna(end_date):

            active_mask &= (

                forecast_df["date"]
                <= end_date
            )

        # ---------------------
        # APPLY % BENEFITS
        # ---------------------

        for col in percentage_columns:

            benefit_value = (

                float(
                    row.get(col, 0)
                ) / 100
            )

            forecast_df.loc[
                active_mask,
                col
            ] += benefit_value

        # ---------------------
        # APPLY OPERATIONAL
        # ---------------------

        for col in operational_columns:

            benefit_value = float(
                row.get(col, 0)
            )

            forecast_df.loc[
                active_mask,
                col
            ] += benefit_value

        # -------------------------
        # APPLY AHT CHANGE
        # -------------------------

        forecast_df["effective_aht"] = (

            forecast_df["aht_seconds"]

            + forecast_df["aht_change"]
        )

        forecast_df["effective_aht"] = (

            forecast_df["effective_aht"]
            .clip(lower=60)
        )

        # -------------------------
        # APPLY OCCUPANCY CHANGE
        # -------------------------

        forecast_df["occupancy"] = (

            forecast_df["occupancy"]

            + (
                forecast_df[
                    "occupancy_change"
                ] / 100
            )
        )

        forecast_df["occupancy"] = (

            forecast_df["occupancy"]
            .clip(
                lower=0.50,
                upper=0.99
            )
        )

        # -------------------------
        # APPLY SHRINKAGE CHANGE
        # -------------------------

        forecast_df["shrinkage"] = (

            forecast_df["shrinkage"]

            + (
                forecast_df[
                    "shrinkage_change"
                ] / 100
            )
        )

        forecast_df["shrinkage"] = (

            forecast_df["shrinkage"]
            .clip(
                lower=0.0,
                upper=0.60
            )
        )

    return forecast_df