import numpy as np


# -----------------------------------
# REGIME DEFINITIONS
# -----------------------------------

REGIMES = {


    "stable": {

        "volatility": 0.03,
        "drift": 0.000,
    },

    "elevated": {

        "volatility": 0.12,
        "drift": 0.04,
    },

    "incident": {

        "volatility": 0.28,
        "drift": 0.10,
    },

    "recovery": {

        "volatility": 0.10,
        "drift": -0.03,
    }
}

REGIME_LEVELS = {

    "stable": 1.00,

    "elevated": 1.08,

    "incident": 1.18,

    "recovery": 0.95,
}

# -----------------------------------
# TRANSITION MATRIX
# -----------------------------------

TRANSITIONS = {

    "stable": {

        "stable": 0.72,
        "elevated": 0.18,
        "incident": 0.03,
        "recovery": 0.07,
    },

    "elevated": {

        "stable": 0.25,
        "elevated": 0.50,
        "incident": 0.15,
        "recovery": 0.10,
    },

    "incident": {

        "stable": 0.10,
        "elevated": 0.40,
        "incident": 0.25,
        "recovery": 0.25,
    },

    "recovery": {

        "stable": 0.55,
        "elevated": 0.10,
        "incident": 0.05,
        "recovery": 0.30,
    }
}


# -----------------------------------
# NEXT REGIME
# -----------------------------------

def get_next_regime(
    current_regime
):

    transition_probs = TRANSITIONS[
        current_regime
    ]

    next_regime = np.random.choice(

        list(
            transition_probs.keys()
        ),

        p=list(
            transition_probs.values()
        )
    )

    return next_regime


# -----------------------------------
# APPLY REGIME EFFECT
# -----------------------------------

def apply_regime_effect(

    baseline_value,
    regime
):

    config = REGIMES[
        regime
    ]

    shock = np.random.normal(

        config["drift"],
        config["volatility"]
    )

    adjusted_value = (

        baseline_value

        * (
            1 + shock
        )
    )

    return max(
        adjusted_value,
        0
    )