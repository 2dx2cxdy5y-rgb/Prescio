from copy import deepcopy


SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}


class LifecycleEngine:

    def compare_snapshots(
        self,
        current_insights,
        previous_insights
    ):

        previous_lookup = {
            insight.id: insight
            for insight in previous_insights
        }

        current_ids = set()

        enriched_insights = []

        for current in current_insights:

            current_ids.add(current.id)

            previous = previous_lookup.get(
                current.id
            )

            if previous:

                self._apply_lifecycle_state(
                    current,
                    previous
                )

            else:

                current.lifecycle_state = "new"

            enriched_insights.append(current)

        resolved_insights = self._detect_resolved(
            current_ids,
            previous_lookup
        )

        return (
            enriched_insights,
            resolved_insights
        )
    def _apply_lifecycle_state(
        self,
        current,
        previous
    ):

        current.previous_severity = (
            previous.severity
        )

        current.previous_metric_value = (
            previous.metric_value
        )

        current.occurrence_count = (
            previous.occurrence_count + 1
        )

        current.first_seen = (
            previous.first_seen
            or previous.created_at
        )

        current.last_seen = previous.created_at

        current_rank = SEVERITY_RANK.get(
            current.severity,
            0
        )

        previous_rank = SEVERITY_RANK.get(
            previous.severity,
            0
        )

        # ---------------------------------
        # Numeric deltas
        # ---------------------------------

        if (
            current.metric_value is not None
            and previous.metric_value is not None
        ):

            current.delta_value = (
                current.metric_value
                - previous.metric_value
            )

            if previous.metric_value != 0:

                current.delta_percent = (
                    current.delta_value
                    / previous.metric_value
                ) * 100

        # ---------------------------------
        # Lifecycle classification
        # ---------------------------------

        if current_rank > previous_rank:

            current.lifecycle_state = (
                "worsening"
            )

        elif current_rank < previous_rank:

            current.lifecycle_state = (
                "improving"
            )

        else:

            current.lifecycle_state = (
                "persistent"
            )
            
    def _detect_resolved(
        self,
        current_ids,
        previous_lookup
    ):

        resolved = []

        for (
            insight_id,
            previous
        ) in previous_lookup.items():

            if insight_id not in current_ids:

                resolved_insight = deepcopy(
                    previous
                )

                resolved_insight.lifecycle_state = (
                    "resolved"
                )

                resolved.append(
                    resolved_insight
                )

        return resolved