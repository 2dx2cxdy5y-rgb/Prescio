import streamlit as st


PASSWORD = st.secrets["APP_PASSWORD"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    password = st.text_input(
        "Enter Password",
        type="password"
    )

    if password == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()

    st.stop()
    
import pandas as pd
import subprocess
import os
import traceback
import base64
import shutil

from datetime import datetime
from Engine.dataset_registry import (
    DATASETS
)
from Engine.scenario_store import (
    save_scenario,
    load_scenario,
    list_scenarios
)

from Engine.comparison_engine import (
    compare_scenarios
)

from Engine.queue_initialisation_engine import (
    initialise_new_queues
)

from Engine.commentary_engine import (

    generate_executive_commentary,
    generate_budget_commentary,
    generate_workforce_commentary,
    generate_risk_commentary,
    generate_transformation_commentary,
    generate_demand_commentary,
)

from Components.sidebar_panel import (
    open_sidebar_panel,
    close_sidebar_panel
)

from Engine.insight_renderer import (
    render_insight
)

from Engine.workforce_insight_engine import (
    generate_workforce_insights
)

from Engine.insight_prioritisation_engine import (
    prioritise_insights
)

from Engine.aggregation_engine import (
    aggregate_insights
)

from Engine.aggregation_engine import (
    generate_executive_narrative
)

from Tabs.executive_tab import (
    render_executive_tab
)

from Engine.intelligence_pipeline_engine import (
    generate_all_insights
)

from Tabs.workforce_tab import (
    render_workforce_tab
)

from Tabs.transformation_tab import render_transformation_tab

from Tabs.budget_tab import render_budget_tab

from Tabs.demand_tab import render_demand_tab

from Tabs.risk_tab import render_risk_tab

from Tabs.scenario_tab import (
    render_scenario_tab
)

from Tabs.dataset_tab import (
    render_dataset_tab
)

from Tabs.configuration_tab import (
    render_configuration_tab
)

from Components.file_upload_container import (
    render_file_upload
)

from Components.data_editor_container import (
    render_data_editor
)

from Tabs.validation_tab import (
    render_validation_tab
)

from Engine.publish_plan_engine import (
    publish_plan
)

from Engine.active_plan_engine import (
    build_active_plan
)

from Engine.forecast_accuracy_engine import (
    calculate_forecast_accuracy
)

from Engine.narrative_engine import (
    generate_enterprise_outlook,
    generate_queue_health_briefings
)

from Tabs.planning_grid_tab import render_planning_grid



def run_planning_engine():

    # -----------------------------------
    # GENERATE BASELINE FORECAST
    # -----------------------------------

    forecast_profile = st.session_state.get(

        "forecast_profile",

        "Operational"
    )

    forecast_env = os.environ.copy()

    forecast_env[
        "FORECAST_PROFILE"
    ] = forecast_profile

    forecast_result = subprocess.run(

        ["python3", "-m", "Engine.forecast_engine"],

        capture_output=True,

        text=True,

        env=forecast_env
    )

    print(forecast_result.stdout)
    print(forecast_result.stderr)

    if forecast_result.returncode != 0:

        st.error(
            "Forecast engine failed."
        )

        st.code(
            forecast_result.stderr
        )

        return False

    # -----------------------------------
    # RUN SCENARIO ENGINE
    # -----------------------------------

    result = subprocess.run(

        ["python3", "-m", "Engine.scenario_engine"],

        capture_output=True,

        text=True
    )

    if result.returncode != 0:

        error_text = result.stderr

        if (

            "All planning dates must be week commencing Mondays"

            in error_text
        ):

            start = error_text.find(

                "All planning dates must be week commencing Mondays"
            )

            st.error(

                error_text[start:]
            )

        else:

            st.error(
                "Planning engine failed."
            )

            st.code(
                error_text
            )

        return False

    # -----------------------------------
    # BUILD ACTIVE PLAN
    # -----------------------------------

    try:

        build_active_plan()
        
        calculate_forecast_accuracy()

    except Exception as e:

        st.error(
            "Plan finalisation failed."
        )

        st.code(str(e))

        return False

    return True



# -----------------------------------
# VALIDATION FUNCTION
# -----------------------------------

def validate_columns(
    dataframe,
    required_columns
):

    missing_columns = [

        col for col in required_columns

        if col not in dataframe.columns
    ]

    if missing_columns:

        return False, missing_columns

    return True, []

# -----------------------------------
# DATASET QUALITY FUNCTION
# -----------------------------------

# -----------------------------------
# QUEUE FILTER FUNCTION
# -----------------------------------

def filter_queue_data(

    dataframe,

    selected_queue
):

    if selected_queue == "All Queues":

        return dataframe.copy()

    return (

        dataframe[

            dataframe["queue"]
            == selected_queue
        ]

        .copy()
    )

def get_base64_image(image_path):

    with open(image_path, "rb") as img_file:

        return base64.b64encode(
            img_file.read()
        ).decode()

def sidebar_section_header(title):

    st.sidebar.markdown(
        f"""
        <div style="
            font-size:18px;
            font-weight:600;
            color:white;
            margin-top:20px;
            margin-bottom:10px;
        ">
            {title}
        </div>
        """,
        unsafe_allow_html=True
    )
            
# -----------------------------------
# QUEUE NORMALISATION
# -----------------------------------

def normalise_queue_column(

    dataframe,

    column_name="queue"
):

    dataframe[column_name] = (

        dataframe[column_name]

        .astype(str)

        .str.strip()

        .str.lower()
    )

    return dataframe

def dataset_quality_check(

    file_path,
    required_columns
):

    try:

        df = pd.read_csv(file_path)

        row_count = len(df)

        missing_values = (
            df.isnull().sum().sum()
        )

        valid, missing_columns = (
            validate_columns(
                df,
                required_columns
            )
        )

        last_modified = datetime.fromtimestamp(
            os.path.getmtime(file_path)
        ).strftime(
            "%Y-%m-%d %H:%M"
        )

        return {

            "Dataset": os.path.basename(
                file_path
            ),

            "Rows": row_count,

            "Missing Values": int(
                missing_values
            ),

            "Validation": (
                "Valid"
                if valid
                else "Invalid"
            ),

            "Last Updated": last_modified
        }

    except Exception:

        return {

            "Dataset": os.path.basename(
                file_path
            ),

            "Rows": 0,

            "Missing Values": 0,

            "Validation": "Error",

            "Last Updated": "Unknown"
        }

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Prescio",
    page_icon="🅿️",
    layout="wide"
)

st.markdown("""
<style>

section[data-testid="stSidebar"] {
    background-color: #1F2E42;
}

/* Main background */

.stApp {
    background-color: #121B29;
}

/* Content cards */


.prescio-header {

    background: linear-gradient(
        135deg,
        #1F2E42 0%,
        #2A3C54 50%,
        #3A506B 100%
    );

    padding: 40px;

    border-radius: 12px;

    margin-bottom: 30px;
    
    border: 1px solid rgba(255,255,255,0.06);
}

.prescio-title {

    font-size: 62px;

    font-weight: 500;

    letter-spacing: 0px;

    color: white;
}

.prescio-title {

    font-family:
        Inter,
        "Segoe UI",
        system-ui,
        sans-serif;

    font-size: 50px;

    font-weight: 600;

    letter-spacing: 0.5px;

    color: white;

    margin-bottom: 8px;
}

.prescio-version {

    margin-top: 15px;

    display: inline-block;

    padding: 6px 14px;

    border-radius: 20px;

    background-color: #1E3552;

    color: white;

    font-size: 13px;
}

.prescio-context-bar {

    background-color: #132844;

    border-radius: 10px;

    padding: 14px 20px;

    margin-bottom: 25px;

    color: #DCE6F2;

    font-size: 14px;

    font-weight: 500;
}

.prescio-context-label {

    color: #8FB7E8;

    font-weight: 600;
}

</style>
""",
unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------

st.markdown(
    """
    <div class="prescio-header">

    <div class="prescio-title">
        Prescio
    </div>

    <div class="prescio-subtitle">
        Strategic Workforce Planning &
        Operational Intelligence Platform
    </div>

    <div class="prescio-version">
        Version 1.0
    </div>

    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# SIDEBAR BRANDING
# -----------------------------------

st.sidebar.markdown(
    """
    <div style="text-align:center; padding-top:0px; padding-bottom:10px;">
    """,
    unsafe_allow_html=True
)

st.sidebar.image(
    "Assets/prescio_logo.png",
    width=250
)

st.sidebar.markdown(
    """
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# SIDEBAR CONTROLS
# -----------------------------------

# -----------------------------------
# PLATFORM MODE
# -----------------------------------

sidebar_section_header(
    "Platform Mode"
)

platform_mode = st.sidebar.radio(

    "",

    [
        "Intelligence Hub",
        "Planning Workbench"
    ],

    label_visibility="collapsed"
)

# -----------------------------------
# NAVIGATION
# -----------------------------------

sidebar_section_header(
    "Navigation"
)

if platform_mode == "Intelligence Hub":

    selected_page = st.sidebar.radio(
        "",
        [
            "Executive Intelligence",
            "Demand",
            "Workforce",
            "Budget",
            "Risk",
            "Transformation",
            "Scenario Comparison"
        ],
        label_visibility="collapsed"
    )

else:

    selected_page = st.sidebar.radio(
        "",
        [
            "Dataset Explorer",
            "Forecast Engineering",
            "Workforce Engineering",
            "Transformation Engineering",
            "Planning Table",
            "Configuration",
            "Workbench Health",
            "Scenario Comparison"
        ],
        label_visibility="collapsed"
    )
    
# -----------------------------------
# QUEUE SELECTION
# -----------------------------------

queue_master_df = pd.read_csv(
    DATASETS["queue_master"]["path"]
)

queue_master_df = normalise_queue_column(
    queue_master_df
)

available_queues = sorted(
    queue_master_df["queue"].unique()
)

sidebar_section_header(
    "Queue Selection"
)

selected_queue = st.sidebar.selectbox(

    "",

    ["All Queues"] + available_queues,

    label_visibility="collapsed"
)


# -----------------------------------
# QUEUE DEFAULTS
# -----------------------------------

if selected_queue != "All Queues":

    selected_queue_config = (

        queue_master_df[
            queue_master_df["queue"]
            == selected_queue
        ]

        .iloc[0]
    )

    default_aht = int(
        selected_queue_config[
            "default_aht"
        ]
    )

    default_occupancy = int(
        selected_queue_config[
            "default_occupancy"
        ]
    )

    default_shrinkage = int(
        selected_queue_config[
            "default_shrinkage"
        ]
    )
    default_sla = int(
    selected_queue_config[
        "target_service_level"
    ]
    )

    default_answer_seconds = int(
        selected_queue_config[
            "target_answer_seconds"
        ]
    )

    work_type = (
        selected_queue_config[
            "work_type"
        ]
    )
    queue_controls_disabled = False

else:

    default_aht = 600

    default_occupancy = 85

    default_shrinkage = 27

    queue_controls_disabled = True
    default_sla = 80

    default_answer_seconds = 20

    work_type = "mixed"

if platform_mode == "Intelligence Hub":
    queue_controls_disabled = True
    
    
# -----------------------------------
# DEFAULT PARAMETER VALUES
# -----------------------------------

aht_seconds = default_aht

occupancy = default_occupancy

shrinkage = default_shrinkage

sla = default_sla

answer_seconds = default_answer_seconds


# -----------------------------------
# SCENARIO MANAGEMENT PANEL
# -----------------------------------

sidebar_section_header(
    "Scenario Management"
)


# -----------------------------
# LOAD SCENARIO
# -----------------------------

available_scenarios = (
    list_scenarios()
)


selected_scenario = st.sidebar.selectbox(

    "Load Scenario",

    ["None"] + available_scenarios,
    
    label_visibility="collapsed"
)

loaded_scenario = {}

if selected_scenario != "None":

    loaded_scenario = load_scenario(
        selected_scenario
    )

# -----------------------------
# SAVE SCENARIO
# -----------------------------

close_sidebar_panel()

scenario_name = st.sidebar.text_input(
    "Scenario Name",
    value=loaded_scenario.get(
        "scenario_name",
        "Baseline"
    )
)

scenario_description = st.sidebar.text_area(
    "Scenario Description",
    value=loaded_scenario.get(
        "scenario_description",
        ""
    ),
    height=150,
    placeholder="""
Describe the scenario assumptions,
drivers, or operational changes.
"""
)

scenario_assumptions = {

    "aht_seconds": aht_seconds,

    "occupancy": occupancy / 100,

    "shrinkage": shrinkage / 100,

    "target_service_level": (
        sla / 100
        if work_type == "call"
        else None
    ),

    "target_answer_seconds": (
        answer_seconds
        if work_type == "call"
        else None
    )
}



if platform_mode == "Planning Workbench":
    
    # -----------------------------------
    # SCENARIO SAVE FLAG
    # -----------------------------------

    scenario_save_requested = False

    if st.sidebar.button(
        "Save Scenario"
    ):

        save_scenario(

            scenario_name,

            {
                "scenario_name":
                    scenario_name,

                "scenario_description":
                    scenario_description,

                "assumptions":
                    scenario_assumptions
            }
        )

        shutil.copy(

            DATASETS["active_plan"]["path"],

            f"Output/Scenarios/{scenario_name}_forecast.csv"

        )
        
        scenario_save_requested = True
        
        st.sidebar.success(
            f"{scenario_name} saved."
        )


  
    # -----------------------------------
    # RUN ENGINE
    # -----------------------------------

    if st.sidebar.button(
        "Generate Plan"
    ):

        if run_planning_engine():

            st.sidebar.success(
                "Planning Engine Executed"
            )


    if st.sidebar.button(
        "Publish Plan",
        key="sidebar_publish_plan"
    ):

        result = publish_plan()

        st.sidebar.success(
            result["message"]
        )

        st.rerun()

history_df = pd.read_csv(
    "Data/published_plan_snapshot_history.csv"
)

last_published = (
    history_df["snapshot_date"]
    .max()
)

st.sidebar.caption(
    f"Last Published: {last_published}"
)

# -----------------------------------
# LOAD DATA
# -----------------------------------

try:

    active_plan_path = (
        DATASETS["active_plan"]["path"]
    )

    resolved_plan_path = (
        DATASETS["resolved_forecast"]["path"]
    )

    if os.path.exists(
        active_plan_path
    ):

        forecast_df = pd.read_csv(
            active_plan_path
        )

    else:

        forecast_df = pd.read_csv(
            resolved_plan_path
        )

    forecast_df = normalise_queue_column(
        forecast_df
    )
    
    historical_df = pd.read_csv(

        DATASETS[
            "historical_operational_data"
        ]["path"]
    ) 

    historical_df = normalise_queue_column(
        historical_df
    )

    historical_actuals_staging = pd.read_csv(

        DATASETS[
            "historical_actuals_staging"
        ]["path"]
    )

    historical_actuals_staging = (

        normalise_queue_column(
            historical_actuals_staging
        )
    )

    # -----------------------------------
    # FILTER DATA
    # -----------------------------------

    filtered_forecast_df = filter_queue_data(

        forecast_df,

        selected_queue
    )

    filtered_historical_df = filter_queue_data(

        historical_df,

        selected_queue
    )


    # -----------------------------------
    # NORMALISE MERGE KEYS
    # -----------------------------------

    filtered_forecast_df["date"] = pd.to_datetime(
        filtered_forecast_df["date"],
        dayfirst=True,
        errors="coerce"
    ).dt.normalize()

    filtered_historical_df["date"] = pd.to_datetime(
        filtered_historical_df["date"],
        dayfirst=True,
        errors="coerce"
    ).dt.normalize()
    

    # -----------------------------------
    # DISPLAY DATES
    # -----------------------------------

    # -----------------------------------
    # DISPLAY DATES
    # -----------------------------------

    filtered_forecast_df["date_display"] = (

        filtered_forecast_df["date"]

        .dt.strftime("%d/%m/%Y")
    )

    filtered_historical_df["date_display"] = (

        filtered_historical_df["date"]

        .dt.strftime("%d/%m/%Y")
    )


    # -----------------------------------
    # FORECAST VARIANCE BASE
    # -----------------------------------

    forecast_variance_base = (

        filtered_forecast_df

        .groupby(
            ["date", "queue"],
            as_index=False
        )

        .agg({

            "demand": "sum",

            "resolved_forecast": "sum",

            "aht_seconds": "mean",

            "target_service_level": "mean"

        })
    )

    # -----------------------------------
    # HISTORICAL VARIANCE BASE
    # -----------------------------------

    historical_variance_base = (

        filtered_historical_df

        .groupby(
            ["date", "queue"],
            as_index=False
        )

        .agg({

            "historical_demand": "sum",

            "historical_aht": "mean",

            "historical_sla": "mean"

        })
    )

    # -----------------------------------
    # HISTORICAL VARIANCE LAYER
    # -----------------------------------

    variance_df = pd.merge(

        forecast_variance_base,

        historical_variance_base,

        on=["date", "queue"],

        how="left"
    )


    # -----------------------------------
    # DISPLAY DATE
    # -----------------------------------

    variance_df["date_display"] = (

        variance_df["date"]

        .dt.strftime("%d/%m/%Y")
    )

    # -----------------------------------
    # DEMAND VARIANCE
    # -----------------------------------

    variance_df["demand_variance"] = (

        variance_df["resolved_forecast"]

        - variance_df["historical_demand"]
    )

    # -----------------------------------
    # DEMAND VARIANCE %
    # -----------------------------------

    variance_df["demand_variance_pct"] = (

        variance_df["demand_variance"]

        / variance_df["historical_demand"]
            .replace(0, pd.NA)

    ) * 100

    # -----------------------------------
    # AHT VARIANCE
    # -----------------------------------

    variance_df["aht_variance"] = (

        variance_df["aht_seconds"]

        - variance_df["historical_aht"]
    )

    # -----------------------------------
    # SLA VARIANCE
    # -----------------------------------

    variance_df["sla_variance"] = (

        variance_df["target_service_level"]

        - variance_df["historical_sla"]
    )

    # -----------------------------------
    # VALIDATION
    # -----------------------------------

    duplicate_check = variance_df.duplicated(
        subset=["date", "queue"]
    ).sum()

    if duplicate_check > 0:

        st.error(
            f"Variance dataset contains "
            f"{duplicate_check} duplicate rows."
        )


    # -----------------------------------
    # WEEKLY IMPACT DATA
    # -----------------------------------

    if os.path.exists(
        DATASETS["weekly_impacts"]["path"]
    ):

        weekly_impact_df = pd.read_csv(
            DATASETS["weekly_impacts"]["path"]
        )

        forecast_intelligence_df = pd.read_csv(

            DATASETS[
                "forecast_intelligence"
            ]["path"]
        )

    else:

        weekly_impact_df = pd.DataFrame(
            columns=[
                "date",
                "queue",
                "impact_type",
                "driver",
                "effect"
            ]
        )

    # -----------------------------------
    # RISK DATA
    # -----------------------------------

    risk_df = pd.read_csv(
        DATASETS["executive_risk"]["path"]
    )

    # -----------------------------------
    # PORTFOLIO DATA
    # -----------------------------------

    portfolio_df = pd.read_csv(
        DATASETS["programme_portfolio"]["path"]
    )

    # -----------------------------------
    # DATE FORMATTING
    # -----------------------------------

    if not weekly_impact_df.empty:

        weekly_impact_df["date"] = (
            pd.to_datetime(
                weekly_impact_df["date"],
                dayfirst=True,
                errors="coerce"
                
            )
        )

    # -----------------------------------
    # COST
    # -----------------------------------

    if "total_cost" in forecast_df.columns:

        total_cost = (
            forecast_df["total_cost"].sum()
        )

    else:

        total_cost = 0
    # -----------------------------------
    # KPI STRIP
    # -----------------------------------


    overall_risk = (
        risk_df.iloc[0]["overall_risk"]
    )
    # -----------------------------
    # RISK COLOUR STATES
    # -----------------------------

    if overall_risk == "Critical":

        risk_icon = "🔴"

    elif overall_risk == "High":

        risk_icon = "🟠"

    elif overall_risk == "Medium":

        risk_icon = "🟡"

    else:

        risk_icon = "🟢"


    # =====================================
    # GENERATE ENTERPRISE INTELLIGENCE
    # =====================================

    all_insights = generate_all_insights(

        forecast_df,
        filtered_forecast_df,

        selected_queue,

        generate_executive_commentary,
        generate_risk_commentary,
        generate_workforce_insights
    )

    # -----------------------------------
    # TABS
    # -----------------------------------

    if platform_mode == "Intelligence Hub":

        if selected_page == "Executive Intelligence":

            render_executive_tab(

                forecast_df,
                filtered_forecast_df,

                selected_queue,

                generate_executive_commentary,
                generate_risk_commentary,

                prioritise_insights,
                aggregate_insights,

                generate_executive_narrative,

                generate_enterprise_outlook,

                generate_queue_health_briefings,

                render_insight,

                DATASETS,

                weekly_impact_df,

                overall_risk,

                forecast_intelligence_df,

                all_insights
            )
  
        
        
        
        elif selected_page == "Demand":

            render_demand_tab(

                forecast_df,
                filtered_forecast_df,

                filtered_historical_df,

                variance_df,

                selected_queue,

                DATASETS,
                
                validate_columns,

                run_planning_engine,

                generate_demand_commentary,

                render_insight
            )
                
                
                
                
                
                
        elif selected_page == "Workforce":

            render_workforce_tab(

                forecast_df,
                filtered_forecast_df,


                selected_queue,

                generate_workforce_commentary,

                render_insight,

                DATASETS,

                validate_columns,
                run_planning_engine,
                
               mode="intelligence" 
            )



            
        elif selected_page == "Budget":

            render_budget_tab(

                forecast_df,
                filtered_forecast_df,

                selected_queue,

                generate_budget_commentary,

                render_insight
            )
                
            
            
            
            
        elif selected_page == "Risk":

            render_risk_tab(

                forecast_df,
                filtered_forecast_df,

                selected_queue,

                overall_risk,

                risk_df,

                generate_risk_commentary,

                render_insight
            )
                
                
                

        elif selected_page == "Transformation":

            render_transformation_tab(

                forecast_df,
                filtered_forecast_df,

                selected_queue,

                portfolio_df,

                DATASETS,

                validate_columns,

                run_planning_engine,

                generate_transformation_commentary,

                render_insight,

                mode="intelligence"

            )






        elif selected_page == "Scenario Comparison":

            render_scenario_tab(

                list_scenarios,

                load_scenario,

                compare_scenarios
            )
                



    else:



        if selected_page == "Dataset Explorer":

            render_dataset_tab(

                filtered_forecast_df,

                selected_queue,

                DATASETS,
                
                historical_actuals_staging
            )





        elif selected_page == "Forecast Engineering":

            render_demand_tab(

                forecast_df,
                filtered_forecast_df,

                filtered_historical_df,

                variance_df,

                selected_queue,

                DATASETS,
                
                validate_columns,

                run_planning_engine,

                generate_demand_commentary,

                render_insight,

                mode="engineering"
            )






        elif selected_page == "Workforce Engineering":

            render_workforce_tab(

                forecast_df,
                filtered_forecast_df,


                selected_queue,

                generate_workforce_commentary,

                render_insight,

                DATASETS,

                validate_columns,
                run_planning_engine,
                
                mode="engineering"
                
            )





        elif selected_page == "Transformation Engineering":

            render_transformation_tab(

                forecast_df,
                filtered_forecast_df,

                selected_queue,

                portfolio_df,

                DATASETS,

                validate_columns,

                run_planning_engine,

                generate_transformation_commentary,

                render_insight,

                mode="engineering"
            )



        elif selected_page == "Planning Table":

            render_planning_grid(
                forecast_df,
                selected_queue,
                DATASETS
            )

        elif selected_page == "Configuration":

            render_configuration_tab(

                DATASETS,

                initialise_new_queues,

                run_planning_engine
            )
            
        elif selected_page == "Workbench Health":

            render_validation_tab(
                DATASETS
            )            

        elif selected_page == "Scenario Comparison":

            render_scenario_tab(

                list_scenarios,

                load_scenario,

                compare_scenarios
            )                
                
            
            
            
            

except Exception as e:

    st.error(str(e))

    st.code(traceback.format_exc())