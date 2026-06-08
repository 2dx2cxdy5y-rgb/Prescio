import pandas as pd

import numpy as np

import os

from Engine.dataset_registry import (
    DATASETS
)

from Engine.data_ingestion_engine import (
    load_historical_operational_data
)

from Engine.logging_engine import (
    log_info
)

from prophet import Prophet

from Engine.regime_engine import (

    REGIMES,

    REGIME_LEVELS,

    get_next_regime
)

from Engine.profile_config_engine import (
    load_forecast_profiles
)

from Engine.forecast_freeze_engine import (
    archive_forecast_snapshot
)



# -----------------------------------
# FORECAST ENGINE
# -----------------------------------

def generate_baseline_forecast(

    profile="Operational"

):

    log_info(
        "Generating baseline forecast..."
    )

    # -----------------------------------
    # FORECAST SOURCE CONFIGURATION
    # -----------------------------------

    forecast_config_df = pd.read_csv(

        DATASETS[
            "forecast_configuration"
        ]["path"]
    )

    forecast_source = (

        forecast_config_df.loc[
            0,
            "forecast_source"
        ]
    )

#    forecast_offset_weeks = int(
#
 #       forecast_config_df.loc[
  #          0,
   #         "forecast_offset_weeks"
#        ]
#    )
#
#    forecast_horizon_weeks = int(
#
#        forecast_config_df.loc[
#            0,
#            "forecast_horizon_weeks"
#        ]
#    )

    queue_forecast_config_df = pd.read_csv(

        DATASETS[
            "forecast_queue_config"
        ]["path"]
    )

    generated_queues = (

        queue_forecast_config_df.loc[

            queue_forecast_config_df[
                "forecast_source"
            ] == "Generated",

            "queue"
        ]

        .astype(str)

        .str.strip()

        .tolist()
    )

    imported_queues = (

        queue_forecast_config_df.loc[

            queue_forecast_config_df[
                "forecast_source"
            ] == "Imported",

            "queue"
        ]

        .astype(str)

        .str.strip()

        .tolist()
    )

    print(
        "IMPORTED QUEUES:",
        imported_queues
    )



    print(
        "GENERATED QUEUES:",
        generated_queues
    )

    print(

        "QUEUE CONFIG LOADED",

        len(queue_forecast_config_df)
    )

    if forecast_source == "Hybrid":

        print(
            "HYBRID MODE ACTIVE"
        )

        for _, row in (

            queue_forecast_config_df

            .iterrows()
        ):

            log_info(

                f"{row['queue']} -> "

                f"{row['forecast_source']}"
            )




    log_info(

        f"Forecast source: "
        f"{forecast_source}"
    )

    # -----------------------------------
    # IMPORTED FORECAST MODE
    # -----------------------------------

    if forecast_source == "Hybrid":

        log_info(

            "Hybrid forecast mode selected."
        )

    if forecast_source in [

        "Imported"
    ]:

        log_info(
            "Using imported forecast."
        )

        imported_forecast_df = pd.read_csv(

            DATASETS[
                "imported_forecast"
            ]["path"]
        )

        imported_forecast_df["date"] = pd.to_datetime(

            imported_forecast_df["date"],

            format="%d/%m/%Y",

            errors="raise"
            
        )

        imported_forecast_df["date_display"] = (

            imported_forecast_df["date"]

            .dt.strftime("%d %b %Y")
        )

        imported_forecast_df["upper_bound"] = (

            imported_forecast_df["demand"]
        )

        imported_forecast_df["lower_bound"] = (

            imported_forecast_df["demand"]
        )

        imported_forecast_df["date"] = (

            imported_forecast_df["date"]

            .dt.strftime("%d/%m/%Y")
        )

        imported_forecast_df = (

            imported_forecast_df[

                [
                    "date",
                    "date_display",
                    "upper_bound",
                    "lower_bound",
                    "queue",
                    "demand"
                ]
            ]
        )

        imported_forecast_df.to_csv(

            DATASETS[
                "baseline_forecast"
            ]["path"],

            index=False
        )

        log_info(
            "Imported forecast loaded."
        )

        return

    # -----------------------------------
    # LOAD FORECAST PROFILES
    # -----------------------------------

    FORECAST_PROFILES = (
        load_forecast_profiles()
    )

    profile_config = FORECAST_PROFILES[
        profile
    ]

    residual_scale = profile_config[
        "residual_scale"
    ]

    trend_strength = profile_config[
        "trend_strength"
    ]

    seasonality_strength = profile_config[
        "seasonality_strength"
    ]

    enable_regimes = profile_config[
        "enable_regimes"
    ]

    positive_bias = profile_config.get(
        "positive_bias",
        0
    )

    negative_bias = profile_config.get(
        "negative_bias",
        0
    )

    # -----------------------------------
    # LOAD NORMALISED HISTORY
    # -----------------------------------

    historical_df = (
        load_historical_operational_data()
    )

    # -----------------------------------
    # DATE FORMATTING
    # -----------------------------------

    # -----------------------------------
    # LOAD HISTORICAL ADJUSTMENTS
    # -----------------------------------

    adjustments_df = pd.read_csv(

        DATASETS[
            "historical_adjustments"
        ]["path"]
    )

    # -----------------------------------
    # DATE FORMATTING
    # -----------------------------------

    adjustments_df["start_date"] = pd.to_datetime(

        adjustments_df["start_date"],

        dayfirst=True,

        errors="coerce"
    )

    adjustments_df["end_date"] = pd.to_datetime(

        adjustments_df["end_date"],

        dayfirst=True,

        errors="coerce"
    )

    # -----------------------------------
    # SORT DATA
    # -----------------------------------

    historical_df = (

        historical_df

        .sort_values(
            by=["queue", "date"]
        )
    )

    # -----------------------------------
    # FORECAST OUTPUT
    # -----------------------------------

    forecast_output = []

    # -----------------------------------
    # PROCESS EACH QUEUE
    # -----------------------------------

    queues = historical_df[
        "queue"
    ].unique()

    for queue in queues:

        log_info(
            f"Forecasting queue: {queue}"
        )

        queue_df = historical_df[

            historical_df["queue"]
            == queue

        ].copy()

        queue_df = (
            queue_df.sort_values(
                by="date"
            )
        )

        queue_df["historical_demand"] = (

            queue_df[
                "historical_demand"
            ]

            .astype(float)
        )

        # -----------------------------------
        # APPLY FORECAST CONDITIONING
        # -----------------------------------

        queue_adjustments = adjustments_df[

            adjustments_df["queue"]
            == queue
        ]

        for _, adjustment in queue_adjustments.iterrows():
            
            adjustment_action = adjustment[
                "adjustment_action"
            ]


            mask = (

                (queue_df["date"] >= adjustment["start_date"])

                &

                (queue_df["date"] <= adjustment["end_date"])
            )

            # -----------------------------
            # EXCLUDE ANOMALY
            # -----------------------------

            if adjustment_action == "exclude":

                rolling_average = (

                    queue_df[
                        "historical_demand"
                    ]

                    .rolling(
                        window=4,
                        center=True
                    )

                    .mean()
                )

                replacement_value = (

                    rolling_average.mean()
                )

                queue_df.loc[

                    mask,

                    "historical_demand"

                ] = replacement_value


            # -----------------------------
            # SMOOTH VOLATILITY
            # -----------------------------

            elif adjustment_action == "smooth":

                smoothed_values = (

                    queue_df[
                        "historical_demand"
                    ]

                    .rolling(
                        window=4,
                        center=True
                    )

                    .mean()
                )

                queue_df.loc[

                    mask,

                    "historical_demand"

                ] = smoothed_values



        # -----------------------------------
        # PREPARE PROPHET DATA
        # -----------------------------------

        prophet_df = pd.DataFrame({

            "ds": queue_df["date"],

            "y": queue_df[
                "historical_demand"
            ]
        })

        # -----------------------------------
        # BUILD MODEL
        # -----------------------------------

        model = Prophet(

            yearly_seasonality=True,

            weekly_seasonality=True,

            daily_seasonality=False,

            changepoint_prior_scale=0.15,

            seasonality_prior_scale=20,

            seasonality_mode="additive"
        )

        model.add_seasonality(

            name="monthly",

            period=30.5,

            fourier_order=5
        )

        # -----------------------------------
        # FIT MODEL
        # -----------------------------------

        model.fit(
            prophet_df
        )

        # -----------------------------------
        # FUTURE HORIZON
        # -----------------------------------

        future = model.make_future_dataframe(

            periods=52,

            freq="W-MON"
        )

        # -----------------------------------
        # GENERATE FORECAST
        # -----------------------------------

        forecast = model.predict(
            future
        )

        # -----------------------------------
        # HISTORICAL RESIDUAL ANALYSIS
        # -----------------------------------

        historical_forecast = forecast.iloc[
            :len(prophet_df)
        ].copy()

        historical_actuals = prophet_df[
            "y"
        ].reset_index(drop=True)

        historical_prediction = historical_forecast[
            "yhat"
        ].reset_index(drop=True)

        historical_residuals = (

            historical_actuals

            - historical_prediction
        )

        # -----------------------------------
        # BASE FORECAST
        # -----------------------------------

        base_forecast = (

            forecast["yhat"]

            .clip(lower=0)

            .reset_index(drop=True)
        )

        forecast_mean = np.mean(
            base_forecast
        )

        forecast_values = (

            forecast_mean +

            (
                base_forecast
                - forecast_mean
            )

            * trend_strength
        )

        forecast_values = pd.Series(
            forecast_values
        )

        # -----------------------------------
        # LONG-RUN MEAN REVERSION
        # -----------------------------------

        recent_mean = (

            queue_df[
                "historical_demand"
            ]

            .tail(26)

            .mean()
        )

        reversion_strength = 0.18

        future_start = len(prophet_df)

        future_steps = len(forecast_values) - future_start

        for i in range(future_steps):

            idx = future_start + i

            reversion_weight = (

                (i + 1) / future_steps
            )

            forecast_values.iloc[idx] = (

                forecast_values.iloc[idx]

                * (1 - reversion_strength * reversion_weight)

                +

                recent_mean

                * (reversion_strength * reversion_weight)
            )

        # -----------------------------------
        # RESIDUAL VOLATILITY REPLAY
        # -----------------------------------

        future_start = len(prophet_df)

        future_length = (

            len(forecast_values)

            - future_start
        )

        sampled_residuals = np.random.choice(

            historical_residuals,

            size=future_length,

            replace=True
        )

        # -----------------------------------
        # DE-BIAS RESIDUALS
        # -----------------------------------

        sampled_residuals = (

            sampled_residuals

            - np.mean(sampled_residuals)
        )

        # Scale residual influence

        sampled_residuals = (

            sampled_residuals

            * residual_scale

            * seasonality_strength
        )

        # Apply only to future horizon

        forecast_values.iloc[
            future_start:
        ] = (

            forecast_values.iloc[
                future_start:
            ]

            + sampled_residuals
        )

        forecast_values = forecast_values.clip(
            lower=0
        )

        forecast_values = (

            forecast_values

            * (

                1

                + positive_bias

                + negative_bias
            )
        )

        # -----------------------------------
        # FORECAST CONFIDENCE BOUNDS
        # -----------------------------------

        forecast_std = (

            queue_df[
                "historical_demand"
            ]

            .std()
        )

        upper_forecast = (

            forecast_values

            + (forecast_std * 0.75)
        )

        lower_forecast = (

            forecast_values

            - (forecast_std * 0.75)
        )

        # -----------------------------------
        # FORECAST DATES
        # -----------------------------------

        last_date = (
            queue_df["date"].max()
        )

        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(
                weeks=1
            ),
            periods=52,
            freq="W-MON"
        )

        # -----------------------------------
        # FUTURE FORECAST ONLY
        # -----------------------------------

        forecast_values = forecast_values.iloc[
            future_start:
        ].reset_index(drop=True)

        upper_forecast = upper_forecast.iloc[
            future_start:
        ].reset_index(drop=True)

        lower_forecast = lower_forecast.iloc[
            future_start:
        ].reset_index(drop=True)

        # -----------------------------------
        # BUILD OUTPUT
        # -----------------------------------

        for (

            forecast_date,

            forecast_value,

            upper_value,

            lower_value

        ) in zip(

            forecast_dates,

            forecast_values,

            upper_forecast,

            lower_forecast
        ):

            print(
                f"""
                QUEUE: {queue}
                DATE: {forecast_date}
                VALUE: {round(forecast_value, 0)}
                """
            )

            forecast_output.append({

                "date": forecast_date.strftime(
                    "%d/%m/%Y"
                ),

                "date_display": forecast_date.strftime(
                    "%d %b %Y"
                ),
                "upper_bound": int(
                    round(upper_value)
                ),

                "lower_bound": int(
                    round(lower_value)
                ),

                "queue": queue,

                "demand": int(
                    round(forecast_value)
                )
            })

    # -----------------------------------
    # OUTPUT DATAFRAME
    # -----------------------------------

    forecast_df = pd.DataFrame(
        forecast_output
    )

    if forecast_source == "Hybrid":

        print(
            "BUILDING HYBRID FORECAST"
        )

        imported_forecast_df = pd.read_csv(

            DATASETS[
                "imported_forecast"
            ]["path"]
        )  
        
        print(

            "IMPORTED ROWS:",

            len(
                imported_forecast_df
            )
        )

        imported_forecast_df["date"] = pd.to_datetime(

            imported_forecast_df["date"],
            
            format="%d/%m/%Y",
            
            errors="raise"
            

        )

        imported_forecast_df["date_display"] = (

            imported_forecast_df["date"]

            .dt.strftime(
                "%d %b %Y"
            )
        )
 
        imported_forecast_df["upper_bound"] = (

            imported_forecast_df[
                "demand"
            ]
        ) 

        imported_forecast_df["lower_bound"] = (

            imported_forecast_df[
                "demand"
            ]
        )

        imported_forecast_df["date"] = (

            imported_forecast_df["date"]

            .dt.strftime(
                "%d/%m/%Y"
            )
        )

        imported_forecast_df = (

            imported_forecast_df[

                [
                    "date",
                    "date_display",
                    "upper_bound",
                    "lower_bound",
                    "queue",
                    "demand"
                ]
            ]
        )

        print(

            "IMPORTED COLUMNS:",

            imported_forecast_df.columns.tolist()
        )


        # -----------------------------------
        # FILTER GENERATED QUEUES
        # -----------------------------------

        forecast_df = (

            forecast_df[

                forecast_df["queue"]

                .astype(str)

                .str.strip()

                .isin(generated_queues)

            ]

            .copy()
        )

        # -----------------------------------
        # FILTER IMPORTED QUEUES
        # -----------------------------------

        imported_forecast_df = (

            imported_forecast_df[

                imported_forecast_df["queue"]

                .astype(str)

                .str.strip()

                .isin(imported_queues)

            ]

            .copy()
        )

        hybrid_forecast_df = pd.concat(

            [

                forecast_df,

                imported_forecast_df

            ],

            ignore_index=True
        )

        print(

            "GENERATED ROWS:",

            len(
                forecast_df
            )
        )

        print(

            "HYBRID ROWS:",

            len(
                hybrid_forecast_df
            )
        )

        print(

            "HYBRID QUEUES:",

            sorted(

                hybrid_forecast_df[
                    "queue"
                ]

                .astype(str)

                .str.strip()

                .unique()
            )
        )



                
    # -----------------------------------
    # SAVE BASELINE FORECAST
    # -----------------------------------

    # -----------------------------------
    # DUPLICATE VALIDATION
    # -----------------------------------

    if forecast_source == "Hybrid":

        validation_df = (

            hybrid_forecast_df
        )

    else:

        validation_df = (

            forecast_df
        )

    duplicates = (

        validation_df

        .duplicated(

            subset=[

                "date",

                "queue"

            ],

            keep=False
        )
    )

    if duplicates.any():

        print(

            "DUPLICATE FORECAST ROWS DETECTED"
        )

        print(

            validation_df[
                duplicates
            ]
        )

        raise ValueError(

            "Duplicate queue/date combinations detected."
        )
                
    if forecast_source == "Hybrid":

        archive_forecast_snapshot(
            hybrid_forecast_df
        )

        hybrid_forecast_df.to_csv(

            DATASETS[
                "baseline_forecast"
            ]["path"],

            index=False
        )

    else:

        archive_forecast_snapshot(
            forecast_df
        )

        forecast_df.to_csv(

            DATASETS[
                "baseline_forecast"
            ]["path"],

            index=False
        )


# -----------------------------------
# EXECUTION
# -----------------------------------

if __name__ == "__main__":

    selected_profile = os.getenv(

        "FORECAST_PROFILE",

        "Operational"
    )

    generate_baseline_forecast(

        profile=selected_profile
    )
