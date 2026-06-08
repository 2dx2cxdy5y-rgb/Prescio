import pandas as pd

from Engine.pipeline_engine import (
    PlanningPipeline
)

from Engine.pipeline_steps import (

    overlay_step,
    transformation_step,
    staffing_step,
    repeat_demand_step,
    workforce_step,
    risk_step,
)

from Engine.logging_engine import (
    log_info,
)

from Engine.dataset_registry import (
    DATASETS
)

from Engine.data_ingestion_engine import (
    parse_uk_dates
)

from Engine.historical_normalisation_engine import (
    generate_normalised_history
)

from Engine.data_ingestion_engine import (

    load_baseline_forecast,

    load_workforce_supply,

    load_queue_master
)

from Models.execution_context import (
    create_execution_context
)

from Engine.execution_reporting_engine import (
    build_execution_summary
)

from Engine.forecast_resolution_engine import (
    resolve_forecast_layers
)

# -----------------------------
# PERCENTAGE CONVERSION
# -----------------------------

def convert_percentages_to_decimal(
    dataframe,
    columns
):

    for col in columns:

        if col in dataframe.columns:

            dataframe[col] = (
                pd.to_numeric(
                    dataframe[col],
                    errors="coerce"
                )
                / 100
            )

    return dataframe


# -----------------------------
# MAIN ORCHESTRATION
# -----------------------------

def generate_resolved_forecast():


    # -----------------------------
    # LOAD DATA
    # -----------------------------

    forecast_df = (
        load_baseline_forecast()
    )

    forecast_df["queue"] = (
        forecast_df["queue"]
        .astype(str)
        .str.strip()
        .str.lower()
    )


    forecast_df["date_display"] = (
        forecast_df["date"]
        .dt.strftime("%d/%m/%Y")
    )

    # -----------------------------
    # SCENARIO LAYERS
    # -----------------------------

    layers_df = pd.read_csv(
        DATASETS["scenario_layers"]["path"]
    )

    layers_df = (
        convert_percentages_to_decimal(

            layers_df,

            [
                "impact_value"
            ]
        )
    )

    # -----------------------------
    # WORKFORCE SUPPLY
    # -----------------------------

    supply_df = (
        load_workforce_supply()
    )


    supply_df["date_display"] = (
        supply_df["date"]
        .dt.strftime("%d/%m/%Y")
    )

    # -----------------------------
    # RAMP PROFILES
    # -----------------------------

    ramp_df = pd.read_csv(
        DATASETS["ramp_profiles"]["path"]
    )

    # -----------------------------
    # FINANCIALS
    # -----------------------------

    financial_df = pd.read_csv(
        DATASETS["financial_assumptions"]["path"]
    )

    # -----------------------------
    # TRANSFORMATION
    # -----------------------------



    # -----------------------------
    # PROGRAMME PORTFOLIO
    # -----------------------------

    portfolio_df = pd.read_csv(
        DATASETS["programme_portfolio"]["path"]
    )

    if "queue" in portfolio_df.columns:

        portfolio_df["queue"] = (
            portfolio_df["queue"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    if "start_date" in portfolio_df.columns:

        portfolio_df = parse_uk_dates(
            portfolio_df,
            "start_date"
        )

    if "end_date" in portfolio_df.columns:

        portfolio_df = parse_uk_dates(
            portfolio_df,
            "end_date"
        )

    # -----------------------------
    # QUEUE CONFIG
    # -----------------------------

    queue_config_df = pd.read_csv(
        DATASETS["queue_config"]["path"]
    )

    # -----------------------------
    # BUDGET
    # -----------------------------

    budget_df = pd.read_csv(
        DATASETS["budget"]["path"]
    )

    budget_df = parse_uk_dates(
        budget_df,
        "date"
    )

    budget_df["queue"] = (
        budget_df["queue"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------
    # BUDGET CHANGES
    # -----------------------------

    budget_changes_df = pd.read_csv(
        DATASETS["budget_changes"]["path"]
    )

    budget_changes_df = parse_uk_dates(
        budget_changes_df,
        "date"
    )

    budget_changes_df["queue"] = (
        budget_changes_df["queue"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    print(
        "\nBUDGET CHANGES LOADED\n"
    )

    print(
        budget_changes_df.head()
    )

    # -----------------------------
    # QUEUE MASTER
    # -----------------------------

    queue_master_df = (
        load_queue_master()
    )

    queue_master_df["queue"] = (
        queue_master_df["queue"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------
    # MERGE QUEUE MASTER
    # -----------------------------

    forecast_df = forecast_df.merge(

        queue_master_df,

        on="queue",

        how="left"
    )

    # -----------------------------
    # VALIDATE QUEUE MASTER
    # -----------------------------

    required_queue_fields = [

        "default_aht",
        "default_occupancy",
        "default_shrinkage",
        "default_contracted_hours",
        "default_opening_fte",
        "work_type",
        "concurrency",
        "weekly_open_hours",
        "target_service_level",
        "target_answer_seconds"
    ]

    missing_values = (
        forecast_df[
            required_queue_fields
        ]
        .isnull()
        .any()
    )

    if missing_values.any():

        raise ValueError(

            f"""
    Missing queue master values:

    {missing_values}
    """
        )

    # -----------------------------
    # STANDARDISED FIELDS
    # -----------------------------

    forecast_df["aht_seconds"] = (
        forecast_df["default_aht"]
    )

    forecast_df["occupancy"] = (
        forecast_df["default_occupancy"] / 100
    )

    forecast_df["shrinkage"] = (
        forecast_df["default_shrinkage"] / 100
    )

    forecast_df["contracted_hours_per_week"] = (
        forecast_df["default_contracted_hours"]
    )

    # -----------------------------
    # NUMERIC CONVERSION
    # -----------------------------

    supply_df["attrition"] = (
        supply_df["attrition"].astype(float)
    )

    supply_df["new_hires"] = (
        supply_df["new_hires"].astype(float)
    )

    ramp_df["productivity"] = (
        ramp_df["productivity"].astype(float)
    )

    # -----------------------------
    # FORECAST RESOLUTION
    # -----------------------------

    forecast_df, layer_execution_log = (

        resolve_forecast_layers(
            forecast_df
        )
    )

    # -----------------------------
    # ENTERPRISE FORECAST
    # -----------------------------

    forecast_df["resolved_demand"] = (

        forecast_df[
            "resolved_forecast"
        ]
    )

    # -----------------------------
    # BUILD BUDGET TIMELINE
    # -----------------------------

    # -----------------------------
    # BUILD BUDGET TIMELINE
    # -----------------------------

    budget_timeline_rows = []

    for queue in forecast_df["queue"].unique():

        queue_forecast = (

            forecast_df[
                forecast_df["queue"] == queue
            ][["date"]]

            .copy()
        )

        # -----------------------------
        # BASELINE BUDGET
        # -----------------------------

        baseline_budget = (

            queue_master_df.loc[
                queue_master_df["queue"] == queue,
                "budget_fte"
            ].iloc[0]
        )

        queue_forecast["budgeted_fte_new"] = (
            baseline_budget
        )

        # -----------------------------
        # FUTURE CHANGES
        # -----------------------------

        queue_budget_changes = (

            budget_changes_df[
                budget_changes_df["queue"] == queue
            ]

            .copy()
        )

        if not queue_budget_changes.empty:

            queue_budget_changes = (

                queue_budget_changes

                .sort_values(
                    "date"
                )
            )

            for _, change in (

                queue_budget_changes.iterrows()
            ):

                queue_forecast.loc[

                    queue_forecast["date"]
                    >= change["date"],

                    "budgeted_fte_new"

                ] = change["budget_fte"]

        queue_forecast["queue"] = queue

        budget_timeline_rows.append(
            queue_forecast
        )

    budget_timeline_df = pd.concat(

        budget_timeline_rows,

        ignore_index=True
    )

    if "budgeted_fte_new" in forecast_df.columns:

        forecast_df = forecast_df.drop(
            columns=["budgeted_fte_new"]
        )

    forecast_df = forecast_df.merge(

        budget_timeline_df,

        on=[
            "date",
            "queue"
        ],

        how="left"
    )


    print("\nTIMELINE CHECK\n")

    print(

        forecast_df[
            [
                "date",
                "queue",
                "budgeted_fte_new"
            ]
        ]

        .head(20)

    )


        
    # -----------------------------
    # MERGE BUDGET
    # -----------------------------


    forecast_df = forecast_df.merge(

        budget_df,

        on=[
            "date",
            "queue"
        ],

        how="left"
    )

    # -----------------------------
    # IMPACT LOGS
    # -----------------------------

    impact_log = []

    weekly_impact_log = []

    # -----------------------------
    # FINANCIAL ASSUMPTIONS
    # -----------------------------

    salary_per_fte = float(

        financial_df.loc[
            financial_df["metric"]
            == "salary_per_fte",
            "value"
        ].values[0]
    )

    recruitment_cost_per_hire = float(

        financial_df.loc[
            financial_df["metric"]
            == "recruitment_cost_per_hire",
            "value"
        ].values[0]
    )

    contractor_cost_per_fte = float(

        financial_df.loc[
            financial_df["metric"]
            == "contractor_cost_per_fte",
            "value"
        ].values[0]
    )

    overtime_cost_per_fte = float(

        financial_df.loc[
            financial_df["metric"]
            == "overtime_cost_per_fte",
            "value"
        ].values[0]
    )

    # -----------------------------
    # EXECUTION CONTEXT
    # -----------------------------

    execution_context = (
        create_execution_context()
    )

    log_info(

        f"""
    Execution started:

    Execution ID:
    {execution_context.execution_id}

    Scenario:
    {execution_context.scenario_name}

    Pipeline Version:
    {execution_context.pipeline_version}
    """
    )

    # -----------------------------
    # BUILD PIPELINE CONTEXT
    # -----------------------------

    context = {
        
        "execution_context": execution_context,
        "forecast_df": forecast_df,
        "budget_df": budget_df,
        "layers_df": layers_df,
        "portfolio_df": portfolio_df,
        "supply_df": supply_df,
        "ramp_df": ramp_df,
        "salary_per_fte": salary_per_fte,
        "recruitment_cost_per_hire": recruitment_cost_per_hire,
        "contractor_cost_per_fte": contractor_cost_per_fte,
        "overtime_cost_per_fte": overtime_cost_per_fte,
        "queue_config_df": queue_config_df
    }

    # -----------------------------
    # BUILD PIPELINE
    # -----------------------------

    pipeline = PlanningPipeline()

    pipeline.add_step(

        "historical_normalisation",

        lambda context: (
            generate_normalised_history() or context
        )
    )

    pipeline.add_step(
        "overlay",
        overlay_step
    )

    pipeline.add_step(
        "transformation",
        transformation_step
    )

    pipeline.add_step(
        "staffing",
        staffing_step
    )

    pipeline.add_step(
        "workforce",
        workforce_step
    )

    pipeline.add_step(
        "repeat_demand",
        repeat_demand_step
    )

    pipeline.add_step(
        "risk",
        risk_step
    )

    # -----------------------------
    # EXECUTE PIPELINE
    # -----------------------------

    context = pipeline.run(
        context
    )

    # -----------------------------
    # EXECUTION SUMMARY
    # -----------------------------

    execution_summary_df = (

        build_execution_summary(

            context["execution_log"]
        )
    )

    execution_summary_df.to_csv(

        "Output/execution_summary.csv",

        index=False
    )

    execution_log_df = pd.DataFrame(

        context["execution_log"]
    )

    execution_log_df.to_csv(

        "Output/execution_log.csv",

        index=False
    )

    # -----------------------------
    # EXTRACT OUTPUTS
    # -----------------------------

    forecast_df = context[
        "forecast_df"
    ]


    required_output_columns = [

        "gross_requirement",
        "available_supply",
        "productive_supply",
        "fte_gap"
    ]

    missing_columns = [

        col
        for col in required_output_columns
        if col not in forecast_df.columns
    ]

    if missing_columns:

        raise ValueError(

            f"""
    Missing pipeline outputs:

    {missing_columns}
    """
        )

    portfolio_df = context[
        "portfolio_df"
    ]

    supply_df = context[
        "supply_df"
    ]

    risk_df = context[
        "risk_df"
    ]

    impact_log = context[
        "impact_log"
    ]

    weekly_impact_log = context[
        "weekly_impact_log"
    ]

    # -----------------------------
    # OUTPUT RESULTS
    # -----------------------------

    weekly_impact_df = pd.DataFrame(
        weekly_impact_log
    )

    impact_df = pd.DataFrame(
        impact_log
    )

    # -----------------------------
    # SAFETY FALLBACKS
    # -----------------------------

    if weekly_impact_df.empty:

        log_info(
            "No weekly impacts generated"
        )

    if impact_df.empty:

        log_info(
            "No layer impacts generated"
        )

    # -----------------------------
    # FORMAT IMPACT DATES
    # -----------------------------

    if (

        not weekly_impact_df.empty

        and

        "date" in weekly_impact_df.columns

    ):

        weekly_impact_df["date"] = (

            pd.to_datetime(

                weekly_impact_df["date"],

                errors="coerce",

                dayfirst=True
            )

            .dt.strftime("%d/%m/%Y")
        )


    # -----------------------------
    # FORMAT OUTPUT DATES
    # -----------------------------

    export_forecast_df = forecast_df.copy()

    export_forecast_df["date"] = (

        export_forecast_df["date"]

        .dt.strftime("%d/%m/%Y")
    )


    # -----------------------------
    # SAVE OUTPUTS
    # -----------------------------

    print("\nBEFORE CSV WRITE\n")

    print(

        forecast_df[
            [
                "queue",
                "budgeted_fte_new"
            ]
        ].head(20)

    )

    export_forecast_df.to_csv(

        "output/resolved_forecast.csv",

        index=False
    )

    impact_df.to_csv(

        "output/layer_impacts.csv",

        index=False
    )

    # -----------------------------
    # LOGGING
    # -----------------------------

    log_info(
        "Final forecast generated"
    )

    log_info(
        "Layer impact summary generated"
    )

    log_info(
        "Output files written"
    )

    log_info(

        f"""
    Execution completed:

    Execution ID:
    {execution_context.execution_id}
    """
    )

    log_info(
        "Execution telemetry written"
    )


    print("\nFINAL FORECAST CHECK\n")

    print(

        forecast_df[
            [
                "date",
                "queue",
                "budgeted_fte_new"
            ]
        ].head(20)

    )




    return forecast_df

if __name__ == "__main__":

    generate_resolved_forecast()    