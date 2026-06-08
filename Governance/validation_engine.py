from dataclasses import dataclass
from typing import List

import pandas as pd

from Contracts.dataset_contracts import DatasetContract
from Shared.enums import DataType


# ==========================================================
# VALIDATION RESULT OBJECTS
# ==========================================================

@dataclass
class ValidationIssue:

    severity: str

    message: str


@dataclass
class ValidationResult:

    passed: bool

    issues: List[ValidationIssue]


# ==========================================================
# DATA TYPE MAPPING
# ==========================================================

DTYPE_MAP = {

    "object": DataType.STRING,

    "str": DataType.STRING,

    "int64": DataType.INTEGER,

    "float64": DataType.FLOAT,

    "datetime64[ns]": DataType.DATE,

    "datetime64[us]": DataType.DATE
}


# ==========================================================
# MAIN VALIDATION FUNCTION
# ==========================================================

def validate_dataset(
    df: pd.DataFrame,
    contract: DatasetContract
):

    issues = []

    # ------------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # ------------------------------------------------------

    dataframe_columns = set(df.columns)

    required_columns = {
        column.name
        for column in contract.columns
    }

    missing_columns = (
        required_columns
        - dataframe_columns
    )

    for column in missing_columns:

        issues.append(
            ValidationIssue(
                severity="ERROR",
                message=f"Missing column: {column}"
            )
        )

    # ------------------------------------------------------
    # CHECK PRIMARY KEY DUPLICATES
    # ------------------------------------------------------

    duplicate_count = df.duplicated(
        subset=contract.primary_keys
    ).sum()

    if duplicate_count > 0:

        issues.append(
            ValidationIssue(
                severity="ERROR",
                message=(
                    f"{duplicate_count} duplicate "
                    f"primary key rows found"
                )
            )
        )

    # ------------------------------------------------------
    # CHECK NULL VALUES
    # ------------------------------------------------------

    for column in contract.columns:

        if column.nullable:
            continue

        if column.name not in df.columns:
            continue

        null_count = df[column.name].isna().sum()

        if null_count > 0:

            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    message=(
                        f"{column.name} contains "
                        f"{null_count} null values"
                    )
                )
            )

    # ------------------------------------------------------
    # CHECK DATA TYPES
    # ------------------------------------------------------

    for column in contract.columns:

        if column.name not in df.columns:
            continue

        actual_dtype = str(
            df[column.name].dtype
        )

        mapped_dtype = DTYPE_MAP.get(
            actual_dtype
        )

        # --------------------------------------------------
        # ALLOW INTEGERS WHERE FLOAT EXPECTED
        # --------------------------------------------------

        if (
            column.dtype == DataType.FLOAT
            and mapped_dtype == DataType.INTEGER
        ):
            continue

        # --------------------------------------------------
        # STANDARD TYPE CHECK
        # --------------------------------------------------

        if mapped_dtype != column.dtype:

            issues.append(
                ValidationIssue(
                    severity="WARNING",
                    message=(
                        f"{column.name} expected "
                        f"{column.dtype} but got "
                        f"{actual_dtype}"
                    )
                )
            )

    # ------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------

    errors = [
        issue
        for issue in issues
        if issue.severity == "ERROR"
    ]

    return ValidationResult(
        passed=len(errors) == 0,
        issues=issues
    )