from dataclasses import dataclass
from typing import List

from Shared.enums import DataType


@dataclass
class ColumnContract:

    name: str

    dtype: DataType

    required: bool = True

    nullable: bool = False


@dataclass
class DatasetContract:

    dataset_name: str

    columns: List[ColumnContract]

    primary_keys: List[str]


# ==========================================================
# HISTORICAL OPERATIONAL DATA CONTRACT
# ==========================================================

HISTORICAL_OPERATIONAL_DATA_CONTRACT = DatasetContract(

    dataset_name="historical_operational_data",

    primary_keys=[
        "date",
        "queue"
    ],

    columns=[

        ColumnContract(
            name="date",
            dtype=DataType.DATE
        ),

        ColumnContract(
            name="queue",
            dtype=DataType.STRING
        ),

        ColumnContract(
            name="historical_demand",
            dtype=DataType.INTEGER
        ),

        ColumnContract(
            name="historical_aht",
            dtype=DataType.FLOAT
        ),

        ColumnContract(
            name="historical_sla",
            dtype=DataType.FLOAT,
            nullable=True
        )
    ]
)

# ==========================================================
# WORKFORCE SUPPLY CONTRACT
# ==========================================================

WORKFORCE_SUPPLY_CONTRACT = DatasetContract(

    dataset_name="workforce_supply",

    primary_keys=[
        "date",
        "queue"
    ],

    columns=[

        ColumnContract(
            name="date",
            dtype=DataType.DATE
        ),

        ColumnContract(
            name="queue",
            dtype=DataType.STRING
        ),

        ColumnContract(
            name="attrition",
            dtype=DataType.FLOAT
        ),

        ColumnContract(
            name="new_hires",
            dtype=DataType.FLOAT
        )
    ]
)

# ==========================================================
# BASELINE FORECAST CONTRACT
# ==========================================================

BASELINE_FORECAST_CONTRACT = DatasetContract(

    dataset_name="baseline_forecast",

    primary_keys=[
        "date",
        "queue"
    ],

    columns=[

        ColumnContract(
            name="date",
            dtype=DataType.DATE
        ),

        ColumnContract(
            name="queue",
            dtype=DataType.STRING
        ),

        ColumnContract(
            name="demand",
            dtype=DataType.FLOAT
        )
    ]
)

# ==========================================================
# QUEUE MASTER CONTRACT
# ==========================================================

QUEUE_MASTER_CONTRACT = DatasetContract(

    dataset_name="queue_master",

    primary_keys=[
        "queue"
    ],

    columns=[

        ColumnContract(
            name="queue",
            dtype=DataType.STRING
        ),

        ColumnContract(
            name="default_aht",
            dtype=DataType.FLOAT
        ),

        ColumnContract(
            name="default_occupancy",
            dtype=DataType.FLOAT
        ),

        ColumnContract(
            name="default_shrinkage",
            dtype=DataType.FLOAT
        )
    ]
)
