import streamlit as st


def render_section_header(

    title,

    divider=True,

    caption=None
):

    if divider:

        st.divider()

    st.subheader(
        title
    )

    if caption:

        st.caption(
            caption
        )