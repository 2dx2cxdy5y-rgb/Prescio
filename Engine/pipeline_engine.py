from Engine.logging_engine import (
    log_info,
    log_error
)

from Engine.audit_engine import (
    record_pipeline_run
)

from datetime import datetime
import time

# -----------------------------
# PIPELINE ENGINE
# -----------------------------

class PlanningPipeline:

    def __init__(self):

        self.steps = []

        self.execution_log = []

    # -------------------------
    # REGISTER STEP
    # -------------------------

    def add_step(
        self,
        step_name,
        step_function,
        dependencies=None
    ):

        if dependencies is None:

            dependencies = []

        self.steps.append({

            "name": step_name,

            "function": step_function,

            "dependencies": dependencies
        })

    # -------------------------
    # EXECUTE PIPELINE
    # -------------------------

    def run(
        self,
        context
    ):

        pipeline_start = time.time()

        executed_steps = set()

        for step in self.steps:

            step_name = step["name"]

            # ---------------------
            # VALIDATE DEPENDENCIES
            # ---------------------

            for dependency in step["dependencies"]:

                if dependency not in executed_steps:

                    raise ValueError(

                        f"Pipeline dependency failure: "
                        f"{step_name} requires "
                        f"{dependency}"
                    )

            log_info(
                f"Running pipeline step: {step_name}"
            )

            step_start = time.time()
            
            step_status = "SUCCESS"

            step_error = None

            try:

                context = step[
                    "function"
                ](context)

            except Exception as error:

                log_error(
                    f"Pipeline step failed: "
                    f"{step_name}"
                )

                log_error(
                    str(error)
                )

                step_status = "FAILED"

                step_error = str(error)

                record_pipeline_run(

                    scenario_name="Baseline",

                    runtime_seconds=(
                        time.time() - pipeline_start
                    ),

                    status="Failed"
                )

                raise

            executed_steps.add(step_name)

            step_duration = (
                time.time() - step_start
            )

            self.execution_log.append({

                "step": step_name,

                "status": step_status,

                "duration_seconds": round(
                    step_duration,
                    4
                ),

                "timestamp": datetime.utcnow(),

                "error": step_error
            })

            log_info(
                f"Completed step: "
                f"{step_name} "
                f"({step_duration:.2f}s)"
            )

        total_duration = (
            time.time() - pipeline_start
        )

        log_info(
            f"Pipeline completed "
            f"({total_duration:.2f}s total)"
        )

        record_pipeline_run(

            scenario_name="Baseline",

            runtime_seconds=total_duration,

            status="Success"
        )

        context["execution_log"] = (
            self.execution_log
        )

        return context