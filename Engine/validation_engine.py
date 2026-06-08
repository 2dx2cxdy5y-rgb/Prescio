import os
import pandas as pd


# =====================================================
# COLUMN VALIDATION
# =====================================================

def validate_columns(
    dataframe,
    required_columns,
    dataframe_name
):

    missing_columns = [

        col for col in required_columns

        if col not in dataframe.columns
    ]

    if missing_columns:

        raise ValueError(

            f"{dataframe_name} missing columns: "
            f"{missing_columns}"
        )


# =====================================================
# STANDARD RESULT OBJECT
# =====================================================

def create_validation_result(
    category,
    status,
    message,
    fix_location=None,
    fix_action=None,
    details=None,
    title=None
):

    return {

        "category": category,

        "status": status,

        "message": message,

        "fix_location": fix_location,

        "fix_action": fix_action,

        "details": details,
        
        "title": title,
    }


# =====================================================
# DATASET HEALTH
# =====================================================

def validate_dataset_exists(
    dataset_name,
    dataset_path
):

    if os.path.exists(dataset_path):

        return create_validation_result(

            "Dataset Health",

            "pass",

            f"{dataset_name} available"
        )

    return create_validation_result(

        "Dataset Health",

        "critical",

        f"{dataset_name} missing"
    )


# =====================================================
# QUEUE SYNCHRONISATION
# =====================================================

def validate_queue_synchronisation(
    DATASETS
):

    results = []

    queue_master_df = pd.read_csv(

        DATASETS[
            "queue_master"
        ]["path"]
    )

    master_queues = set(

        queue_master_df["queue"]

        .astype(str)

        .str.strip()

        .str.lower()
    )

    def validate_queue_dataset(

        dataset_name,
        dataframe

    ):

        if "queue" not in dataframe.columns:

            return create_validation_result(

                "Queue Synchronisation",

                "warning",

                f"{dataset_name} has no queue column",

                fix_location="Configuration",

                fix_action="Check dataset structure"
            )

        dataset_queues = set(

            dataframe["queue"]

            .astype(str)

            .str.strip()

            .str.lower()
        )

        missing_queues = (

            master_queues
            - dataset_queues
        )

        if missing_queues:

            return create_validation_result(

                "Queue Synchronisation",

                "warning",

                (
                    f"{dataset_name} missing: "

                    + ", ".join(
                        sorted(
                            missing_queues
                        )
                    )
                ),

                fix_location="Configuration",

                fix_action="Synchronise queues from Queue Master"
            )

        return create_validation_result(

            "Queue Synchronisation",

            "pass",

            f"{dataset_name} synchronised"
        )

    # ---------------------------------
    # Queue Config
    # ---------------------------------

    queue_config_df = pd.read_csv(

        DATASETS[
            "queue_config"
        ]["path"]
    )

    results.append(

        validate_queue_dataset(

            "queue_config",

            queue_config_df
        )
    )

    # ---------------------------------
    # Ramp Profiles
    # ---------------------------------

    ramp_profiles_df = pd.read_csv(

        DATASETS[
            "ramp_profiles"
        ]["path"]
    )

    results.append(

        validate_queue_dataset(

            "ramp_profiles",

            ramp_profiles_df
        )
    )

    return results


# =====================================================
# MODEL COVERAGE
# =====================================================

def validate_model_coverage(
    DATASETS
):

    results = []

    queue_master_df = pd.read_csv(

        DATASETS[
            "queue_master"
        ]["path"]
    )

    master_queues = set(

        queue_master_df["queue"]

        .astype(str)

        .str.strip()

        .str.lower()
    )

    workforce_supply_df = pd.read_csv(

        DATASETS[
            "workforce_supply"
        ]["path"]
    )

    workforce_queues = set(

        workforce_supply_df["queue"]

        .astype(str)

        .str.strip()

        .str.lower()
    )
    
    covered_queues = (

        master_queues
        & workforce_queues
    )

    missing_queues = sorted(

        master_queues

        - workforce_queues
    )

    configured_queues = sorted(

        covered_queues
    )
    
    total_queues = len(
        master_queues
    )

    covered_count = len(
        covered_queues
    )    
    
    results.append(

        create_validation_result(

            "Model Coverage",

            "info",

            (
                f"{covered_count} of "
                f"{total_queues} queues have "
                "workforce events configured"
            ),

            fix_location=
                "Workforce Engineering",

            fix_action=
                "Add hiring or attrition events "
                "if workforce interventions "
                "are required",

            details={

                "configured_label":
                    "Queues With Events",

                "missing_label":
                    "Queues Without Events",

                "configured_queues":
                    configured_queues,

                "missing_queues":
                    missing_queues
            }
        
        )
    )

    historical_df = pd.read_csv(

        DATASETS[
            "historical_operational_data"
        ]["path"]
    )

    historical_queues = set(

        historical_df["queue"]

        .astype(str)

        .str.strip()

        .str.lower()
    )

    history_covered = (

        master_queues
        & historical_queues
    )
    
    history_missing = sorted(

        master_queues

        - historical_queues
    )    
    
    history_configured = sorted(

        history_covered
    )    

    history_count = len(

        history_covered
    )

    results.append(

        create_validation_result(

            "Model Coverage",

            "info",
            

            (
                f"{history_count} of "

                f"{total_queues} queues have "

                "historical data"
            ),

            fix_location=
                "Dataset Explorer",

            fix_action=
                "Load historical operational data",

            details={

                "configured_label":
                    "Queues With History",

                "missing_label":
                    "Queues Without History",

                "configured_queues":
                    history_configured,

                "missing_queues":
                    history_missing
            }
        )
    ) 

    forecast_df = pd.read_csv(

        DATASETS[
            "resolved_forecast"
        ]["path"]
    )

    forecast_queues = set(

        forecast_df["queue"]

        .astype(str)

        .str.strip()

        .str.lower()
    )

    forecast_covered = (

        master_queues
        & forecast_queues
    )

    forecast_missing = sorted(

        master_queues

        - forecast_queues
    )

    forecast_configured = sorted(

        forecast_covered
    )

    forecast_count = len(

        forecast_covered
    )

    results.append(

        create_validation_result(

            "Model Coverage",

            "info",

            (
                f"{forecast_count} of "

                f"{total_queues} queues have "

                "forecast coverage"
            ),

            fix_location=
                "Forecast Engine",

            fix_action=
                "Generate forecast for missing queues",

            details={

                "configured_label":
                    "Queues With Forecasts",

                "missing_label":
                    "Queues Without Forecasts",

                "configured_queues":
                    forecast_configured,

                "missing_queues":
                    forecast_missing
            }
        )
    )


       

    return results


# =====================================================
# MASTER VALIDATION
# =====================================================

def run_platform_validation(
    DATASETS
):

    results = []

    # ---------------------------------
    # Dataset Health
    # ---------------------------------

    for dataset_name, config in DATASETS.items():

        results.append(

            validate_dataset_exists(

                dataset_name,

                config["path"]
            )
        )

    # ---------------------------------
    # Queue Synchronisation
    # ---------------------------------

    results.extend(

        validate_queue_synchronisation(
            DATASETS
        )
    )

    # ---------------------------------
    # Model Coverage
    # ---------------------------------

    results.extend(

        validate_model_coverage(
            DATASETS
        )
    )

    return results