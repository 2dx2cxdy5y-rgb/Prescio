import streamlit as st

from Shared.severity_config import (
    SEVERITY_ICONS
)


def render_insight(
    st,
    insight
):

    severity_icon = SEVERITY_ICONS.get(
        insight.severity,
        "⚪"
    )

    st.markdown(

        f"""
<h2>
{severity_icon}
{insight.headline}
</h2>
""",

        unsafe_allow_html=True
    )

    st.write(
        insight.summary
    )

    if insight.recommendation:

        st.markdown(

            f"""
**Recommended Action**

{insight.recommendation}
"""
        )

    st.divider()