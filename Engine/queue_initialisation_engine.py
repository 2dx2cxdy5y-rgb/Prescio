import pandas as pd
import os

from Engine.configuration_map import (
    QUEUE_DEFAULTS
)
from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------------
# GENERIC QUEUE SYNC
# -----------------------------------

def sync_dataset(

    dataset_path,
    queue_master_df,
    default_values
):

    if not os.path.exists(
        dataset_path
    ):

        return

    df = pd.read_csv(
        dataset_path
    )

    if df.empty:

        if dataset_path.endswith(
            "workforce_supply.csv"
        ):

            return

    existing_queues = set(
        df["queue"].unique()
    )

    master_queues = set(
        queue_master_df["queue"].unique()
    )

    missing_queues = (
        master_queues
        - existing_queues
    )

    if not missing_queues:

        return

    template_rows = []

    # -----------------------------------
    # USE FIRST QUEUE AS TEMPLATE
    # -----------------------------------

    template_queue = (
        df["queue"].iloc[0]
    )

    template_df = df[
        df["queue"] == template_queue
    ]

    for queue in missing_queues:

        new_rows = template_df.copy()

        new_rows["queue"] = queue

        # -----------------------------------
        # QUEUE DEFAULTS
        # -----------------------------------

        queue_defaults = (

            queue_master_df[
                queue_master_df["queue"] == queue
            ].iloc[0]
        )

        # -----------------------------------
        # APPLY DEFAULTS
        # -----------------------------------

        for column, value in default_values.items():

            if column not in new_rows.columns:

                continue

            # -----------------------------------
            # MASTER-DRIVEN VALUE
            # -----------------------------------

            if isinstance(value, str):

                if value in queue_defaults.index:

                    new_rows[column] = (
                        queue_defaults[value]
                    )

            # -----------------------------------
            # STATIC VALUE
            # -----------------------------------

            else:

                new_rows[column] = value

        # -----------------------------------
        # APPEND NEW ROWS
        # -----------------------------------

        template_rows.append(
            new_rows
        )

    # -----------------------------------
    # SAVE EXPANDED DATASET
    # -----------------------------------

    if template_rows:

        expanded_df = pd.concat(

            [df] + template_rows,

            ignore_index=True
        )

        expanded_df.to_csv(
            dataset_path,
            index=False
        )


# -----------------------------------
# MASTER INITIALISATION
# -----------------------------------

def initialise_new_queues():

    queue_master_df = pd.read_csv(
        "Data/queue_master.csv"
    )

    for dataset, defaults in QUEUE_DEFAULTS.items():

        sync_dataset(

            f"Data/{dataset}",

            queue_master_df,

            defaults
        )

    # -----------------------------------
    # FORECAST
    # -----------------------------------

    sync_dataset(

        "Data/baseline_forecast.csv",

        queue_master_df,

        {
            "demand": 0
        }
    )

    # -----------------------------------
    # QUEUE CONFIG
    # -----------------------------------

    sync_dataset(

       DATASETS["queue_config"]["path"],

        queue_master_df,

        {
            "opening_fte": "default_opening_fte"
        }
    )

    # -----------------------------------
    # BUDGET
    # -----------------------------------

    sync_dataset(

        "Data/budget_forecast.csv",

        queue_master_df,

        {
            "budgeted_fte": 0
        }
    )

    # -----------------------------------
    # TRANSFORMATION
    # -----------------------------------

    sync_dataset(

        "Data/transformation_assumptions.csv",

        queue_master_df,

        {
            "ai_deflection": 0,
            "productivity_gain": 0
        }
    )

    # -----------------------------------
    # RAMP PROFILE
    # -----------------------------------

    sync_dataset(

        "Data/ramp_profiles.csv",

        queue_master_df,

        {
            "ramp_percentage": 100
        }
    )