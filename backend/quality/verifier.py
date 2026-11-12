from typing import Dict, List, Any, Optional
from datetime import datetime

class DataVerifier:
    @staticmethod
    def evaluate_record(
        category: str,
        field_name: str,
        value: Any,
        source_url: str,
        academic_year: Optional[str] = None,
        confidence_score: float = 0.85
    ) -> Dict[str, Any]:
        """
        Evaluates a fact record, assigns verification status, and prepares source tracking.
        """
        if not source_url:
            return {
                "status": "NEEDS_REVIEW",
                "reason": "Missing original source URL"
            }

        if value is None or str(value).strip() == "" or str(value).lower() in ("none", "null", "n/a"):
            return {
                "status": "NEEDS_REVIEW",
                "reason": "Empty or placeholder field value"
            }

        # Check academic year timeliness
        current_year = datetime.now().year
        if academic_year:
            try:
                base_year = int(academic_year.split("-")[0])
                if current_year - base_year > 3:
                    return {
                        "status": "OUTDATED",
                        "reason": f"Information pertains to {academic_year}, older than 3 years."
                    }
            except Exception:
                pass

        if confidence_score < 0.70:
            return {
                "status": "NEEDS_REVIEW",
                "reason": f"Low confidence extraction score ({confidence_score})"
            }

        return {
            "status": "VERIFIED",
            "reason": "Valid source URL and verified content bounds"
        }

    @staticmethod
    def detect_conflicts(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifies if two distinct official sources report contradictory values for the same field.
        Marks both as CONFLICTING and records conflict details.
        """
        grouped = {}
        for r in records:
            key = (r.get("category"), r.get("field_name"), r.get("academic_year"))
            grouped.setdefault(key, []).append(r)

        processed = []
        for key, rec_list in grouped.items():
            if len(rec_list) > 1:
                # Check if values differ across distinct URLs
                unique_values = {rec.get("extracted_value"): rec.get("source_url") for rec in rec_list}
                if len(unique_values) > 1:
                    conflict_summary = "Conflicting values reported across official pages: " + \
                        ", ".join([f"'{v}' from {u}" for v, u in unique_values.items()])
                    for rec in rec_list:
                        rec["verification_status"] = "CONFLICTING"
                        rec["conflict_details"] = {"summary": conflict_summary, "candidates": list(unique_values.keys())}
                        processed.append(rec)
                    continue

            for rec in rec_list:
                processed.append(rec)

        return processed
