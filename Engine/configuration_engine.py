import pandas as pd

from Engine.data_ingestion_engine import (

    load_queue_master,

    load_workforce_supply
)

# -----------------------------------
# SYNCHRONISE QUEUES
# -----------------------------------

def synchronise_queue_structures():

    queue_master_df = (
        load_queue_master()
    )

    active_queues = (

        queue_master_df["queue"]

        .astype(str)

        .str.strip()

        .str.lower()

        .unique()

        .tolist()
    )

    # -----------------------------------
    # WORKFORCE SUPPLY
    # -----------------------------------

    workforce_df = (
        load_workforce_supply()
    )

    existing_queues = (
        workforce_df["queue"]
        .unique()
        .tolist()
    )

    missing_queues = [

        q for q in active_queues

        if q not in existing_queues
    ]

    if missing_queues:

        template_rows = workforce_df[
            workforce_df["queue"]
            == existing_queues[0]
        ]

        new_rows = []

        for queue in missing_queues:

            queue_rows = (
                template_rows.copy()
            )

            queue_rows["queue"] = queue

            queue_rows["attrition"] = 0

            queue_rows["new_hires"] = 0

            new_rows.append(
                queue_rows
            )

        workforce_df = pd.concat(

            [workforce_df] + new_rows,

            ignore_index=True
        )

    workforce_df.to_csv(

        "Data/workforce_supply.csv",

        index=False
    )

    return True