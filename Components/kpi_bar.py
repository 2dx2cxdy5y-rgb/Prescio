import streamlit as st


def render_kpi_bar(
    metrics
):

    columns = st.columns(
        len(metrics)
    )

    for column, metric in zip(
        columns,
        metrics
    ):

        label = metric.get(
            "label",
            ""
        )

        value = metric.get(
            "value",
            ""
        )

        delta = metric.get(
            "delta",
            None
        )

        help_text = metric.get(
            "help",
            None
        )

        column.metric(

            label=label,

            value=value,

            delta=delta,

            help=help_text
        )