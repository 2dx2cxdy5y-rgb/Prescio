import streamlit as st


def render_chart_container(

    title,

    chart_function,

    divider=True,

    caption=None
):

    if divider:

        st.divider()

    render_spacing()

    st.subheader(
        title
    )

    if caption:

        st.caption(
            caption
        )

    render_spacing()

    chart_function()


def render_spacing():

    st.markdown("")