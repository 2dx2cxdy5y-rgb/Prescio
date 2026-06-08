import pandas as pd

from Engine.dataset_registry import (
    DATASETS
)

from Engine.workforce_engine import (
    calculate_available_supply,
    calculate_productive_supply,
    calculate_fte_gap
)

from Engine.staffing_engine import (
    calculate_staffing_requirements
)

from Engine.risk_engine import (
    calculate_risk
)

from Engine.transformation_engine import (
    apply_transformation_benefits
)

from Engine.overlay_engine import (
    apply_scenario_layers
)

from Engine.validation_engine import (
    validate_columns
)
from Engine.schema_engine import (
    validate_schema
)

# -----------------------------
# OVERLAY STEP
# -----------------------------

def overlay_step(context):
    validate_columns(

    context["forecast_df"],

    [
        "date",
        "queue",
        "resolved_demand"
    ],  

    "forecast_df"
    )

    layers_df = pd.read_csv(

        DATASETS[
            "forecast_layers"
        ]["path"]
    )

    validate_columns(

        layers_df,

        [
            "layer_name",
            "priority",
            "layer_type",
            "compounding_mode",
            "active"
        ],

        "layers_df"
    )

    validate_schema(
        context["forecast_df"],
        "forecast_df"
    )

    validate_schema(
        layers_df,
        "layers_df"
    )

    context["layers_df"] = layers_df
    
    forecast_df, impact_log = (

        apply_scenario_layers(

            context["forecast_df"],
            context["layers_df"]
        )
    )

    print(forecast_df.columns.tolist())

    context["forecast_df"] = (
        forecast_df
    )

    context["impact_log"] = (
        impact_log
    )

    return context

# -----------------------------
# TRANSFORMATION STEP
# -----------------------------

def transformation_step(context):

    validate_schema(
        context["portfolio_df"],
        "portfolio_df"
    )
    
    validate_columns(

        context["forecast_df"],

        [
            "resolved_demand"
        ],

        "forecast_df"
    )

    forecast_df = (

        apply_transformation_benefits(

            context["forecast_df"],
            context["portfolio_df"]
        )
    )

    context["forecast_df"] = (
        forecast_df
    )
    
    forecast_df["productivity_gain"] = (
        forecast_df["productivity_gain"]
        .fillna(0)
    )

    forecast_df[
        "effective_productive_hours"
    ] = (

        forecast_df[
            "contracted_hours_per_week"
        ]

        * (
            1 - forecast_df["shrinkage"]
        )

        * (
            1
            + (
                forecast_df[
                    "productivity_gain"
                ]
            )
        )
    )

    context["forecast_df"] = forecast_df

    return context  
# -----------------------------
# STAFFING STEP
# -----------------------------

def staffing_step(context):
    validate_columns(

        context["forecast_df"],

        [
            "effective_aht",
            "effective_productive_hours"
        ],

        "forecast_df"
    )
    context["forecast_df"] = (

        calculate_staffing_requirements(

            context["forecast_df"],

        )
    )

    return context

# -----------------------------
# REPEAT DEMAND STEP
# -----------------------------

def repeat_demand_step(
    context
):

    forecast_df = context[
        "forecast_df"
    ].copy()

    # -------------------------
    # SORT DATA
    # -------------------------

    forecast_df = forecast_df.sort_values(

        [
            "queue",
            "date"
        ]
    )

    # -------------------------
    # INITIALISE
    # -------------------------

    forecast_df[
        "repeat_demand"
    ] = 0.0

    # -------------------------
    # PROCESS EACH QUEUE
    # -------------------------

    for queue in forecast_df[
        "queue"
    ].unique():

        queue_mask = (
            forecast_df["queue"]
            == queue
        )

        queue_df = (
            forecast_df[
                queue_mask
            ].copy()
        )

        queue_df = (
            queue_df.sort_values(
                "date"
            )
        )

        for i in range(
            len(queue_df) - 1
        ):

            current_index = (
                queue_df.index[i]
            )

            next_index = (
                queue_df.index[i + 1]
            )

            requirement = float(

                forecast_df.loc[
                    current_index,
                    "gross_requirement"
                ]
            )

            supply = float(

                forecast_df.loc[
                    current_index,
                    "available_supply"
                ]
            )

            demand = float(

                forecast_df.loc[
                    current_index,
                    "resolved_demand"
                ]
            )

            # ---------------------
            # ONLY UNDERSTAFFING
            # ---------------------

            gap = (
                supply - requirement
            )

            if gap >= 0:

                continue

            # ---------------------
            # STRESS RATIO
            # ---------------------

            stress_ratio = min(

                abs(gap)
                / max(requirement, 1),

                1
            )

            # ---------------------
            # REPEAT RATE
            # ---------------------

            repeat_rate = min(

                (
                    stress_ratio
                    ** 1.5
                ) * 0.15,

                0.15
            )

            # ---------------------
            # REPEAT DEMAND
            # ---------------------

            repeat_contacts = (
                demand
                * repeat_rate
            )

            # ---------------------
            # APPLY TO NEXT WEEK
            # ---------------------

            forecast_df.loc[
                next_index,
                "repeat_demand"
            ] += repeat_contacts

            forecast_df.loc[
                next_index,
                "resolved_demand"
            ] += repeat_contacts

    context[
        "forecast_df"
    ] = forecast_df

    return context

# -----------------------------
# WORKFORCE STEP
# -----------------------------

def workforce_step(context):
    validate_schema(
        context["supply_df"],
        "supply_df"
    )
    
    validate_columns(

        context["supply_df"],

        [
            "date",
            "queue",
            "attrition",
            "new_hires"
        ],

        "supply_df"
    )
    context["supply_df"] = (

    calculate_available_supply(

        context["forecast_df"],
        context["supply_df"],

    )
    
)

    context["forecast_df"]["requirement_vs_budget"] = (

        context["forecast_df"]["gross_requirement"]

        - context["forecast_df"]["budgeted_fte_new"]

    ).round(2)

    print(
        context["forecast_df"][
            [
                "gross_requirement",
                "budgeted_fte_new",
                "requirement_vs_budget"
            ]
        ].head()
    )

    # -----------------------------------
    # REMOVE OLD SUPPLY COLUMN
    # -----------------------------------

    if "available_supply" in context["forecast_df"].columns:

        context["forecast_df"] = (
            context["forecast_df"]
            .drop(
                columns=["available_supply"]
            )
        )

    # -----------------------------------
    # MERGE NEW SUPPLY
    # -----------------------------------

    context["forecast_df"] = (
        context["forecast_df"].merge(

            context["supply_df"][
                [
                    "queue",
                    "date",
                    "available_supply",
                    "new_hires",
                    "manual_attrition",
                    "structural_attrition",
                    "total_attrition",
                    "attrition"
                ]
            ],

            on=["date", "queue"],
            how="left"
        )
    )

    context["forecast_df"][
        "available_supply"
    ] = (

        context["forecast_df"][
            "available_supply"
        ]

        .fillna(0)
    )

    for column in [

        "new_hires",

        "manual_attrition",

        "structural_attrition",

        "total_attrition",

        "attrition"
    ]:

        context["forecast_df"][column] = (

            context["forecast_df"][column]

            .fillna(0)
        )

    for column in [

        "new_hires",

        "manual_attrition",

        "structural_attrition",

        "total_attrition"
    ]:

        context["forecast_df"][column] = (

            context["forecast_df"][column]

            .fillna(0)
        )

    context["forecast_df"] = (

        calculate_productive_supply(

            context["forecast_df"],
            context["supply_df"],
            context["ramp_df"]
        )
    )
    context["forecast_df"][
    "productive_supply"
    ] = (

    context["forecast_df"][
        "productive_supply"
    ]

    .fillna(0)
)
    context["forecast_df"] = (

        calculate_fte_gap(
            context["forecast_df"]
        )
    )

    context["forecast_df"]["budget_variance"] = (

        context["forecast_df"]["available_supply"]

        - context["forecast_df"]["budgeted_fte_new"]

    ).round(2)

    context["forecast_df"]["requirement_vs_budget"] = (

        context["forecast_df"]["gross_requirement"]
        
        - context["forecast_df"]["budgeted_fte_new"]


    ).round(2)

    weekly_impact_log = []

    for _, row in context["supply_df"].iterrows():

        if row["new_hires"] > 0:

            weekly_impact_log.append({

                "date": row["date"],
                
                "queue": row["queue"],

                "impact_type": "Workforce",

                "driver": "Hiring",

                "effect": (
                    f"+{row['new_hires']} hires"
                )
            })

        if row["attrition"] > 0:

            weekly_impact_log.append({

                "date": row["date"],
                
                "queue": row["queue"],

                "impact_type": "Workforce",

                "driver": "Attrition",

                "effect": (
                    f"-{row['attrition']} attrition"
                )
            })

    context["weekly_impact_log"] = (
        weekly_impact_log
    )    
    return context

# -----------------------------
# RISK STEP
# -----------------------------

def risk_step(context):

    validate_columns(

        context["forecast_df"],

        [
            "fte_gap",
            "requirement_vs_budget"
        ],

        "forecast_df"
    )

    context["risk_df"] = (

        calculate_risk(

            context["forecast_df"]
        )
    )

    return context

