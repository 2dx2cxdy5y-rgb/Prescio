from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class Insight:

    # -------------------------------------
    # Core identity
    # -------------------------------------

    id: str
    domain: str
    category: str

    # -------------------------------------
    # Priority
    # -------------------------------------

    severity: str
    priority_score: float = 0.0

    # -------------------------------------
    # Narrative
    # -------------------------------------

    headline: str = ""
    summary: str = ""
    recommendation: str = ""

    # -------------------------------------
    # Context
    # -------------------------------------

    enterprise_context: str = ""
    local_context: str = ""

    # -------------------------------------
    # Metrics
    # -------------------------------------

    metric: Optional[str] = None
    metric_value: Optional[float] = None
    variance: Optional[float] = None

    # -------------------------------------
    # Impact
    # -------------------------------------

    impact_type: Optional[str] = None
    impact_value: float = 0.0

    # -------------------------------------
    # References
    # -------------------------------------

    queue: Optional[str] = None
    scenario: Optional[str] = None
    
    # -------------------------------------
    # Execution Lineage
    # -------------------------------------

    execution_id: Optional[str] = None

    source_engine: Optional[str] = None

    source_pipeline_step: Optional[str] = None    

    # -------------------------------------
    # Metadata
    # -------------------------------------

    tags: List[str] = field(
        default_factory=list
    )

    status: str = "new"

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    root_causes: List[str] = field(
        default_factory=list
    )

    # -------------------------------------
    # Lifecycle Intelligence
    # -------------------------------------

    lifecycle_state: str = "new"

    previous_severity: Optional[str] = None

    previous_metric_value: Optional[float] = None

    delta_value: Optional[float] = None

    delta_percent: Optional[float] = None

    occurrence_count: int = 1

    first_seen: Optional[datetime] = None

    last_seen: Optional[datetime] = None

    resolved_at: Optional[datetime] = None
    
    source_engine: Optional[str] = None

    source_pipeline_step: Optional[str] = None