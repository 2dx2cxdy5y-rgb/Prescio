import pandas as pd
import os

from Engine.dataset_registry import (
    DATASETS
)

# -----------------------------
# SAVE SCENARIO
# -----------------------------

def save_scenario(
    scenario_name,
    assumptions
):

    output_path = (
        f"output/scenarios/"
        f"{scenario_name}.csv"
    )

    scenario_df = pd.DataFrame(
        [assumptions]
    )

    scenario_df.to_csv(
        output_path,
        index=False
    )

# -----------------------------
# LOAD SCENARIO
# -----------------------------

def load_scenario(
    scenario_name
):

    input_path = (
        f"output/scenarios/"
        f"{scenario_name}.csv"
    )

    if not os.path.exists(
        input_path
    ):

        raise ValueError(
            f"Scenario not found: "
            f"{scenario_name}"
        )

    return pd.read_csv(
        input_path
    ).iloc[0].to_dict()

# -----------------------------
# LIST SCENARIOS
# -----------------------------

def list_scenarios():

    scenario_folder = (
        "output/scenarios"
    )

    if not os.path.exists(
        scenario_folder
    ):

        return []

    scenario_files = [

        file.replace("_forecast.csv", "")

        for file in os.listdir(
            scenario_folder
        )

        if file.endswith("_forecast.csv")
    ]

    return sorted(
        scenario_files
    )
    