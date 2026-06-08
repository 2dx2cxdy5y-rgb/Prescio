from Models.insight_schema import Insight
from Utils.insight_identity import generate_insight_id


def create_insight(
    domain,
    category,
    severity,

    headline,
    summary,

    recommendation="",

    enterprise_context="",
    local_context="",

    metric=None,
    metric_value=None,
    variance=None,

    impact_type=None,
    impact_value=0,

    queue=None,
    scenario=None,

    execution_id=None,

    source_engine=None,

    source_pipeline_step=None,

    tags=None
):

    return Insight(

        # Identity
        id=generate_insight_id(
            domain=domain,
            category=category,
            headline=headline,
            queue=queue or ""
        ),

        domain=domain,
        category=category,

        # Priority
        severity=severity,

        # Narrative
        headline=headline,
        summary=summary,
        recommendation=recommendation,

        # Context
        enterprise_context=enterprise_context,
        local_context=local_context,

        # Metrics
        metric=metric,
        metric_value=metric_value,
        variance=variance,

        # Impact
        impact_type=impact_type,
        impact_value=impact_value,

        # References
        queue=queue,
        scenario=scenario,

        execution_id=execution_id,

        source_engine=source_engine,

        source_pipeline_step=source_pipeline_step,

        # Metadata
        tags=tags or []
    )