import streamlit as st

from Shared.severity_config import (
    SEVERITY_ICONS
)


def render_commentary_card(

    st,
    insight

):

    severity_icon = SEVERITY_ICONS.get(

        insight.severity,

        "⚪"
    )

    st.markdown(

        f"""
### {severity_icon} {insight.headline}
"""
    )

    st.markdown(

        insight.summary
    )

    if insight.recommendation:

        st.markdown(

            """
#### Recommended Action
"""
        )

        st.write(

            insight.recommendation
        )

    st.divider()