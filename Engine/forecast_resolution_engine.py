import pandas as pd

from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------------
# FORECAST RESOLUTION ENGINE
# -----------------------------------

def resolve_forecast_layers(

    forecast_df
):

    forecast_df = forecast_df.copy()

    # -----------------------------------
    # LOAD FORECAST LAYERS
    # -----------------------------------

    layers_df = pd.read_csv(

        DATASETS[
            "forecast_layers"
        ]["path"]
    )

    # -----------------------------------
    # ACTIVE LAYERS ONLY
    # -----------------------------------

    layers_df = layers_df[

        layers_df["active"] == True
    ]

    # -----------------------------------
    # SORT BY PRIORITY
    # -----------------------------------

    layers_df = layers_df.sort_values(
        by="priority"
    )

    # -----------------------------------
    # BASE FORECAST
    # -----------------------------------

    forecast_df[
        "base_layer"
    ] = (

        forecast_df[
            "demand"
        ].astype(float)
    )

    # -----------------------------------
    # GROWTH FORECAST
    # -----------------------------------

    forecast_df[
        "growth_layer"
    ] = (

        forecast_df[
            "base_layer"
        ].copy()
    )

    # -----------------------------------
    # SEASONALITY FORECAST
    # -----------------------------------

    forecast_df[
        "seasonality_layer"
    ] = (

        forecast_df[
            "growth_layer"
        ].copy()
    )

    # -----------------------------------
    # TRANSFORMATION FORECAST
    # -----------------------------------

    forecast_df[
        "transformation_layer"
    ] = (

        forecast_df[
            "seasonality_layer"
        ].copy()
    )

    # -----------------------------------
    # OPERATIONAL FORECAST
    # -----------------------------------

    forecast_df[
        "operational_layer"
    ] = (

        forecast_df[
            "transformation_layer"
        ].copy()
    )

    # -----------------------------------
    # RESOLVED FORECAST
    # -----------------------------------

    forecast_df[
        "resolved_forecast"
    ] = (

        forecast_df[
            "operational_layer"
        ].copy()
    )

    # -----------------------------------
    # EXECUTION LOG
    # -----------------------------------

    layer_execution_log = []

    # -----------------------------------
    # EXECUTE LAYERS
    # -----------------------------------

    for _, layer in layers_df.iterrows():

        layer_name = layer[
            "layer_name"
        ]

        layer_type = layer[
            "layer_type"
        ]

        compounding_mode = layer[
            "compounding_mode"
        ]

        # -----------------------------------
        # CUSTOMER GROWTH LAYER
        # -----------------------------------

        if layer_name == "customer_growth":

            growth_df = pd.read_csv(

                DATASETS[
                    "demand_drivers"
                ]["path"]
            )

            growth_df["start_date"] = pd.to_datetime(

                growth_df["start_date"],

                dayfirst=True,

                errors="coerce"
            )

            growth_df["end_date"] = pd.to_datetime(

                growth_df["end_date"],

                dayfirst=True,

                errors="coerce"
            )

            forecast_df["date"] = pd.to_datetime(

                forecast_df["date"],

                dayfirst=True,

                errors="coerce"
            )

            for _, driver in growth_df.iterrows():

                queue = driver["queue"]

                growth_rate = float(
                    driver["growth_rate"]
                )

                start_date = driver[
                    "start_date"
                ]

                end_date = driver[
                    "end_date"
                ]

                queue_mask = (

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

                impacted_rows = (
                    forecast_df.loc[
                        queue_mask
                    ]
                )

                total_periods = len(
                    impacted_rows
                )

                if total_periods == 0:

                    continue

                growth_curve = [

                    1 + (
                        growth_rate
                        * (
                            period
                            / total_periods
                        )
                    )

                    for period in range(
                        total_periods
                    )
                ]

                forecast_df.loc[

                    queue_mask,

                    "growth_layer"

                ] = (

                    forecast_df.loc[
                        queue_mask,
                        "growth_layer"
                    ].values

                    * growth_curve
                )

            forecast_df[
                "seasonality_layer"
            ] = (

                forecast_df[
                    "growth_layer"
                ].copy()
            )

            forecast_df[
                "transformation_layer"
            ] = (

                forecast_df[
                    "seasonality_layer"
                ].copy()
            )

            forecast_df[
                "operational_layer"
            ] = (

                forecast_df[
                    "transformation_layer"
                ].copy()
            )

        # -----------------------------------
        # TRANSFORMATION LAYER
        # -----------------------------------

        if layer_name == "transformation":

            transformation_df = pd.read_csv(

                DATASETS[
                    "transformation_benefits"
                ]["path"]
            )

            if not transformation_df.empty:

                transformation_df["queue"] = (

                    transformation_df["queue"]

                    .astype(str)

                    .str.strip()

                    .str.lower()
                )

                transformation_df["date"] = pd.to_datetime(

                    transformation_df["date"],

                    dayfirst=True,

                    errors="coerce"
                )

                for _, transformation in (

                    transformation_df.iterrows()
                ):

                    queue = transformation["queue"]

                    transformation_date = (
                        transformation["date"]
                    )

                    ai_deflection = float(

                        transformation.get(
                            "ai_deflection",
                            0
                        )
                    )

                    demand_change = float(

                        transformation.get(
                            "demand_change",
                            0
                        )
                    )

                    transformation_mask = (

                        (forecast_df["queue"] == queue)

                        &

                        (
                            forecast_df["date"]
                            == transformation_date
                        )
                    )

                    future_mask = (

                        (forecast_df["queue"] == queue)

                        &

                        (
                            forecast_df["date"]
                            >= transformation_date
                        )
                    )

                    base_values = (

                        forecast_df.loc[
                            future_mask,
                            "operational_layer"
                        ]
                    )

                    # -----------------------------------
                    # PRESERVE VOLATILITY
                    # -----------------------------------

                    rolling_baseline = (
                        base_values.copy()
                    )

                    # -----------------------------------
                    # TRANSFORMATION IMPACT
                    # -----------------------------------

                    transformation_impact = (

                        (
                            rolling_baseline
                            * (ai_deflection / 100)
                        )

                        -

                        (
                            rolling_baseline
                            * (demand_change / 100)
                        )
                    )

                    # -----------------------------------
                    # APPLY STRATEGIC SHIFT
                    # -----------------------------------

                    forecast_df.loc[

                        future_mask,

                        "transformation_layer"

                    ] = (

                        base_values
                        - transformation_impact
                    )

            forecast_df[
                "operational_layer"
            ] = (

                forecast_df[
                    "transformation_layer"
                ].copy()
            )

        # -----------------------------------
        # SCENARIO LAYER
        # -----------------------------------

        if layer_name == "scenario":

            scenario_df = pd.read_csv(

                DATASETS[
                    "scenario_layers"
                ]["path"]
            )

            if not scenario_df.empty:

                scenario_df["queue"] = (

                    scenario_df["queue"]

                    .astype(str)

                    .str.strip()

                    .str.lower()
                )

                scenario_df["start_date"] = pd.to_datetime(

                    scenario_df["start_date"],

                    dayfirst=True,

                    errors="coerce"
                )

                scenario_df["end_date"] = pd.to_datetime(

                    scenario_df["end_date"],

                    dayfirst=True,

                    errors="coerce"
                )

                for _, scenario in (

                    scenario_df.iterrows()
                ):

                    queue = scenario["queue"]

                    start_date = (
                        scenario["start_date"]
                    )

                    end_date = (
                        scenario["end_date"]
                    )

                    impact_pct = float(

                        scenario.get(
                            "impact_pct",
                            0
                        )
                    )

                    scenario_mask = (

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

                    multiplier = (

                        1 + (impact_pct / 100)
                    )

                    forecast_df.loc[

                        scenario_mask,

                        "operational_layer"

                    ] *= multiplier

        # -----------------------------------
        # OPERATIONAL OVERLAY LAYER
        # -----------------------------------

        if layer_name == "operational_overlay":

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

                    start_date = overlay[
                        "start_date"
                    ]

                    end_date = overlay[
                        "end_date"
                    ]

                    overlay_type = overlay[
                        "overlay_type"
                    ]

                    adjustment_value = float(

                        overlay[
                            "adjustment_value"
                        ]
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

                    if overlay_type == "volume_pct":

                        forecast_df.loc[

                            overlay_mask,

                            "operational_layer"

                        ] *= (
                            1 + adjustment_value
                        )

        layer_execution_log.append({

            "layer": layer_name,

            "type": layer_type,

            "mode": compounding_mode
        })

    # -----------------------------------
    # FINAL RESOLVED FORECAST
    # -----------------------------------

    forecast_df[
        "resolved_forecast"
    ] = (

        forecast_df[
            "operational_layer"
        ].fillna(0)
    )

    return (

        forecast_df,

        layer_execution_log
    )