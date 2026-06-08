from collections import defaultdict

# -----------------------------------
# LIFECYCLE WEIGHTS
# -----------------------------------

LIFECYCLE_SCORE_MODIFIERS = {

    "new": 0,
    "persistent": 10,
    "worsening": 25,
    "improving": -5,
    "resolved": -20
}

# -----------------------------------
# SEVERITY WEIGHTS
# -----------------------------------

SEVERITY_WEIGHTS = {

    "critical": 100,
    "high": 75,
    "medium": 50,
    "low": 25,
    "info": 5
}


# -----------------------------------
# CATEGORY GROUPS
# -----------------------------------

CATEGORY_GROUP_MAP = {

    "staffing_gap":
        "workforce_pressure",

    "financial_risk":
        "financial_pressure",

    "service_risk":
        "service_pressure",

    "transformation":
        "transformation"
}


# -----------------------------------
# PRIORITY SCORING
# -----------------------------------

def calculate_priority_score(
    insight
):

    severity_score = (
        SEVERITY_WEIGHTS.get(
            insight.severity,
            0
        )
    )

    impact_score = min(
        abs(insight.impact_value),
        50
    )

    lifecycle_modifier = (

        LIFECYCLE_SCORE_MODIFIERS.get(

            insight.lifecycle_state,

            0
        )
    )

    # -----------------------------------
    # PERSISTENCE ESCALATION
    # -----------------------------------

    persistence_bonus = 0

    if insight.lifecycle_state == "persistent":

        persistence_bonus = (

            insight.occurrence_count * 2
        )

    total_score = (

        severity_score
        + impact_score
        + lifecycle_modifier
        + persistence_bonus
    )

    return total_score


# -----------------------------------
# PRIORITISATION ENGINE
# -----------------------------------

def prioritise_insights(
    insights
):

    # -----------------------------
    # APPLY SCORES
    # -----------------------------

    for insight in insights:

        insight.priority_score = (
            calculate_priority_score(
                insight
            )
        )

    # -----------------------------
    # SORT INSIGHTS
    # -----------------------------

    ranked_insights = sorted(

        insights,

        key=lambda x: x.priority_score,

        reverse=True
    )

    # -----------------------------
    # GROUP INSIGHTS
    # -----------------------------

    grouped_insights = (
        defaultdict(list)
    )

    for insight in ranked_insights:

        group = (
            CATEGORY_GROUP_MAP.get(
                insight.category,
                "other"
            )
        )

        grouped_insights[group].append(
            insight
        )

    return {

        "ranked_insights":
            ranked_insights,

        "grouped_insights":
            dict(grouped_insights)
    }