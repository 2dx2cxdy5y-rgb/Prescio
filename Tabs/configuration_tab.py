import streamlit as st
import pandas as pd
import os

from Components.section_header import (
    render_section_header
)

from Components.page_title import (
    render_title
)

from Components.data_editor_container import (
    render_data_editor
)

from Components.help_header import (
    render_help_header
)

# =====================================================
# QUEUE MASTER CONFIGURATION
# =====================================================

def render_queue_master_configuration(

    DATASETS,

    initialise_new_queues,

    run_planning_engine
):

    render_title(

        "Platform Configuration",

        divider=False,

        caption=(
            "Queue master data, "
            "platform configuration, "
            "and structural management."
        )
    )

    # -----------------------------
    # QUEUE MASTER
    # -----------------------------

    render_section_header(
        "Queue Master"
    )

    queue_master_df = pd.read_csv(
        DATASETS["queue_master"]["path"]
    )

    # -----------------------------
    # SAVE CALLBACK
    # -----------------------------

    def save_queue_master_changes(
        edited_df
    ):

        edited_df.to_csv(

            DATASETS["queue_master"]["path"],

            index=False
        )

        initialise_new_queues()

        if run_planning_engine():

            st.success(
                "Queue master updated."
            )

            st.rerun()

    # -----------------------------
    # EDITOR
    # -----------------------------

    render_data_editor(

        dataframe=queue_master_df,

        save_button_label="Save Queue Configuration",

        save_callback=save_queue_master_changes,

        editor_key="queue_master_editor"
    )

# =====================================================
# QUEUE INITIALISATION
# =====================================================

def render_queue_initialisation(

    initialise_new_queues,

    run_planning_engine
):

    render_section_header(
        "Queue Initialisation"
    )

    # -----------------------------
    # INITIALISE BUTTON
    # -----------------------------

    if st.button(
        "Initialise New Queues"
    ):

        initialise_new_queues()

        if run_planning_engine():

            st.success(
                "New queues initialised."
            )

            st.rerun()
    st.divider()

# =====================================================
# FORECAST PROFILE CONFIGURATION
# =====================================================

# =====================================================
# FORECAST PROFILE CONFIGURATION
# =====================================================

def render_forecast_profile_configuration(

    run_planning_engine
):

    render_help_header(

        "Forecast Profile Configuration",

        """

### Forecast Profile Guidance

#### Residual Scale
Controls how much historical operational variability is replayed into the forecast.

#### Trend Strength
Controls amplification or dampening of the structural forecast trend.

#### Seasonality Strength
Controls the intensity of cyclical demand patterns.

#### Enable Regimes
Activates stochastic operational regime behaviour.

#### Positive Bias
Applies a gradual upward adjustment to forecast trajectory.

#### Negative Bias
Applies a gradual downward adjustment to forecast trajectory.

"""
    )

    # -----------------------------------
    # LOAD PROFILE DATASET
    # -----------------------------------

    profile_df = pd.read_csv(
        "Data/forecast_profiles.csv"
    )

    # -----------------------------------
    # SAVE CALLBACK
    # -----------------------------------

    def save_profile_changes(
        edited_df
    ):

        validation_errors = []

        for _, row in edited_df.iterrows():

            profile_name = row["profile"]

            if not (
                0 <= row["residual_scale"] <= 2
            ):

                validation_errors.append(

                    f"{profile_name}: "
                    f"Residual scale must be between 0 and 2."
                )

            if not (
                0 <= row["trend_strength"] <= 2
            ):

                validation_errors.append(

                    f"{profile_name}: "
                    f"Trend strength must be between 0 and 2."
                )

            if not (
                0 <= row["seasonality_strength"] <= 2
            ):

                validation_errors.append(

                    f"{profile_name}: "
                    f"Seasonality strength must be between 0 and 2."
                )

            if not (
                -1 <= row["positive_bias"] <= 1
            ):

                validation_errors.append(

                    f"{profile_name}: "
                    f"Positive bias must be between -1 and 1."
                )

            if not (
                -1 <= row["negative_bias"] <= 1
            ):

                validation_errors.append(

                    f"{profile_name}: "
                    f"Negative bias must be between -1 and 1."
                )

        if validation_errors:

            for error in validation_errors:

                st.error(error)

            return

        edited_df.to_csv(

            "Data/forecast_profiles.csv",

            index=False
        )

        if run_planning_engine():

            st.success(
                "Forecast profiles updated."
            )

            st.rerun()

    # -----------------------------------
    # PROFILE EDITOR
    # -----------------------------------

    edited_df = render_data_editor(

        dataframe=profile_df,

        save_button_label=(
            "Save Forecast Profiles"
        ),

        save_callback=save_profile_changes,

        editor_key="forecast_profile_editor"
    )

    # -----------------------------------
    # PROFILE VALIDATION
    # -----------------------------------

    validation_warnings = []

    for _, row in edited_df.iterrows():

        profile = row["profile"]

        if row["residual_scale"] > 1.0:

            validation_warnings.append(

                f"{profile}: Residual Scale exceeds recommended maximum (1.0)."
            )

        if row["trend_strength"] > 2.0:

            validation_warnings.append(

                f"{profile}: Trend Strength exceeds recommended maximum (2.0)."
            )

        if row["seasonality_strength"] > 2.0:

            validation_warnings.append(

                f"{profile}: Seasonality Strength exceeds recommended maximum (2.0)."
            )

        if row["positive_bias"] > 0.25:

            validation_warnings.append(

                f"{profile}: Positive Bias exceeds recommended maximum (+25%)."
            )

        if row["negative_bias"] < -0.25:

            validation_warnings.append(

                f"{profile}: Negative Bias exceeds recommended minimum (-25%)."
            )

    # -----------------------------------
    # DISPLAY VALIDATION
    # -----------------------------------

    if validation_warnings:

        render_section_header(

            "Forecast Profile Validation",

            divider=False
        )

        for warning in validation_warnings:

            st.warning(
                warning
            )

    else:

        st.success(

            "Forecast profile validation passed."
        )



# =====================================================
# FORECAST CONFIGURATION
# =====================================================

def render_forecast_configuration(

    DATASETS,

    run_planning_engine
):

    render_help_header(

        "Forecast Configuration",

        """

### Forecast Source

Generated Forecast

- Uses Prescio forecasting engine
- Forecast profiles available
- Historical demand drives forecast

---

Imported Forecast

- Uses uploaded forecast file
- Forecast profiles disabled
- Uploaded forecast becomes source of truth

---

### Demand Overlays

Enabled

- Overlay adjustments applied

Disabled

- Forecast used without overlays

"""
    )

    config_df = pd.read_csv(

        DATASETS[
            "forecast_configuration"
        ]["path"]
    )

    queue_config_df = pd.read_csv(

        DATASETS[
            "forecast_queue_config"
        ]["path"]
    )

    forecast_source = (

        config_df.loc[
            0,
            "forecast_source"
        ]
    )

    overlays_enabled = (

        str(

            config_df.loc[
                0,
                "overlays_enabled"
            ]

        ).lower() == "true"
    )

    # ---------------------------------
    # FORECAST SOURCE
    # ---------------------------------

    forecast_source = st.radio(

        "Forecast Source",

        [

            "Generated",

            "Imported",

            "Hybrid"
        ],

    index=[

        "Generated",

        "Imported",

        "Hybrid"

    ].index(

        forecast_source
    )
    )

    if forecast_source == "Hybrid":

        render_section_header(

            "Queue Forecast Sources",

            divider=False
        )

        edited_queue_config = (

            queue_config_df.copy()
        )

        edited_queue_config = st.data_editor(

            edited_queue_config,

            use_container_width=True,

            hide_index=True,

            column_config={

                "forecast_source": st.column_config.SelectboxColumn(

                    "Forecast Source",

                    options=[

                        "Generated",

                        "Imported"
                    ],

                    required=True
                )
            }
        )

    else:

        edited_queue_config = (

            queue_config_df.copy()
        )
        
    imported_forecast_df = pd.read_csv(

        DATASETS[
            "imported_forecast"
        ]["path"]
    )

    imported_queue_config = (

        edited_queue_config[

            edited_queue_config[
                "forecast_source"
            ] == "Imported"
        ]
    )

    configured_imported_queues = set(

        imported_queue_config[
            "queue"
        ]

        .astype(str)

        .str.strip()
    )

    forecast_file_queues = set(

        imported_forecast_df[
            "queue"
        ]

        .astype(str)

        .str.strip()
    )

    missing_imported_queues = (

        configured_imported_queues

        - forecast_file_queues
    )

    unused_imported_queues = (

        forecast_file_queues

        - configured_imported_queues
    )

    render_section_header(

        "Forecast Source Validation",

        divider=False
    )

    if forecast_source == "Generated":

        st.info(

            "Generated Forecast Mode. Forecasts will be generated from historical demand."
        )

    elif forecast_source == "Imported":

        st.info(

            f"Imported Forecast Mode. "

            f"{len(imported_forecast_df)} rows available."
        )

        st.caption(

            f"Queues Found: "

            f"{len(forecast_file_queues)}"
        )

        st.info(
            f"Imported Forecast Mode. "
            f"{len(imported_forecast_df)} rows available."
        )

    else:   # Hybrid

        if not missing_imported_queues:

            st.success(

                "All imported queues have forecasts."
            )

        else:

            st.warning(

                "Missing imported forecasts for: "

                + ", ".join(

                    sorted(
                        missing_imported_queues
                    )
                )
            )
        

        if unused_imported_queues:

            st.info(
                

                "Unused imported forecasts detected: "

                + ", ".join(

                    sorted(
                        unused_imported_queues
                    )
                )
            )

    st.divider()

    uploaded_forecast_file = None

    forecast_upload_valid = True

    forecast_ready_to_save = False

    if forecast_source != "Generated":

        render_section_header(

            "Imported Forecast Upload",

            divider=False
        )

        # ---------------------------------
        # TEMPLATE GENERATION
        # ---------------------------------

        if forecast_source == "Imported":

            queue_master_df = pd.read_csv(

                DATASETS[
                    "queue_master"
                ]["path"]
            )

            template_queues = (

                queue_master_df[
                    "queue"
                ]

                .astype(str)

                .str.strip()

                .unique()
            )

        else:

            template_queues = sorted(

                configured_imported_queues
            )

        template_df = pd.DataFrame({

            "date": [

                "01/06/2026"

            ] * len(template_queues),

            "queue": template_queues,

            "demand": [

                ""

            ] * len(template_queues)

        })

        st.download_button(

            "Download Forecast Template",

            data=template_df.to_csv(
                index=False
            ),

            file_name="forecast_template.csv",

            mime="text/csv"
        )

        st.caption(

            f"Queues Included: {len(template_queues)}"
        )

        st.caption(

            "Download a template matching the current forecast configuration."
        )

        forecast_ready_to_save = False

        uploaded_forecast_file = st.file_uploader(

            "Upload Forecast CSV",

            type=["csv"]
        )

        if uploaded_forecast_file is not None:

            st.success(

                "Forecast file selected."
            )

            uploaded_forecast_df = pd.read_csv(

                uploaded_forecast_file
            )

            if uploaded_forecast_df.empty:

                st.error(

                    "Forecast file contains no forecast rows."
                )

                forecast_upload_valid = False

            required_columns = {

                "date",

                "queue",

                "demand"
            }

            actual_columns = set(

                uploaded_forecast_df.columns
            )

            missing_columns = (

                required_columns

                - actual_columns
            )

            if missing_columns:

                st.error(

                    "Missing columns: "

                    + ", ".join(

                        sorted(
                            missing_columns
                        )
                    )
                )

                forecast_upload_valid = False
                    
            uploaded_forecast_raw_df = (

                uploaded_forecast_df.copy()
            )

            date_validation_pass = True

            try:

                pd.to_datetime(

                    uploaded_forecast_df["date"],

                    format="%d/%m/%Y",

                    errors="raise"
                )

            except Exception:

                date_validation_pass = False

            if date_validation_pass:

                st.success(
                    "Date format valid (DD/MM/YYYY)"
                )

            else:

                st.error(
                    "Invalid date format. Expected DD/MM/YYYY."
                )

            st.caption(

                f"Rows: {len(uploaded_forecast_df)}"
            )

            st.dataframe(

                uploaded_forecast_df,

                use_container_width=True,

                height=250
            )

            uploaded_queues = sorted(

                uploaded_forecast_df[
                    "queue"
                ]

                .astype(str)

                .str.strip()

                .unique()
            )

            st.caption(

                f"Queues Found: {len(uploaded_queues)}"
            )

            st.caption(

                ", ".join(
                    uploaded_queues
                )
            )
    
            uploaded_forecast_df["date"] = pd.to_datetime(

                uploaded_forecast_df["date"],

                dayfirst=True
            )

            forecast_start = (

                uploaded_forecast_df[
                    "date"
                ].min()
            )

            st.caption(

                f"Forecast Start: "
                f"{forecast_start.strftime('%d %b %Y')}"
            )

            forecast_end = (

                uploaded_forecast_df[
                    "date"
                ].max()
            )

            st.caption(

                f"Forecast End: "
                f"{forecast_end.strftime('%d %b %Y')}"
            )

            configured_imported_queues = sorted(

                edited_queue_config.loc[

                    edited_queue_config[
                        "forecast_source"
                    ] == "Imported",

                    "queue"
                ]

                .astype(str)

                .str.strip()

                .unique()
            )

            # ---------------------------------
            # EXPECTED QUEUES
            # ---------------------------------

            if forecast_source == "Imported":

                queue_master_df = pd.read_csv(

                    DATASETS[
                        "queue_master"
                    ]["path"]
                )

                expected_queues = set(

                    queue_master_df[
                        "queue"
                    ]

                    .astype(str)

                    .str.strip()
                )

                st.markdown(
                    "**Expected Forecast Queues**"
                )

                display_queues = sorted(
                    expected_queues
                )

            else:

                expected_queues = set(

                    configured_imported_queues
                )

                st.markdown(
                    "**Configured Imported Queues**"
                )

                display_queues = sorted(
                    configured_imported_queues
                )

            st.caption(

                ", ".join(
                    display_queues
                )
            )

            # ---------------------------------
            # EXPECTED QUEUES
            # ---------------------------------


                
            missing_queues = sorted(

                expected_queues

                -

                set(
                    uploaded_queues
                )
            )

            unexpected_queues = sorted(

                set(
                    uploaded_queues
                )

                -

                expected_queues
            )

            forecast_upload_valid = (

                forecast_upload_valid

                and

                len(missing_queues) == 0

                and

                len(unexpected_queues) == 0
            )

            forecast_ready_to_save = (

                uploaded_forecast_file is not None

                and

                forecast_upload_valid
                
                and 
                
                date_validation_pass
            )

            st.caption(

                f"Forecast Save Ready: "

                f"{'YES' if forecast_ready_to_save else 'NO'}"
            )

            st.markdown(
                "**Forecast Queue Validation**"
            )

            if forecast_upload_valid:

                st.success(

                    "Uploaded forecast matches queue configuration."
                )

            else:

                st.warning(

                    "Uploaded forecast does not match queue configuration."
                )

            if missing_queues:

                st.caption(
                    "Missing Queues:"
                )

                st.caption(
                    ", ".join(
                        missing_queues
                    )
                )

            if unexpected_queues:

                st.caption(
                    "Unexpected Queues:"
                )

                st.caption(
                    ", ".join(
                        unexpected_queues
                    )
                )

            st.caption(

                f"Validation Status: "

                f"{'PASS' if forecast_upload_valid else 'FAIL'}"
            )
                                                                        
    # ---------------------------------
    # OVERLAYS
    # ---------------------------------

    overlays_enabled = st.checkbox(

        "Apply Demand Overlays",

        value=overlays_enabled
    )

    forecast_offset_weeks = st.number_input(

        "Forecast Freeze Horizon (Weeks)",

        min_value=0,

        max_value=52,

        value=int(

            config_df.get(
                "forecast_offset_weeks",
                pd.Series([4])
            ).iloc[0]
        )
    )

    forecast_horizon_weeks = st.number_input(

        "Forecast Horizon (Weeks)",

        min_value=1,

        max_value=104,

        value=int(

            config_df.get(
                "forecast_horizon_weeks",
                pd.Series([52])
            ).iloc[0]
        )
    )

    forecast_green_threshold = st.number_input(

        "Forecast Green Threshold (%)",

        min_value=50,

        max_value=100,

        value=int(
            config_df.loc[
                0,
                "forecast_green_threshold"
            ]
        )
    )

    forecast_amber_threshold = st.number_input(

        "Forecast Amber Threshold (%)",

        min_value=50,

        max_value=100,

        value=int(
            config_df.loc[
                0,
                "forecast_amber_threshold"
            ]
        )
    )

    # ---------------------------------
    # SAVE
    # ---------------------------------

    save_enabled = True

    if uploaded_forecast_file is not None:

        save_enabled = forecast_upload_valid
        
    if st.button(

        "Save Forecast Configuration",

        disabled=not save_enabled
    ):

        if forecast_ready_to_save:

            uploaded_forecast_raw_df.to_csv(

                DATASETS[
                    "imported_forecast"
                ]["path"],

                index=False
            )

            st.success(

                "Imported forecast saved."
            )
            
        pd.DataFrame([{

            "forecast_source":
                forecast_source,

            "overlays_enabled":
                overlays_enabled,

            "forecast_offset_weeks":
                forecast_offset_weeks,

            "forecast_horizon_weeks":
                forecast_horizon_weeks,

            "forecast_green_threshold":
                forecast_green_threshold,

            "forecast_amber_threshold":
                forecast_amber_threshold

        }]).to_csv(



            DATASETS[
                "forecast_configuration"
            ]["path"],

            index=False
        )

        edited_queue_config.to_csv(

            DATASETS[
                "forecast_queue_config"
            ]["path"],

            index=False
        )

        st.success(
            "Forecast configuration saved. Re-run the planning engine to apply changes."
        )

        if run_planning_engine():

            st.success(

                "Forecast configuration updated."
            )

            st.rerun()

    st.divider()
    
    render_section_header(

        "Workforce Configuration",

        divider=False
    )

    render_ramp_profile_configuration(

        DATASETS
    )

    # ---------------------------------
    # SAVE CONFIRMATION
    # ---------------------------------

    if st.session_state.get(

        "ramp_profiles_saved",

        False
    ):

        st.success(

            "Ramp profiles updated successfully."
        )

        st.session_state[
            "ramp_profiles_saved"
        ] = False
        
# =====================================================
# RAMP PROFILE CONFIGURATION
# =====================================================

def render_ramp_profile_configuration(

    DATASETS
):

    render_help_header(

        "Ramp Profile Configuration",

        """

### Ramp Profile Guidance

Ramp profiles define the productivity
of new starters during onboarding.

Week 1 = first week after joining.

1.00 = fully productive.

0.50 = 50% productive.

Each queue can have its own
learning curve.

"""
    )

    # ---------------------------------
    # LOAD RAMP DATA
    # ---------------------------------

    ramp_df = pd.read_csv(

        DATASETS[
            "ramp_profiles"
        ]["path"]
    )

    # ---------------------------------
    # PIVOT FOR DISPLAY
    # ---------------------------------

    pivot_df = (

        ramp_df

        .pivot(

            index="week_since_start",

            columns="queue",

            values="productivity"
        )

        .reset_index()
    )

    pivot_df.columns.name = None

    pivot_df.columns = [

        str(col)

        for col in pivot_df.columns
    ]

    pivot_df = pivot_df.rename(

        columns={

            "week_since_start":
                "Week"
        }
    )

    # ---------------------------------
    # DISPLAY TABLE
    # ---------------------------------

    def save_ramp_profiles(
        edited_df
    ):

        saved_df = (

            edited_df

            .melt(

                id_vars=[
                    "Week"
                ],

                var_name="queue",

                value_name="productivity"
            )
        )

        saved_df = saved_df.rename(

            columns={

                "Week":
                    "week_since_start"
            }
        )

        saved_df = saved_df.sort_values(

            [
                "queue",
                "week_since_start"
            ]
        )

        saved_df.to_csv(

            DATASETS[
                "ramp_profiles"
            ]["path"],

            index=False
        )

        st.session_state[
            "ramp_profiles_saved"
        ] = True

        st.rerun()


    edited_df = render_data_editor(

        dataframe=pivot_df,

        save_button_label=(
            "Save Ramp Profiles"
        ),

        save_callback=save_ramp_profiles,

        editor_key="ramp_profile_editor",

        num_rows="fixed"
    )

    # ---------------------------------
    # RAMP VALIDATION
    # ---------------------------------

    validation_warnings = []

    for column in edited_df.columns:

        if column == "Week":

            continue

        if edited_df[column].max() > 1:

            validation_warnings.append(

                f"{column}: Productivity exceeds 100%."
            )

        if edited_df[column].min() < 0:

            validation_warnings.append(

                f"{column}: Productivity below 0%."
            )

    if validation_warnings:

        render_section_header(

            "Ramp Profile Validation",

            divider=False
        )

        for warning in validation_warnings:

            st.warning(
                warning
            )

    else:

        st.success(

            "Ramp profile validation passed."
        )

    # =====================================================
    # SCENARIO MANAGEMENT
    # =====================================================

def render_scenario_management():

    render_section_header(
        "Scenario Management"
    )

    scenario_folder = (
        "Output/Scenarios"
    )

    if not os.path.exists(
        scenario_folder
    ):

        st.info(
            "No scenarios found."
        )

        return

    scenario_names = sorted(

        [

            file.replace(
                "_forecast.csv",
                ""
            )

            for file in os.listdir(
                scenario_folder
            )

            if file.endswith(
                "_forecast.csv"
            )

        ]
    )

    selected_scenario = st.selectbox(

        "Scenario",

        scenario_names
    )

    if selected_scenario == "Baseline":

        st.info(
            "Baseline cannot be deleted."
        )

        return

    confirm_delete = st.checkbox(

        f"Delete {selected_scenario}"
    )

    if (

        confirm_delete

        and

        st.button(
            "Delete Scenario"
        )

    ):

        forecast_file = (

            f"Output/Scenarios/"
            f"{selected_scenario}_forecast.csv"
        )

        assumption_file = (

            f"Output/Scenarios/"
            f"{selected_scenario}.csv"
        )

        if os.path.exists(
            forecast_file
        ):

            os.remove(
                forecast_file
            )

        if os.path.exists(
            assumption_file
        ):

            os.remove(
                assumption_file
            )

        st.success(

            f"{selected_scenario} deleted."
        )

        st.rerun()
        

# =====================================================
# MAIN TAB RENDERER
# =====================================================

def render_configuration_tab(

    DATASETS,

    initialise_new_queues,

    run_planning_engine
):

    render_queue_master_configuration(

        DATASETS,

        initialise_new_queues,

        run_planning_engine
    )

    render_queue_initialisation(

        initialise_new_queues,

        run_planning_engine
    )

    render_forecast_profile_configuration(

        run_planning_engine
    )

    render_forecast_configuration(

        DATASETS,

        run_planning_engine
    )
    
    render_scenario_management()
    