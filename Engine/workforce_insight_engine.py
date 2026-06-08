from Engine.insight_engine import (
    create_insight
)


def generate_workforce_insights(

    forecast_df

):

    insights = []

    # ---------------------------------
    # PROCESS EACH QUEUE
    # ---------------------------------

    queues = (
        forecast_df["queue"]
        .unique()
    )

    for queue in queues:

        queue_df = forecast_df[

            forecast_df["queue"]
            == queue
        ]

        # ---------------------------------
        # FIND WORST FTE GAP
        # ---------------------------------

        min_gap = (
            queue_df["fte_gap"]
            .min()
        )

        # ---------------------------------
        # CREATE STAFFING INSIGHT
        # ---------------------------------

        if min_gap < -20:

            severity = "critical"

        elif min_gap < -10:

            severity = "high"

        elif min_gap < -5:

            severity = "medium"

        else:

            severity = None

        if severity:

            insights.append(



                create_insight(

                    domain="workforce",

                    category="staffing_gap",

                    severity=severity,

                    headline=(
                        f"{queue} queue "
                        f"understaffed"
                    ),

                    summary=(
                        f"Worst projected "
                        f"FTE gap is "
                        f"{round(min_gap, 1)}."
                    ),

                    recommendation=(
                        "Increase staffing "
                        "or reduce shrinkage."
                    ),

                    metric="fte_gap",

                    metric_value=min_gap,

                    impact_type="fte",

                    impact_value=abs(min_gap),

                    queue=queue,

                    source_engine=(
                        "workforce_insight_engine"
                    ),

                    source_pipeline_step=(
                        "generate_workforce_insights"
                    ),

                    tags=[
                        "capacity",
                        "service_risk"
                    ]
                )
            )

    return insights