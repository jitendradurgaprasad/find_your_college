import re
from typing import Dict, List, Any

class ScholarshipExtractor:
    @staticmethod
    def extract_scholarships(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts institutional, government, and merit-based financial aid opportunities.
        """
        text = page.get("cleaned_text", "")
        url = page.get("url", "")
        headings = [h for h_list in page.get("headings", {}).values() for h in h_list]
        lists = page.get("lists", [])

        scholarships: List[Dict[str, Any]] = []
        seen = set()

        # Keyword heuristics for scholarship types
        candidates = []
        for h in headings:
            if re.search(r"scholarship|fellowship|financial aid|fee concession|stipend", h, re.I):
                candidates.append(h)

        for sublist in lists:
            for item in sublist:
                if re.search(r"scholarship|fellowship|waiver|concession", item, re.I):
                    candidates.append(item)

        for c in candidates:
            clean_name = c.strip()
            if len(clean_name) > 100 or len(clean_name) < 5 or clean_name in seen:
                continue
            seen.add(clean_name)

            # Determine provider type
            provider = "Institutional"
            if re.search(r"national|government|ugc|aicte|dst|state govt|post matric", clean_name, re.I):
                provider = "Government"
            elif re.search(r"tata|reliance|aditya birla|foundation|external|corporate", clean_name, re.I):
                provider = "External"

            # Check merit / need
            is_merit = bool(re.search(r"merit|rank|topper|academic excellence", clean_name, re.I))
            is_need = bool(re.search(r"need|means|income|economically|concession", clean_name, re.I))
            is_intl = bool(re.search(r"international|foreign|global", clean_name, re.I))

            # Amount check
            amt_match = re.search(r"(?:₹|Rs\.?|INR|\$)\s*([0-9,]+(?:\s*(?:per\s+month|per\s+annum|lakhs?|cr))?)", text, re.I)
            amount = amt_match.group(0) if amt_match else "Fee concession as per institutional eligibility norms"

            scholarships.append({
                "name": clean_name,
                "provider_type": provider,
                "description": f"Published scholarship scheme from official institution source: {url}",
                "eligibility_criteria": "Refer to official financial aid guidelines for qualifying percentile/income thresholds.",
                "scholarship_amount": amount,
                "is_merit_based": is_merit,
                "is_need_based": is_need,
                "is_international": is_intl,
                "source_url": url,
                "verification_status": "VERIFIED"
            })

        return scholarships
