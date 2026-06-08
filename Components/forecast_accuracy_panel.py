import streamlit as st
import pandas as pd


def render_forecast_accuracy_panel(
    selected_queue
):

    st.subheader(
        "Forecast Accuracy"
    )

    try:

        summary_df = pd.read_csv(
            "Output/forecast_accuracy_summary.csv"
        )

        accuracy_df = pd.read_csv(
            "Output/forecast_accuracy.csv"
        )

        if selected_queue != "All Queues":

            accuracy_df = (

                accuracy_df[

                    accuracy_df["queue"]

                    ==

                    selected_queue.lower()
                ]
            )
        
    except Exception:

        st.warning(
            "Forecast accuracy not available."
        )

        return

    if summary_df.empty:

        st.warning(
            "Forecast accuracy not available."
        )

        return

    # accuracy_score = (

    #     summary_df.loc[
    #         0,
    #         "accuracy_score"
    #     ]
    # )

    # average_forecast_error = (

    #     summary_df.loc[
    #         0,
    #         "average_forecast_error"
    #     ]
    # )

    # forecast_bias = (

    #     summary_df.loc[
    #         0,
    #         "forecast_bias"
    #     ]
    # )

    # periods_measured = (

    #     summary_df.loc[
    #         0,
    #         "periods_measured"
    #     ]
    # )

    try:

        accuracy_df = pd.read_csv(
            "Output/forecast_accuracy.csv"
        )

    except Exception:

        st.warning(
            "Forecast accuracy not available."
        )

        return

    if selected_queue != "All Queues":

        accuracy_df = (

            accuracy_df[

                accuracy_df["queue"]

                ==

                selected_queue.lower()
            ]
        )

    if accuracy_df.empty:

        st.warning(
            "No forecast accuracy data available."
        )

        return

    average_forecast_error = (

        accuracy_df[
            "abs_variance_pct"
        ]

        .mean()
    )

    forecast_bias = (

        accuracy_df[
            "variance_pct"
        ]

        .mean()
    )

    accuracy_score = (

        100

        -

        average_forecast_error
    )

    periods_measured = len(
        accuracy_df
    )

    comparison_chart_df = (

        accuracy_df

        .groupby(
            "date"
        )

        .agg(

            Forecast_Demand=(

                "demand",
                "sum"
            ),

            Actual_Demand=(

                "historical_demand",
                "sum"
            )
        )

        .reset_index()
    )

    comparison_chart_df[
        "Forecast_Index"
    ] = (

        comparison_chart_df[
            "Forecast_Demand"
        ]

        /

        comparison_chart_df[
            "Forecast_Demand"
        ].mean()
    )

    comparison_chart_df[
        "Actual_Index"
    ] = (

        comparison_chart_df[
            "Actual_Demand"
        ]

        /

        comparison_chart_df[
            "Actual_Demand"
        ].mean()
    )

    comparison_chart_df[
        "Shape_Error"
    ] = (

        comparison_chart_df[
            "Forecast_Index"
        ]

        -

        comparison_chart_df[
            "Actual_Index"
        ]

    ).abs()

    average_shape_error = (

        comparison_chart_df[
            "Shape_Error"
        ]

        .mean()
    )

    shape_accuracy = (

        100

        -

        (
            average_shape_error
            * 100
        )
    )
        
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Accuracy Score",
            f"{accuracy_score:.1f}%"
        )

    with col2:

        st.metric(
            "Average Error",
            f"{average_forecast_error:.1f}%"
        )

    with col3:

        st.metric(
            "Forecast Bias",
            f"{forecast_bias:.1f}%"
        )
        
    with col4:

        st.metric(

            "Shape Accuracy",

            f"{shape_accuracy:.1f}%"
        )
        
    with col5:

        st.metric(
            "Periods",
            f"{periods_measured:,}"
        )

    try:

        queue_accuracy_df = pd.read_csv(
            "Output/queue_accuracy.csv"
        )

        if selected_queue != "All Queues":

            queue_accuracy_df = (

                queue_accuracy_df[

                    queue_accuracy_df["queue"]

                    ==

                    selected_queue.lower()
                ]
            )
            
        display_df = queue_accuracy_df.copy()

        display_df["Accuracy"] = (

            display_df["accuracy_score"]

            .round(1)

            .astype(str)

            + "%"
        )

        display_df["Bias"] = (

            display_df["bias"]

            .round(1)

            .astype(str)

            + "%"
        )

        config_df = pd.read_csv(
            "Data/forecast_configuration.csv"
        )

        green_threshold = float(
            config_df.loc[
                0,
                "forecast_green_threshold"
            ]
        )

        amber_threshold = float(
            config_df.loc[
                0,
                "forecast_amber_threshold"
            ]
        )

        display_df["Status"] = (

            display_df["accuracy_score"]

            .apply(

                lambda x:

                "🟢"
                if x >= green_threshold

                else "🟠"
                if x >= amber_threshold

                else "🔴"
            )
        )

        display_df = display_df[
            [
                "queue",
                "Accuracy",
                "Bias",
                "Status"
            ]
        ]

        display_df["queue"] = (

            display_df["queue"]

            .astype(str)

            .str.title()
        )


        display_df.columns = [

            "Queue",

            "Accuracy",

            "Bias",

            "Status"
        ]




        st.markdown(
            "#### Queue Accuracy"
        )

        st.dataframe(
            display_df,
            use_container_width=True
        )

    except Exception:

        pass

    st.divider()
    
    st.markdown(
        "#### Forecast Accuracy Trend"
    )    
    
    accuracy_trend_df = (

    accuracy_df

    .groupby(
        "date"
    )[
        "abs_variance_pct"
    ]

    .mean()

    .reset_index()
)
    
    accuracy_trend_df["date"] = pd.to_datetime(

        accuracy_trend_df["date"],

        errors="coerce"
    )
    
    accuracy_trend_df = (

        accuracy_trend_df

        .sort_values(
            "date"
        )
    )    
    accuracy_trend_df = (

        accuracy_trend_df

        .rename(

            columns={

                "abs_variance_pct":
                    "Forecast Error %"
            }
        )
    )

    st.line_chart(

        accuracy_trend_df

        .set_index(
            "date"
        )[
            "Forecast Error %"
        ]
    )
    
    st.divider()

    st.markdown(
        "#### Forecast vs Actual Demand"
    )

    comparison_chart_df = (

        accuracy_df

        .groupby(
            "date"
        )

        .agg(

            Forecast_Demand=(

                "demand",
                "sum"
            ),

            Actual_Demand=(

                "historical_demand",
                "sum"
            )
        )

        .reset_index()
    )    

    comparison_chart_df["date"] = pd.to_datetime(

        comparison_chart_df["date"],

        errors="coerce"
    )

    comparison_chart_df = (

        comparison_chart_df

        .sort_values(
            "date"
        )
    )

    comparison_chart_df[
        "Forecast_Index"
    ] = (

        comparison_chart_df[
            "Forecast_Demand"
        ]

        /

        comparison_chart_df[
            "Forecast_Demand"
        ].mean()
    )

    comparison_chart_df[
        "Actual_Index"
    ] = (

        comparison_chart_df[
            "Actual_Demand"
        ]

        /

        comparison_chart_df[
            "Actual_Demand"
        ].mean()
    )

    st.line_chart(

        comparison_chart_df

        .set_index(
            "date"
        )[
            [
                "Forecast_Demand",
                "Actual_Demand"
            ]
        ]
    )
    
    
    
    