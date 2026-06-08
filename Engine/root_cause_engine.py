# =========================================================
# ROOT CAUSE ENGINE
# =========================================================

def identify_root_causes(

    insight,
    forecast_df
):

    root_causes = []

    queue = insight.queue

    if not queue:

        return root_causes

    queue_df = forecast_df[

        forecast_df["queue"]
        == queue
    ]

    if queue_df.empty:

        return root_causes

    # -----------------------------------------------------
    # DEMAND GROWTH
    # -----------------------------------------------------

    avg_demand_change = (
        queue_df[
            "demand_change"
        ].mean()
    )

    if avg_demand_change > 0.05:

        root_causes.append(
            "Elevated demand growth"
        )

    # -----------------------------------------------------
    # AHT PRESSURE
    # -----------------------------------------------------

    avg_aht_change = (
        queue_df[
            "aht_change"
        ].mean()
    )

    if avg_aht_change > 0.05:

        root_causes.append(
            "Increasing handling time"
        )

    # -----------------------------------------------------
    # SHRINKAGE
    # -----------------------------------------------------

    avg_shrinkage = (
        queue_df[
            "shrinkage"
        ].mean()
    )

    if avg_shrinkage > 0.35:

        root_causes.append(
            "High shrinkage levels"
        )

    # -----------------------------------------------------
    # OCCUPANCY
    # -----------------------------------------------------

    avg_occupancy = (
        queue_df[
            "occupancy"
        ].mean()
    )

    if avg_occupancy > 0.9:

        root_causes.append(
            "Excessive occupancy pressure"
        )

    return root_causes