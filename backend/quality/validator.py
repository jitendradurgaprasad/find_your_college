import re
from typing import Dict, Any, Optional
from datetime import datetime

class DataValidator:
    @staticmethod
    def is_valid_email(email: Optional[str]) -> bool:
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def is_valid_phone(phone: Optional[str]) -> bool:
        if not phone:
            return False
        cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
        return len(cleaned) >= 8 and len(cleaned) <= 15 and cleaned.isdigit()

    @staticmethod
    def is_valid_url(url: Optional[str]) -> bool:
        if not url:
            return False
        pattern = r"^https?:\/\/[^\s\/$.?#].[^\s]*$"
        return bool(re.match(pattern, url.strip()))

    @staticmethod
    def calculate_completeness_score(data: Dict[str, Any]) -> float:
        """
        Calculates institutional profile completeness score (0% to 100%).
        Based on presence of essential attributes across 10 critical dimensions.
        """
        checks = [
            bool(data.get("name")),
            bool(data.get("official_website")),
            bool(data.get("institution_type")),
            bool(data.get("country") and data.get("state")),
            bool(data.get("accreditation")),
            bool(data.get("description")),
            bool(data.get("admissions") and len(data["admissions"]) > 0),
            bool(data.get("programs") and len(data["programs"]) > 0),
            bool(data.get("scholarships") and len(data["scholarships"]) > 0),
            bool(data.get("placements") and len(data["placements"]) > 0),
            bool(data.get("faculty") and len(data["faculty"]) > 0),
            bool(data.get("facilities") and len(data["facilities"]) > 0),
            bool(data.get("contact_email") or data.get("contacts"))
        ]
        score = (sum(1 for c in checks if c) / len(checks)) * 100.0
        return round(score, 2)
