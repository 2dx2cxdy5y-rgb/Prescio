import pandas as pd
import os

from datetime import datetime

def validate_historical_data(

    upload_df,

    queue_master_df
):

    required_columns = [

        "date",
        "queue",
        "historical_demand",
        "historical_aht",
        "historical_sla"
    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in upload_df.columns
    ]    
    
    if missing_columns:

        return {

            "valid": False,

            "message": (

                "Missing required columns: "

                + ", ".join(
                    missing_columns
                )
            )
        }


    # -----------------------------------
    # DATE VALIDATION
    # -----------------------------------

    parsed_dates = pd.to_datetime(

        upload_df["date"],

        format="%d/%m/%Y",

        errors="coerce"
    )

    invalid_dates = parsed_dates.isna().sum()

    if invalid_dates > 0:

        return {

            "valid": False,

            "message": (

                f"{invalid_dates} invalid date(s) detected. "

                "Expected format DD/MM/YYYY"
            )
        }
        
    # -----------------------------------
    # QUEUE VALIDATION
    # -----------------------------------

    configured_queues = set(

        queue_master_df["queue"]

        .dropna()

        .astype(str)

        .str.strip()
    )

    uploaded_queues = set(

        upload_df["queue"]

        .dropna()

        .astype(str)

        .str.strip()
    )

    invalid_queues = sorted(

        uploaded_queues

        - configured_queues
    )        
        
    if invalid_queues:

        return {

            "valid": False,

            "message": (

                "Unknown queue(s): "

                + ", ".join(
                    invalid_queues
                )
            )
        }

    # -----------------------------------
    # TIMELINE VALIDATION
    # -----------------------------------

    weekly_dates = (

        parsed_dates

        .dropna()

        .sort_values()

        .unique()
    )

    expected_dates = pd.date_range(

        start=min(weekly_dates),

        end=max(weekly_dates),

        freq="W-MON"
    )

    missing_dates = sorted(

        set(expected_dates)

        - set(weekly_dates)
    )

    warning_message = None

    if missing_dates:

        warning_message = (

            f"{len(missing_dates)} week(s) missing "
            "from historical timeline"
        )

    # -----------------------------------
    # DUPLICATE VALIDATION
    # -----------------------------------

    duplicate_rows = (

        upload_df

        .duplicated(

            subset=[

                "date",

                "queue"
            ],

            keep=False
        )
    )

    duplicate_details = (

        upload_df.loc[
            duplicate_rows,
            ["date", "queue"]
        ]

        .drop_duplicates()
    )
    
    duplicate_count = (

        duplicate_rows.sum()
    )
    
    if duplicate_count > 0:

        duplicate_examples = [

            f"{row.date} | {row.queue}"

            for row in duplicate_details.head(10).itertuples()
        ]

        return {

            "valid": False,

            "message": (

                f"{duplicate_count} duplicate "

                "date/queue record(s) detected\n\n"

                + "\n".join(
                    duplicate_examples
                )
            )
        }
        
        
        
    return {

        "valid": True,

        "message": "Validation passed",

        "warning": warning_message
    }
    
def process_historical_actuals(
    upload_df
):

    rows_uploaded = len(
        upload_df
    )

    queues_uploaded = (

        upload_df["queue"]

        .nunique()
    )

    parsed_dates = pd.to_datetime(

        upload_df["date"],

        format="%d/%m/%Y",

        errors="coerce"
    )

    start_date = (

        parsed_dates.min()

        .strftime("%d/%m/%Y")
    )

    end_date = (

        parsed_dates.max()

        .strftime("%d/%m/%Y")
    )

    timestamp = (

        pd.Timestamp.now()

        .strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

    audit_record = pd.DataFrame([{

        "timestamp": timestamp,

        "rows_uploaded": rows_uploaded,

        "queues_uploaded": queues_uploaded,

        "start_date": start_date,

        "end_date": end_date
    }])

    audit_file = (

        "Data/historical_upload_audit.csv"
    )

    if os.path.exists(
        audit_file
    ):

        audit_df = pd.read_csv(
            audit_file
        )

    else:

        audit_df = pd.DataFrame(

            columns=[

                "timestamp",

                "rows_uploaded",

                "queues_uploaded",

                "start_date",

                "end_date"
            ]
        )

    audit_df = pd.concat(

        [

            audit_df,

            audit_record

        ],

        ignore_index=True
    )
    
    audit_df.to_csv(

        "Data/historical_upload_audit.csv",

        index=False
    )    



    # -----------------------------------
    # SAVE HISTORICAL DATA
    # -----------------------------------

    upload_df.to_csv(

        "Data/historical_actuals_staging.csv",

        index=False
    )
    
    audit_df.to_csv(

        audit_file,

        index=False
    )
    
    return {

        "success": True,

        "message": (

            "Historical actuals uploaded to staging successfully"
        )
    }    
    
def reset_staging_from_production():

    production_df = pd.read_csv(

        "Data/historical_operational_data.csv"
    )

    production_df.to_csv(

        "Data/historical_actuals_staging.csv",

        index=False
    )

    return {

        "success": True,

        "message": (

            "Staging reset from production"
        )
    }
    
def promote_staging_to_production():

    production_file = (
        "Data/historical_operational_data.csv"
    )

    staging_file = (
        "Data/historical_actuals_staging.csv"
    )
    
    timestamp = (

        datetime.now()

        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    archive_file = (

        "Data/Archive/"

        f"historical_operational_data_"

        f"{timestamp}.csv"
    )
    
    production_df = pd.read_csv(
        production_file
    )

    production_df.to_csv(

        archive_file,

        index=False
    )
    
    staging_df = pd.read_csv(
        staging_file
    )

    staging_df.to_csv(

        production_file,

        index=False
    )
    
    return {

        "success": True,

        "message": (

            "Staging promoted to production"
        )
    }