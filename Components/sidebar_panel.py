import streamlit as st


def open_sidebar_panel(
    title,
    background_color="#1E2530",
    border_color="#313A46"
):

    st.sidebar.markdown(
        f"""
<div style="
padding: 15px;
border-radius: 10px;
background-color: {background_color};
border: 1px solid {border_color};
margin-top: 10px;
margin-bottom: 10px;
">

<h4 style="
margin-top: 0px;
margin-bottom: 15px;
color: #FFFFFF;
">

{title}

</h4>
""",
        unsafe_allow_html=True
    )


def close_sidebar_panel():

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True
    )