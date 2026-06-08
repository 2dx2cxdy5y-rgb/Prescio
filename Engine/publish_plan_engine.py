import pandas as pd


def publish_plan():



    resolved_df = pd.read_csv(
        "Output/resolved_forecast.csv"
    )

    print(
        "Resolved rows:",
        len(resolved_df)
    )


    resolved_df.to_csv(
        "Data/published_plan.csv",
        index=False
    )


    snapshot_df = resolved_df.copy()

    snapshot_df["snapshot_date"] = (

        pd.Timestamp.now()

        .strftime("%d/%m/%Y %H:%M:%S")
    )

    history_file = (

        "Data/published_plan_snapshot_history.csv"
    )

    try:

        history_df = pd.read_csv(
            history_file
        )

    except:

        history_df = pd.DataFrame()

    history_df = pd.concat(

        [

            history_df,

            snapshot_df

        ],

        ignore_index=True
    )

    history_df.to_csv(

        history_file,

        index=False
    )


    return {

        "success": True,

        "message":
            "Plan published successfully"
    }
    
if __name__ == "__main__":

    result = publish_plan()

    print(
        result["message"]
    )