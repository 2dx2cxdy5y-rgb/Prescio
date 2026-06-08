import pandas as pd
import os


def archive_forecast_snapshot(
    forecast_df
):

    snapshot_date = pd.Timestamp.now().strftime(
        "%d/%m/%Y"
    )

    snapshot_df = forecast_df.copy()

    snapshot_df = snapshot_df.rename(
        columns={
            "date": "forecast_date"
        }
    )

    snapshot_df["snapshot_date"] = (
        snapshot_date
    )

    snapshot_df = snapshot_df[
        [
            "snapshot_date",
            "forecast_date",
            "queue",
            "demand"
        ]
    ]

    history_file = (
        "Data/forecast_snapshot_history.csv"
    )

    if os.path.exists(
        history_file
    ):

        history_df = pd.read_csv(
            history_file
        )

    else:

        history_df = pd.DataFrame(
            columns=[
                "snapshot_date",
                "forecast_date",
                "queue",
                "demand"
            ]
        )

    history_df = pd.concat(

        [
            history_df,
            snapshot_df
        ],

        ignore_index=True
    )

    history_df.to_csv(

        history_file,

        index=False
    )