from dataclasses import dataclass

from datetime import datetime

import uuid


# ==========================================================
# EXECUTION CONTEXT
# ==========================================================

@dataclass
class ExecutionContext:

    execution_id: str

    scenario_name: str

    pipeline_version: str

    run_timestamp: datetime


# ==========================================================
# FACTORY
# ==========================================================

def create_execution_context(

    scenario_name="baseline",

    pipeline_version="1.0"

):

    return ExecutionContext(

        execution_id=str(uuid.uuid4()),

        scenario_name=scenario_name,

        pipeline_version=pipeline_version,

        run_timestamp=datetime.utcnow()
    )