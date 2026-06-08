import streamlit as st


def render_title(

    title,

    divider=True,

    caption=None
):

    if divider:

        st.divider()

    st.title(
        title
    )

    if caption:

        st.caption(
            caption
        )