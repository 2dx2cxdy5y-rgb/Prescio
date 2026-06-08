import pandas as pd

from Contracts.dataset_contracts import (

    HISTORICAL_OPERATIONAL_DATA_CONTRACT,

    WORKFORCE_SUPPLY_CONTRACT,

    BASELINE_FORECAST_CONTRACT,

    QUEUE_MASTER_CONTRACT
)

from Governance.validation_engine import (
    validate_dataset
)


# ==========================================================
# UK DATE PARSER
# ==========================================================

def parse_uk_dates(
    dataframe,
    column_name,
    
    require_monday=False
):

    try:

        dataframe[column_name] = (

            pd.to_datetime(

                dataframe[column_name],

                dayfirst=True,

                errors="raise"
            )

            .dt.normalize()
        )

        # ---------------------------------
        # MONDAY VALIDATION
        # ---------------------------------

        if require_monday:

            invalid_dates = dataframe[

                dataframe[
                    column_name
                ].dt.dayofweek != 0
            ]

            if not invalid_dates.empty:

                invalid_list = (

                    invalid_dates[
                        column_name
                    ]

                    .dt.strftime(
                        "%d/%m/%Y"
                    )

                    .tolist()
                )

                raise ValueError(

                    "All planning dates must be "
                    "week commencing Mondays.\n\n"

                    f"Invalid dates:\n"

                    + "\n".join(
                        invalid_list
                    )
                )

        return dataframe

    except ValueError:
        raise

    except Exception as e:

        raise ValueError(

            f"""
Invalid UK date format detected
in column '{column_name}'.

Expected format:
DD/MM/YYYY

Example:
17/08/2026

Original error:
{str(e)}
"""
        )


# ==========================================================
# VALIDATION HELPER
# ==========================================================

def run_validation(
    dataframe,
    contract
):

    validation = validate_dataset(
        df=dataframe,
        contract=contract
    )

    if not validation.passed:

        messages = [

            f"[{issue.severity}] {issue.message}"

            for issue in validation.issues
        ]

        raise ValueError(

            "\n".join(messages)
        )

    return dataframe


# ==========================================================
# HISTORICAL OPERATIONAL DATA
# ==========================================================

def load_historical_operational_data():

    df = pd.read_csv(
        "Data/historical_operational_data.csv"
    )

    df = parse_uk_dates(
        dataframe=df,
        column_name="date",
        
        require_monday=True
    )

    df = run_validation(
        dataframe=df,
        contract=HISTORICAL_OPERATIONAL_DATA_CONTRACT
    )

    return df

# ==========================================================
# HISTORICAL ACTUALS STAGING
# ==========================================================

def load_historical_actuals_staging():

    df = pd.read_csv(
        "Data/historical_actuals_staging.csv"
    )

    df = parse_uk_dates(
        dataframe=df,
        column_name="date",
        
        require_monday=True
    )

    df = run_validation(
        dataframe=df,
        contract=HISTORICAL_OPERATIONAL_DATA_CONTRACT
    )

    return df

# ==========================================================
# WORKFORCE SUPPLY
# ==========================================================

def load_workforce_supply():

    df = pd.read_csv(
        "Data/workforce_supply.csv"
    )

    df = parse_uk_dates(
        dataframe=df,
        column_name="date",
        
        require_monday=True
    )

    df = run_validation(
        dataframe=df,
        contract=WORKFORCE_SUPPLY_CONTRACT
    )

    return df


# ==========================================================
# BASELINE FORECAST
# ==========================================================

def load_baseline_forecast():

    df = pd.read_csv(
        "Data/baseline_forecast.csv"
    )

    df = parse_uk_dates(
        dataframe=df,
        column_name="date",
        
        require_monday=True
    )

    df = run_validation(
        dataframe=df,
        contract=BASELINE_FORECAST_CONTRACT
    )

    return df


# ==========================================================
# QUEUE MASTER
# ==========================================================

def load_queue_master():

    df = pd.read_csv(
        "Data/queue_master.csv"
    )

    df = run_validation(
        dataframe=df,
        contract=QUEUE_MASTER_CONTRACT
    )

    return df