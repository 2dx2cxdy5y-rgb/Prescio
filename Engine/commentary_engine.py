from Engine.insight_engine import (
    create_insight
)


# -----------------------------------
# WORKFORCE COMMENTARY
# -----------------------------------

def generate_workforce_commentary(

    forecast_df,
    filtered_forecast_df,
    selected_queue

):

    insights = []

    # -----------------------------------
    # WORKFORCE METRICS
    # -----------------------------------

    overall_gap = (
        filtered_forecast_df[
            "fte_gap"
        ].min()
    )

    peak_surplus = (
        filtered_forecast_df[
            "fte_gap"
        ].max()
    )

    understaff_weeks = len(

        filtered_forecast_df[
            filtered_forecast_df[
                "fte_gap"
            ] < 0
        ]
    )

    overstaff_weeks = len(

        filtered_forecast_df[
            filtered_forecast_df[
                "fte_gap"
            ] > 0
        ]
    )

    # -----------------------------------
    # SEVERITY
    # -----------------------------------

    if overall_gap < -20:

        severity = "critical"

    elif overall_gap < -10:

        severity = "high"

    elif overall_gap < -5:

        severity = "medium"

    else:

        severity = "low"

    # -----------------------------------
    # SUMMARY
    # -----------------------------------

    if understaff_weeks == 0:

        summary = (

            f"Workforce capacity remains "
            f"above forecast demand "
            f"throughout the planning horizon. "

            f"Peak surplus reaches "
            f"{peak_surplus:.1f} FTE."
        )

    elif overstaff_weeks == 0:

        summary = (

            f"Workforce capacity remains "
            f"below forecast demand for "
            f"{understaff_weeks} weeks. "

            f"Peak deficit reaches "
            f"{abs(overall_gap):.1f} FTE."
        )

    else:

        summary = (

            f"The queue experiences both "
            f"surplus and deficit capacity "
            f"during the planning horizon. "

            f"Peak deficit reaches "
            f"{abs(overall_gap):.1f} FTE."
        )

    # -----------------------------------
    # RECOMMENDATION
    # -----------------------------------

    if understaff_weeks == 0:

        recommendation = (

            "Review workforce utilisation, "
            "redeployment opportunities and "
            "planned investment assumptions."
        )

    elif overstaff_weeks == 0:

        recommendation = (

            "Additional staffing, outsourcing "
            "or productivity intervention "
            "should be evaluated."
        )

    else:

        recommendation = (

            "Recruitment activity should begin "
            "before surplus capacity is exhausted."
        )

    # -----------------------------------
    # HEADLINE
    # -----------------------------------

    if selected_queue == "All Queues":

        headline = (
            "Enterprise Workforce Outlook"
        )

    else:

        headline = (
            f"{selected_queue.title()} "
            f"Workforce Outlook"
        )

    # -----------------------------------
    # CREATE INSIGHT
    # -----------------------------------

    insights.append(

        create_insight(

            domain="workforce",

            category="staffing_gap",

            severity=severity,

            headline=headline,

            summary=summary,

            recommendation=recommendation,

            metric="fte_gap",

            metric_value=overall_gap,

            source_engine=(
                "commentary_engine"
            ),

            source_pipeline_step=(
                "generate_workforce_commentary"
            ),

            impact_type="fte",

            impact_value=abs(overall_gap),

            queue=selected_queue
        )
    )

    return insights


# -----------------------------------
# EXECUTIVE COMMENTARY
# -----------------------------------

def generate_executive_commentary(

    forecast_df,
    filtered_forecast_df,
    selected_queue

):

    insights = []

    total_gap = (
        filtered_forecast_df[
            "fte_gap"
        ].sum()
    )

    if total_gap < -100:

        severity = "critical"

    elif total_gap < -50:

        severity = "high"

    else:

        severity = "medium"

    insights.append(

        create_insight(

            domain="executive",

            category="service_risk",

            severity=severity,

            headline=(
                "Enterprise delivery pressure rising"
            ),

            summary=(
                f"Cumulative FTE gap "
                f"is {round(total_gap,1)}."
            ),

            recommendation=(
                "Review enterprise delivery "
                "capacity."
            ),

            metric="fte_gap",

            metric_value=total_gap,

            source_engine=(
                "commentary_engine"
            ),

            source_pipeline_step=(
                "generate_executive_commentary"
            ),

            impact_type="fte",

            impact_value=abs(total_gap)
        )
    )

    return insights


# -----------------------------------
# PLACEHOLDERS
# -----------------------------------

# -----------------------------------
# BUDGET COMMENTARY
# -----------------------------------

def generate_budget_commentary(

    forecast_df,
    filtered_forecast_df,
    selected_queue

):

    insights = []

    budget_gap = (

        filtered_forecast_df[
            "requirement_vs_budget"
        ].sum()
    )

    # -----------------------------------
    # SEVERITY
    # -----------------------------------

    if budget_gap < -100:

        severity = "critical"

    elif budget_gap < -50:

        severity = "high"

    elif budget_gap < -20:

        severity = "medium"

    else:

        severity = "low"

    # -----------------------------------
    # SUMMARY
    # -----------------------------------

    if budget_gap < 0:

        summary = (

            f"Forecast workforce requirements "
            f"exceed budget assumptions by "
            f"{abs(budget_gap):.1f} FTE."
        )

    else:

        summary = (

            f"Budget assumptions exceed "
            f"forecast workforce requirements "
            f"by {budget_gap:.1f} FTE."
        )

    # -----------------------------------
    # RECOMMENDATION
    # -----------------------------------

    if budget_gap < -50:

        recommendation = (

            "Review affordability assumptions, "
            "workforce establishment and planned "
            "investment commitments."
        )

    elif budget_gap < 0:

        recommendation = (

            "Monitor budget pressure and validate "
            "planned workforce growth."
        )

    else:

        recommendation = (

            "Current budget assumptions appear "
            "sufficient to support forecast demand."
        )


    if selected_queue == "All Queues":

        headline = (
            "Enterprise Budget Outlook"
        )

    else:

        headline = (
            f"{selected_queue.title()} "
            f"Budget Outlook"
        )
        
    # -----------------------------------
    # CREATE INSIGHT
    # -----------------------------------

    insights.append(

        create_insight(

            domain="budget",

            category="financial_risk",

            severity=severity,

            headline=headline,

            summary=summary,

            recommendation=recommendation,

            metric="requirement_vs_budget",

            metric_value=budget_gap,

            source_engine="commentary_engine",

            source_pipeline_step=(
                "generate_budget_commentary"
            ),

            impact_type="fte",

            impact_value=abs(budget_gap),

            queue=selected_queue
        )
    )

    return insights


# -----------------------------------
# RISK COMMENTARY
# -----------------------------------

def generate_risk_commentary(

    forecast_df,
    filtered_forecast_df,
    selected_queue

):

    insights = []

    min_gap = (
        filtered_forecast_df[
            "fte_gap"
        ].min()
    )

    risk_weeks = len(

        filtered_forecast_df[
            filtered_forecast_df[
                "fte_gap"
            ] < 0
        ]
    )

    # -----------------------------------
    # SEVERITY
    # -----------------------------------

    if min_gap < -20:

        severity = "critical"

    elif min_gap < -10:

        severity = "high"

    elif min_gap < -5:

        severity = "medium"

    else:

        severity = "low"

    # -----------------------------------
    # SUMMARY
    # -----------------------------------

    if risk_weeks == 0:

        summary = (

            "No material workforce delivery "
            "risk is currently projected."
        )

    else:

        summary = (

            f"Workforce capacity falls below "
            f"forecast demand for "
            f"{risk_weeks} weeks. "

            f"Peak workforce deficit reaches "
            f"{abs(min_gap):.1f} FTE."
        )

    # -----------------------------------
    # RECOMMENDATION
    # -----------------------------------

    if severity == "critical":

        recommendation = (

            "Review contingency plans, service "
            "protection measures and workforce "
            "capacity assumptions."
        )

    elif severity == "high":

        recommendation = (

            "Monitor workforce risk exposure and "
            "prepare mitigation actions."
        )

    else:

        recommendation = (

            "Continue monitoring forecast delivery "
            "performance."
        )


    if selected_queue == "All Queues":

        headline = (
            "Enterprise Risk Outlook"
        )

    else:

        headline = (
            f"{selected_queue.title()} "
            f"Risk Outlook"
        )
        
    # -----------------------------------
    # CREATE INSIGHT
    # -----------------------------------

    insights.append(

        create_insight(

            domain="risk",

            category="service_risk",

            severity=severity,

            headline=headline,

            summary=summary,

            recommendation=recommendation,

            metric="fte_gap",

            metric_value=min_gap,

            source_engine="commentary_engine",

            source_pipeline_step=(
                "generate_risk_commentary"
            ),

            impact_type="fte",

            impact_value=abs(min_gap),

            queue=selected_queue
        )
    )

    return insights


# -----------------------------------
# TRANSFORMATION COMMENTARY
# -----------------------------------

def generate_transformation_commentary(

    forecast_df,
    filtered_forecast_df,
    selected_queue

):

    insights = []

    max_ai = (

        filtered_forecast_df[
            "ai_deflection"
        ].max()
    )

    # -----------------------------------
    # SEVERITY
    # -----------------------------------

    if max_ai >= 0.30:

        severity = "high"

    elif max_ai >= 0.15:

        severity = "medium"

    else:

        severity = "low"

    # -----------------------------------
    # SUMMARY
    # -----------------------------------

    summary = (

        f"AI and automation initiatives "
        f"have the potential to reduce "
        f"forecast demand by up to "
        f"{max_ai * 100:.1f}%."
    )

    # -----------------------------------
    # RECOMMENDATION
    # -----------------------------------

    if max_ai >= 0.30:

        recommendation = (

            "Transformation benefits represent "
            "a significant workforce planning "
            "opportunity and should be prioritised."
        )

    elif max_ai >= 0.15:

        recommendation = (

            "Review transformation delivery plans "
            "and expected productivity benefits."
        )

    else:

        recommendation = (

            "Limited transformation benefit is "
            "currently projected."
        )


    if selected_queue == "All Queues":

        headline = (
            "Enterprise Transformation Outlook"
        )

    else:

        headline = (
            f"{selected_queue.title()} "
            f"Transformation Outlook"
        )
        
    insights.append(

        create_insight(

            domain="transformation",

            category="transformation",

            severity=severity,

            headline=headline,

            summary=summary,

            recommendation=recommendation,

            metric="ai_deflection",

            metric_value=max_ai,

            source_engine="commentary_engine",

            source_pipeline_step=(
                "generate_transformation_commentary"
            ),

            impact_type="percentage",

            impact_value=max_ai * 100,

            queue=selected_queue
        )
    )

    return insights


# -----------------------------------
# DEMAND COMMENTARY
# -----------------------------------

def generate_demand_commentary(

    forecast_df,
    filtered_forecast_df,
    selected_queue

):

    insights = []

    start_demand = (
        filtered_forecast_df[
            "resolved_forecast"
        ].iloc[0]
    )

    end_demand = (
        filtered_forecast_df[
            "resolved_forecast"
        ].iloc[-1]
    )

    demand_growth = (

        (
            end_demand -
            start_demand
        )

        /

        max(start_demand, 1)

    ) * 100

    # -----------------------------------
    # SEVERITY
    # -----------------------------------

    if demand_growth >= 15:

        severity = "high"

    elif demand_growth >= 5:

        severity = "medium"

    else:

        severity = "low"

    # -----------------------------------
    # SUMMARY
    # -----------------------------------

    if demand_growth >= 0:

        summary = (

            f"Demand is forecast to increase "
            f"by {demand_growth:.1f}% over the "
            f"planning horizon."
        )

    else:

        summary = (

            f"Demand is forecast to decrease "
            f"by {abs(demand_growth):.1f}% over "
            f"the planning horizon."
        )

    # -----------------------------------
    # RECOMMENDATION
    # -----------------------------------

    if demand_growth >= 15:

        recommendation = (

            "Review workforce growth plans and "
            "capacity expansion assumptions."
        )

    elif demand_growth >= 5:

        recommendation = (

            "Monitor forecast growth and ensure "
            "staffing plans remain aligned."
        )

    else:

        recommendation = (

            "Continue monitoring forecast demand "
            "trends."
        )

    if selected_queue == "All Queues":

        headline = (
            "Enterprise Demand Outlook"
        )

    else:

        headline = (
            f"{selected_queue.title()} "
            f"Demand Outlook"
        )
        
    insights.append(

        create_insight(

            domain="demand",

            category="forecast_growth",

            severity=severity,

            headline=headline,

            summary=summary,

            recommendation=recommendation,

            metric="resolved_forecast",

            metric_value=end_demand,

            source_engine="commentary_engine",

            source_pipeline_step=(
                "generate_demand_commentary"
            ),

            impact_type="percentage",

            impact_value=demand_growth,

            queue=selected_queue
        )
    )

    return insights