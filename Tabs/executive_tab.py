import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from Engine.intelligence_registry_engine import (
    get_executive_insights
)

from Components.section_header import (
    render_section_header
)

from Components.page_title import (
    render_title
)

from Components.kpi_strip import (
    render_kpi_strip
)

from Components.chart_container import (
    render_chart_container
)

from Engine.queue_diagnostic_engine import (
    generate_queue_diagnostics
)

from Engine.narrative_engine import (
    build_queue_profile
)

from Engine.driver_narrative_engine import (
    generate_driver_narrative
)


def render_executive_tab(

    forecast_df,
    filtered_forecast_df,

    selected_queue,

    generate_executive_commentary,
    generate_risk_commentary,

    prioritise_insights,
    aggregate_insights,

    generate_executive_narrative,

    generate_enterprise_outlook,

    generate_queue_health_briefings,

    render_insight,

    DATASETS,

    weekly_impact_df,

    overall_risk,

    forecast_intelligence_df,
    
    all_insights
):

    queue_diagnostics = (
        generate_queue_diagnostics(
            forecast_df
        )
    )

    sales_profile = (
        build_queue_profile(
            "sales",
            forecast_df
        )
    )

    from Engine.queue_driver_engine import (
        determine_primary_driver
    )

    from Engine.driver_narrative_engine import (
        generate_driver_narrative
    )

    for diagnostic in queue_diagnostics:

        driver = determine_primary_driver(
            diagnostic
        )

        narrative = (
            generate_driver_narrative(
                diagnostic,
                driver
            )
        )
        
    from Engine.queue_driver_engine import (
        determine_primary_driver
    )

    render_title(
        "Executive Intelligence",
        divider=False
    )

    st.caption(
        "Operational decision intelligence overview"
    )

    st.divider()

    # =========================================
    # GENERATE INSIGHTS
    # =========================================

    executive_insights = (
        get_executive_insights(
            all_insights
        )
    )

    for insight in executive_insights:

        print(
            insight.queue,
            insight.category,
            insight.severity
        )
        
    prioritised_output = prioritise_insights(
        executive_insights
    )

    ranked_insights = prioritised_output[
        "ranked_insights"
    ]


    grouped_insights = prioritised_output[
        "grouped_insights"
    ]

    aggregated_themes = aggregate_insights(
        ranked_insights
    )

    executive_narrative = (
        generate_executive_narrative(
            aggregated_themes
        )
    )

    # =========================================
    # KPI CALCULATIONS
    # =========================================

    highest_severity = "info"

    if ranked_insights:

        highest_severity = (
            ranked_insights[0]
            .severity
        )

    active_risks = len([

        i for i in ranked_insights

        if i.severity in [
            "critical",
            "high"
        ]
    ])

    worst_gap = round(
        forecast_df["fte_gap"].min(),
        1
    )

    avg_demand_change = round(
        forecast_df[
            "demand_change"
        ].mean() * 100,
        1
    )

    max_ai = round(
        forecast_df[
            "ai_deflection"
        ].max() * 100,
        1
    )

    # =========================================
    # ENTERPRISE KPI STRIP
    # =========================================

    render_section_header(
        "Enterprise KPI Overview",
        divider=False
    )

    render_kpi_strip([

        {
            "label": "Enterprise Severity",
            "value": highest_severity.upper()
        },

        {
            "label": "Active Risks",
            "value": active_risks
        },

        {
            "label": "Worst FTE Gap",
            "value": worst_gap
        },

        {
            "label": "Demand Change %",
            "value": f"{avg_demand_change}%"
        },

        {
            "label": "AI Opportunity %",
            "value": f"{max_ai}%"
        }
    ])



    render_section_header(
        "Enterprise Outlook"
    )

    
    enterprise_outlook = (
        generate_enterprise_outlook(
            ranked_insights,
            forecast_df
        )
    )
 
    st.info(
        enterprise_outlook
    )
        
    render_section_header(
        "Queue Health Briefings"
    )
    
    queue_briefings = (
        generate_queue_health_briefings(
            all_insights,
            forecast_df
        )
    )
    
    for briefing in queue_briefings:

        st.markdown(
            briefing["headline"]
        )

        st.write(
            briefing["narrative"]
        )

        st.divider()