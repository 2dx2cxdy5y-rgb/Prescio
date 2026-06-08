import pandas as pd

# -----------------------------------
# LOAD FORECAST PROFILES
# -----------------------------------

def load_forecast_profiles():

    profile_df = pd.read_csv(
        "Data/forecast_profiles.csv"
    )

    profiles = {}

    for _, row in profile_df.iterrows():

        profiles[
            row["profile"]
        ] = {

            "residual_scale":
                row["residual_scale"],

            "trend_strength":
                row["trend_strength"],

            "seasonality_strength":
                row["seasonality_strength"],

            "enable_regimes":
                row["enable_regimes"],

            "positive_bias":
                row["positive_bias"],

            "negative_bias":
                row["negative_bias"],

            "description":
                row["description"]
        }

    return profiles