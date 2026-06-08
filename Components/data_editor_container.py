import streamlit as st


def render_data_editor(

    dataframe,

    save_button_label,

    save_callback,

    editor_key=None,

    num_rows="dynamic",

    width="stretch",
    
    column_config=None
):

    edited_df = st.data_editor(

        dataframe,

        width=width,

        num_rows=num_rows,

        key=editor_key,
        
        column_config=column_config
    )

    if st.button(
        save_button_label
    ):

        save_callback(
            edited_df
        )

    return edited_df