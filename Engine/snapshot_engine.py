import json
import os

from dataclasses import asdict
from datetime import datetime

from Models.insight_schema import Insight

class SnapshotEngine:

    SNAPSHOT_DIR = "Snapshots"

    CURRENT_FILE = (
        f"{SNAPSHOT_DIR}/current_insights.json"
    )

    PREVIOUS_FILE = (
        f"{SNAPSHOT_DIR}/previous_insights.json"
    )
    
    def save_current_snapshot(
        self,
        insights
    ):

        os.makedirs(
            self.SNAPSHOT_DIR,
            exist_ok=True
        )

        # ---------------------------------
        # Move current -> previous
        # ---------------------------------

        if os.path.exists(
            self.CURRENT_FILE
        ):

            if os.path.exists(
                self.PREVIOUS_FILE
            ):
                os.remove(
                    self.PREVIOUS_FILE
                )

            os.rename(
                self.CURRENT_FILE,
                self.PREVIOUS_FILE
            )

        # ---------------------------------
        # Serialize insights
        # ---------------------------------

        serialized = []

        for insight in insights:

            item = asdict(insight)

            # Datetime serialization
            for key, value in item.items():

                if isinstance(
                    value,
                    datetime
                ):
                    item[key] = (
                        value.isoformat()
                    )

            serialized.append(item)

        # ---------------------------------
        # Save current snapshot
        # ---------------------------------

        with open(
            self.CURRENT_FILE,
            "w"
        ) as f:

            json.dump(
                serialized,
                f,
                indent=2
            )
            
    def load_previous_snapshot(self):

        if not os.path.exists(
            self.PREVIOUS_FILE
        ):
            return []

        with open(
            self.PREVIOUS_FILE,
            "r"
        ) as f:

            raw = json.load(f)

        insights = []

        for item in raw:

            # -----------------------------
            # Restore datetime fields
            # -----------------------------

            for field in [
                "created_at",
                "first_seen",
                "last_seen",
                "resolved_at"
            ]:

                if item.get(field):

                    item[field] = (
                        datetime.fromisoformat(
                            item[field]
                        )
                    )

            insights.append(
                Insight(**item)
            )

        return insights            