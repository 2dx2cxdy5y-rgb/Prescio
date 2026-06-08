# -----------------------------------
# FORECAST PROFILES
# -----------------------------------

FORECAST_PROFILES = {

    "Strategic": {

        "residual_scale": 0.15,

        "trend_strength": 0.90,

        "seasonality_strength": 0.80,

        "enable_regimes": False,

        "description":
            "Smooth long-range planning forecast"
    },

    "Operational": {

        "residual_scale": 0.35,

        "trend_strength": 1.00,

        "seasonality_strength": 1.00,

        "enable_regimes": False,

        "description":
            "Balanced operational forecast"
    },

    "Volatile": {

        "residual_scale": 0.65,

        "trend_strength": 1.05,

        "seasonality_strength": 1.15,

        "enable_regimes": True,

        "description":
            "High variability operational environment"
    },

    "Stress": {

        "residual_scale": 0.40,

        "trend_strength": 0.85,

        "seasonality_strength": 0.90,

        "enable_regimes": False,

        "negative_bias": -0.05,

        "description":
            "Downside planning scenario"
    },

    "Aggressive Growth": {

        "residual_scale": 0.45,

        "trend_strength": 1.15,

        "seasonality_strength": 1.10,

        "enable_regimes": False,

        "positive_bias": 0.06,

        "description":
            "Expansion / growth planning scenario"
    }
}