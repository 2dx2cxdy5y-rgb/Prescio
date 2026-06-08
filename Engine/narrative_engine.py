from collections import defaultdict

def build_queue_profile(
    queue,
    forecast_df
):

    queue_df = forecast_df[
        forecast_df["queue"] == queue
    ].copy()

    if queue_df.empty:

        return None

    peak_gap_row = queue_df.loc[
        queue_df["fte_gap"].idxmin()
    ]

    worst_budget = (
        queue_df[
            "budget_variance"
        ].min()
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

    if not understaffed_periods.empty:

        understaff_start = (
            understaffed_periods
            .iloc[0]["date_display"]
        )

        understaff_end = (
            understaffed_periods
            .iloc[-1]["date_display"]
        )

        understaff_weeks = len(
            understaffed_periods
        )

    else:

        understaff_start = None
        understaff_end = None
        understaff_weeks = 0


    overstaffed_periods = (
        queue_df[
            queue_df["fte_gap"] > 0
        ]
    )

    if not overstaffed_periods.empty:

        overstaff_start = (
            overstaffed_periods
            .iloc[0]["date_display"]
        )

        overstaff_end = (
            overstaffed_periods
            .iloc[-1]["date_display"]
        )

        overstaff_weeks = len(
            overstaffed_periods
        )

        peak_surplus = round(
            overstaffed_periods[
                "fte_gap"
            ].max(),
            1
        )

    else:

        overstaff_start = None
        overstaff_end = None
        overstaff_weeks = 0
        peak_surplus = 0

    # ---------------------------------
    # CAPACITY PATTERN CLASSIFICATION
    # ---------------------------------

    capacity_pattern = "balanced"

    if (

        understaff_weeks > 0

        and

        overstaff_weeks == 0

    ):

        capacity_pattern = (
            "persistent_understaffing"
        )

    elif (

        overstaff_weeks > 0

        and

        understaff_weeks > 0

    ):

        capacity_pattern = (
            "surplus_then_understaffed"
        )

    elif (

        overstaff_weeks > 0

        and

        understaff_weeks == 0

    ):

        capacity_pattern = (
            "persistent_surplus"
        )
    
    demand_growth = (

        (
            queue_df["demand"].iloc[-1]
            -
            queue_df["demand"].iloc[0]
        )

        /

        max(
            queue_df["demand"].iloc[0],
            1
        )

    ) * 100

    return {

        "peak_gap":
            peak_gap_row["fte_gap"],

        "peak_gap_date":
            peak_gap_row["date_display"],

        "demand_growth":
            round(
                demand_growth,
                1
            ),

        "max_ai_deflection":
            round(
                queue_df[
                    "ai_deflection"
                ].max() * 100,
                1
            ),

        "max_productivity_gain":
            round(
                queue_df[
                    "productivity_gain"
                ].max() * 100,
                1
            ),

        "worst_budget":
            round(
                worst_budget,
                1
            ),

        "avg_budget_variance":
            round(
                avg_budget_variance,
                1
            ),

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
            peak_surplus,

        "capacity_pattern":
            capacity_pattern
    }
    
def generate_enterprise_outlook(
    ranked_insights,
    forecast_df
):

    queue_profiles = []

    queues = sorted(
        forecast_df["queue"]
        .dropna()
        .unique()
    )

    for queue in queues:

        profile = build_queue_profile(
            queue,
            forecast_df
        )

        queue_profiles.append({

            "queue": queue,

            "profile": profile
        })

    critical_queues = [

        q["queue"]

        for q in queue_profiles

        if q["profile"]["peak_gap"] < -20
    ]

    warning_queues = [

        q["queue"]

        for q in queue_profiles

        if (
            q["profile"]["peak_gap"] >= -20
            and
            q["profile"]["peak_gap"] < -5
        )
    ]

    worst_gap = round(
        forecast_df["fte_gap"].min(),
        1
    )

    max_ai = round(
        forecast_df["ai_deflection"].max() * 100,
        1
    )

    return (

        f"{len(critical_queues)} critical queues and "
        f"{len(warning_queues)} emerging risk queues "
        f"have been identified across the planning horizon. "

        f"Enterprise workforce pressure peaks at "
        f"{abs(worst_gap):.1f} FTE. "

        f"Current transformation initiatives are forecast "
        f"to deliver up to {max_ai:.1f}% AI deflection."
    )


def generate_queue_health_briefings(
    ranked_insights,
    forecast_df
):

    queue_briefings = []

    queues = sorted(
        forecast_df["queue"]
        .dropna()
        .unique()
    )

    for queue in queues:

        profile = build_queue_profile(
            queue,
            forecast_df
        )

        demand_growth = (
            profile["demand_growth"]
        )

        peak_gap = abs(
            profile["peak_gap"]
        )

        peak_gap_date = (
            profile["peak_gap_date"]
        )

        understaff_weeks = (
            profile["understaff_weeks"]
        )

        understaff_start = (
            profile["understaff_start"]
        )

        overstaff_weeks = (
            profile["overstaff_weeks"]
        )

        overstaff_end = (
            profile["overstaff_end"]
        )

        peak_surplus = (
            profile["peak_surplus"]
        )

        capacity_pattern = (
            profile["capacity_pattern"]
        )

        queue_insights = [

            i

            for i in ranked_insights

            if (
                str(i.queue).lower()
                == str(queue).lower()
            )
        ]

        top_insight = None

        if queue_insights:

            top_insight = sorted(
                queue_insights,
                key=lambda x: x.priority_score,
                reverse=True
            )[0]
        
        severity = None

        if top_insight:

            severity = top_insight.severity



        # -------------------------
        # DETERMINE STATUS
        # -------------------------

        # DETERMINE STATUS

        if profile["peak_gap"] < -20:

            status = "🔴"

        elif profile["peak_gap"] < -5:

            status = "🟠"

        else:

            status = "🟢"

        # -------------------------
        # TOP QUEUE INSIGHT
        # -------------------------

        if capacity_pattern != "balanced":


            understaff_weeks = profile[
                "understaff_weeks"
            ]

            overstaff_weeks = profile[
                "overstaff_weeks"
            ]

            demand_growth = profile[
                "demand_growth"
            ]

            # ---------------------------------
            # GROWTH BAND
            # ---------------------------------

            if demand_growth >= 15:

                growth_band = "high"

            elif demand_growth >= 5:

                growth_band = "moderate"

            else:

                growth_band = "low"

                        
            productivity_gain = profile[
                "max_productivity_gain"
            ]

            narrative = ""


            # ---------------------------------
            # CAPACITY STORY
            # ---------------------------------

            # ---------------------------------
            # IMPACT NARRATIVE
            # ---------------------------------

            if capacity_pattern == "persistent_understaffing":

                impact_text = (

                    "Current workforce plans leave the "
                    "queue below required staffing levels "
                    "for most of the planning horizon."
                )

            elif capacity_pattern == "surplus_then_understaffed":

                if understaff_weeks > overstaff_weeks:

                    impact_text = (

                        "Initial surplus capacity provides "
                        "only a temporary buffer. Workforce "
                        "pressure dominates most of the "
                        "planning horizon once demand growth "
                        "absorbs available capacity."
                    )

                else:

                    impact_text = (

                        "Workforce plans remain broadly "
                        "balanced through much of the "
                        "planning horizon. Capacity pressure "
                        "emerges later as demand growth "
                        "outpaces available resources."
                    )

            elif capacity_pattern == "persistent_surplus":

                impact_text = (

                    "Available workforce capacity exceeds "
                    "forecast demand throughout the planning "
                    "horizon."
                )

            else:

                impact_text = (

                    "Workforce plans remain broadly aligned "
                    "with forecast demand."
                )

            # ---------------------------------
            # FINAL NARRATIVE
            # ---------------------------------

            # ---------------------------------
            # RECOMMENDATION
            # ---------------------------------

            if capacity_pattern == "persistent_understaffing":

                recommendation_text = (

                    "Current workforce plans are "
                    "structurally insufficient for "
                    "forecast demand. Additional hiring, "
                    "outsourcing or significant productivity "
                    "intervention should be evaluated "
                    "before service performance deteriorates."
                )

            elif capacity_pattern == "surplus_then_understaffed":

                if severity == "critical":

                    if growth_band == "high":

                        recommendation_text = (

                            "Strong forecast demand growth is "
                            "expected to absorb available capacity "
                            "rapidly. Recruitment, outsourcing or "
                            "major productivity initiatives should "
                            "begin before the surplus position is "
                            "exhausted."
                        )

                    else:

                        recommendation_text = (

                            "Current surplus capacity delays but "
                            "does not prevent significant future "
                            "workforce pressure. Workforce expansion "
                            "plans should be initiated before the "
                            "surplus position is exhausted."
                        )

                elif severity == "high":

                    recommendation_text = (

                        "Existing surplus capacity provides "
                        "short-term resilience. Workforce plans "
                        "should be strengthened before capacity "
                        "falls below forecast demand."
                    )

                else:

                    if growth_band == "low":

                        recommendation_text = (

                            "Demand growth remains relatively "
                            "modest and current surplus capacity "
                            "provides substantial short-term "
                            "resilience. Workforce plans should be "
                            "reviewed before the projected capacity "
                            "crossover point."
                        )

                    else:

                        recommendation_text = (

                            "Existing surplus capacity provides "
                            "a temporary buffer. Recruitment plans "
                            "should be phased ahead of the projected "
                            "capacity crossover point."
                        )

            elif capacity_pattern == "persistent_surplus":

                recommendation_text = (

                    "Forecast staffing exceeds projected "
                    "demand. Review workforce utilisation, "
                    "redeployment opportunities and planned "
                    "investment assumptions."
                )

            else:

                recommendation_text = (

                    "Continue monitoring forecast demand "
                    "and workforce performance."
                )





                                                            
            if capacity_pattern == "persistent_understaffing":

                situation_text = (

                    f"Demand is forecast to change by "
                    f"{profile['demand_growth']:.1f}% over the "
                    f"planning horizon. "

                    f"Workforce capacity falls below forecast "
                    f"demand from {profile['understaff_start']} "
                    f"for {profile['understaff_weeks']} weeks. "

                    f"The workforce deficit peaks at "
                    f"{abs(profile['peak_gap']):.1f} FTE."
                )

            elif capacity_pattern == "surplus_then_understaffed":

                situation_text = (

                    f"Demand is forecast to change by "
                    f"{profile['demand_growth']:.1f}% over the "
                    f"planning horizon. "

                    f"The queue begins with surplus capacity of "
                    f"{profile['peak_surplus']:.1f} FTE. "

                    f"This surplus is exhausted after "
                    f"{profile['overstaff_weeks']} weeks. "

                    f"Workforce pressure then emerges for "
                    f"{profile['understaff_weeks']} weeks."
                )

            elif capacity_pattern == "persistent_surplus":

                situation_text = (

                    f"Demand is forecast to change by "
                    f"{profile['demand_growth']:.1f}% over the "
                    f"planning horizon. "

                    f"Available workforce capacity remains above "
                    f"forecast demand throughout the period. "

                    f"Peak surplus reaches "
                    f"{profile['peak_surplus']:.1f} FTE."
                )
                
            narrative = (

                f"Situation:\n\n"

                f"{situation_text}\n\n"

                f"Impact:\n\n"

                f"{impact_text}\n\n"

                f"Transformation:\n\n"

                f"AI deflection reaches "
                f"{profile['max_ai_deflection']:.1f}% "
                f"and productivity improvements reach "
                f"{profile['max_productivity_gain']:.1f}%.\n\n"

                f"Recommended Action:\n\n"

                f"{recommendation_text}"
            )                
                

        else:

            narrative = (

                "No material demand, workforce, "
                "risk, budget or transformation "
                "issues currently projected."
            )

        queue_briefings.append({

            "headline":
                f"{status} {queue.title()}",

            "narrative":
                narrative
        })

    return queue_briefings