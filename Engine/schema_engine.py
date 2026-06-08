# -----------------------------
# DATA SCHEMAS
# -----------------------------

DATA_SCHEMAS = {

    "forecast_df": {

        "required_columns": [

            "date",
            "demand"
        ]
    },

    "layers_df": {

        "required_columns": [

            "layer_name",
            "priority",
            "layer_type",
            "compounding_mode",
            "active"
        ]
    },

    "supply_df": {

        "required_columns": [

            "date",
            "attrition",
            "new_hires"
        ]
    },

    "transformation_df": {

        "required_columns": [

            "date",
            "ai_deflection",
            "productivity_gain"
        ]
    },

    "portfolio_df": {

        "required_columns": [

            "programme",
            "queue",
            "start_date",
            "end_date",
            "ai_deflection",
            "demand_change",
            "aht_change",
            "productivity_gain",
            "occupancy_change",
            "shrinkage_change",
            "delay_weeks",
            "dependency"
        ]
    }
}
# -----------------------------
# VALIDATE SCHEMA
# -----------------------------

def validate_schema(

    dataframe,
    schema_name
):

    schema = DATA_SCHEMAS[
        schema_name
    ]

    required_columns = schema[
        "required_columns"
    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in dataframe.columns
    ]

    if missing_columns:

        raise ValueError(

            f"{schema_name} missing columns: "
            f"{missing_columns}"
        )
        