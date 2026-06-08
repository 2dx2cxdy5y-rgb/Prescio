import pandas as pd


def calculate_forecast_accuracy():

    published_df = pd.read_csv(
        "Data/test_published_plan.csv"
    )

    historical_df = pd.read_csv(
        "Data/historical_operational_data.csv"
    )

    published_df["date"] = pd.to_datetime(
        published_df["date"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    historical_df["date"] = pd.to_datetime(
        historical_df["date"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    comparison_df = pd.merge(

        published_df[
            [
                "date",
                "queue",
                "demand"
            ]
        ],

        historical_df[
            [
                "date",
                "queue",
                "historical_demand"
            ]
        ],

        on=[
            "date",
            "queue"
        ],

        how="inner"
    )

    latest_date = (

        comparison_df[
            "date"
        ]

        .max()
    )

    cutoff_date = (

        latest_date

        - pd.DateOffset(
            months=12
        )
    )

    comparison_df = (

        comparison_df[

            comparison_df["date"]

            >=

            cutoff_date
        ]
    )


    comparison_df["variance"] = (

        comparison_df[
            "historical_demand"
        ]

        -

        comparison_df[
            "demand"
        ]
    )

    comparison_df["variance_pct"] = (

        comparison_df[
            "variance"
        ]

        /

        comparison_df[
            "demand"
        ]
    ) * 100

    comparison_df["abs_variance_pct"] = (

        comparison_df[
            "variance_pct"
        ]

        .abs()
    )

    queue_accuracy_df = (

        comparison_df

        .groupby(
            "queue"
        )

        .agg(

            average_error=(

                "abs_variance_pct",

                "mean"
            ),

            bias=(

                "variance_pct",

                "mean"
            )

        )

        .reset_index()
    )

    queue_accuracy_df[
        "accuracy_score"
    ] = (

        100

        -

        queue_accuracy_df[
            "average_error"
        ]
    )

    queue_accuracy_df.to_csv(

        "Output/queue_accuracy.csv",

        index=False
    )


    print(
        "\nQUEUE ACCURACY"
    )

    print(
        queue_accuracy_df
    )



    average_forecast_error = (

        comparison_df[
            "abs_variance_pct"
        ]

        .mean()
    )

    forecast_bias = (

        comparison_df[
            "variance_pct"
        ]

        .mean()
    )

    accuracy_score = (

        100

        -

        average_forecast_error
    )









    print(
        "\nFORECAST ACCURACY KPIs"
    )

    print(
        "Accuracy Score:",
        round(
            accuracy_score,
            2
        ),
        "%"
    )

    print(
        "Average Forecast Error:",
        round(
            average_forecast_error,
            2
        ),
        "%"
    )

    print(
        "Forecast Bias:",
        round(
            forecast_bias,
            2
        ),
        "%"
    )

    print(
        "Periods Measured:",
        len(
            comparison_df
        )
    )

    comparison_df.to_csv(

        "Output/forecast_accuracy.csv",

        index=False
    )

    kpi_df = pd.DataFrame(
        [
            {
                "accuracy_score":
                    round(
                        accuracy_score,
                        2
                    ),

                "average_forecast_error":
                    round(
                        average_forecast_error,
                        2
                    ),

                "forecast_bias":
                    round(
                        forecast_bias,
                        2
                    ),

                "periods_measured":
                    len(
                        comparison_df
                    )
            }
        ]
    )

    kpi_df.to_csv(

        "Output/forecast_accuracy_summary.csv",

        index=False
    )

    return {
        "success": True
    }


if __name__ == "__main__":

    result = calculate_forecast_accuracy()

    print(result)