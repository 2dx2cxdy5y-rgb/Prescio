import pandas as pd

import os

from datetime import datetime

# -----------------------------
# RECORD PIPELINE RUN
# -----------------------------

def record_pipeline_run(

    scenario_name,
    runtime_seconds,
    status
):

    output_path = (
        "Output/run_metadata.csv"
    )

    run_record = {

        "run_timestamp": (
            datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
        ),

        "scenario_name": scenario_name,

        "runtime_seconds": round(
            runtime_seconds,
            2
        ),

        "status": status
    }

    if os.path.exists(output_path):

        existing_df = pd.read_csv(
            output_path
        )

    else:

        existing_df = pd.DataFrame()

    updated_df = pd.concat(

        [
            existing_df,
            pd.DataFrame([run_record])
        ],

        ignore_index=True
    )

    updated_df.to_csv(
        output_path,
        index=False
    )