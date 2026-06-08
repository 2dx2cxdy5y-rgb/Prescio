import pandas as pd

# -----------------------------
# STAFFING CALCULATIONS
# -----------------------------

def calculate_erlang_uplift(

    interval_volume,
    aht_seconds,
    service_level,
    answer_time,
    occupancy

):

    # -------------------------
    # TRAFFIC INTENSITY
    # -------------------------

    erlangs = (

        interval_volume
        * aht_seconds

    ) / 1800

    # -------------------------
    # BASE QUEUE PRESSURE
    # -------------------------

    occupancy_pressure = (

        occupancy - 0.7

    ) * 1.5

    occupancy_pressure = max(
        occupancy_pressure,
        0
    )

    # -------------------------
    # SLA PRESSURE
    # -------------------------

    sla_pressure = (
        service_level / 100
    ) * 0.15

    # -------------------------
    # ANSWER SPEED PRESSURE
    # -------------------------

    speed_pressure = max(

        (
            30 - answer_time
        ) / 100,

        0
    )

    # -------------------------
    # VOLUME VOLATILITY
    # -------------------------

    volume_pressure = 1 / (
        max(erlangs, 1) ** 0.5
    )

    # -------------------------
    # TOTAL UPLIFT
    # -------------------------

    uplift = (

        1

        + occupancy_pressure

        + sla_pressure

        + speed_pressure

        + volume_pressure
    )

    return uplift

def calculate_staffing_requirements(
    forecast_df
):

    # -------------------------
    # INITIALISE
    # -------------------------

    forecast_df["workload_hours"] = 0.0

    forecast_df["net_requirement"] = 0.0

    forecast_df["gross_requirement"] = 0.0

    # -------------------------
    # CALL WORK
    # -------------------------

    call_mask = (
        forecast_df["work_type"]
        == "call"
    )

    forecast_df.loc[
        call_mask,
        "workload_hours"
    ] = (

        forecast_df.loc[
            call_mask,
            "resolved_forecast"
        ]

        * forecast_df.loc[
            call_mask,
            "effective_aht"
        ]

    ) / 3600

    base_call_requirement = (

        forecast_df.loc[
            call_mask,
            "workload_hours"
        ]

        / (

            forecast_df.loc[
                call_mask,
                "effective_productive_hours"
            ]

            * forecast_df.loc[
                call_mask,
                "occupancy"
            ]
        )
    )

    # -------------------------
    # AVERAGE INTERVAL VOLUME
    # -------------------------

    forecast_df.loc[
        call_mask,
        "average_interval_volume"
    ] = (

        forecast_df.loc[
            call_mask,
            "resolved_forecast"
        ]

        / (

            forecast_df.loc[
                call_mask,
                "weekly_open_hours"
            ]

            * 2
        )
    )

    # -------------------------
    # ERLANG UPLIFT
    # -------------------------

    forecast_df.loc[
        call_mask,
        "erlang_uplift"
    ] = forecast_df.loc[
        call_mask
    ].apply(

        lambda row:

        calculate_erlang_uplift(

            row[
                "average_interval_volume"
            ],

            row[
                "effective_aht"
            ],

            row[
                "target_service_level"
            ],

            row[
                "target_answer_seconds"
            ],

            row[
                "occupancy"
            ]
        ),

        axis=1
    )

    # -------------------------
    # FINAL REQUIREMENT
    # -------------------------

    forecast_df.loc[
        call_mask,
        "net_requirement"
    ] = (

        base_call_requirement

        * forecast_df.loc[
            call_mask,
            "erlang_uplift"
        ]
    )

    # -------------------------
    # WORKLOAD
    # -------------------------

    workload_mask = (
        forecast_df["work_type"]
        == "workload"
    )

    forecast_df.loc[
        workload_mask,
        "workload_hours"
    ] = (

        forecast_df.loc[
            workload_mask,
            "resolved_forecast"
        ]

        * forecast_df.loc[
            workload_mask,
            "effective_aht"
        ]

    ) / 3600

    forecast_df.loc[
        workload_mask,
        "net_requirement"
    ] = (

        forecast_df.loc[
            workload_mask,
            "workload_hours"
        ]

        / (

            forecast_df.loc[
                workload_mask,
                "effective_productive_hours"
            ]

            * forecast_df.loc[
                workload_mask,
                "occupancy"
            ]
        )
    )

    # -------------------------
    # CHAT
    # -------------------------

    chat_mask = (
        forecast_df["work_type"]
        == "chat"
    )

    forecast_df.loc[
        chat_mask,
        "workload_hours"
    ] = (

        forecast_df.loc[
            chat_mask,
            "resolved_forecast"
        ]

        * forecast_df.loc[
            chat_mask,
            "effective_aht"
        ]

    ) / (

        3600

        * forecast_df.loc[
            chat_mask,
            "concurrency"
        ]
    )

    forecast_df.loc[
        chat_mask,
        "net_requirement"
    ] = (

        forecast_df.loc[
            chat_mask,
            "workload_hours"
        ]

        / (

            forecast_df.loc[
                chat_mask,
                "effective_productive_hours"
            ]

            * forecast_df.loc[
                chat_mask,
                "occupancy"
            ]
        )
    )

    # -------------------------
    # GROSS REQUIREMENT
    # -------------------------

    forecast_df["gross_requirement"] = (
        forecast_df["net_requirement"]
    )

    # -------------------------
    # ROUNDING
    # -------------------------

    rounding_columns = [

        "workload_hours",
        "net_requirement",
        "gross_requirement"
    ]

    for col in rounding_columns:

        forecast_df[col] = (
            forecast_df[col]
            .round(2)
        )

    return forecast_df