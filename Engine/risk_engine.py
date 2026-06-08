import pandas as pd

from Engine.config import (
    SERVICE_RISK_HIGH,
    SERVICE_RISK_MEDIUM,
    OVERALL_RISK_CRITICAL,
    OVERALL_RISK_HIGH,
    OVERALL_RISK_MEDIUM
)

from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------
# EXECUTIVE RISK ENGINE
# -----------------------------

def calculate_risk(

    forecast_df,
):

    risk_results = []

    # -------------------------
    # OVERALL METRICS
    # -------------------------

    total_gap = (
        forecast_df["fte_gap"].sum()
    )

    total_budget_pressure = (

    forecast_df[
        "requirement_vs_budget"
    ].sum()
)


    # -------------------------
    # SERVICE DELIVERY RISK
    # -------------------------

    if total_gap < SERVICE_RISK_HIGH:

        service_risk = "High"

    elif total_gap < SERVICE_RISK_MEDIUM:

        service_risk = "Medium"

    else:

        service_risk = "Low"

    # -------------------------
    # BUDGET RISK
    # -------------------------

    if total_budget_pressure > 1:

        budget_risk = "High"

    elif total_budget_pressure > 5:

        budget_risk = "Medium"

    else:

        budget_risk = "Low"


    # -------------------------
    # OVERALL SCORE
    # -------------------------

    risk_scores = {

        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    overall_score = (

        risk_scores[service_risk]

        + risk_scores[budget_risk]
    )

    # -------------------------
    # OVERALL RISK
    # -------------------------

    if overall_score >= OVERALL_RISK_CRITICAL:

        overall_risk = "Critical"

    elif overall_score >= OVERALL_RISK_HIGH:

        overall_risk = "High"

    elif overall_score >= OVERALL_RISK_MEDIUM: 

        overall_risk = "Medium"

    else:

        overall_risk = "Low"

    # -------------------------
    # BUILD OUTPUT
    # -------------------------

    risk_results.append({

        "service_delivery_risk":
            service_risk,

        "budget_risk":
            budget_risk,

        "overall_risk":
            overall_risk
    })

    risk_df = pd.DataFrame(
        risk_results
    )

    return risk_df