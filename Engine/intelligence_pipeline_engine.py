from Engine.root_cause_engine import (
    identify_root_causes
)
# =========================================================
# INTELLIGENCE PIPELINE ENGINE
# =========================================================

def generate_all_insights(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_executive_commentary,
    generate_risk_commentary,
    generate_workforce_insights
):

    all_insights = []

    # -----------------------------------------------------
    # EXECUTIVE INSIGHTS
    # -----------------------------------------------------

    executive_insights = (
        generate_executive_commentary(

            forecast_df,
            filtered_forecast_df,

            selected_queue
        )
    )

    all_insights.extend(
        executive_insights
    )

    # -----------------------------------------------------
    # RISK INSIGHTS
    # -----------------------------------------------------

    risk_insights = (
        generate_risk_commentary(

            forecast_df,
            filtered_forecast_df,

            selected_queue
        )
    )

    all_insights.extend(
        risk_insights
    )

    # -----------------------------------------------------
    # WORKFORCE INSIGHTS
    # -----------------------------------------------------

    workforce_insights = (
        generate_workforce_insights(
            forecast_df
        )
    )

    all_insights.extend(
        workforce_insights
    )

    # -----------------------------------------------------
    # ROOT CAUSE ENRICHMENT
    # -----------------------------------------------------

    for insight in all_insights:

        insight.root_causes = (
            identify_root_causes(

                insight,
                forecast_df
            )
        )
    
    return all_insights