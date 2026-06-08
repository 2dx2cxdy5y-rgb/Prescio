def generate_queue_narrative(
    diagnostic
):

    queue = diagnostic["queue"]

    status = diagnostic["status"]

    demand_growth = diagnostic["demand_growth"]

    peak_gap = diagnostic["peak_gap"]

    peak_gap_date = diagnostic["peak_gap_date"]

    budget_variance = diagnostic["budget_variance"]

    ai = diagnostic["max_ai_deflection"]

    productivity = diagnostic["max_productivity"]

    if status == "critical":

        narrative = (

            f"{queue.title()} is projected to face "
            f"significant operational pressure. "

            f"Demand changes by {demand_growth:.1f}% "

            f"while workforce deficits peak at "
            f"{abs(peak_gap):.1f} FTE on "
            f"{peak_gap_date}. "

            f"Current transformation initiatives "
            f"deliver {ai:.1f}% AI deflection and "
            f"{productivity:.1f}% productivity "
            f"improvement, which is insufficient "
            f"to offset projected capacity gaps."
        )

    elif status == "warning":

        narrative = (

            f"{queue.title()} shows emerging "
            f"capacity pressure. Workforce gaps "
            f"remain manageable but should be "
            f"monitored closely."
        )

    else:

        narrative = (

            f"{queue.title()} remains operationally "
            f"stable with no material workforce or "
            f"demand risks currently projected."
        )

    return narrative