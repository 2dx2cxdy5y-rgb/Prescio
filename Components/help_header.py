import streamlit as st


def render_help_header(

    title,

    help_markdown,

    divider=True
):

    header_col1, header_col2 = st.columns(
        [12, 1]
    )

    with header_col1:

        st.markdown(
            f"## {title}"
        )

    with header_col2:

        st.markdown(
            "<div style='padding-top: 12px'></div>",
            unsafe_allow_html=True
        )

        with st.popover("ℹ️"):

            st.markdown(
                help_markdown
            )

