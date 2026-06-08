import pandas as pd

from Engine.dataset_registry import (
    DATASETS
)

from Engine.logging_engine import (
    log_info
)

# -----------------------------------
# FORECAST INTELLIGENCE ENGINE
# -----------------------------------

def generate_forecast_intelligence():

    log_info(
        "Generating forecast intelligence..."
    )

    # -----------------------------------
    # LOAD FORECAST
    # -----------------------------------

    forecast_df = pd.read_csv(

        DATASETS[
            "baseline_forecast"
        ]["path"]
    )

    # -----------------------------------
    # DATE FORMATTING
    # -----------------------------------

    forecast_df["date"] = pd.to_datetime(

        forecast_df["date"],

        dayfirst=True,

        errors="coerce"
    )

    # -----------------------------------
    # OUTPUT
    # -----------------------------------

    intelligence_output = []

    # -----------------------------------
    # PROCESS QUEUES
    # -----------------------------------

    queues = forecast_df[
        "queue"
    ].unique()

    for queue in queues:

        queue_df = forecast_df[

            forecast_df["queue"]
            == queue

        ].copy()

        queue_df = (
            queue_df.sort_values(
                by="date"
            )
        )

        # -----------------------------------
        # METRICS
        # -----------------------------------

        starting_demand = (
            queue_df["demand"]
            .iloc[0]
        )

        ending_demand = (
            queue_df["demand"]
            .iloc[-1]
        )

        demand_change = (
            (
                ending_demand
                - starting_demand
            )
            / starting_demand
        ) * 100

        volatility = (
            queue_df["demand"]
            .std()
        )

        confidence_width = (

            (
                queue_df[
                    "upper_bound"
                ]

                -

                queue_df[
                    "lower_bound"
                ]
            )

            .mean()
        )

        peak_demand = (
            queue_df["demand"]
            .max()
        )

        trough_demand = (
            queue_df["demand"]
            .min()
        )

        # -----------------------------------
        # TREND COMMENTARY
        # -----------------------------------

        if demand_change > 10:

            trend_comment = (
                "Demand is forecast to "
                "increase materially "
                "over the planning horizon."
            )

        elif demand_change > 3:

            trend_comment = (
                "Demand is forecast to "
                "increase moderately "
                "over the planning horizon."
            )

        elif demand_change < -10:

            trend_comment = (
                "Demand is forecast to "
                "decline materially "
                "over the planning horizon."
            )

        elif demand_change < -3:

            trend_comment = (
                "Demand is forecast to "
                "decline moderately "
                "over the planning horizon."
            )

        else:

            trend_comment = (
                "Demand is forecast to "
                "remain broadly stable."
            )

        # -----------------------------------
        # VOLATILITY COMMENTARY
        # -----------------------------------

        if volatility > 1500:

            volatility_comment = (
                "Forecast volatility is "
                "elevated, indicating "
                "higher operational uncertainty."
            )

        elif volatility > 800:

            volatility_comment = (
                "Forecast volatility is "
                "moderate, with periodic "
                "demand fluctuations expected."
            )

        else:

            volatility_comment = (
                "Forecast volatility remains "
                "relatively contained."
            )

        # -----------------------------------
        # CONFIDENCE COMMENTARY
        # -----------------------------------

        if confidence_width > 3000:

            confidence_comment = (
                "Forecast confidence ranges "
                "are wide, suggesting elevated "
                "scenario variability."
            )

        elif confidence_width > 1500:

            confidence_comment = (
                "Forecast confidence ranges "
                "indicate moderate uncertainty."
            )

        else:

            confidence_comment = (
                "Forecast confidence ranges "
                "remain relatively narrow."
            )

        # -----------------------------------
        # SEASONALITY COMMENTARY
        # -----------------------------------

        seasonal_variation = (
            peak_demand
            - trough_demand
        )

        if seasonal_variation > 4000:

            seasonal_comment = (
                "Pronounced seasonal demand "
                "patterns are visible."
            )

        elif seasonal_variation > 2000:

            seasonal_comment = (
                "Moderate seasonal demand "
                "variation is expected."
            )

        else:

            seasonal_comment = (
                "Limited seasonal variation "
                "is currently forecast."
            )

        # -----------------------------------
        # FINAL COMMENTARY
        # -----------------------------------

        commentary = " ".join([

            trend_comment,

            volatility_comment,

            confidence_comment,

            seasonal_comment
        ])

        intelligence_output.append({

            "queue": queue,

            "demand_change_pct": round(
                demand_change,
                1
            ),

            "volatility": round(
                volatility,
                0
            ),

            "confidence_width": round(
                confidence_width,
                0
            ),

            "commentary": commentary
        })

    # -----------------------------------
    # OUTPUT DATAFRAME
    # -----------------------------------

    intelligence_df = pd.DataFrame(
        intelligence_output
    )

    # -----------------------------------
    # SAVE OUTPUT
    # -----------------------------------

    intelligence_df.to_csv(

        "output/forecast_intelligence.csv",

        index=False
    )

    log_info(
        "Forecast intelligence generated."
    )


# -----------------------------------
# EXECUTION
# -----------------------------------

if __name__ == "__main__":

    generate_forecast_intelligence()