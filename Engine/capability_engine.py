import pandas as pd


# -----------------------------
# CAPABILITY ENGINE
# -----------------------------

def calculate_capability_gaps(

    capability_req_df,
    capability_supply_df,
    forecast_df
):

    queue_requirements = (

        forecast_df.groupby("queue")[
            "gross_requirement"
        ]
        .mean()
        .to_dict()
    )

    capability_results = []

    # -------------------------
    # ITERATE REQUIREMENTS
    # -------------------------

    for _, row in capability_req_df.iterrows():

        queue = row["queue"]

        skill_group = row["skill_group"]

        seniority = row["seniority"]

        required_ratio = row["required_ratio"]

        queue_requirement = (
            queue_requirements.get(queue, 0)
        )

        required_fte = (
            queue_requirement
            * required_ratio
        )

        # ---------------------
        # MATCH SUPPLY
        # ---------------------

        supply_match = capability_supply_df[

            (
                capability_supply_df[
                    "queue"
                ]
                == queue
            )

            &

            (
                capability_supply_df[
                    "skill_group"
                ]
                == skill_group
            )

            &

            (
                capability_supply_df[
                    "seniority"
                ]
                == seniority
            )
        ]

        # ---------------------
        # AVAILABLE FTE
        # ---------------------

        if not supply_match.empty:

            available_fte = (

                supply_match[
                    "available_fte"
                ].values[0]
            )

        else:

            available_fte = 0

        # ---------------------
        # GAP
        # ---------------------

        capability_gap = (

            available_fte
            - required_fte
        )

        capability_results.append({

            "queue":
                queue,
            
            "skill_group":
                skill_group,

            "seniority":
                seniority,

            "required_fte":
                round(required_fte, 2),

            "available_fte":
                round(available_fte, 2),

            "capability_gap":
                round(capability_gap, 2)
        })

    capability_df = pd.DataFrame(
        capability_results
    )

    return capability_df