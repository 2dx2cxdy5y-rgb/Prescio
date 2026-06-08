def determine_primary_driver(
    diagnostic
):

    demand_growth = diagnostic[
        "demand_growth"
    ]

    peak_gap = diagnostic[
        "peak_gap"
    ]

    ai = diagnostic[
        "max_ai_deflection"
    ]

    productivity = diagnostic[
        "max_productivity"
    ]

    budget = diagnostic[
        "budget_variance"
    ]

    if peak_gap < -20:

        if demand_growth > 10:

            return (
                "demand_growth"
            )

        if ai < 5 and productivity < 5:

            return (
                "transformation_gap"
            )

        return (
            "workforce_shortfall"
        )

    if budget < -20:

        return (
            "budget_constraint"
        )

    return (
        "stable"
    )