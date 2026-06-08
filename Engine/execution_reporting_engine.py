import pandas as pd


# ==========================================================
# EXECUTION SUMMARY
# ==========================================================

def build_execution_summary(
    execution_log
):

    execution_df = pd.DataFrame(
        execution_log
    )

    if execution_df.empty:

        return pd.DataFrame()

    summary = {

        "total_steps": len(execution_df),

        "successful_steps": len(
            execution_df[
                execution_df["status"]
                == "SUCCESS"
            ]
        ),

        "failed_steps": len(
            execution_df[
                execution_df["status"]
                == "FAILED"
            ]
        ),

        "total_runtime_seconds": round(

            execution_df[
                "duration_seconds"
            ].sum(),

            2
        )
    }

    return pd.DataFrame([summary])