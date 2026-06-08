from collections import defaultdict


# ==========================================================
# SEVERITY RANKING
# ==========================================================

SEVERITY_RANK = {

    "critical": 4,

    "high": 3,

    "medium": 2,

    "low": 1,

    "info": 0
}


# ==========================================================
# ENTERPRISE THEMES
# ==========================================================

THEME_MAP = {

    "workforce": (
        "Enterprise Delivery Risk"
    ),

    "executive": (
        "Enterprise Delivery Risk"
    ),

    "risk": (
        "Enterprise Delivery Risk"
    ),

    "budget": (
        "Financial Exposure"
    ),

    "demand": (
        "Demand Volatility"
    ),

    "transformation": (
        "Transformation Opportunity"
    )
}


# ==========================================================
# COMPOSE ENTERPRISE INTELLIGENCE
# ==========================================================

def compose_enterprise_intelligence(

    insights
):

    grouped_insights = defaultdict(list)

    for insight in insights:

        theme = THEME_MAP.get(

            insight.domain,

            "Other"
        )

        grouped_insights[
            theme
        ].append(insight)

    return grouped_insights


# ==========================================================
# PRIORITISE ENTERPRISE THEMES
# ==========================================================

def prioritise_enterprise_themes(

    grouped_insights
):

    prioritised = []

    for theme, insights in grouped_insights.items():

        max_severity = max(

            insights,

            key=lambda x: SEVERITY_RANK.get(
                x.severity,
                0
            )
        )

        prioritised.append({

            "theme": theme,

            "severity": max_severity.severity,

            "insight_count": len(insights),

            "insights": insights
        })

    prioritised.sort(

        key=lambda x: SEVERITY_RANK.get(
            x["severity"],
            0
        ),

        reverse=True
    )

    return prioritised