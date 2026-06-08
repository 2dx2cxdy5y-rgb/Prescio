import pandas as pd


def build_active_plan():

    published_df = pd.read_csv(
        "Data/published_plan.csv"
    )

    queue_master_df = pd.read_csv(
        "Data/queue_master.csv"
    )

    budget_lookup = dict(

        zip(
            queue_master_df["queue"],
            queue_master_df["budget_fte"]
        )

    )

    if "budget_fte" not in published_df.columns:

        published_df["budget_fte"] = (

            published_df["queue"]
            .map(budget_lookup)

        )

    if "budgeted_fte_new" not in published_df.columns:

        published_df["budgeted_fte_new"] = (

            published_df["queue"]
            .map(budget_lookup)

        )








    resolved_df = pd.read_csv(
        "Output/resolved_forecast.csv"
    )

    config_df = pd.read_csv(
        "Data/forecast_configuration.csv"
    )

    print("\nPUBLISHED COLUMNS\n")
    print(
        published_df.columns.tolist()
    )

    print("\nRESOLVED COLUMNS\n")
    print(
        resolved_df.columns.tolist()
    )

    print("\nPUBLISHED PLAN HAS BUDGET COLUMNS?\n")
    print(
        "budget_fte" in published_df.columns,
        "budgeted_fte_new" in published_df.columns
    )

    print("\nRESOLVED FORECAST HAS BUDGET COLUMNS?\n")
    print(
        "budget_fte" in resolved_df.columns,
        "budgeted_fte_new" in resolved_df.columns
    )

    freeze_weeks = int(

        config_df.loc[
            0,
            "forecast_offset_weeks"
        ]
    )

    published_df["date"] = pd.to_datetime(

        published_df["date"],

        dayfirst=True,

        errors="coerce"
    )

    resolved_df["date"] = pd.to_datetime(

        resolved_df["date"],

        dayfirst=True,

        errors="coerce"
    )

    freeze_dates = sorted(

        published_df["date"]

        .dropna()

        .unique()
    )[:freeze_weeks]

    frozen_df = published_df[

        published_df["date"]

        .isin(freeze_dates)

    ]

    future_df = resolved_df[

        ~resolved_df["date"]

        .isin(freeze_dates)

    ]

    active_df = pd.concat(

        [
            frozen_df,
            future_df
        ],

        ignore_index=True
    )

    active_df = active_df.sort_values(
        "date"
    )

    active_df["date"] = (

        pd.to_datetime(
            active_df["date"]
        )

        .dt.strftime(
            "%d/%m/%Y"
        )
    )

    active_df.to_csv(

        "Data/active_plan.csv",

        index=False
    )

    return {

        "success": True,

        "rows": len(active_df)
    }
    
if __name__ == "__main__":

    result = build_active_plan()

    print(result)