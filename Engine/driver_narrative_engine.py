def generate_driver_narrative(
    diagnostic,
    driver
):

    queue = diagnostic["queue"].title()

    peak_gap = abs(
        diagnostic["peak_gap"]
    )

    understaff_start = (
        diagnostic["understaff_start"]
    )

    understaff_end = (
        diagnostic["understaff_end"]
    )

    understaff_weeks = (
        diagnostic["understaff_weeks"]
    )

    overstaff_start = (
        diagnostic["overstaff_start"]
    )

    overstaff_end = (
        diagnostic["overstaff_end"]
    )

    overstaff_weeks = (
        diagnostic["overstaff_weeks"]
    )

    peak_surplus = (
        diagnostic["peak_surplus"]
    )

    peak_gap_date = (
        diagnostic["peak_gap_date"]
    )

    demand_growth = (
        diagnostic["demand_growth"]
    )

    budget_variance = (
        diagnostic["budget_variance"]
    )

    productivity = (
        diagnostic["max_productivity"]
    )
    
    if driver == "demand_growth":

        return (

            f"{queue} is forecast to "
            f"experience significant demand growth "
            f"over the planning horizon. "

            f"Demand increases by "
            f"{demand_growth:.1f}% while current "
            f"workforce plans do not expand "
            f"sufficiently to absorb the additional "
            f"workload. "

            f"Workforce capacity falls below "
            f"forecast demand from "
            f"{understaff_start} and remains "
            f"constrained for approximately "
            f"{understaff_weeks} weeks. "

            f"The workforce deficit peaks at "
            f"{peak_gap:.1f} FTE during "
            f"{peak_gap_date}. "

            f"Current transformation benefits "
            f"deliver approximately "
            f"{productivity:.1f}% productivity "
            f"improvement which is insufficient "
            f"to offset forecast growth. "

            f"Management attention should focus "
            f"on recruitment planning and "
            f"capacity expansion."
        )
        
    elif driver == "budget_constraint":

        return (

            f"{queue} is forecast to remain "
            f"constrained by available budget. "

            f"Current budget assumptions remain "
            f"below forecast operational "
            f"requirements with average budget "
            f"variance of "
            f"{budget_variance:.1f} FTE. "

            f"Workforce pressure peaks at "
            f"{peak_gap:.1f} FTE during "
            f"{peak_gap_date}. "

            f"Without additional investment "
            f"service performance may become "
            f"increasingly dependent on overtime, "
            f"productivity improvements or "
            f"service trade-offs."
        )
        
    elif driver == "transformation_gap":

        return (

            f"{queue} continues to experience "
            f"workforce pressure despite relatively "
            f"stable demand conditions. "

            f"The largest workforce deficit "
            f"reaches "
            f"{peak_gap:.1f} FTE during "
            f"{peak_gap_date}. "

            f"Current transformation initiatives "
            f"deliver only "
            f"{productivity:.1f}% productivity "
            f"improvement which is insufficient "
            f"to close the projected gap. "

            f"Additional automation, process "
            f"improvement or workforce investment "
            f"may be required."
        )
        
    else:

        return (

            f"{queue} remains operationally "
            f"stable across the planning horizon "
            f"with no material demand, workforce, "
            f"budget or transformation risks "
            f"currently projected."
        )