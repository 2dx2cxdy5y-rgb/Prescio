import streamlit as st

from Components.section_header import (
    render_section_header
)

from Components.page_title import (
    render_title
)

from Components.kpi_strip import (
    render_kpi_strip
)

from Engine.validation_engine import (
    run_platform_validation
)

def render_validation_tab(
    DATASETS
):
    validation_results = (

        run_platform_validation(
            DATASETS
        )
    )
    
    passed = len([

        r

        for r in validation_results

        if r["status"] == "pass"
    ])

    warnings = len([

        r

        for r in validation_results

        if r["status"] == "warning"
    ])

    critical = len([

        r

        for r in validation_results

        if r["status"] == "critical"
    ])
    
    render_title(
        "Workbench Health",
        divider=False
    )

    render_kpi_strip([

        {
            "label": "Passed",
            "value": passed
        },

        {
            "label": "Warnings",
            "value": warnings
        },

        {
            "label": "Critical",
            "value": critical
        }
    ])
    






    dataset_results = [

        r

        for r in validation_results

        if r["category"]
        == "Dataset Health"
    ]

    sync_results = [

        r

        for r in validation_results

        if r["category"]
        == "Queue Synchronisation"
    ]

    coverage_results = [

        r

        for r in validation_results

        if r["category"]
        == "Model Coverage"
    ]
    
    col1, col2, col3 = st.columns(3)    
    
    dataset_failures = [

        r

        for r in dataset_results

        if r["status"] != "pass"
    ]
    
    with col1:

        render_section_header(
            "Dataset Health",
            divider=False
        )

        if not dataset_failures:

            st.markdown(

                f"🟢 All {len(dataset_results)} datasets available"
            )

        else:

            st.markdown(

                f"🟡 {len(dataset_failures)} dataset issues detected"
            )

            for result in dataset_failures:

                st.markdown(

                    f"• {result['message']}"
                )
    
    with col2:

        render_section_header(
            "Queue Synchronisation",
            divider=False
        )

        for result in sync_results:

            if result["status"] == "pass":

                st.markdown(
                    f"🟢 {result['message']}"
                )

            else:

                st.markdown(
                    f"🟡 {result['message']}"
                )    
        
    with col3:

        render_section_header(
            "Model Coverage",
            divider=False
        )

        if not coverage_results:

            st.caption(
                "No coverage checks configured"
            )

        else:

            for result in coverage_results:

                st.markdown(
                    f"🔵 {result['message']}"
                )

                if result.get(
                    "details"
                ):

                    configured = (

                        result["details"][
                            "configured_queues"
                        ]
                    )

                    missing = (

                        result["details"][
                            "missing_queues"
                        ]
                    )

                    st.caption(

                        result["details"][
                            "configured_label"
                        ]
)

                    st.caption(
                        ", ".join(
                            configured
                        )
                    )

                    st.caption(

                        result["details"][
                            "missing_label"
                        ]
                    )

                    st.caption(
                        ", ".join(
                            missing
                        )
                    )

                    if result["fix_location"]:

                        st.caption(
                            f"Fix: {result['fix_location']}"
                        )

                    if result["fix_action"]:

                        st.caption(
                            f"Action: {result['fix_action']}"
                        )