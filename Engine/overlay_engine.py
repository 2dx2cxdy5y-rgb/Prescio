import pandas as pd

from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------------
# APPLY OPERATIONAL OVERLAYS
# -----------------------------------

def apply_scenario_layers(

    forecast_df,
    layers_df=None
):

    forecast_df = forecast_df.copy()

    impact_log = []

    # -----------------------------------
    # LOAD OVERLAYS
    # -----------------------------------

    overlay_df = pd.read_csv(

        DATASETS[
            "demand_overlays"
        ]["path"]
    )

    if not overlay_df.empty:

        overlay_df["queue"] = (

            overlay_df["queue"]

            .astype(str)

            .str.strip()

            .str.lower()
        )

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

        for _, overlay in overlay_df.iterrows():

            queue = overlay["queue"]

            start_date = overlay["start_date"]

            end_date = overlay["end_date"]

            overlay_type = overlay["overlay_type"]

            adjustment_value = float(

                overlay["adjustment_value"]
            )

            overlay_mask = (

                (forecast_df["queue"] == queue)

                &

                (
                    forecast_df["date"]
                    >= start_date
                )

                &

                (
                    forecast_df["date"]
                    <= end_date
                )
            )

            before_total = (

                forecast_df.loc[
                    overlay_mask,
                    "resolved_demand"
                ]

                .sum()
            )

            # -----------------------------------
            # PERCENTAGE OVERLAY
            # -----------------------------------

            if overlay_type == "volume_pct":

                forecast_df.loc[

                    overlay_mask,

                    "resolved_demand"

                ] *= (
                    1 + adjustment_value
                )

            after_total = (

                forecast_df.loc[
                    overlay_mask,
                    "resolved_demand"
                ]

                .sum()
            )

            impact_log.append({

                "layer": f"Overlay - {queue}",

                "before": round(
                    before_total,
                    2
                ),

                "after": round(
                    after_total,
                    2
                ),

                "delta": round(
                    after_total - before_total,
                    2
                )
            })

    return (
        forecast_df,
        impact_log
    )