import pandas as pd


def generate_queue_diagnostics(
    forecast_df
):


    diagnostics = []

    queues = sorted(
        forecast_df["queue"]
        .dropna()
        .unique()
    )

    for queue in queues:

        queue_df = forecast_df[
            forecast_df["queue"] == queue
        ].copy()

        if queue_df.empty:
            continue

        peak_gap = (
            queue_df["fte_gap"]
            .min()
        )

        peak_gap_row = queue_df.loc[
            queue_df["fte_gap"].idxmin()
        ]

        peak_gap_date = (
            peak_gap_row["date_display"]
        )

        start_demand = (
            queue_df["demand"]
            .iloc[0]
        )

        end_demand = (
            queue_df["demand"]
            .iloc[-1]
        )

        demand_growth = (

            (
                end_demand
                -
                start_demand
            )

            /

            max(
                start_demand,
                1
            )

        ) * 100

        latest_gap = (
            queue_df["fte_gap"]
            .iloc[-1]
        )

        average_gap = (
            queue_df["fte_gap"]
            .mean()
        )

        max_gap = abs(
            queue_df["fte_gap"]
            .min()
        )

        max_ai_deflection = (
            queue_df[
                "ai_deflection"
            ].max()
        )

        max_productivity = (
            queue_df[
                "productivity_gain"
            ].max()
        )


        avg_budget_variance = (
            queue_df[
                "budget_variance"
            ].mean()
        )

        understaffed_periods = (
            queue_df[
                queue_df["fte_gap"] < 0
            ]
        )

        understaff_start = None

        if not understaffed_periods.empty:

            understaff_start = (
                understaffed_periods
                .iloc[0]["date_display"]
            )

        understaff_end = None

        if not understaffed_periods.empty:

            understaff_end = (
                understaffed_periods
                .iloc[-1]["date_display"]
            )

        understaff_weeks = len(
            understaffed_periods
        )

        overstaffed_periods = (
            queue_df[
                queue_df["fte_gap"] > 0
            ]
        )

        overstaff_start = None

        if not overstaffed_periods.empty:

            overstaff_start = (
                overstaffed_periods
                .iloc[0]["date_display"]
            )

        overstaff_end = None

        if not overstaffed_periods.empty:

            overstaff_end = (
                overstaffed_periods
                .iloc[-1]["date_display"]
            )

        overstaff_weeks = len(
            overstaffed_periods
        )

        peak_surplus = 0

        if not overstaffed_periods.empty:

            peak_surplus = (
                overstaffed_periods[
                    "fte_gap"
                ].max()
            )





        
        if peak_gap < -20:

            status = "critical"

        elif peak_gap < -5:

            status = "warning"

        else:

            status = "stable"
            
            
            
        diagnostics.append({

            "queue": queue,

            "status": status,

            "understaff_start":
                understaff_start,

            "understaff_end":
                understaff_end,

            "understaff_weeks":
                understaff_weeks,

            "overstaff_start":
                overstaff_start,

            "overstaff_end":
                overstaff_end,

            "overstaff_weeks":
                overstaff_weeks,

            "peak_surplus":
                round(
                    peak_surplus,
                    1
                ),

            "peak_gap":
                round(
                    peak_gap,
                    1
                ),

            "peak_gap_date":
                peak_gap_date,

            "demand_growth":
                round(
                    demand_growth,
                    1
                ),

            "latest_gap":
                round(
                    latest_gap,
                    1
                ),

            "average_gap":
                round(
                    average_gap,
                    1
                ),

            "max_gap":
                round(
                    max_gap,
                    1
                ),

            "max_ai_deflection":
                round(
                    max_ai_deflection * 100,
                    1
                ),

            "max_productivity":
                round(
                    max_productivity * 100,
                    1
                ),


            "budget_variance":
                round(
                    avg_budget_variance,
                    1
                ),
                
    
        })

    return diagnostics