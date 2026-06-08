from Shared.severity_config import (
    SEVERITY_RANK
)

# =========================================================
# INTELLIGENCE REGISTRY ENGINE
# =========================================================


# =========================================================
# FILTER BY DOMAIN
# =========================================================

def filter_insights_by_domain(

    insights,
    domains
):

    return [

        i for i in insights

        if i.domain in domains
    ]


# =========================================================
# FILTER BY SEVERITY
# =========================================================

def filter_insights_by_severity(

    insights,
    severities
):

    return [

        i for i in insights

        if i.severity in severities
    ]


# =========================================================
# SORT BY PRIORITY
# =========================================================

def sort_insights_by_severity(

    insights
):

    return sorted(

        insights,

        key=lambda x: SEVERITY_RANK.get(
            x.severity,
            0
        ),

        reverse=True
    )


# =========================================================
# EXECUTIVE INSIGHTS
# =========================================================

def get_executive_insights(

    insights
):

    filtered = filter_insights_by_severity(

        insights,

        [
            "critical",
            "high"
        ]
    )

    return sort_insights_by_severity(
        filtered
    )


# =========================================================
# OPERATIONAL INSIGHTS
# =========================================================

def get_operational_insights(

    insights
):

    return sort_insights_by_severity(
        insights
    )


# =========================================================
# WORKFORCE INSIGHTS
# =========================================================

def get_workforce_insights(

    insights
):

    filtered = filter_insights_by_domain(

        insights,

        ["workforce"]
    )

    return sort_insights_by_severity(
        filtered
    )


# =========================================================
# RISK INSIGHTS
# =========================================================

def get_risk_insights(

    insights
):

    filtered = filter_insights_by_domain(

        insights,

        ["risk"]
    )

    return sort_insights_by_severity(
        filtered
    )