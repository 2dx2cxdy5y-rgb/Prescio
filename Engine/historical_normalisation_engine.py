import pandas as pd

from Engine.dataset_registry import (
    DATASETS
)

from Engine.data_ingestion_engine import (
    load_historical_operational_data
)

from Engine.logging_engine import (
    log_info
)


def generate_normalised_history():

    # -----------------------------------
    # LOAD RAW HISTORY
    # -----------------------------------

    historical_df = (
        load_historical_operational_data()
    )

    # -----------------------------------
    # LOAD ADJUSTMENTS
    # -----------------------------------

    adjustments_df = pd.read_csv(

        DATASETS[
            "historical_adjustments"
        ]["path"]
    )

    # -----------------------------------
    # DATE FORMATTING
    # -----------------------------------


    adjustments_df["start_date"] = pd.to_datetime(

        adjustments_df["start_date"],

        dayfirst=True,

        errors="coerce"
    )

    adjustments_df["end_date"] = pd.to_datetime(

        adjustments_df["end_date"],

        dayfirst=True,

        errors="coerce"
    )

    # -----------------------------------
    # TRACK STATUS
    # -----------------------------------

    historical_df[
        "normalisation_status"
    ] = "raw"

    historical_df[
        "normalisation_reason"
    ] = ""

    # -----------------------------------
    # PROCESS ADJUSTMENTS
    # -----------------------------------

    for _, adjustment in adjustments_df.iterrows():

        if not adjustment["enabled"]:
            continue

        queue = str(
            adjustment["queue"]
        ).strip().lower()

        metric = adjustment["metric"]

        action = adjustment[
            "adjustment_action"
        ]

        reason = adjustment["reason"]

        start_date = adjustment[
            "start_date"
        ]

        end_date = adjustment[
            "end_date"
        ]

        # -----------------------------------
        # FILTER MATCHING ROWS
        # -----------------------------------

        mask = (

            (historical_df["queue"]
             .str.lower() == queue)

            &

            (historical_df["date"]
             >= start_date)

            &

            (historical_df["date"]
             <= end_date)
        )

        # -----------------------------------
        # EXCLUDE ACTION
        # -----------------------------------

        if action == "exclude":

            historical_df.loc[
                mask,
                "normalisation_status"
            ] = "excluded"

            historical_df.loc[
                mask,
                "normalisation_reason"
            ] = reason

        # -----------------------------------
        # SMOOTH ACTION
        # -----------------------------------

        elif action == "smooth":

            queue_history = historical_df[

                historical_df["queue"]
                .str.lower() == queue
            ].copy()

            rolling_average = (

                queue_history[metric]

                .rolling(4, min_periods=1)

                .mean()
            )

            historical_df.loc[
                mask,
                metric
            ] = int(
                rolling_average.mean()
            )

            historical_df.loc[
                mask,
                "normalisation_status"
            ] = "smoothed"

            historical_df.loc[
                mask,
                "normalisation_reason"
            ] = reason

    # -----------------------------------
    # REMOVE EXCLUDED ROWS
    # -----------------------------------

    normalised_df = historical_df[

        historical_df[
            "normalisation_status"
        ] != "excluded"
    ].copy()

    # -----------------------------------
    # SAVE OUTPUT
    # -----------------------------------

    output_path = (
        "output/normalised_historical_data.csv"
    )

    normalised_df.to_csv(
        output_path,
        index=False
    )

    log_info(
        "Normalised historical data generated."
    )


if __name__ == "__main__":
    generate_normalised_history()