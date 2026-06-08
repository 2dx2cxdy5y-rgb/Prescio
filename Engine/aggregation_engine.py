from collections import defaultdict

SEVERITY_RANK = {

    "critical": 4,

    "high": 3,

    "medium": 2,

    "low": 1,

    "info": 0
}

def get_highest_severity(

    insights
):

    highest = max(

        insights,

        key=lambda x: SEVERITY_RANK.get(
            x.severity,
            0
        )
    )

    return highest.severity

def calculate_theme_score(

    insights
):

    severity_score = max([

        SEVERITY_RANK.get(
            i.severity,
            0
        )

        for i in insights
    ])

    breadth_score = len(insights)

    queue_score = len(set([

        i.queue

        for i in insights

        if i.queue
    ]))

    return (

        severity_score * 10

        + breadth_score * 2

        + queue_score
    )

def aggregate_insights(

    ranked_insights

):

    aggregated = []


    # ---------------------------------
    # GROUP BY CATEGORY
    # ---------------------------------

    grouped = defaultdict(list)

    for insight in ranked_insights:

        grouped[
            insight.category
        ].append(insight)

    # ---------------------------------
    # BUILD AGGREGATES
    # ---------------------------------

    for category, insights in grouped.items():

        # ---------------------------------
        # STAFFING PRESSURE
        # ---------------------------------

        if category == "staffing_gap":

            queues = [

                i.queue

                for i in insights

                if i.queue
            ]

            total_gap = sum([

                abs(i.metric_value)

                for i in insights

                if i.metric_value
            ])

            aggregated.append({

                "headline":
                    "Enterprise staffing pressure detected",

                "summary":
                    (
                        f"{len(queues)} queues "
                        f"show staffing deficits "
                        f"totalling "
                        f"{round(total_gap,1)} FTE."
                    ),

                "severity":
                    get_highest_severity(
                        insights
                    ),

                "queues":
                    queues,

                "theme_score":
                    calculate_theme_score(
                        insights
                    ),

                "category":
                    category,

                "source_insights":
                    insights
            })

        # ---------------------------------
        # SERVICE RISK
        # ---------------------------------

        elif category == "service_risk":

            queues = [

                i.queue

                for i in insights

                if i.queue
            ]

            aggregated.append({

                "headline":
                    "Enterprise service risk rising",

                "summary":
                    (
                        f"Operational delivery risks "
                        f"identified across "
                        f"{len(queues)} queues."
                    ),

                "severity":
                    get_highest_severity(
                        insights
                    ),

                "queues":
                    queues,

                "theme_score":
                    calculate_theme_score(
                        insights
                    ),

                "category":
                    category,

                "source_insights":
                    insights
            })

    aggregated.sort(

        key=lambda x: x[
            "theme_score"
        ],

        reverse=True
    )

    return aggregated

# ==========================================================
# CAUSAL RELATIONSHIPS
# ==========================================================

CAUSAL_MAP = {

    "staffing_gap": (
        "staffing shortages "
        "driving elevated "
        "service delivery risk"
    ),

    "service_risk": (
        "operational instability "
        "affecting delivery confidence"
    ),

    "financial_risk": (
        "budget pressure "
        "impacting workforce capacity"
    ),

    "forecast_variance": (
        "demand volatility "
        "creating operational pressure"
    ),

    "transformation": (
        "automation opportunities "
        "changing workforce demand"
    )
}

# ==========================================================
# GENERATE EXECUTIVE NARRATIVE
# ==========================================================

def generate_executive_narrative(

    aggregated_themes
):

    if not aggregated_themes:

        return (
            "No significant enterprise "
            "risks detected."
        )

    # ---------------------------------
    # TOP THEMES
    # ---------------------------------

    top_themes = aggregated_themes[:3]

    theme_descriptions = []
    causal_descriptions = []

    for theme in top_themes:

        headline = (
            theme["headline"]
            .lower()
        )

        theme_descriptions.append(
            headline
        )

        category = theme.get(
            "category"
        )

        causal_driver = CAUSAL_MAP.get(
            category
        )

        if causal_driver:

            causal_descriptions.append(
                causal_driver
            )

    # ---------------------------------
    # BUILD NARRATIVE
    # ---------------------------------

    if len(theme_descriptions) == 1:

        narrative = (
            theme_descriptions[0]
        )

    elif len(theme_descriptions) == 2:

        narrative = (

            f"{theme_descriptions[0]} "
            f"and "
            f"{theme_descriptions[1]}"
        )

    else:

        narrative = (

            ", ".join(
                theme_descriptions[:-1]
            )

            + " and "

            + theme_descriptions[-1]
        )

    # ---------------------------------
    # CAUSAL SUMMARY
    # ---------------------------------

    causal_summary = ""

    if causal_descriptions:

        unique_causes = list(set(
            causal_descriptions
        ))

        causal_summary = (

            "Primary drivers include "

            + ", ".join(unique_causes)

            + ". "
        )
        
    # ---------------------------------
    # SEVERITY
    # ---------------------------------

    highest_severity = aggregated_themes[0][
        "severity"
    ]

    # ---------------------------------
    # LIFECYCLE ANALYSIS
    # ---------------------------------

    lifecycle_states = []

    for theme in aggregated_themes:

        for insight in theme.get(
            "source_insights",
            []
        ):

            if insight.lifecycle_state:

                lifecycle_states.append(
                    insight.lifecycle_state
                )

    lifecycle_summary = ""

    if "worsening" in lifecycle_states:

        lifecycle_summary = (
            "Conditions continue "
            "to worsen. "
        )

    elif "persistent" in lifecycle_states:

        lifecycle_summary = (
            "Enterprise pressures "
            "remain persistent. "
        )

    elif "improving" in lifecycle_states:

        lifecycle_summary = (
            "Some operational "
            "conditions are improving. "
        )

    # ---------------------------------
    # PREDICTIVE SIGNALS
    # ---------------------------------

    predictive_summary = ""

    worsening_count = lifecycle_states.count(
        "worsening"
    )

    persistent_count = lifecycle_states.count(
        "persistent"
    )

    if worsening_count >= 2:

        predictive_summary = (

            "Current indicators suggest "
            "enterprise conditions are "
            "likely to deteriorate further "
            "over the next planning horizon. "
        )

    elif persistent_count >= 2:

        predictive_summary = (

            "Persistent operational pressures "
            "are likely to continue without "
            "intervention. "
        )
        
    return (

        f"{lifecycle_summary}"

        f"{predictive_summary}"

        f"Enterprise conditions indicate "
        f"{narrative}. "

        f"{causal_summary}"

        f"Highest severity is currently "
        f"{highest_severity}."
    )

    