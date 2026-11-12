from typing import Dict, List, Any, Optional
from datetime import datetime

class ChangeDetector:
    @staticmethod
    def compare_records(
        old_records: List[Dict[str, Any]],
        new_records: List[Dict[str, Any]],
        university_name: str
    ) -> List[Dict[str, Any]]:
        """
        Detects differences between previous snapshots and newly crawled records.
        Categorizes changes into: NEW, MODIFIED, REMOVED.
        """
        old_map = {f"{r.get('category')}_{r.get('field_name')}": r for r in old_records}
        new_map = {f"{r.get('category')}_{r.get('field_name')}": r for r in new_records}

        changes = []
        now = datetime.utcnow()

        # Check for NEW or MODIFIED
        for key, new_rec in new_map.items():
            if key not in old_map:
                changes.append({
                    "university_name": university_name,
                    "category": new_rec.get("category"),
                    "field_name": new_rec.get("field_name"),
                    "change_type": "NEW",
                    "previous_value": None,
                    "current_value": str(new_rec.get("extracted_value")),
                    "detected_at": now,
                    "source_url": new_rec.get("source_url")
                })
            else:
                old_val = str(old_map[key].get("extracted_value", ""))
                new_val = str(new_rec.get("extracted_value", ""))
                if old_val != new_val:
                    changes.append({
                        "university_name": university_name,
                        "category": new_rec.get("category"),
                        "field_name": new_rec.get("field_name"),
                        "change_type": "MODIFIED",
                        "previous_value": old_val,
                        "current_value": new_val,
                        "detected_at": now,
                        "source_url": new_rec.get("source_url")
                    })

        # Check for REMOVED
        for key, old_rec in old_map.items():
            if key not in new_map:
                changes.append({
                    "university_name": university_name,
                    "category": old_rec.get("category"),
                    "field_name": old_rec.get("field_name"),
                    "change_type": "REMOVED",
                    "previous_value": str(old_rec.get("extracted_value")),
                    "current_value": None,
                    "detected_at": now,
                    "source_url": old_rec.get("source_url")
                })

        return changes
