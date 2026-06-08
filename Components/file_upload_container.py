import streamlit as st
import pandas as pd


def render_file_upload(

    label,

    dataset_path,

    required_columns,

    validate_columns,

    success_message,

    uploader_key
):

    uploaded_file = st.file_uploader(

        label,

        type=["csv"],

        key=uploader_key
    )

    if uploaded_file is None:

        return None

    uploaded_df = pd.read_csv(
        uploaded_file
    )

    valid, missing = validate_columns(

        uploaded_df,

        required_columns
    )

    if not valid:

        st.error(
            f"Missing columns: {missing}"
        )

        return None

    uploaded_df.to_csv(

        dataset_path,

        index=False
    )

    st.success(
        success_message
    )

    return uploaded_df