import pandas as pd
from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------------
# AVAILABLE SUPPLY
# -----------------------------------

def calculate_available_supply(

    forecast_df,
    supply_df,

):

    # -----------------------------------
    # BUILD FORECAST TIMELINE
    # -----------------------------------

    supply_projection_df = forecast_df[
        ["date", "queue"]
    ].copy()

    supply_projection_df = (
        supply_projection_df
        .drop_duplicates()
        .sort_values(
            ["queue", "date"]
        )
    )

    supply_projection_df[
        "available_supply"
    ] = 0.0

    supply_projection_df[
        "structural_attrition"
    ] = 0.0

    supply_projection_df[
        "manual_attrition"
    ] = 0.0

    supply_projection_df[
        "total_attrition"
    ] = 0.0

    supply_projection_df[
        "attrition"
    ] = 0.0

    supply_projection_df[
        "new_hires"
    ] = 0.0
    
    # -----------------------------------
    # PROCESS EACH QUEUE
    # -----------------------------------

    for queue in (
        supply_projection_df["queue"]
        .unique()
    ):

        queue_mask = (
            supply_projection_df["queue"]
            == queue
        )

        queue_rows = (
            supply_projection_df[
                queue_mask
            ]
        )

        opening_fte_match = forecast_df.loc[

            forecast_df["queue"]
            == queue,

            "default_opening_fte"
        ]

        attrition_match = forecast_df.loc[

            forecast_df["queue"]
            == queue,

            "default_attrition"
        ]

        if attrition_match.empty:

            raise ValueError(

                f"No attrition configured for queue: {queue}"
            )

        annual_attrition_rate = float(

            attrition_match.iloc[0]
        )

        if opening_fte_match.empty:

            raise ValueError(
                f"No opening FTE configured for queue: {queue}"
            )

        running_supply = float(
            opening_fte_match.iloc[0]
        )

        attrition_bank = 0.0

        # -----------------------------------
        # ITERATE FORECAST WEEKS
        # -----------------------------------

        for idx in queue_rows.index:

            current_date = (
                supply_projection_df.loc[
                    idx,
                    "date"
                ]
            )

            matching_events = supply_df[

                (supply_df["queue"] == queue)

                &

                (supply_df["date"] == current_date)
            ]

            if not matching_events.empty:

                manual_attrition = (

                    matching_events[
                        "attrition"
                    ].sum()
                )

                new_hires = (

                    matching_events[
                        "new_hires"
                    ].sum()
                )

            else:

                manual_attrition = 0

                new_hires = 0

            # -----------------------------------
            # STRUCTURAL ATTRITION
            # -----------------------------------

            weekly_attrition = (

                running_supply

                * annual_attrition_rate

                / 100

                / 52
            )

            attrition_bank += (
                weekly_attrition
            )

            structural_attrition = int(
                attrition_bank
            )

            attrition_bank -= (
                structural_attrition
            )

            total_attrition = (

                structural_attrition

                + manual_attrition
            )


            running_supply = (
                running_supply
                - total_attrition
                + new_hires
            )

            supply_projection_df.loc[
                idx,
                "available_supply"
            ] = round(
                running_supply,
                2
            )

            supply_projection_df.loc[
                idx,
                "structural_attrition"
            ] = structural_attrition

            supply_projection_df.loc[
                idx,
                "manual_attrition"
            ] = manual_attrition

            supply_projection_df.loc[
                idx,
                "total_attrition"
            ] = total_attrition
                        
            supply_projection_df.loc[
                idx,
                "attrition"
            ] = total_attrition            

            supply_projection_df.loc[
                idx,
                "new_hires"
            ] = new_hires

    return supply_projection_df


# -----------------------------------
# PRODUCTIVE SUPPLY
# -----------------------------------

def calculate_productive_supply(

    forecast_df,
    supply_df,
    ramp_df

):

    forecast_df["productive_supply"] = 0.0

    # -------------------------
    # ITERATE FORECAST ROWS
    # -------------------------

    for i in range(len(forecast_df)):

        current_week = forecast_df.loc[
            i,
            "date"
        ]

        current_queue = forecast_df.loc[
            i,
            "queue"
        ]

        # ---------------------
        # BASE SUPPLY
        # ---------------------

        base_supply = forecast_df.loc[
            i,
            "available_supply"
        ]

        productive_supply = base_supply

        # ---------------------
        # FIND HISTORICAL HIRES
        # ---------------------

        queue_supply = supply_df[

            supply_df["queue"]
            == current_queue
        ]

        for j in range(len(queue_supply)):

            hire_week = queue_supply.iloc[j][
                "date"
            ]

            new_hires = queue_supply.iloc[j][
                "new_hires"
            ]

            # -----------------
            # WEEKS SINCE HIRE
            # -----------------

            weeks_since_start = (

                (
                    current_week
                    - hire_week
                ).days // 7
            ) + 1

            # -----------------
            # APPLY RAMP
            # -----------------

            if (
                weeks_since_start > 0
                and new_hires > 0
            ):

                ramp_match = ramp_df[

                    (ramp_df["queue"] == current_queue)

                    &

                    (
                        ramp_df["week_since_start"]
                        == weeks_since_start
                    )
                ]

                if not ramp_match.empty:

                    ramp_factor = (
                        ramp_match.iloc[0][
                            "productivity"
                        ]
                    )

                else:

                    ramp_factor = 1

                productivity_loss = (

                    new_hires
                    * (1 - ramp_factor)
                )

                productive_supply -= (
                    productivity_loss
                )

        # ---------------------
        # SAVE RESULT
        # ---------------------

        forecast_df.loc[
            i,
            "productive_supply"
        ] = round(
            productive_supply,
            2
        )

    return forecast_df

# -----------------------------------
# GAP ANALYSIS
# -----------------------------------

def calculate_fte_gap(

    forecast_df

):

    forecast_df["fte_gap"] = (

        forecast_df["productive_supply"]

        - forecast_df["gross_requirement"]

    ).round(2)

    return forecast_df