import streamlit as st

from Engine.publish_plan_engine import (
    publish_plan
)


def render_publish_plan_panel():

    st.subheader(
        "Publish Plan"
    )

    confirm_publish = st.checkbox(

        "I understand this will replace the current published plan"
    )

    publish_clicked = st.button(

        "Publish Plan",

        key="publish_plan_button"
    )

    if publish_clicked:

        if not confirm_publish:

            st.warning(
                "Please confirm publication first."
            )

            return

        result = publish_plan()

        st.success(
            result["message"]
        )

        st.rerun()